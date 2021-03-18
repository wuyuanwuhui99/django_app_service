from django.http import HttpResponse,JsonResponse
from django.shortcuts import redirect
from music import models
from music.utils import getJsonByList,getJsonByDist,getJson,now,converToJson
import json
from music.utils import batch_dict_camel,extend,download,headers
from music.models import User,FavoriteMusic,Douyin,RecordMusic
import requests #请求模块
from django.db import transaction,connection #事务
import time
from music.content_type import CONTENT_TYPE
import re
import os
import random
from hyper.contrib import HTTP20Adapter
from selenium import webdriver
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
    douyinList = models.Douyin.objects.filter(disabled = "0").order_by("-update_time")
    return JsonResponse(getJsonByList(douyinList))

#登录，
def login(request):
    if (request.method == 'POST'):
        paramsDict = json.loads(request.body)
        res = models.User.objects.filter(user_id=paramsDict["userId"],password = paramsDict["password"])
        if len(res) == 0:
            result = getJson(msg="账号或密码错误",status="fail")
        else:
            request.session["userId"] = paramsDict["userId"]
            data = {}
            data["userId"] = res[0].user_id
            data["username"] = res[0].username
            data["avater"] = res[0].avater
            result = getJson(data=data,msg="登录成功",status="success")
    return JsonResponse(result)

#退出登录
def logout(request):
    request.session.flush()#清除所有session
    return JsonResponse(getJson(msg="退出登录成功",status="success"))

#注册用户
def register(request):
    if (request.method == 'POST'):
        paramsDict = json.loads(request.body)
        user = User()
        user.user_id = paramsDict["userId"]
        user.password =  paramsDict["password"]
        user.email = paramsDict["email"]
        user.age = paramsDict["age"]
        user.avater = paramsDict["avater"]
        user.telephone = paramsDict["telephone"]
        user.save()
        request.session["userId"] = user.user_id
    return JsonResponse(getJson({"name":user.name,"userId":user.user_id,"image":user.avater},msg="注册成功", status="success"))

#获取用户信息
def getUserData(request):
   if "userId" in request.session:
       res = models.User.objects.filter(user_id=request.session["userId"])
       if len(res) == 0:
           res = models.User.objects.filter(role="public")
           index = random.randint(0,len(res)-1)
           userInfo = res[index] #随机选择一条
           data = {}
           data["userId"] = userInfo.user_id
           data["username"] = userInfo.username
           data["avater"] = userInfo.avater
           result = getJson(data=data,msg="", status="success")
       else:
           request.session["userId"] = request.session["userId"]
           data = {}
           data["userId"] = res[0].user_id
           data["username"] = res[0].username
           data["avater"] = res[0].avater
           result = getJson(data=data, msg="", status="success")
       return JsonResponse(result)
   else:
       res = models.User.objects.filter(role="public")
       index = random.randint(0, len(res) - 1)
       userInfo = res[index]  # 随机选择一条
       data = {}
       data["userId"] = userInfo.user_id
       data["username"] = userInfo.username
       data["avater"] = userInfo.avater
       return JsonResponse(getJson(data=data,msg="", status="success"))


#根据用户id查询该用户收藏的列表
def getFavorite(request):
    if "userId" in request.session:
        res = models.FavoriteMusic.objects.filter(user_id=request.session["userId"])
        return JsonResponse(getJsonByList(res,msg="", status="success"))
    else:
        return JsonResponse(getJson(msg="请先登录", status="fail"))


#查询是否收藏该歌曲
def queryFavorite(request):
    mid = request.GET.get("mid")
    if mid != None and "userId" in request.session:
        res = models.FavoriteMusic.objects.filter(user_id=request.session["userId"],mid=mid)
        return JsonResponse(getJsonByList(res, msg="", status="success"))
    else:
        return JsonResponse(getJson([], msg="", status="fail"))


