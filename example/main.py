# /usr/bin/env python3
# -*- coding: utf-8 -*-

from APIMonitor import Monitor

if __name__ == '__main__':

    enableCluster = False
    monitorPath = './apiconfig/'

    if enableCluster:
        redisCluster = [{'host': '127.0.0.1', 'port': '6379'},
                        {'host': '127.0.0.1', 'port': '6380'},
                        {'host': '127.0.0.1', 'port': '6381'}]
    else:
        redisCluster = None

    Monitor(monitorPath, redisCluster).watch()