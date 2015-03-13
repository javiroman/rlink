#!/usr/bin/env python
"""

(C) 2008-2009 Javi Roman <javiroman@kernel-labs.org>

$Id: rlink.py 162 2009-10-21 09:39:47Z jroman $
"""
import sys
import md5
import traceback
import Ice
import os 
import array
import fnmatch
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
    print sys.argv[0] + ': Slice directory not found. Define ICEPY_HOME or ICE_HOME.'
    sys.exit(1)

rlink_home = os.getenv('RLINK_HOME')
if not rlink_home:
    print "please you have to set up RLINK_HOME variable ..."
    os._exit(1)

home = os.getenv('CAP_HOME')
if not home:
    print "please you have to set up CAP_HOME variable ..."
    os._exit(1)

VERSION="0.0.3"
# CONFIG_DIR_NAME = "rlink_main_folder"
CONFIG_DIR_NAME = "rlink"
MAIN_CONFIG_DIR = home + "/" + CONFIG_DIR_NAME
LOCAL_CONFIG_DIR = "rlink"
CONFIG_FILE = MAIN_CONFIG_DIR + "/" + "rlink_client.cfg"
MAKEALLLOG = "MakeAll.log"

Ice.loadSlice('-I' + slice_dir + '/slice ' + MAIN_CONFIG_DIR + "/" + "Rlink.ice")
import Rlink

class SimpleLogger:
    def __init__(self, logroot):
        # possible log rotation here
        # sys.stdout = sys.__stdout__ 
        sys.stderr = open(logroot + "/" + "rlink_client.log" , 'a')
        self.logroot = logroot

    def __call__(self, filelog, string):
        file = open(self.logroot + "/" + filelog, 'a')
        file.write('[' + time.asctime() + '] ')
        file.write(string + '\n')
        file.close()

class Cache:
    def __init__(self, pattern, dir):
        log("rlink_client.log" , "<Cache constructor>")
        self._cache = {}
        self._cachefile = os.path.exists("rlink/.cache")
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
            log("rlink_client.log" , "<no existe cache, creando ...>")
            for i in self._el:
                self._cache[i] = self._md5sum(i)

            f = open('rlink/.cache', 'wb')
            pickle.dump(self._cache, f) 
            f.close()
            self._ml = self._el
        else:
            print "cargando cache"
            f = open('rlink/.cache', 'rb')
            self._cache = pickle.load(f) 
            f.close()
            self._ml = self._purgeList()

        if not self._ml:
            log("rlink_client.log" , "<no objetos modificados>")
        else:
            f = open('rlink/.cache', 'wb')
            pickle.dump(self._cache, f) 
            f.close()

	log_msg = "<Objetos modificados: %d>" % len(self._ml)

        return self._ml

class CallbackFunctionsI(Rlink.CallbackFunctions):
    def backOutputs(self, remote_home, s, file, current=None):
        s = s.replace(remote_home, home)

        try:
            binvalues = array.array('B')
            binvalues.fromlist(file)
	    if s.find(".err") != -1:
	        f = open(s, 'ab')
	    else:
                f = open(s, 'wb')

            binvalues.tofile(f)
            f.close()

            size = os.path.getsize(s)

            log_msg = "received file: " + s + " (size %d)" % size 
            if s.find(".err") > 0 and size > 0:
                log_msg = log_msg + " WARNING"

	    print log_msg
            log("rlink_client.log", log_msg)
        except:
	    log_msg = "No se pudo escribir el fichero %s" % s
            log("rlink_client.log", log_msg)

class MakefileRlink:

    def __init__(self, filename):
        log("rlink_client.log" , "<MakefileRlink constructor>")
        self._filename =  os.getcwd() + "/" + LOCAL_CONFIG_DIR + "/" + filename
        log("rlink_client.log" , "<Processing: " + self._filename + " >")

    def getMakefileName(self):
        return self._filename

    def getObjectsList(self):
        """
	It uses cache file to get only modified files
        """
	c = Cache("*.[o,a]", ".")
	el = c.getModfied()

	return el

