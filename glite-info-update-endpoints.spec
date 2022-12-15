Name:          glite-info-update-endpoints
Version:       4.0.0
Release:       1%{?dist}
Summary:       Updates LDAP endpoints for EGI
Group:         Development/Libraries
License:       ASL 2.0
URL:           https://github.com/EGI-Foundation/glite-info-update-endpoints
Source:        %{name}-%{version}.tar.gz
BuildArch:     noarch
BuildRoot:     %{_tmppath}/%{name}-%{version}-build
BuildRequires: rsync
BuildRequires: make
BuildRequires: python3
BuildRequires: python3-setuptools
BuildRequires: python3-rpm-macros
Requires:      crontabs
Requires:      python3

%description
Updates LDAP endpoints for EGI

%prep
%setup -q

%build

%install
rm -rf %{buildroot}
make install python=python3 prefix=%{buildroot}

%post
if [ ! -f /var/cache/glite/top-urls.conf ]; then
   /usr/bin/glite-info-update-endpoints -c /etc/glite/glite-info-update-endpoints.conf > /var/log/glite/glite-info-update-endpoints.log 2>&1
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%dir %{_sysconfdir}/glite
%dir /var/log/glite
%dir /var/cache/glite
%dir %{_docdir}/%{name}
%config(noreplace) %{_sysconfdir}/glite/glite-info-update-endpoints.conf
%{_bindir}/%{name}
%{_sysconfdir}/cron.hourly/%{name}
/var/cache/glite/%{name}
%{python3_sitelib}/glite_info_update_endpoints/
%{python3_sitelib}/glite_info_update_endpoints-*.egg-info/
%doc %{_docdir}/%{name}/README.md
%doc %{_docdir}/%{name}/AUTHORS.md
%doc %{_docdir}/%{name}/COPYRIGHT
%doc %{_docdir}/%{name}/LICENSE.txt

%changelog
* Thu Dec 15 2022 Baptiste Grenier <baptiste.grenier@egi.eu> - 4.0.0-1
- Quality control using GitHub actions, update community files (#33) (Baptiste Grenier)
- Migrate to Python 3 (#28) (Enol Fernandez)

* Wed Sep 23 2020 Baptiste Grenier <baptiste.grenier@egi.eu> - 3.0.2-1
- Fix manual_file configuration (Baptiste Grenier)
- Enforce pylint and address issues (Baptiste Grenier, Enol Fernández, Andrea Manzi)

* Tue Nov 27 2018 Baptiste Grenier <baptiste.grenier@egi.eu> - 3.0.1-1
- Make manual_file optional in the conf (Bruce Becker)

* Wed Sep 26 2018 Baptiste Grenier <baptiste.grenier@egi.eu> - 3.0.0-1
- Totally drop OSG support (Baptiste Grenier)
- Test and build using Travis, fix sytle (Baptiste Grenier)

* Mon Aug 27 2018 Baptiste Grenier <baptiste.grenier@egi.eu> - 2.0.14-1
- Updated OSG URL (vokac)
- Bug GitHub #1: Silent fail on CentOS 7 when not able to validate GOCDB certificate (vokac)
- Update build, documetation and link to new GitHub repository (Baptiste Grenier)

* Thu Aug 01 2013 Maria Alandes <maria.alandes.pradillo@cern.ch> - 2.0.13-1
- Updated URL
- BUG #99322: Error when manual file does not exist

* Wed Apr 24 2013 Maria Alandes <maria.alandes.pradillo@cern.ch> - 2.0.12-2
- Added Source URL information

* Wed Nov 21 2012 Maria Alandes <maria.alandes.pradillo@cern.ch> - 2.0.12-1
- BUG #98983: Improve error handling in glite-info-update-endpoints

* Tue Sep 11 2012 Maria Alandes <maria.alandes.pradillo@cern.ch> - 2.0.11-1
- BUG #96484: Fixed post install actions
- BUG #97395: Fixed rpmlint errors

* Fri May 25 2012 Laurence Field <laurence.field@cern.ch> - 2.0.10-1
- Changed the location of top-urls.conf to address GGUS #73823

* Thu Apr 19 2012 Laurence Field <laurence.field@cern.ch> - 2.0.9-1
- Added random sleep to cronjob to address GGUS #81404

* Mon Mar 28 2011 Laurence Field <laurence.field@cern.ch> - 2.0.8-1
- Addressed IS-228

* Fri Aug 20 2010 Laurence Field <laurence.field@cern.ch> - 2.0.3-1
- Refactored version that queries the GOCs directly
