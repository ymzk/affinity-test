
#####################################################################

class ManagedObject:
    @classmethod
    def size(cls):
        raise NotImplementedError('{}.size()'.format(cls.__name__))

    @staticmethod
    def construct(mm, ptr, *args, **kwargs):
        pass

    @staticmethod
    def destruct(mm, ptr):
        pass

    @classmethod
    def wrap(cls, mm, ptr):
        return cls(mm, ptr)

    @classmethod
    def assign(cls, mm, ptr, value):
        raise NotImplementedError('{}.assign(mm, ptr, value)'.format(cls.__name__))

    def __init__(self, mm, ptr):
        self._mm  = mm
        self._ptr = ptr

#####################################################################
