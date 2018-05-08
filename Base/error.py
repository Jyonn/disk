""" 180226 Adel Liu

错误表，在编码时不断添加
自动生成eid
"""


class E:
    _error_id = 0

    def __init__(self, msg, release_e=None):
        self.eid = E._error_id
        self.msg = msg
        self.release = release_e if isinstance(release_e, E) else None
        E._error_id += 1


class Error:
    # Debug 错误
    OK = E("没有错误")

    # Release 错误
    ERROR_PARAM = E("参数错误")
    SYSTEM_ERROR = E("系统错误")
    REQUIRE_UNAVAILABLE = E("请求错误")

    ERROR_NOT_FOUND = E("不存在的错误", SYSTEM_ERROR)
    REQUIRE_PARAM = E("缺少参数", ERROR_PARAM)
    REQUIRE_JSON = E("需要JSON数据", ERROR_PARAM)
    REQUIRE_LOGIN = E("请登录后操作")
    STRANGE = E("未知错误", SYSTEM_ERROR)
    REQUIRE_BASE64 = E("参数需要base64编码", ERROR_PARAM)
    ERROR_PARAM_FORMAT = E("错误的参数格式", ERROR_PARAM)
    ERROR_METHOD = E("错误的HTTP请求方法")
    ERROR_VALIDATION_FUNC = E("错误的参数验证函数", ERROR_PARAM)
    REQUIRE_ROOT = E("需要管理员权限")
    ERROR_TUPLE_FORMAT = E("属性元组格式错误", ERROR_PARAM)
    ERROR_PROCESS_FUNC = E("参数预处理函数错误", ERROR_PARAM)
    BETA_CODE_ERROR = E("内测码错误")
    
    NOT_FOUND_CONFIG = E("不存在的配置", REQUIRE_UNAVAILABLE)
    VISIT_KEY_LEN = E("资源密码至少需要3个字符")
    ERROR_CREATE_RIGHT = E("存储读取权限错误", REQUIRE_UNAVAILABLE)
    NOT_FOUND_RIGHT = E("不存在的读取权限", REQUIRE_UNAVAILABLE)
    FAIL_QINIU = E("未知原因导致的七牛端操作错误", SYSTEM_ERROR)
    QINIU_UNAUTHORIZED = E("七牛端身份验证错误", SYSTEM_ERROR)
    ERROR_REQUEST_QINIU = E("七牛请求错误", SYSTEM_ERROR)
    ERROR_DELETE_ROOT_FOLDER = E("无法删除用户根目录", REQUIRE_UNAVAILABLE)
    REQUIRE_EMPTY_FOLDER = E("非空目录无法删除")
    ERROR_RESOURCE_ID = E("错误的资源ID", REQUIRE_UNAVAILABLE)
    ERROR_CREATE_LINK = E("存储链接错误")
    NOT_YOUR_RESOURCE = E("没有操作权限", REQUIRE_UNAVAILABLE)
    REQUIRE_FATHER_OR_ROOT_DELETE = E("不是管理员或父用户，无法删除", REQUIRE_UNAVAILABLE)
    PASSWORD_CHANGED = E("您已改过密码，请重新登录")
    ERROR_RESOURCE_RELATION = E("错误的资源逻辑关系", REQUIRE_UNAVAILABLE)
    ERROR_RESOURCE_TYPE = E("错误的资源类型", REQUIRE_UNAVAILABLE)
    INVALID_PASSWORD = E("密码长度应在6-16个字符之内且无非法字符")
    INVALID_USERNAME = E("用户名只能是包含字母数字和下划线的3-32位字符串")
    INVALID_RNAME = E("资源名称不能包含非法字符（\\/*:\'\"|<>?等）")
    REQUIRE_FILE = E("需要文件资源", REQUIRE_UNAVAILABLE)
    ERROR_GET_ROOT_FOLDER = E("无法读取根目录", REQUIRE_UNAVAILABLE)
    PARENT_NOT_BELONG = E("无法在他人目录下存储", REQUIRE_UNAVAILABLE)
    NOT_READABLE = E("没有读取权限", REQUIRE_UNAVAILABLE)
    ERROR_FILE_PARENT = E("文件资源不能成为父目录", REQUIRE_UNAVAILABLE)
    NOT_FOUND_RESOURCE = E("不存在的资源", REQUIRE_UNAVAILABLE)
    ERROR_RESOURCE_STATUS = E("错误的资源公开信息", REQUIRE_UNAVAILABLE)
    UNAUTH_CALLBACK = E("未经授权的回调函数", REQUIRE_UNAVAILABLE)
    USERNAME_EXIST = E("已存在的用户名，请另择良木")
    JWT_EXPIRED = E("身份认证过期，请重新登录")
    ERROR_JWT_FORMAT = E("身份认证token错误", REQUIRE_UNAVAILABLE)
    JWT_PARAM_INCOMPLETE = E("身份认证token缺少参数", REQUIRE_UNAVAILABLE)
    REQUIRE_DICT = E("需要字典数据", REQUIRE_UNAVAILABLE)
    ERROR_CREATE_USER = E("存储用户错误", SYSTEM_ERROR)
    REQUIRE_GRANT = E("需要可存储用户权限", REQUIRE_UNAVAILABLE)
    ERROR_CREATE_FOLDER = E("存储目录错误", SYSTEM_ERROR)
    ERROR_CREATE_FILE = E("存储文件错误", SYSTEM_ERROR)
    ERROR_PASSWORD = E("错误的用户名或密码")
    NOT_FOUND_USER = E("不存在的用户")
    QTB_AUTH_FAIL = E("齐天簿身份认证失败")
    QTB_GET_INFO_FAIL = E("齐天簿获取用户信息失败")
    EMPTY = E("")

    @classmethod
    def get_error_dict(cls):
        error_dict = dict()
        for k in cls.__dict__:
            if k[0] != '_':
                e = getattr(cls, k)
                if isinstance(e, E):
                    error_dict[k] = dict(eid=e.eid, msg=e.msg)
        return error_dict
