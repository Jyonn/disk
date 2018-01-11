# 171203 Adel Liu
# 错误表，在编码时不断添加


class Error:
    NOT_WRITEABLE = 2026
    REQUIRE_FATHER_OR_ROOT_DELETE = 2025
    PASSWORD_CHANGED = 2024
    ERROR_RESOURCE_RELATION = 2023
    ERROR_RESOURCE_TYPE = 2022
    INVALID_PASSWORD = 2021
    INVALID_USERNAME = 2020
    INVALID_RNAME = 2019
    REQUIRE_FILE = 2018
    ERROR_GET_ROOT_FOLDER = 2017
    PARENT_NOT_BELONG = 2016
    NOT_READABLE = 2015
    ERROR_FILE_PARENT = 2014
    NOT_FOUND_RESOURCE = 2013
    ERROR_RESOURCE_STATUS = 2012
    UNAUTH_CALLBACK = 2011
    USERNAME_EXIST = 2010
    JWT_EXPIRED = 2009
    ERROR_JWT_FORMAT = 2008
    JWT_PARAM_INCOMPLETE = 2007
    REQUIRE_DICT = 2006
    ERROR_CREATE_USER = 2005
    REQUIRE_GRANT = 2004
    CREATE_FOLDER_ERROR = 2003
    CREATE_FILE_ERROR = 2002
    ERROR_PASSWORD = 2001
    NOT_FOUND_USER = 2000

    PROCESS_FUNC_ERROR = 1011
    TUPLE_FORMAT_ERROR = 1010
    REQUIRE_ROOT = 1009
    VALIDATION_FUNC_ERROR = 1008
    PARAM_FORMAT_ERROR = 1007
    REQUIRE_BASE64 = 1006
    ERROR_METHOD = 1005
    STRANGE = 1004
    REQUIRE_LOGIN = 1003
    REQUIRE_JSON = 1002
    REQUIRE_PARAM = 1001
    NOT_FOUND_ERROR = 1000
    OK = 0

    ERROR_DICT = [
        (NOT_WRITEABLE, "没有权限修改资源"),
        (REQUIRE_FATHER_OR_ROOT_DELETE, "不是管理员或父用户，无法删除"),
        (PASSWORD_CHANGED, "密码已改变，需要重新获取token"),
        (ERROR_RESOURCE_RELATION, "错误的资源逻辑关系"),
        (ERROR_RESOURCE_TYPE, "错误的资源类型"),
        (INVALID_PASSWORD, "密码长度应在6-16个字符之内且无非法字符"),
        (INVALID_USERNAME, "用户名只能包含字母数字和下划线"),
        (INVALID_RNAME, "资源名称不能包含非法字符（\\/*:\'\"|<>?等）"),
        (REQUIRE_FILE, "需要文件资源"),
        (ERROR_GET_ROOT_FOLDER, "无法读取根目录"),
        (PARENT_NOT_BELONG, "无法在他人目录下创建"),
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
        (ERROR_CREATE_USER, "创建用户错误"),
        (REQUIRE_GRANT, "需要可创建用户权限"),
        (CREATE_FOLDER_ERROR, "创建目录错误"),
        (CREATE_FILE_ERROR, "创建文件错误"),
        (ERROR_PASSWORD, "错误的用户名或密码"),
        (NOT_FOUND_USER, "不存在的用户"),

        (PROCESS_FUNC_ERROR, "参数预处理函数错误"),
        (TUPLE_FORMAT_ERROR, "属性元组格式错误"),
        (REQUIRE_ROOT, "需要管理员登录"),
        (VALIDATION_FUNC_ERROR, "错误的参数验证函数"),
        (PARAM_FORMAT_ERROR, "错误的参数格式"),
        (REQUIRE_BASE64, "参数需要base64编码"),
        (ERROR_METHOD, "错误的HTTP请求方法"),
        (STRANGE, "未知错误"),
        (REQUIRE_LOGIN, "需要登录"),
        (REQUIRE_JSON, "需要JSON数据"),
        (REQUIRE_PARAM, "缺少参数"),
        (NOT_FOUND_ERROR, "不存在的错误"),
        (OK, "没有错误"),
    ]