#收藏，如果是管理员账号，添加到抖音歌曲表，并下载图片和歌曲
@transaction.atomic #事务
def addFavorite(request):
    if (request.method == 'POST'):
        if "userId" in request.session:
            userId = request.session["userId"]
            paramsDict = batch_dict_camel(json.loads(request.body))#驼峰转下划线
            res = models.FavoriteMusic.objects.filter(user_id=userId,mid=paramsDict["mid"])
            if len(res) > 0 :#如果已经收过该歌曲，返回错误提示
                return JsonResponse(getJson(msg="已经收藏过该歌曲，请勿重复收藏", status="fail"))
            favoriteMusic = FavoriteMusic()
            extend(favoriteMusic,paramsDict,extra={"user_id":"吴怨吴悔","disabled":"0","play_mode":"qq"})#把paramsDict所有属性赋值给favoriteMusic对象
            favoriteMusic.save()#插入数据库
            user = models.User.objects.values("role").get(user_id=userId)
            if user["role"] == "admin":#如果是管理员账号，插入到抖音歌曲表
                res = models.Douyin.objects.values("mid").filter(mid=paramsDict["mid"])#查询数据是否存在
                if len(res) == 0:#如果抖音歌曲表中没有这条数据才插入
                    douyin = Douyin()
                    songFileName = download(paramsDict["name"],"E:\\Node\\music\\public\\audio\\",paramsDict["url"])
                    imageFileName = download(paramsDict["name"], "E:\\Node\\music\\public\\images\\song", paramsDict["image"],ext="jpg")
                    # 除了user_id属性，其他的属性混入,还额外添加disabled字段
                    extend(
                        douyin,
                        paramsDict,
                        exclude=["user_id"],
                        extra={
                            "disabled": "0",
                            "play_mode": "local",
                            "local_url": "/audio/" +songFileName,
                            "local_image":"/images/song/" +imageFileName,
                            "create_time":now(),
                            "update_time":now(),
                            "time":1
                        }
                    )
                    douyin.save()
            return JsonResponse(getJson(msg="收藏成功", status="success"))
        else:
            return JsonResponse(getJson(msg="请先登录", status="fail"))

@transaction.atomic #事务
def deleteFavorite(request):
    if (request.method == 'DELETE'):
        if "userId" in request.session:
            paramsDict = batch_dict_camel(json.loads(request.body))  # 驼峰转下划线
            if "mid" in paramsDict:
                res = models.FavoriteMusic.objects.filter(user_id=request.session["userId"], mid=paramsDict["mid"]).delete()
                if res[0] != 0:#res = (1, {'music.FavoriteMusic': 1})
                    return JsonResponse(getJson(msg="删除成功", status="success"))
                else:
                    return JsonResponse(getJson(msg="您收藏的歌曲不存在", status="fail"))
            else:
                return JsonResponse(getJson(msg="缺少mid参数", status="fail"))
        else:
            return JsonResponse(getJson(msg="请先登录", status="fail"))

@transaction.atomic #事务
def record(request):
    if (request.method == 'POST'):
        paramsDict = batch_dict_camel(json.loads(request.body))  # 驼峰转下划线
        recordMusic = RecordMusic()
        extend(recordMusic,paramsDict)
        recordMusic.save()
        cursor=connection.cursor()
        cursor.execute("UPDATE douyin SET timer = timer+1 WHERE mid = %s",(paramsDict["mid"]))
        cursor.fetchall()
        cursor.execute("UPDATE douyin SET url=%s WHERE mid = %s AND (url='' OR url is null) ", (paramsDict["url"],paramsDict["mid"]))
        cursor.fetchall()
        return JsonResponse(getJson(msg="插入记录成功", status="success"))

#获取推荐音乐数据
def getDiscList(request):
    res = requests.get("https://c.y.qq.com/splcloud/fcgi-bin/fcg_get_diss_by_tag.fcg?g_tk=5381&inCharset=utf-8&outCharset=utf-8&notice=0&format=json&platform=yqq&hostUin=0&sin=0&ein=29&sortId=5&needNewCode=0&categoryId=10000000&rnd=0.6219561219093992", headers=headers)
    return JsonResponse(json.loads(res.text))

def getLyric(request):
    res = requests.get("https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg?g_tk=5381&inCharset=utf-8&outCharset=utf-8&notice=0&format=json&songmid="+request.GET["songmid"]+"&platform=yqq&hostUin=0&needNewCode=0&categoryId=10000000&pcachetime="+str(time.time()),headers=headers)
    return JsonResponse(json.loads(res.text))

def getSingerList(request):
    res = requests.get("https://c.y.qq.com/v8/fcg-bin/v8.fcg?jsonpCallback=getSingerList&g_tk=5381&inCharset=utf-8&outCharset=utf-8&notice=0&format=jsonp&channel=singer&page=list&key=all_all_all&pagesize=100&pagenum=1&hostUin=0&needNewCode=0&platform=yqq",headers=headers)
    return JsonResponse(converToJson(res,"getSingerList"))

def getHotKey(request):
    res = requests.get("https://c.y.qq.com/splcloud/fcgi-bin/gethotkey.fcg?jsonpCallback=getHotKey&uin=0&needNewCode=1&platform=h5&g_tk=5381&inCharset=utf-8&outCharset=utf-8&notice=0&format=jsonp",headers=headers)
    return JsonResponse(converToJson(res,"getHotKey"))

