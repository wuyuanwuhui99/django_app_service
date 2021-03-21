import json
from django.core import serializers
from django.http import JsonResponse
from django.forms.models import model_to_dict
import re
from time import strftime,localtime,time #时间模块
import datetime
import os
import requests
import json
from player.config import APP


def format(value):
    if isinstance(value, datetime.datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(value, datetime.date):
        return value.strftime('%Y-%m-%d')
    else:
        return value

def now():
    return strftime('%Y-%m-%d %H:%M:%S', localtime(time()))

def get_time_stamp():
    ct = time()
    local_time = localtime(ct)
    data_head = strftime("%Y-%m-%d %H:%M:%S", local_time)
    data_secs = (ct - int(ct)) * 1000
    time_stamp = "%s.%03d" % (data_head, data_secs)
    print(time_stamp)

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

def res_success(list=None,dict=None,str=None,msg=None,token=None):
    result = None
    if list != None:
        list = json.loads(serializers.serialize("json", list))
        result = [item["fields"] for item in list]
    elif dict != None:
        result = model_to_dict(dict)
    elif str != None:
        result = str
    return {
        "data": result,
        "status": "SUCCESS",
        "msg": msg,
        "token":token
    }

def res_str_success(data,msg=None,token=None):
    return res_success(str=data,msg=None,token=None)

def res_dict_success(data,msg=None,token=None):
    return res_success(dict=data,msg=None,token=None)

def res_list_success(data,msg=None,token=None):
    return res_success(list=data,msg=None,token=None)

def res_fail(data=None,msg=""):
    return {
        "data": data,
        "status": "FAIL",
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

#把jsonp数据替换掉方法名，并转换成json格式
def converToJson(res,name):
    return json.loads(re.sub(name+"\\(|\\)$", " ", res.text))

def get_app_id(path):
    if path.find("/music") != -1:
        return APP["music"]
    elif path.find("/movie") != -1:
        return APP["movie"]
    elif path.find("/learn") != -1:
        return APP["learn"]
    elif path.find("/ebook") != -1:
        return APP["ebook"]

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')

        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")

        else:
            return json.JSONEncoder.default(self, obj)


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')

        return json.JSONEncoder.default(self, obj)


