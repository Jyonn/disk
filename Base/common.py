""" 190815 Adel Liu """

from QitianSDK import QitianManager

from Config.models import Config, CI
from disk.settings import PROJ_INIT

DEBUG = True


QITIAN_APP_ID = Config.get_value_by_key(CI.QITIAN_APP_ID)
QITIAN_APP_SECRET = Config.get_value_by_key(CI.QITIAN_APP_SECRET)
QITIAN_HOST = Config.get_config_by_key(CI.QITIAN_HOST)

SECRET_KEY = Config.get_value_by_key(CI.PROJECT_SECRET_KEY)
JWT_ENCODE_ALGO = Config.get_value_by_key(CI.JWT_ENCODE_ALGO)

HOST = Config.get_value_by_key(CI.HOST)
ADMIN_QITIAN = Config.get_value_by_key(CI.ADMIN_QITIAN)

if PROJ_INIT:
    MAX_IMAGE_SIZE = MAX_FILE_SIZE = 0
else:
    MAX_IMAGE_SIZE = int(Config.get_value_by_key(CI.MAX_IMAGE_SIZE))
    MAX_FILE_SIZE = int(Config.get_value_by_key(CI.MAX_FILE_SIZE))

qt_manager = QitianManager(
    app_id=QITIAN_APP_ID,
    app_secret=QITIAN_APP_SECRET,
    host=QITIAN_HOST,
    timeout=5
)
