from smartdjango import Params, Validator

from Resource.models import Resource


def remove_dot(res_str_id):
    find_dot = res_str_id.find('.')
    if find_dot != -1:
        res_str_id = res_str_id[:find_dot]
    return res_str_id


class ResourceParams(metaclass=Params):
    model_class = Resource

    rname: Validator
    visit_key: Validator
    status: Validator
    description: Validator
    right_bubble: Validator
    cover: Validator
    cover_type: Validator
    parent: Validator

    resource_getter = Validator('res_str_id', final_name='resource').to(Resource.get_by_id)
    parent_getter = Validator('parent_str_id', final_name='parent').to(Resource.get_by_id)
    shortlink_resource_getter = Validator('res_str_id', final_name='resource').to(remove_dot).to(Resource.get_by_id)
