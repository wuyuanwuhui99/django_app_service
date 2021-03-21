# !/usr/bin/env python
# -*- coding: utf-8 -*-
from music.models import Log
import json
from player.utils import now,get_app_id
from player.jwt_token import Token
from time import time

try:
    from django.utils.deprecation import MiddlewareMixin  # Django 1.10.x
except ImportError:
    MiddlewareMixin = object  # Django 1.4.x - Django 1.9.x


class LogMiddleware(MiddlewareMixin):
    log = Log()

    timer = 0

    def process_request(self, request):
        self.log.method = request.method
        self.log.ip = request.META["REMOTE_ADDR"]
        self.log.headers = json.dumps({i:j for i,j in  request.headers.items()})
        self.log.url = request.path
        self.log.params = json.dumps({i:j for i,j in request.POST.items()})
        self.log.query_string = json.dumps({i:j for i,j in request.GET.items()})
        self.log.start_time = now()
        self.log.description = ""
        self.log.oparation = ""
        self.log.type = request.method
        app_id, app_name = get_app_id(request.path)
        self.log.app_id = app_id
        self.log.app_name = app_name
        self.log.user_id = Token.get_user_id(request)
        self.timer = int(time()*1000)

    def process_response(self, request, response):
        self.log.end_time = now()
        self.log.result = str(response.content,"utf-8")
        if hasattr(request, "state"):
            description,oparation,method = request.state
            self.log.description = description
            self.log.oparation = oparation
            self.log.method = method
        self.log.run_time = int(time()*1000) - self.timer
        self.log.save()
        return response