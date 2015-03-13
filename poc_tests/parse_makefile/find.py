#!/usr/bin/env python

import os
import fnmatch
import sys

def find(pattern, root=os.curdir):
    ol = [] 
    pwd = os.getcwd()

    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
	    ol.append(path.replace(pwd, ".")  + "/" + filename)

    return ol

def main():
    list = find("*.[o,a]", ".")

    print len(list)
    print list

if __name__ == "__main__":
        sys.exit(main())



