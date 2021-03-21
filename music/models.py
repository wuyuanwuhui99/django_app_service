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


class FavoriteMusic(models.Model):
    t_id = models.AutoField(primary_key=True)
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
    other_url = models.CharField(max_length=255)
    local_url = models.CharField(max_length=255)
    disabled = models.CharField(max_length=255)
    user_id = models.CharField(max_length=255)
    lyric = models.TextField()
    local_image = models.CharField(max_length=255)

    class Meta:
        db_table = 'favorite_music'  # 指明数据库表名
        verbose_name = '收藏音乐表'  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称



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


class User(models.Model):
    user_id = models.CharField(primary_key=True,max_length=255)
    password = models.CharField(max_length=255)
    create_date = models.DateTimeField()
    update_date = models.DateTimeField()
    username = models.CharField(max_length = 255)
    telephone = models.CharField(max_length = 255)
    email = models.CharField(max_length = 255)
    avater = models.CharField(max_length = 255)
    birthday = models.CharField(max_length = 255)
    sex = models.CharField(max_length = 255)
    role = models.CharField(max_length = 255)

    class Meta:
        db_table = 'user'  # 指明数据库表名
        verbose_name = '用户表'  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

class Log(models.Model):
    id = models.AutoField(primary_key=True)
    method = models.CharField(max_length = 255)
    url = models.CharField(max_length = 255)
    headers = models.TextField()
    ip = models.CharField(max_length = 255)
    params = models.TextField()
    query_string = models.TextField()
    result = models.TextField()
    start_time = models.DateTimeField()
    run_time = models.IntegerField()
    description = models.CharField(max_length = 255)
    end_time = models.DateTimeField()
    oparation = models.CharField(max_length = 255)
    type = models.CharField(max_length = 255)
    user_id = models.CharField(max_length = 255)
    app_id = models.CharField(max_length = 255)
    app_name = models.CharField(max_length = 255)

    class Meta:
        db_table = 'log'  # 指明数据库表名
        verbose_name = '日志'  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

