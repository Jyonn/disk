from smartdjango import Error, Code


@Error.register
class UserErrors:
    CREATE_USER = Error("新建用户错误", code=Code.InternalServerError)
    USER_NOT_FOUND = Error("不存在的用户", code=Code.NotFound)


class UserValidator:
    MAX_NICKNAME_LENGTH = 10
    MAX_AVATAR_LENGTH = 1024
    MAX_QT_USER_APP_ID_LENGTH = 16
    MAX_QTB_TOKEN_LENGTH = 256
    MAX_DESCRIPTION_LENGTH = 20
