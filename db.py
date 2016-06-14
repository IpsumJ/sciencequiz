import psycopg2
import psycopg2.extensions
from psycopg2.extras import RealDictCursor
import logging


class PGSQLConnection(object):
    def __init__(self, database, user, password, host, port, debug=False):
        self.DEBUG = debug
        self.conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port,
                                     cursor_factory=RealDictCursor)
        self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    def execute(self, query, params=None, insert=False):
        if self.DEBUG:
            cur = self.conn.cursor()
        else:
            cur = self.conn.cursor()
        if insert:
            query += ' RETURNING id'
        res = None
        cur.execute(query, params)
        if insert:
            res = cur.fetchone()['id']
            cur.close()
            return res
        if insert is not None:
            res = cur.fetchall()
        cur.close()
        return res


class LoggingCursor(psycopg2.extensions.cursor):
    def execute(self, sql, args=None):
        logger = logging.getLogger('sql_debug')
        print(args)
        logger.info(self.mogrify(sql, args))

        try:
            psycopg2.extensions.cursor.execute(self, sql, args)
        except Exception as exc:
            logger.error("%s: %s" % (exc.__class__.__name__, exc))
            raise
