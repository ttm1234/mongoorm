from .exceptions import ConnectionErr
from .extensions import MongoClient

__author__ = 'ttm1234'

_singleton_connections = {
    # (host, port, ): MongoClient(),
}
_connections = {
    # db_alias: DatabaseConn(),
}

__all__ = ['register_connection', 'get_database_conn', ]


class DatabaseConn(object):

    def __init__(self, conn, db_alias, db_name):
        self.conn = conn
        self.db_alias = db_alias
        self.db_name = db_name

    @property
    def database(self):
        r = self.conn[self.db_name]
        return r


def register_connection(
        *,
        db_alias, database, host, port, document_class=dict,
        tz_aware=None, connect=None, **kwargs
):
    assert db_alias is not None and database is not None
    db_name = database

    if db_alias in _connections:
        assert (host, port, ) in _singleton_connections, ConnectionErr(
            'same db_alias -{}- must be same host and port'.format(db_alias)
        )
        return None

    conn = _singleton_connections.get((host, port, ))
    if conn is None:
        conn = MongoClient(
            host=host, port=port, document_class=document_class, tz_aware=tz_aware, connect=connect, **kwargs
        )
        _singleton_connections[(host, port, )] = conn

    db_conn = DatabaseConn(conn, db_alias, db_name)
    _connections[db_alias] = db_conn

    return None


def _get_database_conn(db_alias):
    r = _connections.get(db_alias)
    return r


def get_database_conn(db_alias):
    db_conn = _get_database_conn(db_alias)
    if db_conn is None:
        raise ConnectionErr(
            'db_alias -{}- have not be registered, maybe use register_connection() before?'.format(db_alias)
        )
    return db_conn
