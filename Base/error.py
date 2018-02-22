""" 171203 Adel Liu

错误表，在编码时不断添加
"""


class E:
    def __init__(self, error_id):
        self.eid = error_id


class Error:
    NOT_FOUND_CONFIG = E(2037)
    VISIT_KEY_LEN = E(2036)
    ERROR_CREATE_RIGHT = E(2035)
    NOT_FOUND_RIGHT = E(2034)
    FAIL_QINIU = E(2033)
    QINIU_UNAUTHORIZED = E(2032)
    ERROR_REQUEST_QINIU = E(2031)
    ERROR_DELETE_ROOT_FOLDER = E(2030)
    REQUIRE_EMPTY_FOLDER = E(2029)
    ERROR_RESOURCE_ID = E(2028)
    ERROR_CREATE_LINK = E(2027)
    NOT_YOUR_RESOURCE = E(2026)
    REQUIRE_FATHER_OR_ROOT_DELETE = E(2025)
    PASSWORD_CHANGED = E(2024)
    ERROR_RESOURCE_RELATION = E(2023)
    ERROR_RESOURCE_TYPE = E(2022)
    INVALID_PASSWORD = E(2021)
    INVALID_USERNAME = E(2020)
    INVALID_RNAME = E(2019)
    REQUIRE_FILE = E(2018)
    ERROR_GET_ROOT_FOLDER = E(2017)
    PARENT_NOT_BELONG = E(2016)
    NOT_READABLE = E(2015)
    ERROR_FILE_PARENT = E(2014)
    NOT_FOUND_RESOURCE = E(2013)
    ERROR_RESOURCE_STATUS = E(2012)
    UNAUTH_CALLBACK = E(2011)
    USERNAME_EXIST = E(2010)
    JWT_EXPIRED = E(2009)
    ERROR_JWT_FORMAT = E(2008)
    JWT_PARAM_INCOMPLETE = E(2007)
    REQUIRE_DICT = E(2006)
    ERROR_CREATE_USER = E(2005)
    REQUIRE_GRANT = E(2004)
    ERROR_CREATE_FOLDER = E(2003)
    ERROR_CREATE_FILE = E(2002)
    ERROR_PASSWORD = E(2001)
    NOT_FOUND_USER = E(2000)

    BETA_CODE_ERROR = E(1012)
    ERROR_PROCESS_FUNC = E(1011)
    ERROR_TUPLE_FORMAT = E(1010)
    REQUIRE_ROOT = E(1009)
    ERROR_VALIDATION_FUNC = E(1008)
    ERROR_PARAM_FORMAT = E(1007)
    REQUIRE_BASE64 = E(1006)
    ERROR_METHOD = E(1005)
    STRANGE = E(1004)
    REQUIRE_LOGIN = E(1003)
    REQUIRE_JSON = E(1002)
    REQUIRE_PARAM = E(1001)
    ERROR_NOT_FOUND = E(1000)
    OK = E(0)

    ERROR_DICT = [
        (VISIT_KEY_LEN, "资源密码至少需要3个字符"),
        (ERROR_CREATE_RIGHT, "存储读取权限错误"),
        (NOT_FOUND_RIGHT, "不存在的读取权限"),
        (FAIL_QINIU, "未知原因导致的七牛端操作错误"),
        (QINIU_UNAUTHORIZED, "七牛端身份验证错误"),
        (ERROR_REQUEST_QINIU, "七牛请求错误"),
        (ERROR_DELETE_ROOT_FOLDER, "无法删除用户根目录"),
        (REQUIRE_EMPTY_FOLDER, "非空目录无法删除"),
        (ERROR_RESOURCE_ID, "错误的资源ID"),
        (ERROR_CREATE_LINK, "存储链接错误"),
        (NOT_YOUR_RESOURCE, "没有操作权限"),
        (REQUIRE_FATHER_OR_ROOT_DELETE, "不是管理员或父用户，无法删除"),
        (PASSWORD_CHANGED, "密码已改变，需要重新获取token"),
        (ERROR_RESOURCE_RELATION, "错误的资源逻辑关系"),
        (ERROR_RESOURCE_TYPE, "错误的资源类型"),
        (INVALID_PASSWORD, "密码长度应在6-16个字符之内且无非法字符"),
        (INVALID_USERNAME, "用户名只能是包含字母数字和下划线的3-32位字符串"),
        (INVALID_RNAME, "资源名称不能包含非法字符（\\/*:\'\"|<>?等）"),
        (REQUIRE_FILE, "需要文件资源"),
        (ERROR_GET_ROOT_FOLDER, "无法读取根目录"),
        (PARENT_NOT_BELONG, "无法在他人目录下存储"),
        (NOT_READABLE, "没有读取权限"),
        (ERROR_FILE_PARENT, "文件资源不能成为父目录"),
        (NOT_FOUND_RESOURCE, "不存在的资源"),
        (ERROR_RESOURCE_STATUS, "错误的资源公开信息"),
        (UNAUTH_CALLBACK, "未经授权的回调函数"),
        (USERNAME_EXIST, "已存在的用户名"),
        (JWT_EXPIRED, "身份认证过期"),
        (ERROR_JWT_FORMAT, "身份认证token错误"),
        (JWT_PARAM_INCOMPLETE, "身份认证token缺少参数"),
        (REQUIRE_DICT, "需要字典数据"),
        (ERROR_CREATE_USER, "存储用户错误"),
        (REQUIRE_GRANT, "需要可存储用户权限"),
        (ERROR_CREATE_FOLDER, "存储目录错误"),
        (ERROR_CREATE_FILE, "存储文件错误"),
        (ERROR_PASSWORD, "错误的用户名或密码"),
        (NOT_FOUND_USER, "不存在的用户"),

        (BETA_CODE_ERROR, "内测码错误"),
        (ERROR_PROCESS_FUNC, "参数预处理函数错误"),
        (ERROR_TUPLE_FORMAT, "属性元组格式错误"),
        (REQUIRE_ROOT, "需要管理员登录"),
        (ERROR_VALIDATION_FUNC, "错误的参数验证函数"),
        (ERROR_PARAM_FORMAT, "错误的参数格式"),
        (REQUIRE_BASE64, "参数需要base64编码"),
        (ERROR_METHOD, "错误的HTTP请求方法"),
        (STRANGE, "未知错误"),
        (REQUIRE_LOGIN, "需要登录"),
        (REQUIRE_JSON, "需要JSON数据"),
        (REQUIRE_PARAM, "缺少参数"),
        (ERROR_NOT_FOUND, "不存在的错误"),
        (OK, "没有错误"),
    ]
