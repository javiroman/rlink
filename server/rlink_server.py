#!/usr/bin/env python
"""

(C) 2008-2009 Javi Roman <javiroman@kernel-labs.org>

$Id$
"""
import sys
import md5
import traceback
import Ice
import os
import array
import errno
import fnmatch
import popen2
import threading
import pickle
import time

# 
# Important sanity tests.
#
slice_dir = os.getenv('ICEPY_HOME', '')
if len(slice_dir) == 0 or not os.path.exists(os.path.join(slice_dir, 'slice')):
    slice_dir = os.getenv('ICE_HOME', '')
if len(slice_dir) == 0 or not os.path.exists(os.path.join(slice_dir, 'slice')):
    slice_dir = os.path.join('/', 'usr', 'share')
if not os.path.exists(os.path.join(slice_dir, 'slice')):
    print slice_dir
    print sys.argv[0] + ': Slice directory not found. Define ICEPY_HOME or ICE_HOME.'
    sys.exit(1)

home = os.getenv('CAP_HOME')
if not home:
    print "please you have to set up CAP_HOME variable ..."
    os._exit(1)
 
VERSION="0.0.4"
MAIN_CONFIG_DIR = home + "/" + "rlink_main_folder"
CONFIG_FILE = MAIN_CONFIG_DIR + "/" + "rlink_server.cfg"

Ice.loadSlice('-I' + slice_dir + '/slice ' + MAIN_CONFIG_DIR + "/" + "Rlink.ice")
import Rlink

Ice.loadSlice('-I' + slice_dir + '/slice ' + MAIN_CONFIG_DIR + "/" + "DBConnector.ice")
import DBConnector

def mkdirp(directory):
    if not os.path.isdir(directory):
        os.makedirs(directory)

class SimpleLogger:
    def __init__(self, logroot):
        # possible log rotation here
        # sys.stdout = sys.__stdout__
        sys.stderr = open(logroot + "/" + "rlink_server.log" , 'a')
        sys.stdout = open(logroot + "/" + "rlink_server.log" , 'a')
        self.logroot = logroot

    def __call__(self, filelog, string):
        file = open(self.logroot + "/" + filelog, 'a')
        file.write('[' + time.asctime() + '] ')
        file.write(string + '\n')
        file.close()
        print string

class Cache:
    def __init__(self, pattern, dir):
        log("rlink_server.log" , "<Cache constructor>")
        self._cachepathfile = dir + "/" + ".cache"
        self._cache = {}
        self._cachefile = os.path.exists(self._cachepathfile)
        self._el = self._findAllObjects(pattern, dir)
        self._ml = ()

    def _md5sum(self, filename):
        """Return the hex digest of a file without loading it all into memory."""
        fh = open(filename)
        digest = md5.new()
        while 1:
            buf = fh.read(4096)
            if buf == "":
                break
            digest.update(buf)

        fh.close()

        return digest.hexdigest()

    def _findAllObjects(self, pattern, root=os.curdir):
        ol = []
        pwd = os.getcwd()

        for path, dirs, files in os.walk(os.path.abspath(root)):
            for filename in fnmatch.filter(files, pattern):
                if filename == ".cache":
                   continue 

                ol.append(path + "/" + filename)

        return ol

    def _purgeList(self):
        ml = []
        for i in self._el:
            # object is new in filesystem
            if not self._cache.has_key(i):
                ml.append(i)
                self._cache[i] = self._md5sum(i)
                pass
            # object is not modified
            md5 = self._md5sum(i)
            if self._cache[i] == md5:
                pass
            else:
                self._cache[i] = md5
                ml.append(i)

        return ml

    def getModfied(self):
        if not self._cachefile:
            log("rlink_server.log" , "<no existe cache, creando ...>")
            for i in self._el:
                self._cache[i] = self._md5sum(i)

            f = open(self._cachepathfile, 'wb')
            pickle.dump(self._cache, f)
            f.close()
            self._ml = self._el
        else:
            log("rlink_server.log" , "<cargando cache>")
            f = open(self._cachepathfile, 'rb')
            self._cache = pickle.load(f)
            f.close()
            self._ml = self._purgeList()

        if not self._ml:
            log("rlink_server.log" , "<no objetos modificados>")
        else:
            f = open(self._cachepathfile, 'wb')
            pickle.dump(self._cache, f)
            f.close()

        log_msg = "<Objetos modificados: %d>" % len(self._ml)
        log("rlink_server.log" , log_msg)

        return self._ml

