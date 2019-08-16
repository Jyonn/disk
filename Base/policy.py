""" 171203 Adel Liu

七牛上传政策，现全部转变为303重定向，未来会改为callback
"""
from disk.settings import MAX_IMAGE_SIZE, HOST, MAX_FILE_SIZE


FILE_POLICY = dict(
    insertOnly=1,
    callbackBodyType='application/json',
    fsizeMin=1,
    fsizeLimit=MAX_FILE_SIZE,
)
COVER_POLICY = dict(
    insertOnly=1,
    callbackBodyType='application/json',
    fsizeMin=1,
    fsizeLimit=MAX_IMAGE_SIZE,
    mimeLimit='image/*',
)


class Policy:
    @staticmethod
    def file(filename, user_id, parent_id):
        policy = dict(
            callbackUrl='%s/api/res/%s/token' % (HOST, parent_id),
            callbackBody='{"key":"$(key)","user_id":%s,"fsize":$(fsize),"fname":"%s",'
                         '"ftype":"$(mimeType)"}' % (user_id, filename)
        )
        policy.update(FILE_POLICY)
        return policy

    @staticmethod
    def cover(res_id):
        policy = dict(
            callbackUrl='%s/api/res/%s/cover' % (HOST, res_id),
            callbackBody='{"key":"$(key)"}',
        )
        policy.update(COVER_POLICY)
        return policy
