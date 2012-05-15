NAME=arronax
VERSION=0.01
DEBVERSION=${VERSION}
PPA=diesch/testing

DEBUILD=debuild -sa  -v${DEBVERSION} -kB57F5641 -i'icon|.bzr'

.PHONY: clean deb sdist ppa deb

initdeb:
	dh_make -e  devel@florian-diesch.de -p ${NAME}_${DEBVERSION} -c gpl -i --native

clean:
	rm -rf *.pyc build dist  ../${NAME}_${DEBVERSION}* ${NAME}-${VERSION}.egg-info


potfiles:
	find arronax -type f -name \*.py > po/POTFILES.in
	find data -type f -name \*.ui -printf '[type: gettext/glade]%p\n'  >> po/POTFILES.in

sdist:
	python setup.py sdist

egg:
	python setup.py bdist_egg


predeb: sdist
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
	dput ppa:${PPA} ../${NAME}_${DEBVERSION}_source.changes


install: deb
	sudo dpkg -i ../${NAME}_${DEBVERSION}_all.deb
