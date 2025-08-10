from smartdjango import Params, Validator

from User.models import User


class UserParams(metaclass=Params):
    model_class = User

    user_getter = Validator('user_id', final_name='user').to(User.get_by_id)
    qt_user_getter = Validator('qt_user_app_id', final_name='user').to(User.get_by_qtid)

