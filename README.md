# glite-info-update-endpoints

This component is used with Top BDII and is intended to update LDAP endpoints for
EGI. BDII documentation is available at
[gridinfo documentation site](https://gridinfo-documentation.readthedocs.io/).

`glite-info-update-endpoints` is a cron job that runs every hour to download the
list of site BDII URLs that are going to be used by the top level BDII to
publish their resources.

The script uses the `/etc/glite/glite-info-update-endpoints.conf` file which by
default is configured to use EGI's list of site BDIIs. The list of site BDIIs is
taken from the
[EGI Configuration Database (GOCDB)](https://docs.egi.eu/internal/configuration-database/).

## Installing from packages

### On RHEL-based systems

On RHEL-based systems, it's possible to install packages from
 [EGI UMD packages](https://go.egi.eu/umd). The packages are build from this repository,
and tested to work with other components part of the Unified Middleware Distribution.

## Building packages

A Makefile allowing to build source tarball and packages is provided.

### Building a RPM

The required build dependencies are:

- rpm-build
- make
- rsync
- python3
- python3-setuptools

```shell
# Checkout tag to be packaged
$ git clone https://github.com/EGI-Foundation/glite-info-update-endpoints.git
$ cd glite-info-update-endpoints
$ git checkout X.X.X
# Building in a container
$ docker run --rm -v $(pwd):/source -it quay.io/centos/centos:7
[root@8a9d60c61f42 /]# cd /source
[root@8a9d60c61f42 /]# yum install -y rpm-build yum-utils
[root@8a9d60c61f42 /]# yum-builddep -y glite-info-update-endpoints.spec
[root@8a9d60c61f42 /]# make rpm
```

The RPM will be available into the `build/RPMS` directory.

## Installing from source

This procedure is not recommended for production deployment, please consider
using packages.

Get the source by cloning this repository and do a `make install`.

## Preparing a release

- Prepare a changelog from the last version, including contributors' names
- Prepare a PR with
  - Updating version and changelog in
    - [CHANGELOG](CHANGELOG)
    - [glite-info-update-endpoints.spec](glite-info-update-endpoints.spec)
- Once the PR has been merged tag and release a new version in GitHub
  - Packages will be built using GitHub Actions and attached to the release page

## History

This work started under the EGEE project, and was hosted and maintained for a
long time by CERN. This is now hosted here on GitHub, maintained by the BDII
community with support of members of the EGI Federation.
