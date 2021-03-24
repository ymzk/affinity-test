
from memorysimulator.structure import structure

#####################################################################

class _Node(structure('head', 'tail')):
    _grave = None


    @classmethod
    def get_node(cls, mm, head = None, tail = None):
        if cls._grave is None:
            return mm.construct(cls, head, tail)
        else:
            result = cls._grave
            cls._grave = cls._grave.tail
            if head is not None:
                result.head = head
            result.tail = tail
            return result


    @classmethod
    def bury(cls, node):
        result = node.head
        node.head = None
        node.tail = cls._grave
        cls._grave = node
        return result



class List(structure('_front', '_back')):
    @classmethod
    def construct(cls, mm, ptr, *elems):
        self = cls.wrap(mm, ptr)
        if elems:
            it = iter(elems)
            node = self._front = mm.construct(_Node, next(it))
            try:
                while True:
                    v = next(it)
                    new_node = mm.construct(_Node, v)
                    node.tail = new_node
                    node = new_node
            except StopIteration:
                self._back = node


    @classmethod
    def destruct(cls, mm, ptr):
        self = cls.wrap(mm, ptr)
        self.clear()


    def pushfront(self, value):
        front_node = self._front
        new_front_node = _Node.get_node(self._mm, value, front_node)
        if front_node is None:
            self._front = self._back = new_front_node
        else:
            self._front = new_front_node


    def pushback(self, value):
        new_back_node = _Node.get_node(self._mm, value, None)
        if self.isempty():
            self._front = self._back = new_back_node
        else:
            self._back.tail = new_back_node
            self._back = new_back_node


    def popfront(self):
        old_front_node = self._front
        new_front_node = old_front_node.tail
        self._front = new_front_node
        if new_front_node is None:
            self._back = None
        return _Node.bury(old_front_node)


    def isempty(self):
        return self._front is None


    def __bool__(self):
        return not self.isempty()


    def clear(self):
        while self:
            self.popfront()


    def __iter__(self):
        node = self._front
        while node is not None:
            yield node.head
            node = node.tail


    def __repr__(self):
        return 'List[{}]'.format(', '.join(map(repr, self)))

    
    __str__ = __repr__

#####################################################################
