# from User.models import User
# from Base.error import Error
# from Base.response import Ret
# from Base.session import load_session, save_session


def deprint(*args):
    from disk.settings import DEBUG
    if DEBUG:
        print(*args)


# def get_user_from_session(request):
#     user_id = load_session(request, 'user', once_delete=False)
#     if user_id is None:
#         return Ret(Error.REQUIRE_LOGIN)
#     return User.get_user_by_id(user_id)
#
#
# def save_user_to_session(request, user):
#     try:
#         request.session.cycle_key()
#     except:
#         pass
#     save_session(request, 'user', user.pk)
#     return None
#
#
# def logout_user_from_session(request):
#     load_session(request, 'user')
