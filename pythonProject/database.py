import config as cf
import psycopg2

#db = psycopg2.connect(host=cf.host, dbname=cf.database, user=cf.user, password=cf.password, port=cf.port)

#cursor = db.cursor()

class Databases():
    def __init__(self):
        self.db = psycopg2.connect(host=cf.host, dbname=cf.database,user=cf.user,password=cf.password,port=cf.port)
        self.cursor = self.db.cursor()

    def __del__(self):
        self.db.close()
        self.cursor.close()

    def execute(self,query,args={}):
        self.cursor.execute(query,args)
        row = self.cursor.fetchall()
        return row

    def commit(self):
        self.cursor.commit()