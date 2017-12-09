class Singleton(object):
    _shared_state = {}

    def __new__(cls, *args, **kwargs):
        obj = super(Singleton, cls).__new__(cls, *args, **kwargs)
        obj.__dict__ = cls._shared_state
        return obj


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



def safe_assign(dest, dest_key, source, source_key, converter=None):
    ''' Assign dest[dest_key] = source[source_key] only if source[source_key] exists'''
    if source and source_key in source:
        dest[dest_key] = source[source_key]

        if converter:
            dest[dest_key] = converter(dest[dest_key])
