class Meta(object):

    def __init__(self, *,
                 db_alias, collection,
                 use_schema=True,
                 type_check=True,
                 collection_name_repeated=False):
        self.db_alias = db_alias
        self.collection = collection
        self.use_schema = use_schema
        self.type_check = type_check
        self.collection_name_repeated = collection_name_repeated
