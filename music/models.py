from django.db import models
class Douyin(models.Model):
    PLAY_MODE = (
        (0, 'kugou'),
        (1, 'qq'),
        (1, 'local')
    )

    id = models.IntegerField(primary_key=True)
    albummid = models.CharField(max_length = 255)
    duration = models.IntegerField()
    image = models.CharField(max_length = 255)
    mid = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    singer = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    create_time = models.DateTimeField()
    timer = models.IntegerField()
    update_time = models.DateTimeField()
    kugou_url = models.CharField(max_length=255)
    play_mode = models.CharField(choices=PLAY_MODE,max_length=32)
    other_url = models.CharField(max_length=255)
    local_url = models.CharField(max_length=255)
    disabled = models.CharField(max_length=255)
    lyric = models.TextField()
    local_image = models.CharField(max_length=255)

    class Meta:
        db_table = 'douyin'  # 指明数据库表名
        verbose_name = '抖音'  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def resultMap(self):
        return {
            "id":"id",
            "albummid":"albummid",
            "duration":"duration",
            "image":"image",
            "mid":"mid",
            "name":"name",
            "singer":"singer",
            "url":"url",
            "create_time":"createTime",
            "timer":"timer",
            "update_time":"updateTime",
            "kugou_url":"kugouUrl",
            "play_mode":"playMode",
            "other_url":"otherUrl",
            "local_url":"localUrl",
            "disabled":"disabled",
            "lyric":"lyric",
            "local_image":"localImage"
        }

class FavoriteMusic(models.Model):
    id = models.IntegerField()
    albummid = models.CharField(max_length = 255)
    duration = models.IntegerField()
    image = models.CharField(max_length = 255)
    mid = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    singer = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    create_time = models.DateTimeField()
    timer = models.IntegerField()
    update_time = models.DateTimeField()
    kugou_url = models.CharField(max_length=255)
    play_mode =  models.CharField(max_length=255)
    otherUrl = models.CharField(max_length=255)
    localUrl = models.CharField(max_length=255)
    disabled = models.CharField(max_length=255)
    userId = models.CharField(max_length=255)
    lyric = models.TextField()
    localImage = models.CharField(max_length=255)
    favoriteMusicId = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'favorite_music'  # 指明数据库表名
        verbose_name = '收藏音乐表'  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def resultMap(self):
        return {
            "id":"id",
            "albummid":"albummid",
            "duration":"duration",
            "image":"image",
            "mid":"mid",
            "name":"name",
            "singer":"singer",
            "url":"url",
            "create_time":"createTime",
            "timer":"timer",
            "update_time":"updateTime",
            "kugou_url":"kugouUrl",
            "play_mode":"playMode",
            "other_url":"otherUrl",
            "local_url":"localUrl",
            "disabled":"disabled",
            "user_id":"userId",
            "lyric":"lyric",
            "local_image":"localImage"
        }

class RecordMusic(models.Model):
    record_id =  models.AutoField(primary_key=True)
    id = models.IntegerField()
    albummid = models.CharField(max_length = 255)
    duration = models.IntegerField()
    image = models.CharField(max_length = 255)
    mid = models.CharField(max_length = 255)
    name = models.CharField(max_length = 255)
    singer = models.CharField(max_length = 255)
    url = models.CharField(max_length = 255)
    user_id = models.CharField(max_length = 255)
    create_time = models.DateTimeField()
    timer = models.IntegerField()

    class Meta:
        db_table = 'record_music'  # 指明数据库表名
        verbose_name = '记录音乐表'  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def items(self):
        return ['id', 'albummid', 'duration', 'image',"mid","name","singer","url","user_id","create_time","timer"]

    def resultMap(self):
        return {
            "id":"id",
            "albummid":"albummid",
            "duration":"duration",
            "image":"image",
            "mid":"mid",
            "name":"mid",
            "singer":"singer",
            "url":"url",
            "user_id":"userId",
            "create_time":"createTime",
            "timer":"timer"
        }

class User(models.Model):
    user_id = models.CharField(primary_key=True,max_length=255)
    password = models.CharField(max_length = 255)
    create_date = models.DateTimeField()
    update_date = models.DateTimeField()
    username = models.CharField(max_length = 255)
    telephone = models.CharField(max_length = 255)
    email = models.CharField(max_length = 255)
    avater = models.CharField(max_length = 255)
    age = models.IntegerField()
    sex = models.CharField(max_length = 255)
    role = models.CharField(max_length = 255)
    secret_key = models.CharField(max_length = 255)

    class Meta:
        db_table = 'user'  # 指明数据库表名
        verbose_name = '用户表'  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def resultMap(self):
        return {
            "user_id":"user_id",
            "create_date":"createDate",
            "update_date":"updateDate",
            "username":"username",
            "telephone":"telephone",
            "email":"email",
            "avater":"avater",
            "age":"age",
            "sex":"sex",
            "role":"role",
        }