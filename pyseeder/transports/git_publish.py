#!/usr/bin/env python3
# unpythonic script to (re)upload asset to github release
# used for stealthy I2P reseeding
# GENERATE TOKEN for this script here --> https://github.com/settings/tokens
# Check scope: public_repo (shall be enough)

from urllib.parse import urljoin
from mimetypes import guess_type
from pyseeder.utils import TransportException
import requests
import os

TRANSPORT_NAME = "git"

def run(filename, config):
    if "GH_USERNAME" not in config:
        raise TransportException("git: No username specified in config")
    else:
        REPO_USERNAME = config["GH_USERNAME"]
    if "GH_TOKEN" not in config:
        raise TransportException("git: No token specified in config")
    else:
        REPO_TOKEN = config["GH_TOKEN"]
    if "GH_REPO" not in config:
        raise TransportException("git: No repository specified in config")
    else:
        REPO_PATH = config["GH_REPO"]
    if "GH_TAG" not in config:
        raise TransportException("git: No tag specified in config")
    else:
        REPO_TAG = config["GH_TAG"]

    API_URL = "https://api.github.com/"
    asset_name = os.path.split(filename)[1]
    content_type = guess_type(asset_name)[0] or "application/zip"
    creds = (REPO_USERNAME, REPO_TOKEN)
    release_info_url = urljoin(API_URL, "/repos/{}/releases/tags/{}".format(
        REPO_PATH, REPO_TAG))

    # get release info
    resp = requests.get(release_info_url, auth=creds)
    assert resp.status_code is 200, "Successfull auth must return 200"

    # delete old asset
    for x in resp.json()["assets"]:
        if x["name"] == asset_name:
            r = requests.delete(x["url"], auth=creds)
            assert r.status_code is 204, "Deletion must return 204"

    # upload new asset
    # im super lazy
    upload_url = resp.json()["upload_url"].split("{")[0]
    headers = {'Content-Type': content_type}
    params = {'name': asset_name}

    data = open(filename, 'rb').read()
    r = requests.post(upload_url, headers=headers, params=params, auth=creds,
        data=data)
    assert r.status_code is 201, "Upload must return 201"
