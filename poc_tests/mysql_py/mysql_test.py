#!/usr/bin/python
import MySQLdb

try:
    db = MySQLdb.connect(host = "localhost",
                        user = "root", 
                        passwd="adm", 
                        db="rlink-wif")

except MySQLdb.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit (1)

c = db.cursor()

c.execute("select version()")

row = c.fetchone()

print row[0]
print row

c.close()
db.close()

# vim: ts=4:sw=4:et:sts=4:ai:tw=80

