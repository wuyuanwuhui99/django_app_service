# !/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from player.jwt_token import Token
from player.utils import DateEncoder

try:
    from django.utils.deprecation import MiddlewareMixin  # Django 1.10.x
except ImportError:
    MiddlewareMixin = object  # Django 1.4.x - Django 1.9.x


class ResultMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        if request.path.find("/getUserData") != -1:
            data = json.loads(json.dumps(response["data"],cls=DateEncoder))
            token = Token.encode_token(data)
            response["token"] = token
        elif 'Authorization' in request.headers and request.headers["Authorization"] is not None:
            token = Token.update_token(request)
            response["token"] = token
        return response