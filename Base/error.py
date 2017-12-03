class Error:
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

    REQUIRE_BASE64 = 1006
    ERROR_METHOD = 1005
    STRANGE = 1004
    REQUIRE_LOGIN = 1003
    REQUIRE_JSON = 1002
    REQUIRE_PARAM = 1001
    NOT_FOUND_ERROR = 1000
    OK = 0

    ERROR_DICT = [
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

        (REQUIRE_BASE64, "参数需要base64编码"),
        (ERROR_METHOD, "错误的HTTP请求方法"),
        (STRANGE, "未知错误"),
        (REQUIRE_LOGIN, "需要登录"),
        (REQUIRE_JSON, "需要JSON数据"),
        (REQUIRE_PARAM, "缺少参数"),
        (NOT_FOUND_ERROR, "不存在的错误"),
        (OK, "没有错误"),
    ]
