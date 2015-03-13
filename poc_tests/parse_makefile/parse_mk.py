#!/usr/bin/env python

import sys

filename = "makefile.rlink"

def main():

    try:
        fin = open(filename, "r")
        str3 = fin.readlines()
        fin.close()
        print "Contents of file %s:" % filename
        print str3

    except IOError:
        print "File %s does not exist!" % filename


if __name__ == "__main__":
        sys.exit(main())

