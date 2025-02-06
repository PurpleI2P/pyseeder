import os
import time, datetime
import random
import io

from zipfile import ZipFile, ZIP_DEFLATED

import pyseeder.crypto
from pyseeder.routerinfo import RouterInfo
from pyseeder.utils import PyseederException


class SU3File:
    """SU3 file format"""

    def __init__(self, signer_id):
        self.SIGNER_ID = signer_id
        self.SIGNER_ID_LENGTH = len(self.SIGNER_ID)
        self.SIGNATURE_TYPE = 0x0006
        self.SIGNATURE_LENGTH = 512
        self.VERSION_LENGTH = 0x10
        self.FILE_TYPE = None
        self.CONTENT_TYPE = None
        self.CONTENT = None
        self.CONTENT_LENGTH = None
        self.VERSION = str(int(time.time())).encode("utf-8")
        #self.keytype = "RSA_SHA512_4096"
        self.OUTPUT = None

    def write(self, filename, priv_key, priv_key_password=None):
        """Write file to disc"""
        nullbyte = bytes([0])

        self.OUTPUT = "I2Psu3".encode("utf-8")
        self.OUTPUT += bytes([0,0])
        self.OUTPUT += self.SIGNATURE_TYPE.to_bytes(2, "big")
        self.OUTPUT += self.SIGNATURE_LENGTH.to_bytes(2, "big")
        self.OUTPUT += nullbyte
        self.OUTPUT += bytes([self.VERSION_LENGTH])
        self.OUTPUT += nullbyte
        self.OUTPUT += bytes([self.SIGNER_ID_LENGTH])
        self.OUTPUT += self.CONTENT_LENGTH.to_bytes(8, "big")
        self.OUTPUT += nullbyte
        self.OUTPUT += bytes([self.FILE_TYPE])
        self.OUTPUT += nullbyte
        self.OUTPUT += bytes([self.CONTENT_TYPE])
        self.OUTPUT += bytes([0 for _ in range(12)])
        self.OUTPUT += self.VERSION + bytes(
            [0 for _ in range(16 - len(self.VERSION))])
        self.OUTPUT += self.SIGNER_ID.encode("utf-8")
        self.OUTPUT += self.CONTENT

        signature = pyseeder.crypto.get_signature(self.OUTPUT, priv_key, priv_key_password)
        self.OUTPUT += signature

        with open(filename, "wb") as f:
           f.write(self.OUTPUT)

    def reseed(self, netdb, yggseeds):
        """Compress netdb entries and set content"""
        seeds = 75
        zip_file = io.BytesIO()
        dat_files = []
        dat_yggfiles = []

        timelimit = time.time() - float(3600 * 10) # current time minus 10 hours

        for root, dirs, files in os.walk(netdb):
            for f in files:
                if f.endswith(".dat"):
                    path = os.path.join(root, f)

                    if os.path.getmtime(path) < timelimit: # modified time older than 10h
                        continue

                    ri = RouterInfo(path)
                    if ri.isvalid():
                        ygg_file_added = False
                        if yggseeds > 0 and ri.isyggdrasil():
                            dat_yggfiles.append(path)
                            ygg_file_added = True
      
                        if not ygg_file_added:
                            dat_files.append(path)


        if yggseeds > 0:
            if len(dat_yggfiles) == 0:
                raise PyseederException("Can't get enough netDb entries with yggdrasil addresses")
            elif len(dat_yggfiles) > yggseeds:
                dat_yggfiles = random.sample(dat_yggfiles, yggseeds)
            seeds = seeds - len(dat_yggfiles)

        if len(dat_files) == 0:
            raise PyseederException("Can't get enough netDb entries")
        elif len(dat_files) > seeds:
            dat_files = random.sample(dat_files, seeds)

        dat_files.extend(dat_yggfiles)

        with ZipFile(zip_file, "w", compression=ZIP_DEFLATED) as zf:
            for f in dat_files:
                zf.write(f, arcname=os.path.split(f)[1])

        self.FILE_TYPE = 0x00
        self.CONTENT_TYPE = 0x03
        self.CONTENT = zip_file.getvalue()
        self.CONTENT_LENGTH = len(self.CONTENT)
