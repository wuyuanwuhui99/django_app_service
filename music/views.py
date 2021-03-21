from django.http import HttpResponse,JsonResponse
from django.forms.models import fields_for_model,model_to_dict
from django.shortcuts import redirect
from music import models
from player.jwt_token import Token
from player.utils import getJsonByList, getJson,now,converToJson
import json
from player.utils import batch_dict_camel,extend,download
from player.config import C_HEADERS,U_HEADERS,OPARATION,EXPIRED
from music.models import User,FavoriteMusic,Douyin,RecordMusic
import requests #请求模块
from django.db import transaction,connection #事务
import time
from music.content_type import CONTENT_TYPE
import re
import os
import random
from player.utils import res_fail,res_list_success,res_dict_success,res_str_success
from django.core.cache import cache

#设置首页
def musicIndex(request):
    f_name = open(os.getcwd() + "\\music\\static\\index.html", 'rb').read()
    return HttpResponse(f_name,content_type=CONTENT_TYPE["html"])

#获取音乐公共资源,相当于设置静态目录
def getPublic(request):
    ext = re.sub('\?.*', "", request.path.split(".")[-1])
    f_name = open("E:/Node/music/public/"+request.path, 'rb').read()
    return HttpResponse(f_name,content_type=CONTENT_TYPE[ext])

#获取音乐公共资源,相当于设置静态目录
def getStatic(request):
    ext = re.sub('\?.*', "", request.path.split(".")[-1])
    print(os.getcwd()+request.path)
    f_name = open(os.getcwd()+request.path, 'rb').read()
    return HttpResponse(f_name,content_type=CONTENT_TYPE[ext])

def redirectIndex(request):
    return redirect("music/")


#查询抖音歌曲列表
def getDouyinList(request):
    request.state = ("查询抖音歌曲列表",OPARATION["QUERY"],"getDouyinList")
    result = cache.get(request.path)
    if result == None:
        pass
        douyinList = models.Douyin.objects.filter(disabled = "0").order_by("-update_time")[:2]
        result = res_list_success(douyinList)
        cache.set(request.path,json.dumps(result),EXPIRED)
        return JsonResponse(result)
    return JsonResponse(json.loads(result))

#登录，
def login(request):
    if (request.method == 'POST'):
        params = json.loads(request.body)
        res = models.User.objects.filter(user_id=params["userId"],password = params["password"]).first()
        if res == None:
            result = res_fail(msg="账号或密码错误",status="fail")
        else:
            result = res_dict_success(res)
    return JsonResponse(result)

#注册用户
def register(request):
    if (request.method == 'POST'):
        params = json.loads(str(request.body,"utf-8"))
        user = User()
        for key,value in params.items():
            setattr(user,key,value)
        user.create_date = now()
        user.update_date = now()
        user.save()
        token = Token.encode_token(user)
    return JsonResponse(res_dict_success(user,msg="注册成功", token=token))

#获取用户信息
def getUserData(request):
   if 'Authorization' is not  request.headers or  request.headers["Authorization"] is None:
        result = models.User.objects.filter(role="public").order_by('?').first()
        return res_dict_success(result)
   else: #有token
       user_id = Token.get_user_id(request)
       if user_id != None: #如果token有效
           result = models.User.objects.get(user_id=user_id)
           return res_dict_success(result)
       else: #如果token无效
            result = models.User.objects.filter(role="public").order_by('?').first()
            return  res_dict_success(result)

#根据用户id查询该用户收藏的列表
def getFavorite(request):
    user_id = Token.get_user_id(request)
    result = models.FavoriteMusic.objects.filter(user_id=user_id)
    token = Token.update_token(request)
    return JsonResponse(res_list_success(result,token=token))


#查询是否收藏该歌曲
def queryFavorite(request):
    mid = request.GET.get("mid")
    user_id = Token.get_user_id(request)
    if mid != None:
        result = models.FavoriteMusic.objects.filter(user_id=user_id,mid=mid)
        return JsonResponse(res_str_success(len(result)))
    else:
        return JsonResponse(res_fail(msg="缺少mid参数"))


