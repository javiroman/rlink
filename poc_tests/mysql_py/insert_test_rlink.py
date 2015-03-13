#!/usr/bin/python

import sys
import MySQLdb

# connect to the MySQL server
try:
    conn = MySQLdb.connect (host = "localhost",
                            user = "root",
                            passwd = "adm",
                            db = "rlink-wif")
except MySQLdb.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit (1)

try:
    cursor = conn.cursor ()
    print "TRUNCATE TABLE rlink_usuario"
    cursor.execute ("TRUNCATE TABLE rlink_usuario")
    cursor.execute ("""
         INSERT INTO rlink_usuario VALUES
           ('rlink10000', '20091015', 'usuario principal Capgemini', '1'),
           ('rlink10001', '20091015', 'usuario secundario 1', '0'),
           ('rlink10002', '20091015', 'usuario secundario 2', '0'),
           ('rlink10003', '20091015', 'usuario secundario 3', '0'),
           ('rlink10004', '20091015', 'usuario secundario 4', '0'),
           ('rlink10005', '20091015', 'usuario secundario 5', '0'),
           ('rlink10006', '20091015', 'usuario secundario 6', '0'),
           ('rlink10007', '20091015', 'usuario secundario 7', '0'),
           ('rlink10008', '20091015', 'usuario secundario 8', '0'),
           ('rlink10009', '20091015', 'usuario secundario 9', '0'),
           ('rlink33333', '20091015', 'usuario pruebas - no usar', '1')
       """)

    conn.commit ()

    print "Number of rows inserted: %d" % cursor.rowcount

    # perform a fetch loop using fetchall(): get them all at once.
    cursor.execute ("SELECT * FROM rlink_usuario")
    rows = cursor.fetchall()
    for row in rows:
        print "%s, %s %s %s" % (row[0], row[1], row[2], row[3])

    print "Number of rows returned: %d" % cursor.rowcount

    print "TRUNCATE TABLE rlink_aplicacion"
    cursor.execute ("TRUNCATE TABLE rlink_aplicacion")
    cursor.execute ("""
         INSERT INTO rlink_aplicacion VALUES
           ('pos', 100, 'programa sc_beet'),
           ('server/daemons', 100, 'Demonios'),
           ('server/invenper/obj', 100, 'Inverper'),
           ('server/miscelanea/obj', 100, 'Miscelanea'),
           ('server/QUICK_WINS/obj', 100, 'Quick wins'),
           ('server/reparto/obj', 100, 'Reparto'),
           ('server/seguridad/obj', 100, 'Seguridad'),
           ('server/spromo/obj', 100, 'Promo'),
           ('server/tesoreria/obj', 100, 'Tesoreria')
       """)

    conn.commit ()

    print "Number of rows inserted: %d" % cursor.rowcount

    # perform a fetch loop using fetchall(): get them all at once.
    cursor.execute ("SELECT * FROM rlink_aplicacion")
    rows = cursor.fetchall()
    for row in rows:
        print "%s, %s %s" % (row[0], row[1], row[2])

    print "Number of rows returned: %d" % cursor.rowcount
    cursor.close()

except MySQLdb.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit (1)

# No se hace nada hasta este commit
conn.close ()

# vim: ts=4:sw=4:et:sts=4:ai:tw=80

