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
