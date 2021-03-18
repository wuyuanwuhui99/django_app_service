import json
from django.core import serializers
import re
from time import sleep,strftime,localtime,time #时间模块
import datetime
import os
import requests
import json

def format(value):
    if isinstance(value, datetime.datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(value, datetime.date):
        return value.strftime('%Y-%m-%d')
    else:
        return value


#数据库字段名批量转化为驼峰格式
def camel(s):
    s = re.sub(r"(\s|_|-)+", " ", s).title().replace(" ", "")
    return s[0].lower() + s[1:]

# 列表数字字段转驼峰批量转化
def batch_camel_list(slist):
    return [batch_camel_dict(item) for item in slist]

# 数字字典下划线转驼峰
def batch_camel_dict(sDict):
    return {camel(k):v  for k, v in sDict.items()}

def hump2underline(hunp_str):
    p = re.compile(r'([a-z]|\d)([A-Z])')
    sub = re.sub(p, r'\1_\2', hunp_str).lower()
    return sub

# 数字字典驼峰转下划线
def batch_dict_camel(sDict):
    return {hump2underline(k):v  for k, v in sDict.items()}

# 列表数字字段驼峰写法转化下划线
def batch_list_camel(slist):
    return [batch_dict_camel(item) for item in slist]

#把查询的数据编程列表返回
def getJsonByList(lists,status="sucess",msg = ""):
    # result = json.loads(serializers.serialize("json", lists))
    res = []
    for item in lists:
        resultMap = item.resultMap()
        obj = {}
        for key,value in resultMap.items():
            obj[value] = format(getattr(item,key))
        res.append(obj)
    return {
        "data":res,
        "status":status,
        "msg": msg
    }



#返回列表数据第一条
def getJsonByDist(lists,status="sucess",msg = ""):
    result = json.loads(serializers.serialize("json", lists))
    if len(result) > 0:
        result = batch_camel_dict(result[0]["fields"])
    else:
        result = {}
    return {
        "data":result,
        "status":status,
        "msg":msg
    }

#返回json
def getJson(data=None,status="sucess",msg = ""):
    return {
        "data": data,
        "status": status,
        "msg": msg
    }

#把源对象属性值赋值给目标对象,如果attrs为空，这把整个source所有属性赋值给target
#include表示要添加的属性
#exclude表示排除的属性
#extra表示额外要添加的属性
def extend(target,source,include=[],exclude=[],extra={}):
    if len(include) > 0:
        for prop in include:
            if prop in source:
                setattr(target,prop,source[prop])
    else:
        for prop in source :
            if prop not in exclude:
                setattr(target,prop,source[prop])

    for prop in extra:
        setattr(target, prop, extra[prop])

#下载文件
def download(name,path, url,ext="m4a"):
    if url == "":
        return name + "." + ext
    ext = re.sub('\?.*', "", os.path.basename(url).split(".")[-1])
    filename = name + "." + ext
    r = requests.get(url)
    with open(path + filename, 'wb') as f:
        f.write(r.content)
    print("下载文件成功：" + filename + ",时间为：" + strftime('%Y-%m-%d %H:%M:%S', localtime(time())))
    return filename

def now():
    return strftime('%Y-%m-%d %H:%M:%S', localtime(time()))

headers =  {
    "referer":'https://c.y.qq.com/',
    "host": 'c.y.qq.com',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
}

#把jsonp数据替换掉方法名，并转换成json格式
def converToJson(res,name):
    return json.loads(re.sub(name+"\\(|\\)$", " ", res.text))