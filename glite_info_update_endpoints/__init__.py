#!/usr/bin/env python

"""
This component is used with Top BDII and is intented to update LDAP endpoits
for EGI.

glite-info-update-endpoints is a cron job that runs every hour to download
the list of site BDII URLs that are going to be used by the top level
BDII to publish their resources.

The script uses the /etc/glite/glite-info-update-endpoints.conf file which
by default is configured to use EGI's list of site BDIIs.
The list of site BDIIs is taken from the EGI GOCDBs.
"""

import argparse
import logging
import os
import pickle
import ssl
import sys
import time

import configparser
import urllib

from xml.etree import ElementTree

LOG = logging.getLogger()


def setup_logging():
    """creates and returns stderr logger"""
    logging.basicConfig(format="%(asctime)s %(levelname)-8s %(message)s",
                        level=logging.WARN)


def read_config(config_file):
    """Configuration file reader

    Reads the configuration from the given file
    and asserts the correctness and logical consistency
    of the content.
    """
    config = {}
    config_parser = configparser.ConfigParser()
    # First, check whether the configuration file is corrupt overall
    try:
        config_parser.read(config_file)
    except configparser.ParsingError as error:
        LOG.error("Configuration file '%s' contains errors.", config_file)
        LOG.error(str(error))
        sys.exit(1)
    # Then, check for mandatory parameters.
    # EGI and manual have to be set, else we can't continue
    try:
        for parameter in ['EGI', 'manual']:
            try:
                config[parameter] = config_parser.getboolean('configuration',
                                                             parameter)
            except ValueError:
                LOG.error("The value for parameter '%s' is not a boolean",
                          parameter)
                sys.exit(1)
        for parameter in ['output_file', 'cache_dir',
                          'certification_status']:
            config[parameter] = config_parser.get('configuration', parameter)
        for parameter in ['cafile', 'capath']:
            if config_parser.has_option('configuration', parameter):
                config[parameter] = config_parser.get('configuration',
                                                      parameter)
            else:
                config[parameter] = None
    except configparser.NoSectionError:
        LOG.error(("Missing section 'configuration' in"
                   " the configuration file %s."), config_file)
        sys.exit(1)
    except configparser.NoOptionError:
        LOG.error("Missing parameter '%s' in the configuration file %s.",
                  parameter, config_file)
        sys.exit(1)
    # If you do set manual = True , you're gonna need a manual_file
    if config['manual']:
        try:
            config['manual_file'] = config_parser.get('configuration',
                                                      'manual_file')
        except configparser.NoOptionError:
            LOG.error("You have specified manual configuration, but no "
                      "manual_file in the %s configuration file", config_file)
            sys.exit(1)
    return config


def get_url_data(url, capath, cafile):
    """Retrieve the content of a resource at a specific URL"""
    # python urllib2 introduced server certificate validation starting
    # with version 2.7.9 and 3.4 (backported also e.g. to CentOS7). It
    # is no longer possible to download HTTPS data without having server
    # CA certificate in trusted store or explicitely disable verification.
    if hasattr(ssl, 'create_default_context'):
        # pylint: disable=protected-access
        if capath is not None or cafile is not None:
            context = ssl.create_default_context(cafile=cafile, capath=capath)
        else:
            context = ssl._create_unverified_context()
        try:
            return urllib.request.urlopen(url, context=context).read()
        except urllib.error.URLError as error:
            LOG.warning("Error getting info: %s", str(error))
            return None
    else:
        try:
            # Older python versions doesn't really verify server certificate
            return urllib.request.urlopen(url).read()
        except IOError as error:
            LOG.warning("Error getting info: %s", str(error))
            return None


def get_egi_urls(status, capath, cafile):
    """Retrieve production sites from GOCDB"""
    if status not in ["Candidate", "Uncertified", "Certified",
                      "Closed", "Suspended"]:
        LOG.error("'%s' is not a valid certification_status.", status)
        sys.exit(1)

    egi_goc_url = ("https://goc.egi.eu/gocdbpi/public/"
                   "?method=get_site_list&certification_status=%s"
                   "&production_status=Production") % status
    response = get_url_data(egi_goc_url, capath, cafile)
    if not response:
        LOG.warning("unable to get GOCDB Production %s sites", status)
        return None
    root = ElementTree.XML(response)
    egi_urls = {}
    for node in root:
        if not node.attrib['ROC'] in egi_urls.keys():
            egi_urls[node.attrib['ROC']] = []
        egi_urls[node.attrib['ROC']].append((node.attrib['NAME'],
                                             node.attrib['GIIS_URL']))
    return egi_urls


def create_urls_file(output_file, egi_urls, manual, manual_file):
    """Create the Top Level BDII configuration file"""
    now = time.asctime()
    header = """#
# Top Level BDII configuration file
# ---------------------------------
# created on %s
#
# This file is generated, DO NOT EDIT it directly
#
""" % now

    LOG.debug("Writing urls file at %s", output_file)
    if not os.path.exists(os.path.dirname(output_file)):
        LOG.error("Output directory '%s' does not exist.", output_file)
        sys.exit(1)

    with open(output_file + ".tmp", "w") as temp:
        temp.write(header)
        if egi_urls:
            for region in egi_urls:
                temp.write("\n#\n# %s\n# -----------\n#\n" % region)
                for site in egi_urls[region]:
                    temp.write("\n#%s\n" % site[0])
                    temp.write("%s %s\n" % site)
        if manual:
            if os.path.exists(manual_file):
                with open(manual_file) as mfh:
                    temp.write("\n\n# Appended Manual Additions\n\n")
                    temp.write(mfh.read())
            else:
                LOG.error("Manual URL file %s does not exist!",
                          manual_file)
                sys.exit(1)
    os.rename(output_file + ".tmp", output_file)


def main():
    """main entry point"""
    setup_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=True,
                        help="Configuration file", )
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Run in verbose mode")
    args = parser.parse_args()
    if args.verbose:
        LOG.setLevel(logging.DEBUG)
    config = read_config(args.config)

    egi_urls = None
    if config.get('EGI'):
        egi_urls = get_egi_urls(config['certification_status'],
                                config.get('capath'),
                                config.get('cafile'))
        pickle_file = config['cache_dir'] + '/' + 'EGI.pkl'
        if egi_urls:
            LOG.debug("Dumping EGI URLs on cache file %s", pickle_file)
            with open(pickle_file, 'wb') as pfh:
                pickle.dump(egi_urls, pfh)
        else:
            LOG.warning(("EGI GOCDB could not be contacted or returned no"
                         " information about EGI sites."
                         " Using cache file for EGI URLs."))
            try:
                with open(pickle_file, 'rb') as pfh:
                    egi_urls = pickle.load(pfh)
            except IOError as error:
                LOG.warning("Issue opening cache file for EGI URLs: %s", error)

    create_urls_file(config['output_file'], egi_urls, config['manual'],
                     config.get('manual_file'))


if __name__ == "__main__":
    main()
