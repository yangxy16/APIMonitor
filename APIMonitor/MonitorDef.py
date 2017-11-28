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
import re
import json
import time
__author__ = 'yangxy16@lenovo.com'

class ObjectType( object ):
    TYPE_NONE           = 0
    TYPE_COMMON_HTTP    = 1     #常规HTTP交互接口
    TYPE_WEBSERVICE     = 2     #Web Service交互接口

class RequestType( object ):
    TYPE_NONE           = -1    #无法处理的异常
    TYPE_SUCCESS        = 0     #无异常
    TYPE_FAILED         = 1     #HTTP状态异常
    TYPE_TIMEOUT        = 2     #超时
    TYPE_DATAERROR      = 3     #返回数据错误

class AssertType( object ):
    TYPE_NONE           = 0
    TYPE_TEXT           = 1
    TYPE_JSON           = 2
    TYPE_XML            = 3

class AssertValue( object ):
    VALUE_ASSERT_NONE    = 0
    VALUE_ASSERT_SUCCESS = 1
    VALUE_ASSERT_FAILED  = 2

class MonitorStatus( object ):
    STATUS_DATAERROR    = 4001
    STATUS_TIMEOUT      = 4002

#监控对象基类
class MonitorObject( object ):
    __slots__ = ('obj_type', 'url', 'retry_times', 'max_response_time', 'delay_time', 'status', 'resp_time', 'resp_status', 'last_finish_time', 'task_status', 'enabled', 'method', 'assert_data', 'assert_type')

    def __init__( self ):
        self.obj_type = ObjectType.TYPE_NONE
        self.url = ''
        self.retry_times = 3
        self.max_response_time = '3s'
        self.delay_time = '5m'
        self.last_finish_time = 0
        self.resp_time = 0
        self.resp_status = 0
        self.task_status = False
        self.enabled = True
        self.status = [200]
        self.method = ''
        self.assert_data = ''
        self.assert_type = AssertType.TYPE_NONE

    def enabledTask( self ):
        return self.enabled and not self.task_status and int(time.time() - self.last_finish_time + 0.5) >= int(self.delay_time)

    @staticmethod
    def formatTime(strTime):
        nPos = strTime.find('h')
        if nPos == -1:
            nPos = strTime.find('m')
            if nPos == -1:
                nPos = strTime.find('s')
                if nPos == -1:
                    strTime = 3
                else:
                    strTime = float(strTime[0:nPos])
            else:
                strTime = float(strTime[0:nPos]) * 60
        else:
            strTime = float(strTime[0:nPos]) * 3600
        return strTime

    @staticmethod
    def formatAssertType(strData):
        if not strData or len(strData) < 5:
            return AssertType.TYPE_NONE, ''
        match = re.match("text:(.*)", strData, re.M | re.I)
        if not match:
            match = re.match("json:(.*)", strData, re.M | re.I)
            if not match:
                match = re.match("xml:(.*)", strData, re.M | re.I)
                if not match:
                    return AssertType.TYPE_NONE, ''
                else:
                    return AssertType.TYPE_XML, match.group(1)
            else:
                return AssertType.TYPE_JSON, match.group(1)
        else:
            return AssertType.TYPE_TEXT, match.group(1)

    @staticmethod
    def assertJsonData(strJsonData, strAssertData):
        if not strAssertData or not isinstance(strAssertData, str) or len(strAssertData) < 2 or strAssertData.find('=') == -1:
            return AssertValue.VALUE_ASSERT_NONE
        try:
            data = json.loads(strJsonData)
            assert_data = strAssertData.split('=', 1)
            assert_value = assert_data[1]
            assert_keystr = assert_data[0]
            if assert_keystr.find('.') != -1:
                assert_keylst = assert_keystr.split('.')
                l = len(assert_keylst)
                for i in range(l):
                    v = data.get(assert_keylst[i], None)
                    if i < l-1:
                        if v == None:
                            return AssertValue.VALUE_ASSERT_FAILED
                        else:
                            data = v
                    else:
                        if v == None or v != assert_value:
                            return AssertValue.VALUE_ASSERT_FAILED
                        else:
                            return AssertValue.VALUE_ASSERT_SUCCESS
            else:
                v = data.get(assert_keystr, None)
                if v == None or v != assert_value:
                    return AssertValue.VALUE_ASSERT_FAILED
                else:
                    return AssertValue.VALUE_ASSERT_SUCCESS
        except:
            return AssertValue.VALUE_ASSERT_NONE

    @staticmethod
    def assertXmlData(strXmlData, strAssertData):
        return AssertValue.VALUE_ASSERT_SUCCESS