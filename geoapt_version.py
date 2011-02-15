from datetime import date
from subprocess import *
sha = Popen(["git", "rev-parse", "--short", "HEAD"], stdout=PIPE).communicate()[0]
VERSION = " - 0.1.4-dev-" + sha
COPYRIGHT = "(C) 2011 GeoApt LLC"
WEBSITE = "http://geoapt.com/geoapt-data-browser"
