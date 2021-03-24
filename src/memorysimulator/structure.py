
from utility import callviabracket
from memorysimulator.managedobject import ManagedObject

#####################################################################

class StructureBuilder:
    def __init__(self, name, bases, attrs, metaclass):
        self._name      = name
        self._bases     = bases
        self._attrs     = attrs
        self._metaclass = metaclass

        if all(base != ManagedObject for base in self._bases):
            self._bases += (ManagedObject,)


    def build_size(self):
        yield '    @staticmethod'
        yield '    def size():'
        yield '        return {}'.format(len(self._attrs))


    def build_construct(self):
        params = ', '.join('{} = None'.format(attr) for attr in self._attrs)
        yield '    @staticmethod'
        yield '    def construct(mm, ptr, {}):'.format(params)
        for i, attr in enumerate(self._attrs):
            yield '        if {} is not None:'.format(attr)
            yield '            mm[ptr + {}] = {}'.format(i, attr)


    def build_destruct(self):
        yield '    @staticmethod'
        yield '    def destruct(mm, ptr):'
        yield '        pass'


    def build_wrap(self):
        yield '    @classmethod'
        yield '    def wrap(cls, mm, ptr):'
        yield '        return cls(mm, ptr)'

    
    def build_init(self):
        yield '    def __init__(self, mm, ptr):'
        yield '        self._mm = mm'
        yield '        self._ptr = ptr'


    def build_getitem(self):
        yield '    def __getitem__(self, i):'
        yield '        assert 0 <= i < type(self).size()'
        yield '        return self._mm[self._ptr + i]'


    def build_setitem(self):
        yield '    def __setitem__(self, i, value):'
        yield '        assert 0 <= i < type(self).size()'
        yield '        self._mm[self._ptr + i] = value'

    
    def build_getattr(self):
        yield '    def __getattr__(self, attr):'
        for i, attr in enumerate(self._attrs):
            yield '        {} attr == \'{}\':'.format('if' if i == 0 else 'elif', attr)
            yield '            return self._mm[self._ptr + {}]'.format(i)
        yield '        else:'
        yield '            return super().__getattr__(attr)'


    def build_setattr(self):
        yield '    def __setattr__(self, attr, value):'
        for i, attr in enumerate(self._attrs):
            yield '        {} attr == \'{}\':'.format('if' if i == 0 else 'elif', attr)
            yield '            self._mm[self._ptr + {}] = value'.format(i)
        yield '        else:'
        yield '            super().__setattr__(attr, value)'


    def build_iter(self):
        yield '    def __iter__(self):'
        yield '        for i in range(type(self).size()):'
        yield '            yield self._mm[self._ptr + i]'

    
    def build_repr(self):
        yield '    def __repr__(self):'
        yield '        attrs = []'
        for i, attr in enumerate(self._attrs):
            yield '        attrs.append(\'{} = {{}}\'.format(repr(self._mm[self._ptr + {}])))'.format(attr, i)
        yield '        return \'{}({})\'.format(type(self).__name__, \', \'.join(attrs))'


    def build_str(self):
        yield '    def __str__(self):'
        yield '        attrs = []'
        for i, _ in enumerate(self._attrs):
            yield '        attrs.append(repr(self._mm[self._ptr + {}]))'.format(i)
        yield '        return \'{}({})\'.format(type(self).__name__, \', \'.join(attrs))'


    def build_all(self):
        yield 'class {}(*bases, metaclass = metaclass):'.format(self._name)
        yield from self.build_size()
        yield from self.build_construct()
        yield from self.build_destruct()
        yield from self.build_wrap()
        yield from self.build_init()
        yield from self.build_getitem()
        yield from self.build_setitem()
        yield from self.build_getattr()
        yield from self.build_setattr()
        yield from self.build_iter()
        yield from self.build_repr()
        yield from self.build_str()


    def build(self):
        globals = { 'bases' : self._bases, 'metaclass' : self._metaclass }
        locals = {}
        exec('\n'.join(self.build_all()), globals, locals)
        return locals[self._name]



def structure(*attrs, bases = (), name = 'AnonymousStructure', metaclass = type):
    return StructureBuilder(name, bases, attrs, metaclass).build()

#####################################################################
