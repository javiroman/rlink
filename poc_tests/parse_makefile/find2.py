#!/usr/bin/env python

import os
import fnmatch
import sys

def find(pattern, root=os.curdir):
    '''Locate all files matching supplied filename pattern in and below
       supplied root directory.'''
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)

def main():
    list = find("*.[o,a]", ".")
    for i in list:
        print i

if __name__ == "__main__":
        sys.exit(main())



