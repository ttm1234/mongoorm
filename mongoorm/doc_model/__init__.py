import json
import warnings
import bson

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
    from mongoorm import register_connection, DocModel, Meta
    from mongoorm import fields

    db_aliases = {
        'db_alias-db_test1': 'db_test1',
        'db_alias-db_test2': 'db_test2',
    }
    for db_alias, database in db_aliases.items():
        register_connection(
            db_alias=db_alias,
            database=database,
            host='localhost',
            port=27017,
            # username='xxxxxx',
            # password='xxxxxx',
            # authSource='admin',
        )

    class User(DocModel):
        _id = fields.Integer()
        name = fields.String()

         meta = Meta(
            db_alias='db_alias-db_test1',
            collection='test_user',
        )

    """

    def __init__(self, **kwargs):
        """
        :param kwargs: field key, value
        以下属性在 ModelMetaClass 中已被创造
        cls.__mappings__  --> fields
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

    def really_delete(self, really_delete=False):
        assert really_delete
        coll = self._get_collection()
        coll.delete_one({'_id': self._id})

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
    def _valid_keys(cls, d: dict):
        # todo and or ?????
        for k in d.keys():
            k0 = k.split('.')[0]
            if k0 not in cls.__mappings__:
                e = DocModelErr(r'''k ({}) not defined in Model '''.format(k))
                raise put_cls_exception(e, cls)

    @classmethod
    def _new_from_dict(cls, d):
        bson64_keys = []
        m = cls()
        # bson.int64.Int64 to int
        for k, v in d.items():
            if isinstance(v, bson.int64.Int64):
                bson64_keys.append(k)
        m.__dict__['__payload__'].update(d)
        for k in bson64_keys:
            m.__dict__['__payload__'][k] = int(m.__dict__['__payload__'][k])
        return m

    @classmethod
    def find_one(cls, filter=None, *args, **kwargs):
        d = cls._get_collection().find_one(filter=filter, *args, **kwargs)
        if d is None:
            return None

        m = cls._new_from_dict(d)
        return m

    @classmethod
    def find(cls, *args, **kwargs):
        cursor_raw = cls._get_collection().find(*args, **kwargs)
        cur = Cursor(cursor_raw, cls)
        return cur

    @classmethod
    def filter_one_by(cls, **kwargs):
        q = cls._filter_to_find(**kwargs)
        cls._valid_keys(q)
        r = cls.find_one(q)
        return r

    @classmethod
    def filter_by(cls, **kwargs):
        q = cls._filter_to_find(**kwargs)
        cls._valid_keys(q)
        r = cls.find(q)
        return r

    @classmethod
    def find_one_and_update(
            cls, filter, update, i_really_do_not_forget_set_in_update_arg=False,
            sort=None, upsert=False, return_after=False, array_filters=None, **kwargs
    ):
        assert 'return_document' not in kwargs

        if not i_really_do_not_forget_set_in_update_arg:
            for k, v in update.items():
                if not k.startswith('$'):
                    exception = ModelValidErr(r'''you must have forgot $set in 'update' arg,
                    such as {'$set': {k: v}}; or set i_really_do_not_forget_set_in_update=True??? (dangers!!!!)''')
                    raise put_cls_exception(exception, cls)

                cls._valid_keys(v)

        cls._valid_keys(filter)

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

    @classmethod
    def save_many_from_instances(cls, instances, ordered=False, bypass_document_validation=False):
        for i in instances:
            if not isinstance(i, cls):
                exception = ModelValidErr(r'''in method 'save_many_from_instances', 
                instances must all is instance of cls''')
                raise put_cls_exception(exception, cls)

        docs = []
        for m in instances:
            self = m
            if self._use_schame:
                # 数据补全
                self._schame_completion()
            if self._type_check:
                # 检查类型
                self._check_field_type(undefined_is_ok=True)

            docs.append(m.__payload__)

        r = cls._get_collection().insert_many(docs, ordered=ordered, bypass_document_validation=bypass_document_validation)
        return r


if __name__ == '__main__':
    a = dict()
    a.pop('a', None)
