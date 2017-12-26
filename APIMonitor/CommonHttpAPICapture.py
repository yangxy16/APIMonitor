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
import requests as rq
from .MonitorDef import *

__author__ = 'yangxy16@lenovo.com'

# 普通HTTP接口对象
class CommonHttpObject(MonitorObject):
    __slots__ = MonitorObject.__slots__ + ('post_msg', 'custom_header')

    def __init__(self, v):
        super(CommonHttpObject, self).__init__()
        self.url = v['url']
        self.method = v['method']
        self.retry_times = v['retry_times']
        self.max_response_time = v['max_response_time']
        self.status = v['status']
        self.assert_data = v['assert_data']
        self.post_msg = v['post_msg']
        self.delay_time = v['delay_time']
        self.enabled = v['enabled']
        self.obj_type = v['obj_type']
        self.custom_header = v['custom_header']
        self.max_response_time = MonitorObject.formatTime(self.max_response_time)
        self.delay_time = MonitorObject.formatTime(self.delay_time)
        self.assert_type, self.assert_data = MonitorObject.formatAssertType(self.assert_data)

    def request(self):
        start_time = time.time()
        try:
            resp = None
            if self.method == "get":
                resp = rq.get(url=self.url, timeout=self.max_response_time, headers=self.custom_header)
            elif self.method == "post":
                resp = rq.post(url=self.url, data=self.post_msg, timeout=self.max_response_time, headers=self.custom_header)
            self.resp_time = time.time() - start_time
            self.resp_status = resp.status_code
            self.last_finish_time = time.time()
            if self.assert_type == AssertType.TYPE_TEXT:
                if resp.text.find(self.assert_data) == -1:
                    self.resp_status = MonitorStatus.STATUS_DATAERROR
                    return RequestType.TYPE_DATAERROR
            elif self.assert_type == AssertType.TYPE_JSON:
                if MonitorObject.assertJsonData(resp, self.assert_data) != AssertValue.VALUE_ASSERT_SUCCESS:
                    self.resp_status = MonitorStatus.STATUS_DATAERROR
                    return RequestType.TYPE_DATAERROR
            elif self.assert_type == AssertType.TYPE_XML:
                if MonitorObject.assertXmlData(resp, self.assert_data) != AssertValue.VALUE_ASSERT_SUCCESS:
                    self.resp_status = MonitorStatus.STATUS_DATAERROR
                    return RequestType.TYPE_DATAERROR
            for status in self.status:
                if status == self.resp_status:
                    return RequestType.TYPE_SUCCESS
            return RequestType.TYPE_FAILED
        except rq.exceptions.Timeout:
            self.resp_status = MonitorStatus.STATUS_TIMEOUT
            self.resp_time = 0
            self.last_finish_time = time.time() - self.max_response_time
            return RequestType.TYPE_TIMEOUT
        except:
            return RequestType.TYPE_NONE