from bson.py3compat import integer_types


class Cursor(object):

    def __init__(self, _cursor, _cls):
        self._cursor = _cursor
        self._cls = _cls

    @property
    def _obj(self):
        return self._cursor

    @_obj.setter
    def _obj(self, value):
        self._cursor = value

    def __del__(self):
        # todo ??????????
        self._obj.__die()

    def rewind(self):
        self._obj = self._obj.rewind()
        return self

    def limit(self, limit):
        self._obj = self._obj.limit(limit)
        return self

    def skip(self, skip):
        self._obj = self._obj.skip(skip)
        return self

    def __getitem__(self, index):
        if isinstance(index, slice):
            self._obj = self._obj.__getitem__(index)
            return self
        elif isinstance(index, integer_types):
            doc = self._obj.__getitem__(index)
            if doc is None:
                return None

            m = self._cls._new_from_dict(doc)
            return m
        else:
            raise TypeError("index %r cannot be applied to Cursor instances" % index)

    def sort(self, key_or_list, direction=None):
        self._obj = self._obj.sort(key_or_list, direction=direction)
        return self

    def count(self, with_limit_and_skip=False):
        r = self._obj.count(with_limit_and_skip=with_limit_and_skip)
        return r

    def distinct(self, key):
        r = self._obj.distinct(key)
        return r

    def __iter__(self):
        self._obj = self._obj.__iter__()
        return self

    def next(self):
        d = self._obj.next()
        if d is None:
            return None
        r = self._cls._new_from_dict(d)
        return r

    __next__ = next

    def __enter__(self):
        self._obj = self._obj.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._obj.close()



'''
clone
close
limit
skip
__getitem__
max
min
sort
count
distinct
explain
hint
comment
alive
cursor_id
__iter__
next
__enter__
__exit__
__copy__
__deepcopy__
'''


class FakeCur(object):
    def __init__(self, v):
        self.a = v

    def __die(self):
        print('__die ok')

    def _Cursor__die(self):
        print('_Cursor__die ok')

    def __repr__(self):
        r = self.a.__repr__()
        return r


if __name__ == '__main__':
    _cur = FakeCur([1, 2, 3])
    c = Cursor(_cur, None)
    print(c._obj)
    c._obj = FakeCur('haha')
    print(c._obj)

