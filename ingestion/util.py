class Singleton(object):
    _shared_state = {}

    def __new__(cls, *args, **kwargs):
        obj = super(Singleton, cls).__new__(cls, *args, **kwargs)
        obj.__dict__ = cls._shared_state
        return obj


class Event(object):
    pass


class Observable(object):
    def __init__(self):
        self.__callbacks = []

    def subscribe(self, callback):
        self.__callbacks.append(callback)

    def unsubscribe(self, callback):
        self.__callbacks.remove(callback)

    def _fire(self, **attrs):
        e = Event()
        e.source = self
        for k, v in attrs.items():
            setattr(e, k, v)
        for fn in self.__callbacks:
            fn(e)


def list_to_set(l, key):
    ret = set()
    for i in l:
        ret.add(i[key])

    return ret


def list_to_dict(l, key):
    ret = {}
    for i in l:
        ret[i[key]] = i

    return ret
