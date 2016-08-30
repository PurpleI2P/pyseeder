"""Git transport plugin"""
import subprocess
import os, os.path
from shutil import copyfile
from pyseeder.utils import TransportException

TRANSPORT_NAME = "git"

# Push to github repo witout prompting password. 
# Set up SSH keys or change origin URL like that:
# git remote set-url origin https://$USERNAME:$PASSWORD@github.com/$USERNAME/$REPO.git

def run(filename, config): 
    if "folder" not in config:
        raise TransportException("git: No folder specified in config")
    else:
        REPO_FOLDER = config["folder"]

    REPO_FILE = os.path.split(filename)[1]

    if not os.access(REPO_FOLDER, os.W_OK):
        raise TransportException("git: {} access forbidden" \
                .format(REPO_FOLDER))

    if not os.path.isfile(filename):
        raise TransportException("git: input file not found")

    copyfile(filename, os.path.join(REPO_FOLDER, REPO_FILE))

    commands = [
        "git add {}".format(REPO_FILE), 
        "git commit -m 'update'",
        "git push origin master"
    ]

    cwd = os.getcwd()
    os.chdir(REPO_FOLDER)
    for c in commands: subprocess.call(c, shell=True)
    os.chdir(cwd)
