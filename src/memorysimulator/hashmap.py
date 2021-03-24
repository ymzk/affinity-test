
from memorysimulator.structure import structure
from memorysimulator.array import Array

#####################################################################


class DeletedType:
    def __repr__(self):
        return 'DELETED'

DELETED = DeletedType()


#####################################################################


class _Entry(structure('key', 'value', 'next', 'prev')):
    _grave = None

    @classmethod
    def bury(cls, entry):
        entry.key = None
        entry.value = None
        entry.next = cls._grave
        entry.prev = None
        cls._grave = entry

    @classmethod
    def new_entry(cls, mm, key = None, value = None, next = None, prev = None):
        if cls._grave is None:
            return mm.construct(cls, key, value, next, prev)
        else:
            result = cls._grave
            cls._grave = result.next
            if key is not None:
                result.key = key
            if value is not None:
                result.value = value
            result.next = next
            if prev is not None:
                result.prev = prev
            return result


    def __repr__(self):
        return 'Entry({!r}, {!r})'.format(self.key, self.value)


#####################################################################


class HashMap(structure('_capacity', '_size', '_deleted', '_table', '_first', '_last')):
    @classmethod
    def construct(cls, mm, ptr):
        self = cls.wrap(mm, ptr)
        self._capacity = 28
        self._size     = 0
        self._deleted  = 0
        self._table    = mm.construct(Array, 28)
        ## self._first = None
        ## self._last  = None


    @classmethod
    def destruct(cls, mm, ptr):
        self = cls.wrap(mm, ptr)
        for e in self._entries():
            _Entry.bury(e)
        mm.destruct(self._table)


    def _lookup(self, key):
        cap = self._capacity
        index = hash(key) % cap
        while True:
            e = self._table[index]
            if e is None:
                return index, None
            elif e is DELETED or e.key != key:
                index = (index + 1) % cap
            else:
                return index, e


    def _addentry(self, index, key, value):
        ## assert self._table[index] is None
        self._size += 1
        if self._check_and_rehash():
            index, e = self._lookup(key)
            assert e is None
        last_entry = self._last
        new_entry = _Entry.new_entry(self._mm, key, value, None, last_entry)
        if last_entry is None:
            self._first = self._last = new_entry
        else:
            self._last = last_entry.next = new_entry
        self._table[index] = new_entry


    def _check_and_rehash(self):
        capacity = self._capacity
        size     = self._size
        deleted  = self._deleted
        if (size + deleted) * 10 <= capacity * 6:
            return False
        elif size * 100 > capacity * 6 * 8:
            new_capacity = capacity * 2
            self._mm.destruct(self._table)
            self._table = self._mm.construct(Array, new_capacity)
            self._capacity = new_capacity
        else:
            for i in range(capacity):
                self._table[i] = None

        entry = self._first
        while entry is not None:
            index, e = self._lookup(entry.key)
            assert e is None
            self._table[index] = entry
            entry = entry.next
        return True


    def _delentry(self, index, entry):
        ## assert entry is not None and self._table[index] is entry
        self._size -= 1
        self._deleted += 1
        next_entry = entry.next
        prev_entry = entry.prev
        if next_entry is None and prev_entry is None:
            self._first = self._last = None
        elif next_entry is None and prev_entry is not None:
            self._last = prev_entry
            prev_entry.next = None
        elif next_entry is not None and prev_entry is None:
            self._first = next_entry
            next_entry.prev = None
        else:
            next_entry.prev = prev_entry
            prev_entry.next = next_entry
        self._table[index] = DELETED
        _Entry.bury(entry)


    def __getitem__(self, key):
        index, entry = self._lookup(key)
        if entry is None:
            raise KeyError(repr(key))
        else:
            return entry.value


    def __setitem__(self, key, value):
        index, entry = self._lookup(key)
        if entry is None:
            self._addentry(index, key, value)
        else:
            entry.value = value


    def __delitem__(self, key):
        index, entry = self._lookup(key)
        if entry is None:
            raise KeyError(repr(key))
        self._delentry(index, entry)


    def __len__(self):
        return self._size


    def __bool__(self):
        return len(self) > 0


    def items(self):
        entry = self._first
        while entry is not None:
            yield (entry.key, entry.value)
            entry = entry.next

    
    def keys(self):
        for k, _ in self.items():
            yield k


    def values(self):
        for _, v in self.items():
            yield v


    def __repr__(self):
        if len(self) == 0:
            return 'HashMap{}'
        else:
            items = ('{!r} : {!r}'.format(k, v) for k, v in self.items())
            return 'HashMap{{ {} }}'.format(', '.join(items))

#####################################################################
