"""Module for managing transport tasks"""
import urllib.request
from urllib.error import URLError
import os
import importlib

from pyseeder.utils import PyseederException


RESEED_URLS = [
    "https://reseed.i2p-projekt.de/",
    "https://i2p.mooo.com/netDb/",
    "https://netdb.i2p2.no/",
    "https://us.reseed.i2p2.no:444/",       
    "https://uk.reseed.i2p2.no:444/",
    "https://i2p.manas.ca:8443/",
    "https://i2p-0.manas.ca:8443/",
    "https://reseed.i2p.vzaws.com:8443/",
    "https://user.mx24.eu/",
    "https://download.xxlspeed.com/",
]

def download(url, filename):
    """Download .su3 file, return True on success"""
    USER_AGENT = "Wget/1.11.4"

    url = "{}i2pseeds.su3".format(url)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(req) as resp:
            with open(filename, 'wb') as f:
                f.write(resp.read())

        if os.stat(filename).st_size > 0:
            return True
        else:
            return False
    except URLError as e:
        return False


def upload(filename, config):
    """Upload .su3 file with transports"""
    if "transports" in config and "enabled" in config["transports"]:
        for t in config["transports"]["enabled"].split():
            if t in config:
                tconf = config[t]
            else:
                tconf = None

            try:
                importlib.import_module("pyseeder.transports.{}".format(t)) \
                                                .run(filename, tconf)
            except ImportError:
                raise PyseederException(
                        "{} transport can't be loaded".format(t))

