import pymysql
from pymysql.cursors import DictCursor
import config

class Mysql:
    def __init__(self, host=config.HOST, user=config.USER, passwd=config.PASSWD, database=config.DATABASE, charset="utf8"):
        self.conn = pymysql.connect(host=host, user=user, password=passwd, database=database, charset=charset)
        self.cursor = self.conn.cursor(DictCursor)

class Mysql:
    @staticmethod
    def query(sql):
        conn = pymysql.connect(host=config.HOST, user=config.USER, password=config.PASSWD, database=config.DATABASE, charset="utf8")
        cursor = conn.cursor(DictCursor)
        cursor.execute(query=sql)
        result = cursor.fetchall()
        conn.close()
        return result

    @staticmethod
    def update(sql):
        conn = pymysql.connect(host=config.HOST, user=config.USER, password=config.PASSWD, database=config.DATABASE, charset="utf8")
        cursor = conn.cursor(DictCursor)
        cursor.execute(query=sql)
        conn.commit()
        conn.close()
        return True

if __name__ == '__main__':
    s=Mysql()
    str="ss"
    print("{}".format(str))