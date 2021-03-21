
C_HEADERS =  {
    "referer":'https://c.y.qq.com/',
    "host": 'c.y.qq.com',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
}

U_HEADERS =  {
    "referer":'https://u.y.qq.com/',
    "host": 'u.y.qq.com',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
}

SECRET_KEY = "wuwenqiang" #加密秘钥

ALGORITHM = 'HS256' #加密算法

JTI = "4f1g23a12aa" #jwt的唯一ID编号

OPARATION = {
    "ADD":"ADD",
    "DELETE":"DELETE",
    "UPDATE":"UPDATE",
    "QUERY":"QUERY"
}

APP = {
    "music":("com.player.music","在线音乐播放器"),
    "movie":("com.player.movie","在线电影"),
    "learn":("com.player.learn","视频教程"),
    "ebook":("com.player.ebook","电子书")
}
EXPIRED = 60 * 60 * 24 * 30
