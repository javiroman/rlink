#!/usr/bin/python
# animal.py - create animal table and
# retrieve information from it

import sys
import MySQLdb

# connect to the MySQL server
try:
    conn = MySQLdb.connect (host = "localhost",
                            user = "root",
                            passwd = "adm",
                            db = "test")
except MySQLdb.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit (1)

# create the animal table and populate it
try:
    cursor = conn.cursor ()
    cursor.execute ("DROP TABLE IF EXISTS animal")
    cursor.execute ("""
         CREATE TABLE animal
         (
           name     CHAR(40),
           category CHAR(40)
         )
       """)
    cursor.execute ("""
         INSERT INTO animal (name, category)
         VALUES
           ('snake', 'reptile'),
           ('frog', 'amphibian'),
           ('tuna', 'fish'),
           ('racoon', 'mammal')
       """)
    print "Number of rows inserted: %d" % cursor.rowcount

    # perform a fetch loop using fetchone(): get the rows one at a time.
    cursor.execute ("SELECT name, category FROM animal")
    while (1):
        row = cursor.fetchone()
        if row == None:
            break
        print "%s, %s" % (row[0], row[1])
    print "Number of rows returned: %d" % cursor.rowcount

    # perform a fetch loop using fetchall(): get them all at once.
    cursor.execute ("SELECT name, category FROM animal")
    rows = cursor.fetchall()
    for row in rows:
        print "%s, %s" % (row[0], row[1])

    print "Number of rows returned: %d" % cursor.rowcount

   # issue a statement that changes the name by including data values
   # literally in the statement string, then change the name back
   # by using placeholders
    cursor.execute ("""
           UPDATE animal SET name = 'turtle'
           WHERE name = 'snake'
         """)
    print "Number of rows updated: %d" % cursor.rowcount

    cursor.execute ("""
           UPDATE animal SET name = %s
           WHERE name = %s
         """, ("snake", "turtle"))
    print "Number of rows updated: %d" % cursor.rowcount

    # create a dictionary cursor so that column values
    # can be accessed by name rather than by position
    cursor.close()
    cursor = conn.cursor (MySQLdb.cursors.DictCursor)
    cursor.execute ("SELECT name, category FROM animal")
    result_set = cursor.fetchall ()
    for row in result_set:
        print "%s, %s" % (row["name"], row["category"])

    print "Number of rows returned: %d" % cursor.rowcount
    cursor.close ()

except MySQLdb.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit (1)

conn.commit ()
conn.close ()

# vim: ts=4:sw=4:et:sts=4:ai:tw=80
