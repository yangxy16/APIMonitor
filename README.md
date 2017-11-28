## Use Monitor
* Requere Python >= 3.6.0
* pip3 install https://github.com/yangxy16/APIMonitor/releases/download/v0.1.0/APIMonitor-0.1.0.tar.gz

```
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
```

## Configure Monitor
```
支持按照目录读取多个配置文件，格式如下：
  
1.通用HTTP接口参数说明：
    url                 请求地址
    method              get 或 post 请一律用小写形式
    retry_times         失败重试次数
  
    max_response_time   最大请求时间，超过这个时间则认为该接口响应超时即使接口返回200也会把接口状态置为4001，可以接受的时间参数为
                        h、m、s，分别代表小时、分钟、秒，如1h代表1小时，0.1s代表100毫秒，但是接口的正常响应时间不应该超过3s
  
    status              接口返回状态，可以是一组状态[200,301,302]，也可以单个状态[200]
  
    assert_data         支持简单的接口数据校验功能，目前支持三种类型，text纯文本、json、xml
                        1）纯文本类型格式为 text:文本内容，引擎会对response返回的内容进行校验
                        2）json类型格式为 json:key.key.key=value，目前key支持多层嵌套，但不支持数组
                        3）xml类型格式为 xml:key.key.key=value，但是校验功能尚未完成
  
                        如果数据校验失败则接口状态置为4002，如果该属性设置为空字符串则不对response结果进行校验


    post_msg            接口为post方式是提交的字符串参数
    delay_time          接口探测间隔时间，参数设置同max_response_time，最小0.1s
    enabled             表示是否对接口进行探测
  
2.WebService接口参数说明：
    method              远程WebService的函数名
    params              远程WebService的函数参数，参数个数不限，形式必须是param1~paramN，代表从第1个到第N个参数，有序排列
  
    其他参数同HTTP接口
  
3.示例：
{
    "CommonHttpAPI" : [{
        "url" : "http://www.blue-zero.com/WebSocket/",
        "method" : "get",
        "retry_times" : 3,
        "max_response_time" : "3s",
        "status" : [ 200, 301, 302 ],
        "assert_data" : "text:</html>",
        "post_msg" : "json/xml",
        "delay_time" : "10s",
        "enabled" : true
    }],
    "WebServiceAPI" : [{
        "url" : "http://www.soapclient.com/xml/soapresponder.wsdl",
        "retry_times" : 3,
        "max_response_time" : "0.1s",
        "method" : "Method1",
        "params" : { "param1" : "dayu", "param2" : "is cool"},
        "assert_data" : "text:Your input parameters are dayu and is cool",
        "delay_time" : "10s",
        "enabled" : true
    }]
}
```

## ToDoList
```
1）HTTP接口支持设置自定义HTTP头
2）xml格式数据校验
3）支持事务型接口，即：支持上下文数据，比如调用接口首先需要去请求token，或者该接口的参数依赖于某个接口的返回数据
```