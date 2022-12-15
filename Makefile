NAME=$(shell grep Name: *.spec | sed 's/^[^:]*:[^a-zA-Z]*//')
VERSION=$(shell grep Version: *.spec | sed 's/^[^:]*:[^0-9]*//')
RELEASE=$(shell grep Release: *.spec | cut -d"%" -f1 | sed 's/^[^:]*:[^0-9]*//')
build=$(shell pwd)/build
DATE=$(shell date "+%a, %d %b %Y %T %z")
dist=$(shell rpm --eval '%dist' | sed 's/%dist/.el5/')
python ?= python3

default:
	@echo "Nothing to do"

install:
	@echo installing ...
	@mkdir -p $(prefix)/etc/glite
	@mkdir -p $(prefix)/etc/cron.hourly
	@mkdir -p $(prefix)/usr/bin/
	@mkdir -p $(prefix)/var/log/glite
	@mkdir -p $(prefix)/var/cache/glite/$(NAME)
	@mkdir -p $(prefix)/usr/share/doc/$(NAME)
	@mkdir -p $(prefix)/usr/share/licenses/$(NAME)
	$(python) setup.py install --root $(prefix)/
	@install -m 0644 etc/$(NAME).conf $(prefix)/etc/glite/
	@install -m 0755 etc/cron.hourly/$(NAME) $(prefix)/etc/cron.hourly/
	@install -m 0644 README.md $(prefix)/usr/share/doc/$(NAME)/
	@install -m 0644 AUTHORS.md $(prefix)/usr/share/doc/$(NAME)/
	@install -m 0644 COPYRIGHT $(prefix)/usr/share/licenses/$(NAME)/
	@install -m 0644 LICENSE.txt $(prefix)/usr/share/licenses/$(NAME)/

dist:
	@mkdir -p  $(build)/$(NAME)-$(VERSION)/
	rsync -HaS --exclude ".git" --exclude "$(build)" * $(build)/$(NAME)-$(VERSION)/
	cd $(build); tar --gzip -cf $(NAME)-$(VERSION).tar.gz $(NAME)-$(VERSION)/; cd -

sources: dist
	cp $(build)/$(NAME)-$(VERSION).tar.gz .

prepare: dist
	@mkdir -p $(build)/RPMS/noarch
	@mkdir -p $(build)/SRPMS/
	@mkdir -p $(build)/SPECS/
	@mkdir -p $(build)/SOURCES/
	@mkdir -p $(build)/BUILD/
	cp $(build)/$(NAME)-$(VERSION).tar.gz $(build)/SOURCES
	cp $(NAME).spec $(build)/SPECS

srpm: prepare
	rpmbuild -bs --define="dist ${dist}" --define='_topdir ${build}' $(build)/SPECS/$(NAME).spec

rpm: srpm
	rpmbuild --rebuild  --define='_topdir ${build}' --define="dist ${dist}" $(build)/SRPMS/$(NAME)-$(VERSION)-$(RELEASE)$(dist).src.rpm

clean:
	rm -f *~ $(NAME)-$(VERSION).tar.gz
	rm -rf $(build)
	rm -rf glite_info_update_endpoints.egg-info
	rm -rf dist

.PHONY: dist srpm rpm sources clean