#收藏，如果是管理员账号，添加到抖音歌曲表，并下载图片和歌曲
@transaction.atomic #事务
def addFavorite(request):
    if (request.method == 'POST'):
        user_id = Token.get_user_id(request)
        params = json.loads(request.body)#驼峰转下划线
        res = models.FavoriteMusic.objects.filter(user_id=user_id,mid=params["mid"])
        if len(res) > 0 :#如果已经收过该歌曲，返回错误提示
            return JsonResponse(res_fail(msg="已经收藏过该歌曲，请勿重复收藏", status="fail"))
        favoriteMusic = FavoriteMusic()
        extend(favoriteMusic, params)
        favoriteMusic.user_id = user_id
        favoriteMusic.save()#插入数据库
        user = models.User.objects.values("role").get(user_id=user_id)
        if user.role == "admin":#如果是管理员账号，插入到抖音歌曲表
            res = models.Douyin.objects.values("mid").filter(mid=params["mid"])#查询数据是否存在
            if len(res) == 0:#如果抖音歌曲表中没有这条数据才插入
                douyin = Douyin()
                songFileName = download(params["name"],"E:/static/music/audio/",params["url"])
                imageFileName = download(params["name"], "E:/static/music/song/", params["image"],ext="jpg")
                # 除了user_id属性，其他的属性混入,还额外添加disabled字段
                extend(
                    douyin,
                    params,
                    exclude=["user_id"],
                    extra={
                        "disabled": "0",
                        "play_mode": "local",
                        "local_url": "/static/music/audio/" + songFileName,
                        "local_image":"/static/music/song/" + imageFileName,
                        "create_time":now(),
                        "update_time":now(),
                        "time":1
                    }
                )
                douyin.save()
        return JsonResponse(res_str_success(msg="收藏成功", status="success"))


@transaction.atomic #事务
def deleteFavorite(request):
    if (request.method == 'DELETE'):
        user_id = Token.get_user_id(request)
        params = json.loads(request.body)  # 驼峰转下划线
        if "mid" in params:
            res = models.FavoriteMusic.objects.filter(user_id=user_id, mid=params["mid"]).delete()
            if res[0] != 0: #res = (1, {'music.FavoriteMusic': 1})
                return JsonResponse(res_str_success(msg="删除成功"))
            else:
                return JsonResponse(res_fail(msg="您收藏的歌曲不存在"))
        else:
            return JsonResponse(res_fail(msg="缺少mid参数", status="fail"))

@transaction.atomic #事务
def record(request):
    if (request.method == 'POST'):
        params = json.loads(request.body) # 驼峰转下划线
        recordMusic = RecordMusic()
        user_id = Token.get_user_id(request)
        extend(recordMusic,params,extra={"user_id":user_id})
        recordMusic.save()
        cursor = connection.cursor()
        cursor.execute("UPDATE douyin SET timer = timer+1 WHERE mid = %s",(params["mid"]))
        cursor.fetchall()
        cursor.execute("UPDATE douyin SET url=%s WHERE mid = %s AND (url='' OR url is null) ", (params["url"],params["mid"]))
        cursor.fetchall()
        return JsonResponse(res_str_success(msg="插入记录成功", status="success"))

#获取推荐音乐数据
def getDiscList(request):
    res = requests.get("https://c.y.qq.com/splcloud/fcgi-bin/fcg_get_diss_by_tag.fcg?g_tk=5381&inCharset=utf-8&outCharset=utf-8&notice=0&format=json&platform=yqq&hostUin=0&sin=0&ein=29&sortId=5&needNewCode=0&categoryId=10000000&rnd=0.6219561219093992", headers=C_HEADERS)
    return JsonResponse(json.loads(res.text))

def getLyric(request):
    res = requests.get("https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg?g_tk=5381&inCharset=utf-8&outCharset=utf-8&notice=0&format=json&songmid="+request.GET["songmid"]+"&platform=yqq&hostUin=0&needNewCode=0&categoryId=10000000&pcachetime="+str(time.time()),headers=C_HEADERS)
    return JsonResponse(json.loads(res.text))

def getSingerList(request):
    res = requests.get("https://c.y.qq.com/v8/fcg-bin/v8.fcg?jsonpCallback=getSingerList&g_tk=5381&inCharset=utf-8&outCharset=utf-8&notice=0&format=jsonp&channel=singer&page=list&key=all_all_all&pagesize=100&pagenum=1&hostUin=0&needNewCode=0&platform=yqq",headers=C_HEADERS)
    return JsonResponse(converToJson(res,"getSingerList"))

def getHotKey(request):
    res = requests.get("https://c.y.qq.com/splcloud/fcgi-bin/gethotkey.fcg?jsonpCallback=getHotKey&uin=0&needNewCode=1&platform=h5&g_tk=5381&inCharset=utf-8&outCharset=utf-8&notice=0&format=jsonp",headers=C_HEADERS)
    return JsonResponse(converToJson(res,"getHotKey"))

