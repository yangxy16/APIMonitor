#/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
   █████▒█    ██  ▄████▄   ██ ▄█▀       ██████╗ ██╗   ██╗ ██████╗
 ▓██   ▒ ██  ▓██▒▒██▀ ▀█   ██▄█▒        ██╔══██╗██║   ██║██╔════╝
 ▒████ ░▓██  ▒██░▒▓█    ▄ ▓███▄░        ██████╔╝██║   ██║██║  ███╗
 ░▓█▒  ░▓▓█  ░██░▒▓▓▄ ▄██▒▓██ █▄        ██╔══██╗██║   ██║██║   ██║
 ░▒█░   ▒▒█████▓ ▒ ▓███▀ ░▒██▒ █▄       ██████╔╝╚██████╔╝╚██████╔╝
  ▒ ░   ░▒▓▒ ▒ ▒ ░ ░▒ ▒  ░▒ ▒▒ ▓▒       ╚═════╝  ╚═════╝  ╚═════╝
  ░     ░░▒░ ░ ░   ░  ▒   ░ ░▒ ▒░
  ░ ░    ░░░ ░ ░ ░        ░ ░░ ░
           ░     ░ ░      ░  ░
"""
from .MonitorManager import *
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import time
import json
from rediscluster import RedisCluster
import logging
import os
import platform
import math
import uuid
import hashlib
from multiprocessing import cpu_count, freeze_support
from .CommonHttpAPICapture import *
from .WebServiceAPICapture import *

__author__ = 'yangxy16@lenovo.com'

class MonitorImpl( object ):
    def __init__(self, path, cluster_nodes=None):
        self.path = path
        self.redisClusterNodes = cluster_nodes

    def logPath():
        logPath = ''
        try:
            if platform.system() == 'Windows':
                logPath = '.\\Log\\'
            else:
                logPath = './Log/'
            if not os.path.exists(logPath):
                os.makedirs(logPath)
        except:
            pass
        return logPath

    def serializeToJson(lstMonitor, clusterNodes):
        return json.dumps(dict(monitor=lstMonitor, cluster=clusterNodes))

    def monitorObjectCapture(obj, redisCluster):
        obj.task_status = True
        ret_type = RequestType.TYPE_NONE
        for i in range(obj.retry_times):
            ret_type = obj.request()
            if ret_type == RequestType.TYPE_SUCCESS or ret_type == RequestType.TYPE_NONE or ret_type == RequestType.TYPE_DATAERROR:
                break
        time_str = time.strftime('%Y-%m-%dT%H:%M:%S+0800', time.localtime())
        response_time = '{:.2f}'.format(obj.resp_time)
        json_data = json.dumps(
            dict(method=obj.method, url=obj.url, status=obj.resp_status, response_time=response_time,
                 datatime=time_str))
        if redisCluster and ret_type != RequestType.TYPE_SUCCESS and ret_type != RequestType.TYPE_NONE:
            redisCluster.lpush("ESHB:" + obj.url, json_data)
        elif ret_type != RequestType.TYPE_NONE and redisCluster == None:
            logging.info(json_data)
        obj.task_status = False

    def monitorProcessDispatch(jsonData):
        data = json.loads(jsonData)
        lstMonitor = data.get('monitor')
        clusterNodes = data.get('cluster')
        if clusterNodes:
            redisCluster = RedisCluster(startup_nodes=clusterNodes, max_connections=len(lstMonitor), decode_responses=True)
        else:
            redisCluster = None
            md5 = hashlib.md5()
            md5.update(str(uuid.uuid1()).encode('utf-8'))
            filename = MonitorImpl.logPath() + time.strftime('%Y-%m-%d', time.localtime()) + '-' + md5.hexdigest() + '.log'
            logging.basicConfig(level=logging.INFO, format='%(asctime)s,%(message)s', filename=filename)
        monitorObjectList = []
        for v in lstMonitor:
            if v['obj_type'] == ObjectType.TYPE_COMMON_HTTP:
                monitorObjectList.append(CommonHttpObject(v))
            elif v['obj_type'] == ObjectType.TYPE_WEBSERVICE:
                monitorObjectList.append(WebServiceObject(v))
        with ThreadPoolExecutor(max_workers=len(monitorObjectList)) as ThreadPool:
            while True:
                for obj in monitorObjectList:
                    time.sleep(0.1)
                    if obj.enabledTask():
                        ThreadPool.submit(MonitorImpl.monitorObjectCapture, obj, redisCluster)

    def watch( self ):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s,%(message)s',filename=MonitorImpl.logPath() + 'APIMonitor.log')
        logging.info("引擎初始化...")
        try:
            self.monitorObjList = MonitorManager(self.path)
            logging.info("数据加载成功！")
            self.max_process = cpu_count()
            self.dataLen = len(self.monitorObjList)
            if self.dataLen <= 0:
                logging.info("引擎初始化失败")
                return
            if self.max_process > self.dataLen:
                self.max_process = self.dataLen
        except:
            logging.info("引擎初始化失败")
            return

        try:
            freeze_support()
            logging.info("初始化进程池！")
            with ProcessPoolExecutor(max_workers=self.max_process) as ProcessPool:
                fu_list = []
                start, step = 0, 0
                if self.dataLen % self.max_process == 0:
                    step = int(self.dataLen/self.max_process)
                else:
                    step = math.floor( self.dataLen/self.max_process + 1 )
                for i in range(self.max_process):
                    if start + step <= self.dataLen - 1:
                        fu_list.append(ProcessPool.submit(MonitorImpl.monitorProcessDispatch, MonitorImpl.serializeToJson(self.monitorObjList[start:start + step], self.redisClusterNodes)))
                        start += step
                    else:
                        fu_list.append(ProcessPool.submit(MonitorImpl.monitorProcessDispatch, MonitorImpl.serializeToJson(self.monitorObjList[start:], self.redisClusterNodes)))
                        break
                logging.info("引擎初始化成功！")
                for fu in as_completed(fu_list):
                    pass
        except:
            logging.info("引擎初始化失败")