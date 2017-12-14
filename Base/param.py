class Param(object):
    def __init__(self, d):
        if not isinstance(d, dict):
            return
        for k in d.keys():
            self.__setattr__(k, d[k])
