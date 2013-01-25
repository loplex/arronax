NAME=arronax
DEBVERSION=$(shell awk -F '[()]' '/^${NAME}/ {print $$2}'  debian/changelog|head -1)
VERSION=$(shell echo '${DEBVERSION}' | egrep -o '[0-9.-]{3,}')

WEBDIR=/home/diesch/florian-diesch.de/sphinx/neu/source/software/${NAME}/dist

PPA=diesch/testing

DEBUILD=debuild -sa  -v${DEBVERSION} -kB57F5641 -i'icon|.bzr'

.PHONY: clean deb sdist ppa deb

initdeb:
	dh_make -e  devel@florian-diesch.de -p ${NAME}_${DEBVERSION} -c gpl -i --native

clean:
	rm -rf *.pyc build dist  ../*.deb ../*.changes ../*.build ${NAME}-${VERSION}.egg-info


potfiles:
	find ${NAME} -type f -name \*.py > po/POTFILES.in
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

pypi:
	python setup.py register

ppa: sdeb
	dput ppa:${PPA} ../${NAME}*_${DEBVERSION}_source.changes


install: deb
	sudo dpkg -i ../${NAME}*_${DEBVERSION}_all.deb

share: deb
	cp ../${NAME}*_${DEBVERSION}_all.deb ~/Shared/

web: deb sdist
	mkdir -p ${WEBDIR}
	cp ../${NAME}*_${DEBVERSION}_all.deb dist/${NAME}-${VERSION}.tar.gz ${WEBDIR}
