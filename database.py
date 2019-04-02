import mysql.connector


class database(object):

    def __init__(self):
        self._db_connection = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
        self._db_cur = self._db_connection.cursor(buffered=True)

    def query(self, query, params, method):

        if method == "Get":
            self._db_cur.execute(query, params)
        if method == "Insert":
            self._db_cur.execute(query, params)
            self._db_connection.commit()
        elif method == "Update":
            self._db_cur.execute(query, params)
            self._db_connection.commit()
        elif method == "Delete":
            self._db_cur.execute(query, params)
            self._db_connection.commit()

        if self._db_cur.rowcount != 0:
            result = self._db_cur.fetchall()
        else:
            result = None

        return result

    def getselectedconfig(self):
        return self.query("SELECT * from configurations WHERE selected = 1", "", "Get")

    def getrunningconfig(self):
        return self.query("SELECT * from configurations WHERE running = 1", "", "Get")

    def __del__(self):
        self._db_connection.close()