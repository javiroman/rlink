#!/usr/bin/env python
"""

(C) 2008-2009 Javi Roman <javiroman@kenel-labs.org>

$Id$
"""
import sys
import traceback
import Ice
import socket
import signal
import syslog
import time
import os
import MySQLdb

#
# Important sanity tests.
#
slice_dir = os.getenv('ICEPY_HOME', '')
if len(slice_dir) == 0 or not os.path.exists(os.path.join(slice_dir, 'slice')):
    slice_dir = os.getenv('ICE_HOME', '')
if len(slice_dir) == 0 or not os.path.exists(os.path.join(slice_dir, 'slice')):
    slice_dir = os.path.join('/', 'usr', 'share')
if not os.path.exists(os.path.join(slice_dir, 'slice')):
    print sys.argv[0] + ': Slice directory not found. Define ICEPY_HOME or ICE_HOME.'
    sys.exit(1)

MAIN_CONFIG_DIR = os.getcwd()
CONFIG_FILE = MAIN_CONFIG_DIR + "/" + "dbconnector.cfg"
LOG_FILENAME = "dbconnector.log"
VERSION="0.0.3"

Ice.loadSlice('-I' + slice_dir + '/slice ' + MAIN_CONFIG_DIR + "/" + "DBConnector.ice")
import DBConnector

def daemonize():
    # do the UNIX double-fork magic, see Stevens' "Advanced
    # Programming in the UNIX Environment" for details (ISBN 0201563177)
    try:
        pid = os.fork()
        if pid > 0:
            # exit first parent
            sys.exit(0)
    except OSError, e:
        quote = 'broadpro: fork #1 failed: ' + e.errno + '(' + e.strerror + ')'
        syslog.syslog(quote)  
        sys.exit(1)

    # decouple from parent environment
    os.chdir("/") # don't prevent unmounting....
    os.setsid()
    os.umask(0)

    # do second fork
    try:
        pid = os.fork()
        if pid > 0:
            # exit from second parent, print eventual PID before
            sys.exit(0)
    except OSError, e:
        quote = 'broadpro: fork #2 failed: ' + e.errno + '(' + e.strerror + ')'
        syslog.syslog(quote)  
        sys.exit(1)

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
            
class SimpleLogger:
    def __init__(self, logroot):
        # possible log rotation here
        # sys.stdout = sys.__stdout__ 
        sys.stderr = open(logroot + "/" + LOG_FILENAME, 'a')
        self.logroot = logroot

    def __call__(self, filelog, string):
        file = open(self.logroot + "/" + filelog, 'a')
        file.write('[' + time.asctime() + '] ')
        file.write(string + '\n')
        file.close()
        print string

class DBInsertionI(DBConnector.DBInsertion):
    def __init__(self, communicator):
        print "constructor"
        self._localhome = ""
        self._ic = communicator
        self._client = None
        self._db = DataBaseRlink()

    def pingTest(self, s, current=None):
        self._localhome = s
        print s

    def linkerToDBConnector(self, app_linked, target, linker_output, port, current=None):
        if not target:
            target = "all"

        msg_log = "Inserting %s target %s in DB" % (app_linked, target)
        log(LOG_FILENAME, msg_log)

        if linker_output.find("Error") > 0:
            print "linker ERROR!"
            ret = 1
        else:
            print "linked OK"
            ret = 0

        sql_cmd = """INSERT INTO rlink_enlazados VALUES
                  ("%s", %s, "rlink%s", "%s", "%s", %s)
        """ % (time.time(), "NULL", port, app_linked, target, ret)

        self._db.runSql(sql_cmd)

class AppRlinkDBConnector(Ice.Application):
    def __init__(self, service_name="Servidor"):
        log(LOG_FILENAME, "<AppRlinkDBConnector constructor>")
        self.service_name = service_name

    def run(self, args):
        ic = self.communicator()

        # Rlink is got from config file: Rlink.EndPoints
        adapter = ic.createObjectAdapter("DBConnector")
        serv_thread = DBInsertionI(ic)
        ident = ic.stringToIdentity("RlinkDBConnector")
        adapter.add(serv_thread, ident)
        adapter.activate()

        self.communicator().waitForShutdown()

        if self.interrupted():
            print self.appName() + "\nice runtime cleaned shutdown."

def main():
    global log
    log = SimpleLogger(MAIN_CONFIG_DIR)

    log(LOG_FILENAME, "-------------------------------------------------------")
    version = "Rlink DBConnector version %s" % VERSION
    log(LOG_FILENAME, version)
    log(LOG_FILENAME, "-------------------------------------------------------")

    pidfile = open("/home/jroman/DEV/dbconnector/dbconnector.pid", 'w+')
    pidfile.write(str(os.getpid()))
    pidfile.close()

    app = AppRlinkDBConnector()

    if not os.path.exists(CONFIG_FILE):
        log(LOG_FILENAME, "main configuration file missing ...")
        return 1
    else:
        """
        To overwrite Ice system variables we've to initialize InitializationData
        structure, before Ice initialization. The config_file (second
        parameter to app.main, has to be setted up to None.
        """
        id = Ice.InitializationData()
        id.properties = Ice.createProperties()
        id.properties.load(CONFIG_FILE)
        #id.properties.setProperty("IceSSL.DefaultDir", MAIN_CONFIG_DIR + "/" + "client_certs")

        return (app.main(sys.argv, None, id))

if __name__ == "__main__":
    daemonize()
    sys.exit(main())

# vim: ts=4:sw=4:et:sts=4:ai:tw=80
