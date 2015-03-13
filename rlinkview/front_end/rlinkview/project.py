import sys

# Project name
__project__ = "rlinkView"

# Program version
__version__ = "0.0.1"

# Python sanity check: program tested for: 2.5.2
if sys.hexversion < 0x020400F0:
    print "Sorry, python 2.4 or later is required for this version of ameba installer"
    sys.exit(1)

# wxPython sanity check: program tested for this wxPython version.
VERSION_STRING  = '2.8.9.1'

# minimal system tools sanity check
minimal_tools = ("git", "svn", "wget") 

#
# info struct for AboutDialog box.
#
licenseText = """
USB stick BIOS updater License

Copyright (C) 2010 Javier Roman <javiroman@kernel-labs.org>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
aboutText = \
"A \"hello world\" program is a software program that prints out " + \
"\"Hello world!\" on a display device. It is used in many introductory" + \
"tutorials for teaching a programming language.  environment, " + \
"and run-time environment are correctly installed."

copyrightText = "(C) 2010 Spain"

website = ("http://www.example.com", "Rlink.py Viewer")

developers = ["Javier Roman"]

# vim: ts=4:sw=4:et:sts=4:ai:tw=80
