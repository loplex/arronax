SHELL=/bin/bash

NAME=arronax
DEBVERSION=$(shell awk -F '[()]' '/^${NAME}/ {print $$2}'  debian/changelog|head -1)
VERSION=$(shell echo '${DEBVERSION}' | egrep -o '[0-9.-]{3,}')

DEBUILD=debuild -sa -v${DEBVERSION} -us -uc -i'icon|.bzr'

.PHONY: clean deb sdist deb

initdeb:
	dh_make -e lop_in_github@dataplex.cz -p ${NAME}_${DEBVERSION} -c gpl -i --native

clean:
	dpkg-buildpackage -T clean
	rm -rf locale/
	rm -f ../${NAME}{,-nautilus,-caja,-thunar,-nemo}_${DEBVERSION}_all.deb
	rm -f ../${NAME}_${DEBVERSION}{_amd64.buildinfo,.dsc,_source.buildinfo,_source.changes,_amd64.changes,.tar.xz}


potfiles:
	find ${NAME} -type f -name \*.py > po/POTFILES.in
	find nautilus -type f -name \*.py >> po/POTFILES.in
	find data -type f -name \*.desktop.in >> po/POTFILES.in
	find data -type f -name \*.ui -printf '[type: gettext/glade]%p\n'  >> po/POTFILES.in

sdist:
	python setup.py sdist

egg:
	python setup.py bdist_egg


predeb: sdist
	echo "|${DEBVERSION}|${VERSION}"
	cp dist/${NAME}-${VERSION}.tar.gz ../${NAME}_${VERSION}.orig.tar.gz
	rm -r dist
	python setup.py build_i18n

sdeb: predeb
	${DEBUILD} -S

deb:
	${DEBUILD} -b

install: deb
	sudo dpkg -i ../${NAME}*_${DEBVERSION}_all.deb

unpackpo:
	tar xzvf launchpad-export.tar.gz && \
	cd po && \
	mmv '${NAME}-*.po' '#1.po' && \
	cd .. && \
	rm launchpad-export.tar.gz

