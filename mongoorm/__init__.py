"""

[![LICENSE](https://img.shields.io/badge/license-Anti%20996-blue.svg)](https://github.com/996icu/996.ICU/blob/master/LICENSE)

核心理念：
1.定义 orm 映射关系，在此基础上尽量沿用 pymongo 方法和函数
2.查询和构造 model 时不做类型检查。只在保存时检查校验类型，如 .save 和 find_and_modify 等。
3.查询到的 doc 如果 field 有 model 里尚未定义的则隐性保存并在 .save 时原样保存。

todo 查询语法校验 key 是否定义
todo 查询 filter_by[_one] 中支持 and or 等操作
todo 查询的语法改进Model.age >= 1
todo 支持枚举
todo mongodb 其他数据类型
todo 写点 test
todo pymongo 版本适配，当前 pymongo==3.7.2

todo done!!!! 增加 filter_by[_one] 支持 age__gt=1 语法
todo done!!!! self.to_json(), incloude ObjectId()
todo done!!!! 支持 user = User(_id=1, name='xxx', ...)
todo done!!!! DocModel 继承

################## tutorial ############################


# pip3 install mongoorm


from mongoorm import register_connection, DocModel, Meta
from mongoorm import fields
from bson import ObjectId

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


class User(DocModel):
    # must have _id and required=True, as primary key
    _id = fields.FieldInteger(required=True)

    # required=True means must have this field, but it can be None if nullabled=True
    k1 = fields.FieldString(required=True)

    # choices=[1, 2, 3] is the same with choices=[1, 2, 3, None] if nullabled=True
    k2 = fields.FieldInteger(required=False, choices=[1, 2, 3])

    # 1 is integer, not boolean, and True is boolean, not integer
    k3 = fields.FieldBoolean(required=False, nullabled=False)

    # default only works when the required=False
    k4 = fields.FieldFloat(required=False, default=0.1)

    # validation only works when the type_check=True in Meta class
    k5 = fields.FieldList(required=False, validation=lambda a: len(a) > 1)

    # if required=False and default is undefined, there is no this field in mongodb's document after .save
    k6 = fields.FieldDict(required=False, default=dict)

    # FieldObjectId is used for mongodb objectId data
    k7 = fields.FieldObjectId()

    # I don't suggest to use the FieldAny, 过于魔性
    k8 = fields.FieldAny()

    meta = Meta(
        db_alias='db_alias-db_test1',
        collection='test_user',
        use_schema=True,
        type_check=True,
    )


def main():
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

    us = User.find_by(
        k1='afasf',
    )
    print(us[0])

    for u in us:
        print(u._id, u.k1, u.k2)

    u = User.find_one({
        'k1': 'afasf',
    })
    print(u)

    u = User.find_one_by(
        k1='afasf',
    )
    print(u)

    u = User.find_one_and_update(
        {
            'k1': 'afasf',
        },
        {
            '$set': {
                'k2': 666
            },
        },
        upsert=False,
        return_after=True,
    )
    print(u, u._id, u.k2)


if __name__ == '__main__':
    conn_init()
    main()

"""
from .connection import register_connection
from .doc_model import DocModel
from .meta import Meta
