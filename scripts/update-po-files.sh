#!/bin/sh

# run this from the project root

echo Updating *.po files ...

NAME=arronax


## Update *.po files
cd po
intltool-update -p -g "$NAME"