def search(request):
    w = request.GET["w"]
    res = requests.get("https://c.y.qq.com/soso/fcgi-bin/client_search_cp?jsonpCallback=search&g_tk=5381&inCharset=utf-8&outCharset=utf-8&notice=0&format=jsonp&ct=24&qqmusic_ver=1298&new_json=1&remoteplace=txt.yqq.center&searchid=37276201631470540&t=0&aggr=1&cr=1&catZhida=1&lossless=0&flag_qc=0&p=1&n=20&w="+w+"&loginUin=0&hostUin=0&platform=yqq&needNewCode=1",headers=headers)
    return JsonResponse(converToJson(res,"search"))

def getSingerDetail(request):
    singermid = request.GET["keyword"]
    res = requests.get("https://c.y.qq.com/v8/fcg-bin/fcg_v8_singer_track_cp.fcg?jsonpCallback=getSingerDetail&g_tk=5381&inCharset=utf-8&outCharset=utf-8&notice=0&format=jsonp&hostUin=0&needNewCode=0&platform=yqq&order=listen&begin=0&num=80&songstatus=1&singermid="+singermid,headers=headers)
    return JsonResponse(converToJson(res,"getSingerDetail"))

def getRecommend(request):
    res = requests.get("https://c.y.qq.com/musichall/fcgi-bin/fcg_yqqhomepagerecommend.fcg?jsonpCallback=getRecommend&g_tk=5381&inCharset=utf-8&outCharset=utf-8&notice=0&format=jsonp&platform=h5&uin=0&needNewCode=1",headers=headers)
    return JsonResponse(converToJson(res,"getRecommend"))

def getSongList(request):
    res = requests.get("https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg?jsonpCallback=getSongList&type=1&json=1&utf8=1&onlysong=0&disstid="+disstid+"&g_tk=5381&loginUin=0&hostUin=0&platform=yqq&needNewCode=0&inCharset=utf-8&outCharset=utf-8&notice=0&format=jsonp",headers=headers)
    return JsonResponse(converToJson(res,"getSongList"))

def getTopList(request):
    res = requests.get("https://c.y.qq.com/v8/fcg-bin/fcg_myqq_toplist.fcg?jsonpCallback=getTopList&g_tk=5381&loginUin=0&hostUin=0&platform=yqq&needNewCode=0&inCharset=utf-8&outCharset=utf-8&notice=0&format=jsonp&uin=0&needNewCode=1&platform=h5",headers=headers)
    return JsonResponse(converToJson(res,"getTopList"))

def getMusicList(request):
    topid = request.GET["topid"]
    res = requests.get("https://c.y.qq.com/v8/fcg-bin/fcg_v8_toplist_cp.fcg?jsonpCallback=getTopList&g_tk=5381&loginUin=0&hostUin=0&platform=yqq&needNewCode=0&inCharset=utf-8&outCharset=utf-8&notice=0&format=jsonp&topid="+topid+"&needNewCode=1&uin=0&tpl=3&page=detail&type=top&platform=h5&needNewCode=1",headers=headers)
    return JsonResponse(converToJson(res,"getMusicList"))

def getAudioUrl(request):
    songmid = request.GET["songmid"]
    filename = request.GET["filename"]
    res = requests.get("https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg?jsonpCallback=getAudioUrl&g_tk=5381&loginUin=0&hostUin=0&platform=yqq&needNewCode=0&inCharset=utf-8&outCharset=utf-8&notice=0&format=jsonp&cid=205361747&uin=0&songmid="+songmid+"&filename="+filename+"&guid=3397254710",headers=headers)
    return JsonResponse(converToJson(res,"getAudioUrl"))

