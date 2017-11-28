# /usr/bin/env python3
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

import json, os
from .MonitorDef import *
__author__ = 'yangxy16@lenovo.com'

COMMON_HTTP_API = 'CommonHttpAPI'
WEB_SERVICE_API = 'WebServiceAPI'

# 监控对象管理器
class MonitorManager(object):
    def __init__(self, path):
        self.obj_list = []
        json_data = ""
        urls = {}
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for file in filenames:
                    fullpath = os.path.join(dirpath, file)
                    with open(fullpath, "rb") as f:
                        json_data = f.read()
                        if json_data and len(json_data) > 10:
                            tblData = json.loads(json_data)
                            if tblData.get(COMMON_HTTP_API, None) != None:
                                for v in tblData[COMMON_HTTP_API]:
                                    if urls.get(v['url'], None) == None:
                                        v['obj_type'] = ObjectType.TYPE_COMMON_HTTP
                                        self.obj_list.append(v)
                            if tblData.get(WEB_SERVICE_API, None) != None:
                                for v in tblData[WEB_SERVICE_API]:
                                    if urls.get(v['url'], None) == None:
                                        v['obj_type'] = ObjectType.TYPE_WEBSERVICE
                                        self.obj_list.append(v)
        except:
            raise ValueError
        urls.clear()

    def __getitem__(self, i):
        return self.obj_list[i]

    def __iter__(self):
        for obj in self.obj_list:
            yield obj

    def __len__(self):
        return len(self.obj_list)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.obj_list and len(self.obj_list) > 0:
            del self.obj_list[:]