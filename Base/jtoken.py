# 171203 Adel Liu
# 第一次使用jwt身份认证技术

import datetime

import jwt

from Base.error import Error
from Base.response import Ret
from disk.settings import SECRET_KEY, JWT_ENCODE_ALGO


def jwt_e(d, expire_second=60 * 60 * 24):
    """
    jwt签名加密
    :param d: 被加密的字典数据
    :param expire_second: 过期时间
    """
    if not isinstance(d, dict):
        return Ret(Error.STRANGE)
    d['ctime'] = datetime.datetime.now().timestamp()
    d['expire'] = expire_second
    encode_str = jwt.encode(d, SECRET_KEY, algorithm=JWT_ENCODE_ALGO).decode()
    return Ret(Error.OK, (encode_str, d))


def jwt_d(s):
    """
    jwt签名解密
    :param s: 被加密的字符串
    """
    if not isinstance(s, str):
        return Ret(Error.STRANGE)
    try:
        d = jwt.decode(s, SECRET_KEY, JWT_ENCODE_ALGO)
    except:
        return Ret(Error.ERROR_JWT_FORMAT)
    if 'expire' not in d.keys() \
            or 'ctime' not in d.keys() \
            or not isinstance(d['ctime'], float) \
            or not isinstance(d['expire'], int):
        return Ret(Error.JWT_PARAM_INCOMPLETE)
    if datetime.datetime.now().timestamp() > d['ctime'] + d['expire']:
        return Ret(Error.JWT_EXPIRED)
    return Ret(Error.OK, d)
