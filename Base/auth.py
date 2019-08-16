from functools import wraps

from Base.common import ADMIN_QITIAN
from Base.jtoken import JWT
from SmartDjango import ErrorCenter, Packing, E

from Resource.models import ResourceError
from User.models import User


class AuthError(ErrorCenter):
    REQUIRE_ROOT = E("需要管理员权限", hc=401)
    REQUIRE_RIGHT = E("需要{0}权限", E.PH_FORMAT, hc=401)
    EXPIRED = E("登录过期", 401)
    REQUIRE_ADMIN = E("需要管理员登录", hc=401)
    REQUIRE_USER = E("需要登录", hc=401)
    TOKEN_MISS_PARAM = E("认证口令缺少参数{0}", E.PH_FORMAT, hc=400)
    REQUIRE_LOGIN = E("需要登录", hc=401)


AuthError.register()


class Auth:
    @staticmethod
    @Packing.pack
    def validate_token(request):
        jwt_str = request.META.get('HTTP_TOKEN')
        if jwt_str is None:
            return AuthError.REQUIRE_LOGIN

        ret = JWT.decrypt(jwt_str)
        if not ret.ok:
            return ret
        dict_ = ret.body
        return dict_

    @staticmethod
    def get_login_token(user: User):
        token, _dict = JWT.encrypt(dict(
            user_id=user.qt_user_app_id,
        ))
        _dict['token'] = token
        _dict['user'] = user.d()
        return _dict

    @classmethod
    @Packing.pack
    def _extract_user(cls, r):
        r.user = None

        ret = cls.validate_token(r)
        if not ret.ok:
            return ret

        dict_ = ret.body
        user_id = dict_.get('user_id')
        if not user_id:
            return AuthError.TOKEN_MISS_PARAM('user_id')

        from User.models import User
        ret = User.get_by_id(user_id)
        if not ret.ok:
            return ret
        r.user = ret.body

    @staticmethod
    def maybe_login(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            Auth._extract_user(request)
            return func(request, *args, **kwargs)

        return wrapper

    @classmethod
    def require_login(cls, func):
        @wraps(func)
        def wrapper(r, *args, **kwargs):
            ret = cls._extract_user(r)
            if not ret.ok:
                return ret
            return func(r, *args, **kwargs)

        return wrapper

    @classmethod
    def require_owner(cls, func):
        @wraps(func)
        def wrapper(r, *args, **kwargs):
            ret = cls._extract_user(r)
            if not ret.ok:
                return ret
            if not r.d.res.belong(r.user):
                return ResourceError.RESOURCE_NOT_BELONG
            return func(r, *args, **kwargs)
        return wrapper

    @classmethod
    def require_root(cls, func):
        @wraps(func)
        def wrapper(r, *args, **kwargs):
            ret = cls._extract_user(r)
            if not ret.ok:
                return ret
            user = r.user  # type: User
            if user.qt_user_app_id != ADMIN_QITIAN:
                return AuthError.REQUIRE_ROOT
            return func(r, *args, **kwargs)
        return wrapper
