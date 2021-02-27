""" 190815 Adel Liu """

from QitianSDK import QitianManager

from Config.models import Config, CI


DEBUG = True


QITIAN_APP_ID = Config.get_value_by_key(CI.QITIAN_APP_ID)
QITIAN_APP_SECRET = Config.get_value_by_key(CI.QITIAN_APP_SECRET)

SECRET_KEY = Config.get_value_by_key(CI.PROJECT_SECRET_KEY)
JWT_ENCODE_ALGO = Config.get_value_by_key(CI.JWT_ENCODE_ALGO)

HOST = Config.get_value_by_key(CI.HOST)
ADMIN_QITIAN = Config.get_value_by_key(CI.ADMIN_QITIAN)

qt_manager = QitianManager(QITIAN_APP_ID, QITIAN_APP_SECRET, timeout=5)