def getSingleSong(request):
    mid = request.GET["mid"]
    # name = "getplaysongvkey"+str(random.randint(0,1000000000000))
    # path = "/cgi-bin/musics.fcg?-="+name+"&g_tk=5381&sign=zzaxm8ku5i0jeest0af2191b47cc88ba96ab4da4f712f0318&loginUin=275018723&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0&data=%7B%22req%22%3A%7B%22module%22%3A%22CDN.SrfCdnDispatchServer%22%2C%22method%22%3A%22GetCdnDispatch%22%2C%22param%22%3A%7B%22guid%22%3A%222614705516%22%2C%22calltype%22%3A0%2C%22userip%22%3A%22%22%7D%7D%2C%22req_0%22%3A%7B%22module%22%3A%22vkey.GetVkeyServer%22%2C%22method%22%3A%22CgiGetVkey%22%2C%22param%22%3A%7B%22guid%22%3A%222614705516%22%2C%22songmid%22%3A%5B%22"+mid+"%22%5D%2C%22songtype%22%3A%5B0%5D%2C%22uin%22%3A%22275018723%22%2C%22loginflag%22%3A1%2C%22platform%22%3A%2220%22%7D%7D%2C%22comm%22%3A%7B%22uin%22%3A275018723%2C%22format%22%3A%22json%22%2C%22ct%22%3A24%2C%22cv%22%3A0%7D%7D"
    # myHeaders = {}
    # myHeaders[":authority"] = "u.y.qq.com"
    # myHeaders[":method"] = "GET"
    # myHeaders[":path"] = path
    # myHeaders[":scheme"] = "https"
    # myHeaders["Host"] = "u.y.qq.com"
    # myHeaders["accept"] = "application/json, text/javascript, */*; q=0.01"
    # myHeaders["accept-encoding"] = "gzip, deflate, br"
    # myHeaders["accept-language"] = "zh-CN,zh;q=0.9"
    # # myHeaders["cookie"] = "pgv_pvi=6113074176; RK=BMxA3hjjd3; ptcz=ce69d462fa29ff93785c6137a1ecdd2232c7753d313032f9f232fedf95e69269; pgv_pvid=2614705516; ts_uid=1314538738; o_cookie=275018723; ts_refer=www.baidu.com/link; psrf_qqaccess_token=400FF23521963EA1742A34D48E2B1C45; psrf_access_token_expiresAt=1602710732; psrf_qqopenid=AE87CBC404BF38B1ACFE8A121C0034BB; euin=owSkoe6F7i-i; tmeLoginType=2; uin=275018723; psrf_qqrefresh_token=7BCEAA4096A39F977A8794D18401F823; psrf_qqunionid=EDA2BA89A1FA01249DE5D6520FA9478C; yqq_stat=0; pgv_info=ssid=s5494257866; pgv_si=s1622806528; userAction=1; qqmusic_fromtag=66; yq_playschange=0; yq_playdata=; player_exist=1; ts_last=y.qq.com/portal/player.html; yplayer_open=1; yq_index=2"
    # myHeaders["origin"] = "https://y.qq.com"
    # myHeaders["referer"] = "https://y.qq.com/portal/player.html"
    # myHeaders["sec-fetch-mode"] = "cors"
    # myHeaders["sec-fetch-site"] = "same-site"
    # myHeaders["User-Agent"] = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Mobile Safari/537.36"
    # myHeaders["sec-fetch-site"] = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
    # sessions = requests.session()
    # sessions.mount("https://u.y.qq.com", HTTP20Adapter())
    # print("https://u.y.qq.com"+path)
    # res = sessions.get("https://u.y.qq.com"+path, headers=myHeaders)
    # print(res.request.headers)
    # driver = webdriver.Chrome()  # 打开谷歌浏览器
    # driver.get("https://y.qq.com/n/yqq/song/"+mid+".html")
    # driver.implicitly_wait(10)  # 等待页面加载完成
    # time.sleep(2)
    # driver.find_element_by_class_name("js_all_play").click()
    # time.sleep(1)
    # driver.find_element_by_class_name("switcher_plogin").click()
    # driver.find_element_by_class_name("js_all_play").click()
    # driver.switch_to.window(driver.window_handles[1])
    # time.sleep(2)
    # audio = driver.find_elements_by_css_selector("audio")
    # print(audio)
    # audio.get_attrs("src")
    res = requests.get("https://u.y.qq.com/cgi-bin/musicu.fcg?-=getplaysongvkey"+str(random.randint(0,1000000000000))+"&g_tk=5381&loginUin=275018723&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0&data=%7B%22req%22:%7B%22module%22:%22CDN.SrfCdnDispatchServer%22,%22method%22:%22GetCdnDispatch%22,%22param%22:%7B%22guid%22:%222807659112%22,%22calltype%22:0,%22userip%22:%22%22%7D%7D,%22req_0%22:%7B%22module%22:%22vkey.GetVkeyServer%22,%22method%22:%22CgiGetVkey%22,%22param%22:%7B%22guid%22:%222807659112%22,%22songmid%22:[%22"+mid+"%22],%22songtype%22:[0],%22uin%22:%22275018723%22,%22loginflag%22:1,%22platform%22:%2220%22%7D%7D,%22comm%22:%7B%22uin%22:275018723,%22format%22:%22json%22,%22ct%22:24,%22cv%22:0%7D%7D&jsonpCallback=getSingleSong",headers=headers)
    print(res)
    return JsonResponse(converToJson(res,"getSingleSong"))
    # return JsonResponse(getJson(data={}, msg="", status="success"))
