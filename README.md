# mongoorm
<a href="https://996.icu"><img src="https://img.shields.io/badge/link-996.icu-red.svg" alt="996.icu" /></a>

mongo orm python3

[![LICENSE](https://img.shields.io/badge/license-Anti%20996-blue.svg)](https://github.com/996icu/996.ICU/blob/master/LICENSE)

1.0.4 is ok

pip3 install mongoorm

使用方法见 demo.py

```
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

    k9 = fields.Integer(required=False)

    meta = Meta(
        db_alias='db_alias-db_test1',
        collection='test_user',
        use_schema=True,
        type_check=True,
    )


class UserWithSameCollection(DocModel):
    # must have _id and required=True, as primary key
    _id = fields.Integer(required=True)

    k_not_found = fields.Integer(required=False, rich_default=9)

    meta = Meta(
        db_alias='db_alias-db_test1',
        collection='test_user',
        use_schema=True,
        type_check=True,
        collection_name_repeated=True,
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
        k8=0.12345,
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
    u.k9 = 1999999999999

    u.save()
    print('type(u.k9)-before', type(u.k9))
    print(u.k6)

    us = User.find({
        'k1': 'afasf',
    })
    print(us.count())
    us = us.skip(0).limit(999)
    print(us[0])

    us = User.find({})
    us = us.order_by('-_id')
    print('order by', us[0])

    u = User.find_one({
        '_id': 3,
    })
    print(u)
    print('type(u.k9)-after', type(u.k9))

    u = UserWithSameCollection.find_one({})
    print(u)
    print('k_not_found', type(u.k_not_found))

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

    # u1 = User.filter_one_by()
    # us = []
    # for i in range(121, 130, 11):
    #     u = User()
    #     u.__dict__['__payload__'] = copy.deepcopy(u1.__dict__['__payload__'])
    #     u._id = i
    #     u.k2 = 1
    #     us.append(u)
    #
    # r = User.save_many_from_instances(us)
    # print('save_many_from_instances', r)


if __name__ == '__main__':
    conn_init()
    main()

```
