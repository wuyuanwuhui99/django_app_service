# !/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import HttpResponseRedirect
from django.http import HttpResponse,JsonResponse
from player.utils import res_fail
from player.jwt_token import Token
try:
    from django.utils.deprecation import MiddlewareMixin  # Django 1.10.x
except ImportError:
    MiddlewareMixin = object  # Django 1.4.x - Django 1.9.x


class TokenMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.path.find("getway") != -1:
            if 'Authorization' not in  request.headers or  request.headers["Authorization"] is None:
                return HttpResponse(res_fail())
            else:
                state = Token.verify_bearer_token(request.headers["Authorization"])
                if(state == False):
                    return HttpResponse(res_fail(msg="token错误"))
