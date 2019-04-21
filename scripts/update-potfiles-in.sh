#!/bin/sh

# run this from the project root

echo Updating POTFILES.in

NAME=arronax


## Update POTFILES.in
mkdir -p po
find "$NAME" -type f -name \*.py > po/POTFILES.in
find data -type f -name \*.desktop.in >> po/POTFILES.in
find data -type f -name \*.ui -printf '[type: gettext/glade]%p\n' >> po/POTFILES.in


