from django.http import HttpResponse
from django.shortcuts import redirect
from music import models
from player.jwt_token import Token
from player.utils import now
import json
from player.utils import extend,download,get_redis_data
from player.config import OPARATION,EXPIRED
from music.models import User,FavoriteMusic,Douyin,RecordMusic
from django.db import transaction,connection #事务
import time
from music.content_type import CONTENT_TYPE
import re
import os
from random import random
from player.utils import res_fail,res_list_success,res_dict_success,res_data_success
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
        douyinList = models.Douyin.objects.filter(disabled = "0").order_by("-update_time")[:10]
        result = res_list_success(douyinList)
        cache.set(request.path,json.dumps(result),EXPIRED)
        return result
    return json.loads(result)

#登录，
def login(request):
    if (request.method == 'POST'):
        request.state = ("登录",OPARATION["GET"],"login")
        params = json.loads(request.body)
        res = models.User.objects.filter(user_id=params["userId"],password = params["password"]).first()
        if res == None:
            result = res_fail(msg="账号或密码错误",status="fail")
        else:
            result = res_dict_success(res)
    return result

#注册用户
def register(request):
    if (request.method == 'POST'):
        request.state = ("注册用户", OPARATION["ADD"], "register")
        params = json.loads(str(request.body,"utf-8"))
        user = User()
        for key,value in params.items():
            setattr(user,key,value)
        user.create_date = now()
        user.update_date = now()
        user.save()
        token = Token.encode_token(user)
    return res_dict_success(user,msg="注册成功", token=token)

#获取用户信息
def getUserData(request):
   request.state = ("获取用户信息", OPARATION["QUERY"], "getUserData")
   if 'Authorization' not in request.headers or  request.headers["Authorization"] is None:
        result = models.User.objects.filter(role="public").order_by('?').first()
        return res_dict_success(result)
   else: #有token
       user_id = Token.get_user_id(request)
       if user_id != None: #如果token有效
           result = models.User.objects.get(user_id=user_id)
           return res_dict_success(result)
       else: #如果token无效
            result = models.User.objects.filter(role="public").order_by('?').first()
            return res_dict_success(result)

#根据用户id查询该用户收藏的列表
def getFavorite(request):
    request.state = ("根据用户id查询该用户收藏的列表", OPARATION["QUERY"], "getFavorite")
    user_id = Token.get_user_id(request)
    result = models.FavoriteMusic.objects.filter(user_id=user_id)
    token = Token.update_token(request)
    return res_list_success(result,token=token)


#查询是否收藏该歌曲
def queryFavorite(request):
    request.state = ("查询是否收藏该歌曲", OPARATION["QUERY"], "queryFavorite")
    mid = request.GET.get("mid")
    user_id = Token.get_user_id(request)
    if mid != None:
        result = models.FavoriteMusic.objects.filter(user_id=user_id,mid=mid)
        return res_data_success(len(result))
    else:
        return res_fail(msg="缺少mid参数")


#收藏，如果是管理员账号，添加到抖音歌曲表，并下载图片和歌曲
@transaction.atomic #事务
def addFavorite(request):
    if (request.method == 'POST'):
        request.state = ("收藏", OPARATION["ADD"], "addFavorite")
        user_id = Token.get_user_id(request)
        params = json.loads(request.body)#驼峰转下划线
        res = models.FavoriteMusic.objects.filter(user_id=user_id,mid=params["mid"])
        if len(res) > 0 :#如果已经收过该歌曲，返回错误提示
            return res_fail(msg="已经收藏过该歌曲，请勿重复收藏", status="fail")
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
        return res_data_success(msg="收藏成功", status="success")


@transaction.atomic #事务
def deleteFavorite(request):
    if (request.method == 'DELETE'):
        request.state = ("取消收藏", OPARATION["DELETE"], "deleteFavorite")
        user_id = Token.get_user_id(request)
        params = json.loads(request.body)  # 驼峰转下划线
        if "mid" in params:
            res = models.FavoriteMusic.objects.filter(user_id=user_id, mid=params["mid"]).delete()
            if res[0] != 0: #res = (1, {'music.FavoriteMusic': 1})
                return res_data_success(msg="删除成功")
            else:
                return res_fail(msg="您收藏的歌曲不存在")
        else:
            return res_fail(msg="缺少mid参数", status="fail")

