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

import time
from .MonitorDef import *
import zeep
import requests as rq

__author__ = 'yangxy16@lenovo.com'

# 普通HTTP接口对象
class WebServiceObject(MonitorObject):
    __slots__ = MonitorObject.__slots__ + ('params',)

    def __init__(self, v):
        super(WebServiceObject, self).__init__()
        self.url = v['url']
        self.method = v['method']
        self.retry_times = v['retry_times']
        self.max_response_time = v['max_response_time']
        self.params = v['params']
        self.assert_data = v['assert_data']
        self.delay_time = v['delay_time']
        self.enabled = v['enabled']
        self.obj_type = v['obj_type']
        self.max_response_time = MonitorObject.formatTime(self.max_response_time)
        self.delay_time = MonitorObject.formatTime(self.delay_time)
        paramsLst = []
        for key in sorted(self.params.keys()):
            paramsLst.append(self.params[key])
        self.params.clear()
        del self.params
        self.params = paramsLst
        self.assert_type, self.assert_data = MonitorObject.formatAssertType(self.assert_data)

    def request(self):
        start_time = time.time()
        try:
            transport = zeep.Transport(cache=None, timeout=self.max_response_time, operation_timeout=self.max_response_time, session=None)
            client = zeep.Client(self.url, transport=transport)
            resp = client.service[self.method](*self.params)
            self.resp_time = time.time() - start_time
            self.resp_status = 200
            self.last_finish_time = time.time()
            if self.assert_type == AssertType.TYPE_TEXT:
                if resp.find(self.assert_data) == -1:
                    self.resp_status = 404
                    return RequestType.TYPE_DATAERROR
            elif self.assert_type == AssertType.TYPE_JSON:
                if MonitorObject.assertJsonData(resp, self.assert_data) != AssertValue.VALUE_ASSERT_SUCCESS:
                    self.resp_status = MonitorStatus.STATUS_DATAERROR
                    return RequestType.TYPE_DATAERROR
            elif self.assert_type == AssertType.TYPE_XML:
                if MonitorObject.assertXmlData(resp, self.assert_data) != AssertValue.VALUE_ASSERT_SUCCESS:
                    self.resp_status = MonitorStatus.STATUS_DATAERROR
                    return RequestType.TYPE_DATAERROR
            return RequestType.TYPE_SUCCESS
        except rq.exceptions.Timeout:
            self.resp_status = MonitorStatus.STATUS_TIMEOUT
            self.resp_time = 0
            self.last_finish_time = time.time() - self.max_response_time
            return RequestType.TYPE_TIMEOUT
        except:
            self.resp_time = time.time() - start_time
            self.resp_status = 404
            self.last_finish_time = time.time()
            return RequestType.TYPE_FAILED