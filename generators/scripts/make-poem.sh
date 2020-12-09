#!/bin/bash

cd "$(dirname "$0")"
#have python env already set up
cd oisin
./oisincli.py --balladize true --template true -t 250 -of output/dracula-whatever input/dracula.txt
cd ..
./zonelet-page-gen.sh oisin/output/dracula-whatever dracula-whatever
