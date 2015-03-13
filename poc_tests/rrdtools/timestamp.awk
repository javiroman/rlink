#!/bin/gawk -f   
{ print strftime("%c", $0); }
