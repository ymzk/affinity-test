
from memorysimulator.memorymanager import ObjectHeader
from memorysimulator.managedobject import ManagedObject

#####################################################################

class Array(ManagedObject):
    @staticmethod
    def size():
        return None


    @classmethod
    def construct(cls, mm, length, init = None):
        ptr = mm.malloc(length + 2)
        mm[ptr] = ObjectHeader(cls)
        mm[ptr + 1] = length
        data_ptr = ptr + 2
        if init is not None:
            if not callable(init):
                init_value = init
                init = lambda _: init_value
            for i in range(length):
                mm[data_ptr + i] = init(i)
        return cls.wrap(mm, ptr + 1), ptr

    
    @classmethod
    def destruct(cls, mm, ptr):
        pass


    def __init__(self, mm, ptr):
        self._mm = mm
        self._ptr = ptr
        self._data_ptr = ptr + 1

    
    def length(self):
        return self._mm[self._ptr]


    __len__ = length


    def __getitem__(self, index):
        assert 0 <= index < self.length()
        return self._mm[self._data_ptr + index]


    def __setitem__(self, index, value):
        assert 0 <= index < self.length()
        self._mm[self._data_ptr + index] = value


    def __iter__(self):
        for i in range(self.length()):
            yield self[i]


    def __repr__(self):
        return 'Array[{}]'.format(', '.join(map(repr, self)))


    __str__ = __repr__

#####################################################################
