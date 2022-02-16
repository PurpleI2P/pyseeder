#!/usr/bin/env python3
# (re)uploads reseed file to github repository releases as an asset
import requests

from urllib.parse import urljoin
from mimetypes import guess_type
import sys
import os

from pyseeder.utils import TransportException

TRANSPORT_NAME = "github"

def run(filename, config):
    API_URL = "https://api.github.com/"
    asset_name = os.path.split(filename)[-1]
    content_type = guess_type(asset_name)[0] or "application/zip"
    creds = (config["username"], config["token"])
    release_info_url = urljoin(API_URL, "/repos/{}/releases/tags/{}".format(
                config["repo"], config["release_tag"]))

    # get release info
    try:
        release = requests.get(release_info_url, auth=creds)
    except:
        raise TransportException("Failed to connect to GitHub API")

    if release.status_code is not 200:
        raise TransportException("Check your GitHub API auth settings")

    # fetch release assets
    try:
        assets = requests.get(release.json()["assets_url"], auth=creds)
    except:
        raise TransportException("Unable get release assets")

    # delete old asset
    for x in assets.json():
        if x["name"] == asset_name:
            r = requests.delete(x["url"], auth=creds)
            if r.status_code is not 204:
                raise TransportException("Failed to delete asset from GitHub")

    # upload new asset
    upload_url = release.json()["upload_url"].split("{")[0] # wat
    headers = {'Content-Type': content_type}
    params = {'name': asset_name}

    data = open(filename, 'rb').read()
    r = requests.post(upload_url, headers=headers, params=params, auth=creds,
            data=data)

    if r.status_code is not 201:
        raise TransportException("Failed to upload asset to GitHub API : code %d" % (r.status_code))

