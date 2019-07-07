class Meta(object):

    def __init__(self, *,
                 db_alias, collection,
                 use_schema=True,
                 type_check=True,
                 ):
        self.db_alias = db_alias
        self.collection = collection
        self.use_schema = use_schema
        self.type_check = type_check