@transaction.atomic #事务
def record(request):
    if (request.method == 'POST'):
        request.state = ("歌曲记录", OPARATION["ADD"], "addFavorite")
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
        return res_data_success(None,msg="插入记录成功")

#获取推荐音乐数据
def getDiscList(request):
    url = "https://c.y.qq.com/splcloud/fcgi-bin/fcg_get_diss_by_tag.fcg?g_tk=5381&inCharset=utf-8&outCharset=utf-8&notice=0&format=json&platform=yqq&hostUin=0&sin=0&ein=29&sortId=5&needNewCode=0&categoryId=10000000"
    return get_redis_data(url=url, query_string="&rnd=" + str(random()))

def getLyric(request):
    url = "https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg?g_tk=5381&inCharset=utf-8&outCharset=utf-8&notice=0&format=json&songmid="+request.GET["songmid"]+"&platform=yqq&hostUin=0&needNewCode=0&categoryId=10000000";
    return get_redis_data(url=url, query_string="&pcachetime=" + str(int(time.time()*1000)))

def getSingerList(request):
    url = "https://c.y.qq.com/v8/fcg-bin/v8.fcg?jsonpCallback=getSingerList&g_tk=5381&inCharset=utf-8&outCharset=utf-8&notice=0&format=jsonp&channel=singer&page=list&key=all_all_all&pagesize=100&pagenum=1&hostUin=0&needNewCode=0&platform=yqq"
    return get_redis_data(url=url, name="getSingerList")

def getHotKey(request):
    url = "https://c.y.qq.com/splcloud/fcgi-bin/gethotkey.fcg?g_tk=5381&inCharset=utf-8&outCharset=utf-8&notice=0&format=jsonp&uin=0&needNewCode=1&platform=h5&jsonpCallback=getHotKey"
    return get_redis_data(url=url, name="getHotKey")

def search(request):
    w = request.GET["w"]
    catZhida = request.GET["catZhida"]
    p = request.GET["p"]
    n = request.GET["n"]
    url = "https://c.y.qq.com/soso/fcgi-bin/client_search_cp?g_tk=5381&inCharset=utf-8&outCharset=utf-8&notice=0&format=jsonp&ct=24&qqmusic_ver=1298&new_json=1&remoteplace=txt.yqq.center&searchid=37276201631470540&t=0&aggr=1&cr=1&lossless=0&flag_qc=0&loginUin=0&hostUin=0&platform=yqq&needNewCode=1&jsonpCallback=search&catZhida="+catZhida+"&p="+p+"&n="+n+"&w="+w
    return get_redis_data(url=url, name="search")

def getSingerDetail(request):
    singermid = request.GET["singermid"]
    url = "https://c.y.qq.com/v8/fcg-bin/fcg_v8_singer_track_cp.fcg?jsonpCallback=getSingerDetail&g_tk=5381&inCharset=utf-8&outCharset=utf-8&notice=0&format=jsonp&hostUin=0&needNewCode=0&platform=yqq&order=listen&begin=0&num=80&songstatus=1&singermid=" + singermid
    return get_redis_data(url=url, name="getSingerDetail")

