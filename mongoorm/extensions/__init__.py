from pymongo import MongoClient


if __name__ == '__main__':
    conn = MongoClient()
    coll = conn['']['']

    m = coll.find_one()
    coll.save()
    coll.insert_one()
    coll.find_one_and_update()
