import MySQLdb

class DataBaseRlink:
    def __init__(self):
        # connect to the MySQL server
        try:
            self.conn = MySQLdb.connect (host = "localhost",
                                    user = "root",
                                    passwd = "kk5854kk",
                                    db = "rlink-wif")
        except MySQLdb.Error, e:
            msg_log = "Error %d: %s" % (e.args[0], e.args[1]) 
            print msg_log
            log(LOG_FILENAME, msg_log)
            sys.exit (1)

    def __del__(self):
        self.conn.close()
        log(LOG_FILENAME, "close MySQL connection")

    def runSql(self, sql_query):
        msg_log = "SQL query: %s" % sql_query
        log(LOG_FILENAME, msg_log)

        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_query)
            self.conn.commit()
            cursor.close()
        except:
            traceback.print_exc()
            log(LOG_FILENAME, "error in sql query execution, reconnecting")
            self.conn = MySQLdb.connect (host = "localhost",
                                    user = "root",
                                    passwd = "kk5854kk",
                                    db = "rlink-wif")
            cursor = self.conn.cursor()
            cursor.execute(sql_query)
            self.conn.commit()
            cursor.close()
            
# vim: ts=4:sw=4:et:sts=4:ai:tw=80
