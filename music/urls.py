from django.urls import path,re_path
from music.views import *
urlpatterns = [
    # re_path(r'audio.+', getStatic),
    path('music/', musicIndex),
    path('music/getDouyinList/', getDouyinList),
    path('music/login/', login),
    path('music/register/', register),
    path('music/getUserData/', getUserData),
    path('music-getway/getFavorite/', getFavorite),
    path('music-getway/queryFavorite/', queryFavorite),
    path('music-getway/addFavorite/', addFavorite),
    path('music-getway/deleteFavorite/', deleteFavorite),
    path('music/record/', record),
    path('music/getDiscList/', getDiscList),
    path('music/getLyric/', getLyric),
    path('music/getSingerList/', getSingerList),
    path('music/getHotKey/', getHotKey),
    path('music/search/', search),
    path('music/getSingerDetail/', getSingerDetail),
    path('music/getRecommend/', getRecommend),
    path('music/getSongList/', getSongList),
    path('music/getTopList/', getTopList),
    path('music/getMusicList/', getMusicList),
    path('music/getAudioUrl/', getAudioUrl),
    path('music/getSingleSong/', getSingleSong),
    path('music/lyric/', getLyric),
]