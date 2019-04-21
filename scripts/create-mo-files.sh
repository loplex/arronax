#!/bin/sh
#
# run this from the project root
#

echo Creating *.mo files ...

NAME=arronax

cd po

for f in *.po; do
    if [ "$f" != '*.po' ]; then
        lang="$(basename "$f" .po)"
        dir="../data/mo/$lang"
        mkdir -p "$dir"
        intltool-update -g "$NAME" "$lang"
        msgfmt "$f" --output "$dir/$NAME.mo"
    fi
done




