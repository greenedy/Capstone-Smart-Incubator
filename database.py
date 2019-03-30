import mysql.connector


class database(object):

    def __init__(self):
        self._db_connection = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
        self._db_cur = self._db_connection.cursor(buffered=True)

    def query(self, query, params):
        return self._db_cur.execute(query, params)

    def __del__(self):
        self._db_connection.close()