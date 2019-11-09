from .connection import register_connection
from .doc_model import DocModel
from .meta import Meta


"""
[![LICENSE](https://img.shields.io/badge/license-Anti%20996-blue.svg)](https://github.com/996icu/996.ICU/blob/master/LICENSE)

核心理念：
1.查询和构造 model 时不做类型检查。只在保存时检查校验类型，如 .save 和 find_and_modify 和 find_one_and_update 等。
2.查询到的 doc 如果 field 有 model 里尚未定义的则隐性保存并在 .save 时原样保存。

todo 创建 model 的 db_alias-collection 不能重复
todo order_by('-age')
todo 查询 filter_by[_one] 中支持 and or 等操作
todo 支持枚举
todo mongodb 其他数据类型
todo aio_mongoorm
todo 查询的语法改进Model.age >= 1
todo pymongo 版本适配，当前 pymongo==3.7.2

todo done!!!! find one and update 中对应 update 中的kv进行类型校验
todo done!!!! 增加 filter_by[_one] 支持 age__gt=1 语法
todo done!!!! self.to_json(), incloude ObjectId()
todo done!!!! 支持 user = User(_id=1, name='xxx', ...)
todo done!!!! DocModel 继承
todo done!!!! self.really_delete
todo done!!!! 查询语法校验 key 是否定义

################################# tutorial ######################################

# pip3 install mongoorm


from mongoorm import register_connection, DocModel, Meta
from mongoorm import fields
from bson import ObjectId
import copy


config = {
    'host': 'localhost',
    'port': 27017,
    # 'username': '',
    # 'password': '',
}


def conn_init():
    db_aliases = {
        'db_alias-db_test1': 'db_test1',
        'db_alias-db_test2': 'db_test2',
    }
    for db_alias, database in db_aliases.items():
        register_connection(
            db_alias=db_alias,
            database=database,
            host=config['host'],
            port=config['port'],
            # username=config['username'],
            # password=config['password'],
            # authSource='admin',
        )


class Model1(DocModel):
    __inheritance__ = True

    def log_my_id(self):
        print('log_my_id', self._id)


class User(Model1):
    # must have _id and required=True, as primary key
    _id = fields.Integer(required=True)

    # required=True means must have this field, but it can be None if nullabled=True
    k1 = fields.String(required=True)

    # choices=[1, 2, 3] is the same with choices=[1, 2, 3, None] if nullabled=True
    k2 = fields.Integer(required=False, choices=[1, 2, 3])

    # 1 is integer, not boolean, and True is boolean, not integer
    k3 = fields.Boolean(required=False, nullabled=False)

    # default only works when the required=False
    k4 = fields.Float(required=False, default=0.1)

    # validation only works when the type_check=True in Meta class
    k5 = fields.List(required=False, validation=lambda a: len(a) > 1)

    # if required=False and default is undefined, there is no this field in mongodb's document after .save
    k6 = fields.Dict(required=False, default=dict)

    # FieldObjectId is used for mongodb objectId data
    k7 = fields.ObjectId()

    # I don't suggest to use the FieldAny, 过于魔性
    k8 = fields.FieldAny()

    meta = Meta(
        db_alias='db_alias-db_test1',
        collection='test_user',
        use_schema=True,
        type_check=True,
    )


def main():
    u = User(
        _id=2,
        k1='afasf',
        k2=None,
        k3=False,
        k4=999,
        k5=[3, 6, 9],
        k6=dict(),
        k7=ObjectId(),
        k8=0.12345
    )
    u.save()
    print(u)
    print('to_json', u.to_json())

    u = User()
    u._id = 3
    u.k1 = 'afasf'
    u.k2 = None
    u.k3 = True
    u.k4 = 8
    u.k5 = [1, 2]
    # u.k6 = {}
    u.k7 = ObjectId()
    u.k8 = 1234

    u.save()
    print(u.k6)

    us = User.find({
        'k1': 'afasf',
    })
    print(us.count())
    us = us.skip(0).limit(999)
    print(us[0])

    u = User.find_one({
        'k1': 'afasf',
    })
    print(u)

    u = User.find_one_and_update(
        {
            '_id': 3,
        },
        {
            '$set': {
                'k2': 777,
            },
        },
        upsert=False,
        return_after=True,
    )
    print(u, u._id, u.k2, '===')
    u.log_my_id()

    # u = User.find({
    #     'name': '张三',
    #     'province': {
    #         '$ne': '北京',
    #     },
    #     'age': {
    #         '$gte': 20,
    #     },
    #     'phone': {
    #         '$regex': '136',
    #     },
    #     'haha': {
    #         '$exists': True,
    #     },
    # })
    #
    u = User.filter_one_by(
        k1__contains='as',
        k2__gt=0,
        k7__exists=True,
    )
    print(u, 'filter_one_by')

    us = User.filter_by(
        k1__contains='as',
    ).all()
    print(us, us.count(), 'filter_by')
    us[0].really_delete(really_delete=True)
    u = User.filter_by(
        k1__contains='as',
    ).first()
    print(u)

    u1 = User.filter_one_by()
    us = []
    for i in range(21, 30, 1):
        u = User()
        u.__dict__['__payload__'] = copy.deepcopy(u1.__dict__['__payload__'])
        u._id = i
        u.k2 = 1
        us.append(u)

    r = User.save_many_from_instances(us)
    print('save_many_from_instances', r)


if __name__ == '__main__':
    conn_init()
    main()


"""