def search(request):
    w = request.GET["w"]
    res = requests.get("https://c.y.qq.com/soso/fcgi-bin/client_search_cp?jsonpCallback=search&g_tk=5381&inCharset=utf-8&outCharset=utf-8&notice=0&format=jsonp&ct=24&qqmusic_ver=1298&new_json=1&remoteplace=txt.yqq.center&searchid=37276201631470540&t=0&aggr=1&cr=1&catZhida=1&lossless=0&flag_qc=0&p=1&n=20&w="+w+"&loginUin=0&hostUin=0&platform=yqq&needNewCode=1",headers=C_HEADERS)
    return JsonResponse(converToJson(res,"search"))

def getSingerDetail(request):
    singermid = request.GET["keyword"]
    res = requests.get("https://c.y.qq.com/v8/fcg-bin/fcg_v8_singer_track_cp.fcg?jsonpCallback=getSingerDetail&g_tk=5381&inCharset=utf-8&outCharset=utf-8&notice=0&format=jsonp&hostUin=0&needNewCode=0&platform=yqq&order=listen&begin=0&num=80&songstatus=1&singermid="+singermid,headers=C_HEADERS)
    return JsonResponse(converToJson(res,"getSingerDetail"))

def getRecommend(request):
    res = requests.get("https://c.y.qq.com/musichall/fcgi-bin/fcg_yqqhomepagerecommend.fcg?jsonpCallback=getRecommend&g_tk=5381&inCharset=utf-8&outCharset=utf-8&notice=0&format=jsonp&platform=h5&uin=0&needNewCode=1",headers=C_HEADERS)
    return JsonResponse(converToJson(res,"getRecommend"))

def getSongList(request):
    res = requests.get("https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg?jsonpCallback=getSongList&type=1&json=1&utf8=1&onlysong=0&disstid="+disstid+"&g_tk=5381&loginUin=0&hostUin=0&platform=yqq&needNewCode=0&inCharset=utf-8&outCharset=utf-8&notice=0&format=jsonp",headers=C_HEADERS)
    return JsonResponse(converToJson(res,"getSongList"))

def getTopList(request):
    res = requests.get("https://c.y.qq.com/v8/fcg-bin/fcg_myqq_toplist.fcg?jsonpCallback=getTopList&g_tk=5381&loginUin=0&hostUin=0&platform=yqq&needNewCode=0&inCharset=utf-8&outCharset=utf-8&notice=0&format=jsonp&uin=0&needNewCode=1&platform=h5",headers=C_HEADERS)
    return JsonResponse(converToJson(res,"getTopList"))

def getMusicList(request):
    topid = request.GET["topid"]
    res = requests.get("https://c.y.qq.com/v8/fcg-bin/fcg_v8_toplist_cp.fcg?jsonpCallback=getTopList&g_tk=5381&loginUin=0&hostUin=0&platform=yqq&needNewCode=0&inCharset=utf-8&outCharset=utf-8&notice=0&format=jsonp&topid="+topid+"&needNewCode=1&uin=0&tpl=3&page=detail&type=top&platform=h5&needNewCode=1",headers=C_HEADERS)
    return JsonResponse(converToJson(res,"getMusicList"))

def getAudioUrl(request):
    songmid = request.GET["songmid"]
    filename = request.GET["filename"]
    res = requests.get("https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg?jsonpCallback=getAudioUrl&g_tk=5381&loginUin=0&hostUin=0&platform=yqq&needNewCode=0&inCharset=utf-8&outCharset=utf-8&notice=0&format=jsonp&cid=205361747&uin=0&songmid="+songmid+"&filename="+filename+"&guid=3397254710",headers=C_HEADERS)
    return JsonResponse(converToJson(res,"getAudioUrl"))

def getSingleSong(request):
    mid = request.GET["mid"]
    res = requests.get("https://u.y.qq.com/cgi-bin/musicu.fcg?-=getplaysongvkey"+str(random.randint(0,1000000000000))+"&g_tk=5381&loginUin=275018723&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0&data=%7B%22req%22:%7B%22module%22:%22CDN.SrfCdnDispatchServer%22,%22method%22:%22GetCdnDispatch%22,%22param%22:%7B%22guid%22:%222807659112%22,%22calltype%22:0,%22userip%22:%22%22%7D%7D,%22req_0%22:%7B%22module%22:%22vkey.GetVkeyServer%22,%22method%22:%22CgiGetVkey%22,%22param%22:%7B%22guid%22:%222807659112%22,%22songmid%22:[%22"+mid+"%22],%22songtype%22:[0],%22uin%22:%22275018723%22,%22loginflag%22:1,%22platform%22:%2220%22%7D%7D,%22comm%22:%7B%22uin%22:275018723,%22format%22:%22json%22,%22ct%22:24,%22cv%22:0%7D%7D&jsonpCallback=getSingleSong",headers=C_HEADERS)
    print(res)
    return JsonResponse(converToJson(res,"getSingleSong"))
