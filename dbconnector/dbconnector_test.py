#!/usr/bin/env python
"""

(C) 2008-2009 Javi Roman <javiroman@kernel-labs.org>

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
CONFIG_FILE = MAIN_CONFIG_DIR + "/" + "dbconnector_test.cfg"
VERSION="0.0.1"

Ice.loadSlice('-I' + slice_dir + '/slice ' + MAIN_CONFIG_DIR + "/" + "DBConnector.ice")
import DBConnector

class AppRlinkDBConnectorClient(Ice.Application):
    def __init__(self):
        print "<AppRlinkDBConnectorClient constructor>"

    def run(self, args):
        print "<Ice runtime running>"
        ic = self.communicator()

        properties = ic.getProperties()
        proxy = properties.getProperty('DBConnector.Proxy')

        if len(proxy) == 0:
            print " property `DBConnector.Proxy' not set"
            return False

        try:
            servant = \
                DBConnector.DBInsertionPrx.checkedCast(ic.stringToProxy(proxy))

        except Ice.NotRegisteredException:
            print "Execpcion no registrado!!!"
            traceback.print_exc()
            return -1

        servant.pingTest("Hello World DBConnector!")

        if ic:
            try:
                self.communicator().destroy()
            except:
                traceback.print_exc()
                status=1

        return 0

def main():
    print "-------------------------------------------------------"
    version = "DBConnector Tester version %s" % VERSION
    print version
    print "-------------------------------------------------------"

    app = AppRlinkDBConnectorClient()

    if not os.path.exists(CONFIG_FILE):
        print "main configuration file missing ..."
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

        return (app.main(sys.argv, None, id))

if __name__ == "__main__":
    sys.exit(main())

# vim: ts=4:sw=4:et:sts=4:ai:tw=80