class LinkingSession:
    """
    A linking session is the invocation of rlink.py from the
    local Makefile. This session is in the scope of rlink local
    directory.
    """
    def __init__(self, servant, properties, argv):
        log("rlink_client.log" , "<TransferStep constructor>")
        self._servant = servant
        self._properties = properties
        self._doclean = None
	self._target = None
        if len(argv) > 1:
	    self._target = argv[1]
            if argv[1] == "clean":
                self._doclean = 1

    def run(self):
        log("rlink_client.log" , "<LinkingSession.sendObjects()>")
        ret = self.sendObjects()
        if ret == 0:
            return 0

        log("rlink_client.log" , "<LinkingSession.makeLinking()>")
        link_output = self.makeLinking(self._target)
	print link_output
        self._appendMakefileLog(link_output)

	if link_output.find("Error") > 0:
		return -1

        log("rlink_client.log" , "<LinkingSession.getOutputs()>")
        self.getOutputs()
	return 0

    def _appendMakefileLog(self, log):
    	makefile_log = home + "/" + MAKEALLLOG
    	f = open(makefile_log, 'a')	
        f.write("##### START remote linking log ... #####\n")
        f.write(log)
        f.write("##### ... END remote linking log #####\n")
        f.close()
    
    def sendObjects(self):
        #
        # send real base path name, avoid the symlink issue.
        #
        self._servant.pingTest(os.path.realpath(home))

        file_path = self._properties.getProperty('Rlink.Makefile')
        makefile = MakefileRlink(file_path)

        # send remote Makefile
        self.sendFile(makefile.getMakefileName())

        if self._doclean:
            log("rlink_client.log", "<remote clean command launched>")
            relative_path = os.getcwd()
            self._servant.makeLinking(relative_path.replace(os.path.realpath(home) + "/" , ""), "clean")
            return 0

        # send compiler objects changed files
        ol = makefile.getObjectsList()
        for i in ol:
            self.sendFile(i)

        self._servant.pingTest("Transfer completed")

    def makeLinking(self, target):
        """
        CAP_HOME: make -C "remote_abs_path"/server/daemons/Makefile
        """
        relative_path = os.getcwd()
        return self._servant.makeLinking(relative_path.replace(os.path.realpath(home) + "/" , ""), target)

    def getOutputs(self):
        relative_path = os.getcwd()
        self._servant.getOutputs(relative_path.replace(os.path.realpath(home) + "/" , ""))

    def sendFile(self, file_path):
        """Check if the cheksum is changed and compress the file."""
        if not os.path.exists(file_path):
            print "No se pudo leer el fichero %s" % file_path
            return False

        try:
            size = os.path.getsize(file_path)

            f = file(file_path, mode='rb') 
            binvalues = array.array('B')
            binvalues.fromfile(f, size)
            f.close()
        except:
            print "No se pudo leer el fichero %s" % file_path

        self._servant.sendFile(file_path, binvalues.tolist())

class AppRlinkClient(Ice.Application):
    def __init__(self, home):
        log("rlink_client.log" , "<AppRlinkClient constructor>")
        _home = home

    def run(self, args):
        log("rlink_client.log" , "<Ice runtime running>")
        ic = self.communicator()

        properties = ic.getProperties()
        proxy = properties.getProperty('Rlink.Proxy')

        if len(proxy) == 0:
            log("rlink_client.log" , " property `Rlink.Proxy' not set")
            return False

        try:
            servant = \
                Rlink.FileTransferPrx.checkedCast(ic.stringToProxy(proxy))

        except Ice.NotRegisteredException:
            print "Execpcion no registrado!!!"
            traceback.print_exc()
            return -1

        #servant.pingTest("Hello World!")

        adapter = self.communicator().createObjectAdapter("Callback.Client")
        ident = Ice.Identity()
        ident.name = Ice.generateUUID()
        ident.category = ""
        adapter.add(CallbackFunctionsI(), ident)
        adapter.activate()
        servant.ice_getConnection().setAdapter(adapter)
        servant.addClient(ident)

        ts = LinkingSession(servant, properties, sys.argv)

        ret = ts.run()
	if ret == -1:
        	log("rlink_client.log" , "<Linking ERROR!!>")
		return -1

        if ic:
            try:
                self.communicator().destroy()
            except:
                traceback.print_exc()
                status=1

        return 0

def main():
    global log
    log = SimpleLogger(MAIN_CONFIG_DIR + "/logs")

    log("rlink_client.log", "-------------------------------------------------------")
    version = "Rlink Client version %s" % VERSION
    log("rlink_client.log", version)
    log("rlink_client.log", "-------------------------------------------------------")

    app = AppRlinkClient(home)

    if not os.path.exists(CONFIG_FILE):
        log("rlink_client.log", "main configuration file missing ...")
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
        id.properties.setProperty("IceSSL.DefaultDir", MAIN_CONFIG_DIR + "/" + "client_certs")

        return(app.main(sys.argv, None, id))

if __name__ == "__main__":
        sys.exit(main())

# vim: ts=4:sw=4:et:sts=4:ai:tw=80
