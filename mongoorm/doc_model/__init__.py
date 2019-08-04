import json
import warnings

import six
import copy

from .filter_by import FilterBy
from ..utils import JSONEncoder
from ..cursor import Cursor
from ..exceptions import UndefinedError, DocModelErr, ModelValidErr, put_inst_exception, put_cls_exception
from ..model_meta_class import ModelMetaClass
from ..connection import get_database_conn
from .payload_dict import PayloadDict


@six.add_metaclass(ModelMetaClass)
class DocModel(PayloadDict, FilterBy):
    """
    eg.
    class User(DocModel):
        _id = FieldInteger()
        name = FieldString()

         meta = Meta(
            db_alias='db_alias-db_test1',
            collection='test_user',
        )

    """

    def __init__(self, **kwargs):
        """
        :param kwargs: field key, value
        以下属性在 ModelMetaClass.new 中已被创造
        __mappings__  --> fields
        """
        self.__dict__['__payload__'] = dict()
        self.update(kwargs)

    def __repr__(self):
        s = super(DocModel, self).__repr__()
        r = '{}-({})-'.format(s, self.to_json())
        return r

    def get_dict(self):
        return copy.deepcopy(self.__payload__)

    def to_json(self, **kwargs):
        d = self.get_dict()
        if 'cls' not in kwargs:
            kwargs.update(dict(
                cls=JSONEncoder
            ))
        if 'indent' not in kwargs:
            kwargs['indent'] = 4
        return json.dumps(d, **kwargs)

    def save(self, force_insert=False, manipulate=True, check_keys=True, **kwargs):

        if self._use_schame:
            # 数据补全
            self._schame_completion()

        if self._type_check:
            # 检查类型
            self._check_field_type(undefined_is_ok=True)

        d = self.__payload__
        coll = self._get_collection()

        if force_insert:
            warnings.warn("force_insert save = insert_one", DeprecationWarning, stacklevel=2)
            _id = coll.insert(d, manipulate=manipulate, check_keys=check_keys, **kwargs)
        else:
            _id = coll.save(d, manipulate=manipulate, check_keys=check_keys, **kwargs)
        return self

    def _schame_completion(self):
        """
        对于无相应的值，
        如果required=True,直接报错。
        否则
            如果有default,使用
            否则缺失
        """
        d = self.__payload__
        for k, obj in self.__mappings__.items():
            if k not in d:
                if obj.required:
                    raise put_inst_exception(DocModelErr('{} is required'.format(k)), self)

                try:
                    v = obj.get_default_value()
                    d[k] = v
                except UndefinedError as e:
                    pass

    def _check_field_type(self, undefined_is_ok=False):
        d = self.__payload__
        for k, obj in self.__mappings__.items():
            if k not in d:
                if undefined_is_ok:
                    continue
                else:
                    raise put_inst_exception(DocModelErr('check_field_type error, because field: {} is undefined'.format(k)), self)

            v = d[k]
            try:
                obj.validate(v)
            except ModelValidErr as e:
                msg = str(e)
                raise put_inst_exception(ModelValidErr('key {}, {}'.format(k, msg)), self)

    # ============ classmethod =============

    @classmethod
    def _meta_getattr(cls, k):
        return getattr(cls.meta, k)

    @classmethod
    def _meta_setattr(cls, k, v):
        """
        原则上不改这个
        setattr(self.meta, k, v)
        """
        raise Exception()

    @classmethod
    @property
    def _use_schame(cls):
        return cls._meta_getattr('use_schema')

    @classmethod
    @property
    def _type_check(cls):
        return cls._meta_getattr('type_check')

    @classmethod
    def _get_database_conn(cls):
        db_alias = cls._meta_getattr('db_alias')
        db_conn = get_database_conn(db_alias)
        return db_conn

    @classmethod
    def _get_connection(cls):
        db_conn = cls._get_database_conn()
        conn = db_conn.conn
        return conn

    @classmethod
    def _get_database(cls):
        db_conn = cls._get_database_conn()
        db = db_conn.database
        return db

    @classmethod
    def _get_collection(cls):
        coll_name = cls._meta_getattr('collection')
        database = cls._get_database()
        coll = database[coll_name]
        return coll

    @classmethod
    def _new_from_dict(cls, d):
        m = cls()
        m.__dict__['__payload__'].update(d)
        return m

    @classmethod
    def find_one(cls, filter=None, *args, **kwargs):
        d = cls._get_collection().find_one(filter=filter, *args, **kwargs)
        if d is None:
            return None

        m = cls._new_from_dict(d)
        return m

    @classmethod
    def find_one_by(cls,  *args, **kwargs):
        assert len(args) == 0, 'find_one_by only access kwargs'
        filter = kwargs
        r = cls.find_one(filter)
        return r

    @classmethod
    def filter_one_by(cls, **kwargs):
        q = cls._filter_to_find(**kwargs)
        r = cls.find_one(q)
        return r

    @classmethod
    def find(cls, *args, **kwargs):
        cursor_raw = cls._get_collection().find(*args, **kwargs)
        cur = Cursor(cursor_raw, cls)
        return cur

    @classmethod
    def find_by(cls, *args, **kwargs):
        assert len(args) == 0, 'filter_by only access kwargs'
        filter = kwargs
        r = cls.find(filter)
        return r

    @classmethod
    def filter_by(cls, **kwargs):
        q = cls._filter_to_find(**kwargs)
        r = cls.find(q)
        return r

    @classmethod
    def find_one_and_update(
            cls, filter, update, i_really_do_not_forget_set_in_update_arg=False,
            sort=None, upsert=False, return_after=False, array_filters=None, **kwargs
    ):
        assert 'return_document' not in kwargs

        if not i_really_do_not_forget_set_in_update_arg:
            for i in update.keys():
                if not i.startswith('$'):
                    exception = ModelValidErr(r'''you must have forgot $set in 'update' arg,
                    such as {'$set': {k: v}}; or set i_really_do_not_forget_set_in_update=True??? (dangers!!!!)''')
                    raise put_cls_exception(exception, cls)

        for k in filter.keys():
            if k not in cls.__mappings__:
                e = DocModelErr(r'''k ({}) not defined in Model '''.format(k))
                raise put_cls_exception(e, cls)

        d = cls._get_collection().find_one_and_update(
            filter, update, sort=sort, upsert=upsert, return_document=return_after,
            array_filters=array_filters, **kwargs
        )
        if d is None:
            return None
        m = cls._new_from_dict(d)
        return m

    @classmethod
    def aggregate(cls, pipeline, **kwargs):
        r = cls._get_collection().aggregate(pipeline, **kwargs)
        return r


if __name__ == '__main__':
    a = dict()
    a.pop('a', None)
