#!/bin/bash

echo "Ficheros de error > 0:"
echo "~~~~~~~~~~~~~~~~~~~~~"

for i in $(find . -name "*.err");do
        wc -c $i | grep -v ^0
done
