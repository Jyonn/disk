# 171203 Adel Liu
# 七牛上传政策
from disk.settings import MAX_AVATAR_SIZE, HOST, MAX_FILE_SIZE

AVATAR_CALLBACK = '%s/api/user/avatar/callback' % HOST
FILE_CALLBACK = '%s/api/resource/dlpath/callback' % HOST

AVATAR_POLICY = dict(
    insertOnly=1,
    callbackUrl=AVATAR_CALLBACK,
    callbackBodyType='application/json',
    fsizeMin=1,
    fsizeLimit=MAX_AVATAR_SIZE,
    mimeLimit='image/*',
)
FILE_POLICY = dict(
    insertOnly=1,
    callbackUrl=FILE_CALLBACK,
    callbackBodyType='application/json',
    fsizeMin=1,
    fsizeLimit=MAX_FILE_SIZE,
)


def get_avatar_policy(user_id):
    policy = AVATAR_POLICY
    policy['callbackBody'] = '{key=$(key),user_id=%s}' % user_id
    return policy


def get_file_policy(user_id):
    policy = FILE_POLICY
    policy['callbackBody'] = '{key=$(key),user_id=%s,fsize=$(fsize),fname=$(fname)}' % user_id
    return policy