class FileTransferI(Rlink.FileTransfer):
    def __init__(self, communicator, db_servant, port):
        log("rlink_server.log" , "<FileTransferI constructor>")
        self._localhome = ""
        self._ic = communicator
        self._client = None
        self._db_servant = db_servant
        self._port = port

    def pingTest(self, s, current=None):
        self._localhome = s
        print s

    def sendFile(self, s, file, current=None):
        try:
            binvalues = array.array('B')
            binvalues.fromlist(file)

            s = s.replace(self._localhome, home)

            #
            # we've to create the target folders with
            # the exception of makefile.rlink file.
            #
            if s.split("/")[-1] != "makefile.rlink":
                mkdirp(s.replace(s.split("/")[-1], ""))
            else:
                s = s.replace("/rlink/", "/")
                s = s.replace("makefile.rlink", "Makefile")

            print s
            f = open(s, 'wb')
            binvalues.tofile(f)
            f.close()

        except:
            print "No se pudo escribir el fichero %s" % s

    def makeLinking(self, s, target, current=None):
        cmd = "make -C " + home + "/" + s + " " + target
        log("rlink_server.log" , cmd) 

        (child_stdout_and_stderr, child_stdin) = popen2.popen4(cmd)

        return_output = child_stdout_and_stderr.read()

        sys.stdout.write(return_output)
        sys.stdout.flush()

        # We send the linking folder and the output of linker for
        # parsing and error detection.
        self._db_servant.linkerToDBConnector(s, target, return_output, self._port) 

        return return_output

    def _findAllObjects(self, pattern, root=os.curdir):
        ol = [] 
        pwd = os.getcwd()

        for path, dirs, files in os.walk(os.path.abspath(root)):
            for filename in fnmatch.filter(files, pattern):
                ol.append(path + "/" + filename)

        return ol

    def getOutputs(self, s, current=None):
        exes_path = s
        err_path = s

        if exes_path.split("/")[-1] == "obj":
            exes_path = exes_path.replace(exes_path.split("/")[-1], "exes")
        else:
            exes_path = exes_path + "/exes"

        if err_path.split("/")[-1] == "obj":
            err_path = err_path.replace(err_path.split("/")[-1], "err")
        else:
            err_path = err_path + "/err"

        for s in [exes_path, err_path]:
            c = Cache("*", s)
            el = c.getModfied()

            for i in el:
                if not os.path.exists(i):
                    log_msg = "No se pudo leer el fichero %s" % i
                    log("rlink_server.log" , log_msg)
                    return False
                try:
                    size = os.path.getsize(i)
                    f = file(i, mode='rb')
                    binvalues = array.array('B')
                    binvalues.fromfile(f, size)
                    f.close()
                    log_msg = "sending file: %s (size %d)" % (i, size)
                    log("rlink_server.log" , log_msg)
                except:
                    log_msg = "Mierda No se pudo leer el fichero %s" % i
                    log("rlink_server.log" , log_msg)

                # send linked files and errors
                self._client.backOutputs(home, i, binvalues.tolist())

    def addClient(self, ident, current=None):
        print "adding client `" + self._ic.identityToString(ident) + "'"

        client = Rlink.CallbackFunctionsPrx.uncheckedCast(current.con.createProxy(ident))
        self._client = client

class AppRlinkServer(Ice.Application):
    def __init__(self, service_name="Servidor"):
        log("rlink_server.log", "ApplicationServer constructor")
        pid = os.getpid()
        pidfile = open(MAIN_CONFIG_DIR + "/rlink_server.pid", "w")
        str_pid = "%d" % pid
        pidfile.write(str_pid)
        pidfile.close()
        self.service_name = service_name

    def run(self, args):
        ic = self.communicator()

        # DBConnector stuff, client code.
        properties = ic.getProperties()
        proxy = properties.getProperty('DBConnector.Proxy')
        endpoint = properties.getProperty('Rlink.Endpoints')
        port = endpoint.split("-p ")[-1]

        if len(proxy) == 0:
            log("rlink_server.log", "property `DBConnector.Proxy' not set")
            return False
        else:
            log("rlink_server.log", "DBConnector.Proxy finded")

        try:
            servant = \
                DBConnector.DBInsertionPrx.checkedCast(ic.stringToProxy(proxy))

        except Ice.NotRegisteredException:
            log("rlink_server.log", "Execpcion no registrado!!!")
            traceback.print_exc()
            sys.exit(1)

        servant.pingTest("Initialization message from rlink_server.py")
        # Rlink is got from config file: Rlink.EndPoints
        adapter = ic.createObjectAdapter("Rlink")
        serv_thread = FileTransferI(ic, servant, port)
        ident = ic.stringToIdentity("SimplePrinter")
        adapter.add(serv_thread, ident)
        adapter.activate()


        self.communicator().waitForShutdown()

        if self.interrupted():
            print self.appName() + "\nice runtime cleaned shutdown."

def main():
    global log
    log = SimpleLogger(MAIN_CONFIG_DIR + "/logs")

    log("rlink_server.log", "-------------------------------------------------------")
    version = "Rlink Server version %s" % VERSION
    log("rlink_server.log", version)
    log("rlink_server.log", "-------------------------------------------------------")

    app = AppRlinkServer()

    if not os.path.exists(CONFIG_FILE):
        log("rlink_server.log", "main configuration file missing ...")
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
        id.properties.setProperty("IceSSL.DefaultDir", MAIN_CONFIG_DIR + "/" + "server_certs")

        return(app.main(sys.argv, None, id))

if __name__=="__main__":
        sys.exit(main())

# vim: ts=4:sw=4:et:sts=4:ai:tw=80
