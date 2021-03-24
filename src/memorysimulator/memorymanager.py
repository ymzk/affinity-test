
from memorysimulator.managedobject import ManagedObject

#####################################################################

class Ptr:
    def __init__(self, value):
        self._value = value

    def __add__(self, offset):
        assert isinstance(offset, int)
        return Ptr(self._value + offset)

    def __sub__(self, another):
        if isinstance(another, int):
            return Ptr(self._value - another)
        elif isinstance(another, Ptr):
            return Ptr(self._value - another._value)
        else:
            super().__sum__(another)

    def __repr__(self):
        return 'Ptr({})'.format(self._value)

#####################################################################

class ObjectHeader:
    def __init__(self, typeinfo):
        self.typeinfo = typeinfo

    def __repr__(self):
        return 'ObjectHeader({})'.format(self.typeinfo.__name__)

#####################################################################

class MemoryManager:
    def __init__(self, logger):
        self._heap      = []
        self._allocinfo = {}
        self._logger    = logger


    ## low-level interface

    def malloc(self, num_words):
        result = len(self._heap)
        for i in range(num_words):
            self._heap.append(None)
        self._allocinfo[result] = num_words
        self._logger.on_malloc(result, num_words)
        return Ptr(result)


    def free(self, ptr):
        ptr_ = ptr._value
        num_words = self._allocinfo[ptr_]
        for i in range(num_words):
            self._heap[ptr_ + i] = None
        del self._allocinfo[ptr_]
        self._logger.on_free(ptr_, num_words)

    
    def raw_read(self, ptr):
        ptr_ = ptr._value
        self._logger.on_read(ptr_)
        return self._heap[ptr_]


    def write(self, ptr, value):
        ptr_ = ptr._value
        self._logger.on_write(ptr_)
        self._heap[ptr_] = value


    def num_using(self):
        return sum(self._allocinfo.values())


    ## high-level interface

    def construct(self, typ, *args, **kwargs):
        assert issubclass(typ, ManagedObject)
        size = typ.size()
        if size is None:
            result, ptr = typ.construct(self, *args, **kwargs)
            ptr_ = ptr._value
            self._logger.on_construct(ptr_, typ)
            return result
        else:
            ptr = self.malloc(typ.size() + 1)
            ptr_ = ptr._value
            self.write(ptr, ObjectHeader(typ))
            typ.construct(self, ptr + 1, *args, **kwargs)
            self._logger.on_construct(ptr_, typ)
            return typ.wrap(self, ptr + 1)

    
    def destruct(self, obj):
        if isinstance(obj, Ptr):
            ptr = obj
        elif isinstance(obj, ManagedObject):
            ptr = obj._ptr - 1
        else:
            return
        ptr_ = ptr._value
        header = self._heap[ptr_]  ## metadata accesses do not trigger on_read callback
        if isinstance(header, ObjectHeader):
            header.typeinfo.destruct(self, ptr + 1)
            self.free(ptr)


    def read(self, ptr):
        ptr_ = ptr._value
        header = self._heap[ptr_]  ## metadata accesses do not trigger on_read callback
        if isinstance(header, ObjectHeader):
            return header.typeinfo.wrap(self, ptr + 1)
        else:
            return self.raw_read(ptr)


    ## array-like interface

    __getitem__ = read
    __setitem__ = write

#####################################################################
