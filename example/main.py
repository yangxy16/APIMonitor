# /usr/bin/env python3
# -*- coding: utf-8 -*-

from APIMonitor import Monitor

if __name__ == '__main__':

    enableCluster = False
    monitorPath = './apiconfig/'

    if enableCluster:
        redisCluster = [{'host': '10.96.170.30', 'port': '6379'},
                        {'host': '10.96.170.31', 'port': '6379'},
                        {'host': '10.96.170.32', 'port': '6379'}]
    else:
        redisCluster = None

    Monitor(monitorPath, redisCluster).watch()