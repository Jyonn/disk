""" 171203 Adel Liu

七牛上传政策，现全部转变为303重定向，未来会改为callback
"""
from disk.settings import MAX_IMAGE_SIZE, HOST, MAX_FILE_SIZE

AVATAR_CALLBACK = '%s/api/user/avatar/callback' % HOST
FILE_CALLBACK = '%s/api/res/dlpath/callback' % HOST
COVER_CALLBACK = '%s/api/res/cover/callback' % HOST

AVATAR_POLICY = dict(
    insertOnly=1,
    callbackUrl=AVATAR_CALLBACK,
    callbackBodyType='application/json',
    fsizeMin=1,
    fsizeLimit=MAX_IMAGE_SIZE,
    mimeLimit='image/*',
)
FILE_POLICY = dict(
    insertOnly=1,
    callbackUrl=FILE_CALLBACK,
    callbackBodyType='application/json',
    fsizeMin=1,
    fsizeLimit=MAX_FILE_SIZE,
)
COVER_POLICY = dict(
    insertOnly=1,
    callbackUrl=COVER_CALLBACK,
    callbackBodyType='application/json',
    fsizeMin=1,
    fsizeLimit=MAX_IMAGE_SIZE,
    mimeLimit='image/*',
)

# AVATAR_POLICY = dict(
#     insertOnly=1,
#     returnUrl=AVATAR_CALLBACK,
#     # callbackBodyType='application/json',
#     fsizeMin=1,
#     fsizeLimit=MAX_IMAGE_SIZE,
#     mimeLimit='image/*',
# )
# FILE_POLICY = dict(
#     insertOnly=1,
#     returnUrl=FILE_CALLBACK,
#     # callbackBodyType='application/json',
#     fsizeMin=1,
#     fsizeLimit=MAX_FILE_SIZE,
# )
# COVER_POLICY = dict(
#     insertOnly=1,
#     returnUrl=COVER_CALLBACK,
#     # callbackBodyType='application/json',
#     fsizeMin=1,
#     fsizeLimit=MAX_IMAGE_SIZE,
#     mimeLimit='image/*',
# )


# def get_avatar_policy(user_id):
#     """获取用户上传头像policy"""
#     policy = AVATAR_POLICY
#     policy['returnBody'] = '{"key":"$(key)","user_id":%s}' % user_id
#     return policy
#
#
# def get_file_policy(user_id, parent_str_id):
#     """获取用户上传文件policy"""
#     policy = FILE_POLICY
#     policy['returnBody'] = '{"key":"$(key)","user_id":%s,"fsize":$(fsize),"fname":"$(fname)",' \
#                            '"parent_str_id":"%s","ftype": "$(mimeType)"}' \
#                            % (user_id, parent_str_id)
#     return policy
#
#
# def get_cover_policy(res_str_id):
#     """获取用户上传文件封面policy"""
#     policy = COVER_POLICY
#     policy['returnBody'] = '{"key":"$(key)", "res_str_id":"%s"}' % res_str_id
#     return policy


def get_avatar_policy(user_id):
    policy = AVATAR_POLICY
    policy['callbackBody'] = '{"key":"$(key)","user_id":%s}' % user_id
    return policy


def get_res_policy(filename, user_id, parent_str_id):
    policy = FILE_POLICY
    policy['callbackBody'] = '{"key":"$(key)","user_id":%s,"fsize":$(fsize),"fname":"%s",' \
                             '"parent_str_id":"%s","ftype":"$(mimeType)"}' \
                             % (user_id, filename, parent_str_id)
    return policy


def get_cover_policy(res_str_id):
    policy = COVER_POLICY
    policy['callbackBody'] = '{"key":"$(key)","res_str_id":"%s"}' % res_str_id
    return policy
