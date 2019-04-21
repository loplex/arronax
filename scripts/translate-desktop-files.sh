#!/bin/sh

# run this from the project root

echo Translating *.desktop files ...

NAME=arronax

for f in data/desktop/*.desktop.in; do
    intltool-merge po -d -u "$f" data/desktop/"$(basename "$f" .in)"
done

