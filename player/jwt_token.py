import jwt
from player.config import SECRET_KEY,ALGORITHM,JTI
import datetime

class Token(object):

    EXP_DAYS = 30

    # 这里可以对错误类型进行定义
    TOKEN_EXPIRED = 'TOKEN_EXPIRED'
    TOKEN_INVALID = 'TOKEN_INVALID'
    TOKEN_REQUIRED = 'TOKEN_REQUIRED'

    @staticmethod
    def encode_token(data={}):
        try:
            payload = {
                # 过期时间
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=60*60*24*30),
                # 发行时间
                'iat': datetime.datetime.utcnow(),
                # token签发者
                'iss': 'wuwenqiang',
                'data': data,
                "jti": JTI
            }
            """payload 中一些固定参数名称的意义, 同时可以在payload中自定义参数"""
            # iss  【issuer】发布者的url地址
            # sub 【subject】该JWT所面向的用户，用于处理特定应用，不是常用的字段
            # aud 【audience】接受者的url地址
            # exp 【expiration】 该jwt销毁的时间；unix时间戳
            # nbf  【not before】 该jwt的使用时间不能早于该时间；unix时间戳
            # iat   【issued at】 该jwt的发布时间；unix 时间戳
            # jti    【JWT ID】 该jwt的唯一ID编号

            return jwt.encode(
                payload,
                SECRET_KEY,
                algorithm=ALGORITHM,
            )

        except Exception as e:
            print(e)
            return e


    @staticmethod
    def verify_bearer_token(token):
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload:
            return True
        return False

    @staticmethod
    def decode_token(token):
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload:
            return payload["data"]
        return None

    # 获取token中的user_id
    @staticmethod
    def get_user_id(request):
        if 'Authorization' is not request.headers or request.headers["Authorization"] is None:
            return None
        else:
            data = Token.decode_token(request.headers["Authorization"])
            if data and "user_id" in data:
                return data["user_id"]
            else:
                return None
    #更新token
    @staticmethod
    def update_token(request):
        if 'Authorization' is not request.headers or request.headers["Authorization"] is None:
            return None
        data = Token.decode_token(request.headers["Authorization"])
        if data:
            return Token.encode_token(data)
        else:
            return None