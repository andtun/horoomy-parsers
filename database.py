import sqlite3


class DataBase:
    name = ''

    _db_connection = None
    _db_cur = None

    def __init__(self, name):
        self.name = name
        self._db_connection = sqlite3.connect(self.name)
        self._db_cur = self._db_connection.cursor()

    def query(self, query):
        self._db_cur.execute(query)
        self._db_connection.commit()
        return

    def fetch(self, query):
        return self._db_cur.execute(query).fetchall()

    def save(self):
        self._db_connection.commit()

    def __del__(self):
        #self._db_connection.commit()
        self._db_connection.close()

    def delete_table(self, table):
        self.query('DELETE FROM %s;' % table)
        self.query('VACUUM;')

    def format(self):
        # places - places of interest
        cmnd_list = ['' for i in range(2)]
        cmnd_list[0] = """
CREATE TABLE Results (
num INTEGER PRIMARY KEY,
cost INTEGER,
room_num INTEGER,
area INTEGER,
phone TEXT,
date TEXT,
places TEXT,
pics TEXT,
contacts TEXT,
descr TEXT,
adr TEXT,
metro TEXT,
prooflink TEXT,
loc TEXT,
fromwhere TEXT
);
"""

        cmnd_list[1] = """
CREATE TABLE Statuses (
name TEXT,
status TEXT
);
"""
        for cmnd in cmnd_list:
            self.query(cmnd)


if __name__ == "__main__":
    DataBase('parseRes.db').format()






        
