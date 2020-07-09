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

# global-*: global usage should be fixed by using a class
# invalid-name: module name is not appropriate
# pylint: disable=global-statement, global-at-module-level, invalid-name

import ConfigParser
import getopt
import logging
import os
import pickle
import ssl
import sys
import time
import urllib2

try:
    from xml.etree import ElementTree
except ImportError:
    from elementtree import ElementTree

LOG = None
CONFIG = None


def setup_logging():
    """creates and returns stderr logger"""
    global LOG

    LOG = logging.getLogger()
    hdlr = logging.StreamHandler()
    form = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    hdlr.setFormatter(form)
    LOG.addHandler(hdlr)
    LOG.setLevel(logging.WARN)


def parse_args():
    """Parses the command line arguments"""
    global LOG

    try:
        opts, dummy = getopt.getopt(sys.argv[1:], "c:hv",
                                    ["config", "help", "verbose"])
    except getopt.GetoptError as error:
        LOG.error("While parsing arguments: %s.", str(error).strip())
        usage()
        sys.exit(1)
    for opt, arg in opts:
        if opt == "-c" or opt == "--config":
            read_config(arg)
        elif opt == "-h" or opt == "--help":
            usage()
            sys.exit()
        elif opt == "-v" or opt == "--verbose":
            LOG.setLevel(logging.DEBUG)


def read_config(config_file):
    """Configuration file reader

    Reads the configuration from the given file
    and asserts the correctness and logical consistency
    of the content.
    """
    global CONFIG

    CONFIG = {}
    config_parser = ConfigParser.ConfigParser()
    # First, check whether the configuration file is corrupt overall
    try:
        config_parser.read(config_file)
    except ConfigParser.ParsingError as error:
        LOG.error("Configuration file '%s' contains errors.", config_file)
        LOG.error(str(error))
        sys.exit(1)
    # Then, check for mandatory parameters.
    # EGI and manual have to be set, else we can't continue
    try:
        for parameter in ['EGI', 'manual']:
            try:
                CONFIG[parameter] = config_parser.getboolean('configuration',
                                                             parameter)
            except ValueError:
                LOG.error("The value for parameter '%s' is not a boolean",
                          parameter)
                sys.exit(1)
        for parameter in ['output_file', 'cache_dir',
                          'certification_status']:
            CONFIG[parameter] = config_parser.get('configuration', parameter)
        for parameter in ['cafile', 'capath']:
            if config_parser.has_option('configuration', parameter):
                CONFIG[parameter] = config_parser.get('configuration',
                                                      parameter)
            else:
                CONFIG[parameter] = None
    except ConfigParser.NoSectionError:
        LOG.error(("Missing section 'configuration' in"
                   " the configuration file %s."), config_file)
        sys.exit(1)
    except ConfigParser.NoOptionError:
        LOG.error("Missing parameter '%s' in the configuration file %s.",
                  parameter, config_file)
        sys.exit(1)
    # If you do set manual = True , you're gonna need a manual_file
    if CONFIG['manual']:
        try:
            CONFIG['manual_file'] = config_parser.get('configuration',
                                                      'manual_file')
        except ConfigParser.NoOptionError:
            LOG.error("You have specified manual configuration, but no "
                      "manual_file in the %s configuration file", config_file)
            sys.exit(1)


def usage():
    """prints the command line options of the program"""
    print("""
            Usage:""", os.path.basename(sys.argv[0]), """[options]

            Options:
              -c --config  Configuration File
              -h --help    Display this help
              -v --verbose Run in verbose mode

            """)


def get_url_data(url):
    """Retrieve the content of a resource at a specific URL"""
    # python urllib2 introduced server certificate validation starting
    # with version 2.7.9 and 3.4 (backported also e.g. to CentOS7). It
    # is no longer possible to download HTTPS data without having server
    # CA certificate in trusted store or explicitely disable verification.
    if hasattr(ssl, 'create_default_context'):
        capath = CONFIG.get('capath')
        cafile = CONFIG.get('cafile')
        # pylint: disable=protected-access
        if capath is not None or cafile is not None:
            context = ssl.create_default_context(cafile=cafile, capath=capath)
        else:
            context = ssl._create_unverified_context()
        return urllib2.urlopen(url, context=context).read()
    else:
        # older python versions doesn't really verify server certificate
        return urllib2.urlopen(url).read()


def get_egi_urls(status):
    """Retrieve production sites from GOCDB"""
    egi_goc_url = ("https://goc.egi.eu/gocdbpi/public/"
                   "?method=get_site_list&certification_status=%s"
                   "&production_status=Production") % status

    try:
        response = get_url_data(egi_goc_url)
    # pylint: disable=broad-except
    except Exception as error:
        LOG.error("unable to get GOCDB Production %s sites: %s", status,
                  str(error))
        return ""

    root = ElementTree.XML(response)
    egi_urls = {}
    for node in root:
        if not node.attrib['ROC'] in egi_urls.keys():
            egi_urls[node.attrib['ROC']] = []
        egi_urls[node.attrib['ROC']].append((node.attrib['NAME'],
                                             node.attrib['GIIS_URL']))

    return egi_urls


def create_urls_file(egi_urls):
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

    if not os.path.exists(os.path.dirname(CONFIG['output_file'])):
        LOG.error("Output directory '%s' does not exist.",
                  CONFIG['output_file'])
        sys.exit(1)

    file_handle = open(CONFIG['output_file'] + ".tmp", 'w')
    file_handle.write(header)

    if egi_urls:
        for region in egi_urls:
            file_handle.write("\n#\n# %s\n# -----------\n#\n" % region)
            for site in egi_urls[region]:
                file_handle.write("\n#%s\n" % site[0])
                file_handle.write("%s %s\n" % site)

    if CONFIG['manual']:
        if os.path.exists(CONFIG['manual_file']):
            contents = open(CONFIG['manual_file']).read()
            file_handle.write("\n\n# Appended Manual Additions\n\n")
            file_handle.write(contents)
        else:
            LOG.error("Manual URL file %s does not exist!",
                      CONFIG['manual_file'])
            sys.exit(1)

    file_handle.close()
    os.rename(CONFIG['output_file'] + ".tmp", CONFIG['output_file'])


if __name__ == "__main__":
    setup_logging()
    CONFIG = None
    parse_args()

    if not CONFIG:
        LOG.error("No configuration file given.")
        usage()
        sys.exit(1)

    EGI_URLS = None
    if CONFIG.get('EGI'):
        if not CONFIG['certification_status'] in ["Candidate", "Uncertified",
                                                  "Certified", "Closed",
                                                  "Suspended"]:
            MESSAGE = "'%s' is not a valid certification_status." \
                % CONFIG['certification_status']
            LOG.error(MESSAGE)
            sys.exit(1)
        EGI_URLS = get_egi_urls(CONFIG['certification_status'])
        PICKLE_FILE = CONFIG['cache_dir'] + '/' + 'EGI.pkl'
        if EGI_URLS:
            FILE_HANDLE = open(PICKLE_FILE, 'wb')
            pickle.dump(EGI_URLS, FILE_HANDLE)
            FILE_HANDLE.close()
        else:
            LOG.warn(("EGI GOCDB could not be contacted or returned no"
                      " information about EGI sites."
                      " Using cache file for EGI URLs."))
            FILE_HANDLE = open(PICKLE_FILE, 'rb')
            EGI_URLS = pickle.load(FILE_HANDLE)
            FILE_HANDLE.close()

    create_urls_file(EGI_URLS)
