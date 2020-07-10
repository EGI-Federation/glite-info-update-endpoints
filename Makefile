NAME= $(shell grep Name: *.spec | sed 's/^[^:]*:[^a-zA-Z]*//' )
VERSION= $(shell grep Version: *.spec | sed 's/^[^:]*:[^0-9]*//' )
RELEASE= $(shell grep Release: *.spec |cut -d"%" -f1 |sed 's/^[^:]*:[^0-9]*//')
build=$(shell pwd)/build
DATE=$(shell date "+%a, %d %b %Y %T %z")
dist=$(shell rpm --eval '%dist' | sed 's/%dist/.el5/')
python ?= python

default:
	@echo "Nothing to do"

install:
	@echo installing ...
	@mkdir -p ${prefix}/etc/glite
	@mkdir -p ${prefix}/etc/cron.hourly
	@mkdir -p ${prefix}/usr/bin/
	@mkdir -p ${prefix}/var/log/glite
	@mkdir -p ${prefix}/var/cache/glite/glite-info-update-endpoints
	@mkdir -p $(prefix)/usr/share/doc/glite-info-update-endpoints
	${python} setup.py install --root ${prefix}/
	@install -m 0644 etc/glite-info-update-endpoints.conf ${prefix}/etc/glite/
	@install -m 0755 etc/cron.hourly/glite-info-update-endpoints ${prefix}/etc/cron.hourly/
	@install -m 0644 README.md $(prefix)/usr/share/doc/glite-info-update-endpoints/
	@install -m 0644 AUTHORS $(prefix)/usr/share/doc/glite-info-update-endpoints/
	@install -m 0644 COPYRIGHT $(prefix)/usr/share/doc/glite-info-update-endpoints/
	@install -m 0644 LICENSE.txt $(prefix)/usr/share/doc/glite-info-update-endpoints/
	# @install -m 0755 bin/glite-info-update-endpoints ${prefix}/usr/bin/
dist:
	@mkdir -p  $(build)/$(NAME)-$(VERSION)/
	rsync -aHS --exclude ".git" --exclude "$(build)" * $(build)/$(NAME)-$(VERSION)/
	cd $(build); tar --gzip -cf $(NAME)-$(VERSION).src.tgz $(NAME)-$(VERSION)/; cd -

sources: dist
	cp $(build)/$(NAME)-$(VERSION).src.tgz .

prepare: dist
	@mkdir -p  $(build)/RPMS/noarch
	@mkdir -p  $(build)/SRPMS/
	@mkdir -p  $(build)/SPECS/
	@mkdir -p  $(build)/SOURCES/
	@mkdir -p  $(build)/BUILD/
	cp $(build)/$(NAME)-$(VERSION).src.tgz $(build)/SOURCES
	cp $(NAME).spec $(build)/SPECS

srpm: prepare
	@rpmbuild -bs --define="dist ${dist}" --define='_topdir ${build}' $(build)/SPECS/$(NAME).spec

rpm: srpm
	@rpmbuild --rebuild  --define='_topdir ${build}' $(build)/SRPMS/$(NAME)-$(VERSION)-$(RELEASE)${dist}.src.rpm

clean:
	rm -f *~ $(NAME)-$(VERSION).src.tgz
	rm -rf $(build)
	rm -rf glite_info_update_endpoints.egg-info

.PHONY: dist srpm rpm sources clean