def getRecommend(request):
    url = "https://u.y.qq.com/cgi-bin/musics.fcg?-=recom29349756051626663&g_tk=5381&sign=zzadg8hsrunooakff15c4441255ee9ef959d8dacccc3f88&loginUin=0&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0&data=%7B%22comm%22%3A%7B%22ct%22%3A24%7D%2C%22category%22%3A%7B%22method%22%3A%22get_hot_category%22%2C%22param%22%3A%7B%22qq%22%3A%22%22%7D%2C%22module%22%3A%22music.web_category_svr%22%7D%2C%22recomPlaylist%22%3A%7B%22method%22%3A%22get_hot_recommend%22%2C%22param%22%3A%7B%22async%22%3A1%2C%22cmd%22%3A2%7D%2C%22module%22%3A%22playlist.HotRecommendServer%22%7D%2C%22playlist%22%3A%7B%22method%22%3A%22get_playlist_by_category%22%2C%22param%22%3A%7B%22id%22%3A8%2C%22curPage%22%3A1%2C%22size%22%3A40%2C%22order%22%3A5%2C%22titleid%22%3A8%7D%2C%22module%22%3A%22playlist.PlayListPlazaServer%22%7D%2C%22new_song%22%3A%7B%22module%22%3A%22newsong.NewSongServer%22%2C%22method%22%3A%22get_new_song_info%22%2C%22param%22%3A%7B%22type%22%3A5%7D%7D%2C%22new_album%22%3A%7B%22module%22%3A%22newalbum.NewAlbumServer%22%2C%22method%22%3A%22get_new_album_info%22%2C%22param%22%3A%7B%22area%22%3A1%2C%22sin%22%3A0%2C%22num%22%3A20%7D%7D%2C%22new_album_tag%22%3A%7B%22module%22%3A%22newalbum.NewAlbumServer%22%2C%22method%22%3A%22get_new_album_area%22%2C%22param%22%3A%7B%7D%7D%2C%22toplist%22%3A%7B%22module%22%3A%22musicToplist.ToplistInfoServer%22%2C%22method%22%3A%22GetAll%22%2C%22param%22%3A%7B%7D%7D%2C%22focus%22%3A%7B%22module%22%3A%22music.musicHall.MusicHallPlatform%22%2C%22method%22%3A%22GetFocus%22%2C%22param%22%3A%7B%7D%7D%7D"
    return get_redis_data(url=url, name="getRecommend")

def getSongList(request):
    disstid = request.GET["disstid"]
    url = "https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg?g_tk=5381&inCharset=utf-8&outCharset=utf-8&notice=0&format=jsonp&type=1&json=1&utf8=1&onlysong=0&disstid="+disstid+"&loginUin=0&hostUin=0&platform=yqq&needNewCode=0&jsonpCallback=getSongList"
    return get_redis_data(url=url, name="getSongList")

def getTopList(request):
    url = "https://c.y.qq.com/v8/fcg-bin/fcg_myqq_toplist.fcg?jsonpCallback=getTopList&g_tk=5381&loginUin=0&hostUin=0&platform=yqq&needNewCode=0&inCharset=utf-8&outCharset=utf-8&notice=0&format=jsonp&uin=0&needNewCode=1&platform=h5"
    return get_redis_data(url=url, name="getTopList")

def getMusicList(request):
    topid = request.GET["topid"]
    url = "https://c.y.qq.com/v8/fcg-bin/fcg_v8_toplist_cp.fcg?jsonpCallback=getMusicList&g_tk=5381&loginUin=0&hostUin=0&platform=yqq&needNewCode=0&inCharset=utf-8&outCharset=utf-8&notice=0&format=jsonp&topid=" + topid + "&needNewCode=1&uin=0&tpl=3&page=detail&type=top&platform=h5&needNewCode=1"
    return get_redis_data(url=url, name="getMusicList")

def getAudioUrl(request):
    songmid = request.GET["mid"]
    filename = request.GET["filename"]
    url = "https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg?jsonpCallback=getAudioUrl&g_tk=5381&loginUin=0&hostUin=0&platform=yqq&needNewCode=0&inCharset=utf-8&outCharset=utf-8&notice=0&format=jsonp&cid=205361747&uin=0&songmid=" + songmid + "&filename=" + filename + "&guid=3397254710";
    return get_redis_data(url=url, name="getAudioUrl")

def getSingleSong(request):
    songmid = request.GET["songmid"]
    url = "https://u.y.qq.com/cgi-bin/musicu.fcg?jsonpCallback=getSingleSong&g_tk=5381&loginUin=275018723&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0&data=%7B%22req%22:%7B%22module%22:%22CDN.SrfCdnDispatchServer%22,%22method%22:%22GetCdnDispatch%22,%22param%22:%7B%22guid%22:%222807659112%22,%22calltype%22:0,%22userip%22:%22%22%7D%7D,%22req_0%22:%7B%22module%22:%22vkey.GetVkeyServer%22,%22method%22:%22CgiGetVkey%22,%22param%22:%7B%22guid%22:%222807659112%22,%22songmid%22:[%22" + songmid + "%22],%22songtype%22:[0],%22uin%22:%22275018723%22,%22loginflag%22:1,%22platform%22:%2220%22%7D%7D,%22comm%22:%7B%22uin%22:275018723,%22format%22:%22json%22,%22ct%22:24,%22cv%22:0%7D%7D"
    return get_redis_data(url=url,name="getSingleSong",query_string="&-=getplaysongvkey"+ str(random()))
