# Generated by Django 3.0.8 on 2020-08-05 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='douyin',
            name='lyric',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='favoritemusic',
            name='lyric',
            field=models.TextField(),
        ),
    ]
