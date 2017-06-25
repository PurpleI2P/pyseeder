import os
import time, datetime
import random 
import io

from zipfile import ZipFile, ZIP_DEFLATED

import pyseeder.crypto
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

    def write(self, filename, priv_key, priv_key_password=None):
        """Write file to disc"""
        nullbyte = bytes([0])
        with open(filename, "wb") as f:
            f.write("I2Psu3".encode("utf-8"))
            f.write(bytes([0,0]))
            f.write(self.SIGNATURE_TYPE.to_bytes(2, "big"))
            f.write(self.SIGNATURE_LENGTH.to_bytes(2, "big"))
            f.write(nullbyte)
            f.write(bytes([self.VERSION_LENGTH]))
            f.write(nullbyte)
            f.write(bytes([self.SIGNER_ID_LENGTH]))
            f.write(self.CONTENT_LENGTH.to_bytes(8, "big"))
            f.write(nullbyte)
            f.write(bytes([self.FILE_TYPE]))
            f.write(nullbyte)
            f.write(bytes([self.CONTENT_TYPE]))
            f.write(bytes([0 for _ in range(12)]))
            f.write(self.VERSION + bytes(
                [0 for _ in range(16 - len(self.VERSION))]))
            f.write(self.SIGNER_ID.encode("utf-8"))
            f.write(self.CONTENT)

        pyseeder.crypto.append_signature(filename, priv_key, priv_key_password)

    def reseed(self, netdb):
        """Compress netdb entries and set content"""
        zip_file = io.BytesIO()
        dat_files = []

        for root, dirs, files in os.walk(netdb):
            for f in files:
                if f.endswith(".dat"):
                    # TODO check modified time
                    # may be not older than 10h
                    dat_files.append(os.path.join(root, f))

        if len(dat_files) == 0:
            raise PyseederException("Can't get enough netDb entries")
        elif len(dat_files) > 75:
            dat_files = random.sample(dat_files, 75)

        with ZipFile(zip_file, "w", compression=ZIP_DEFLATED) as zf:
            for f in dat_files: 
                zf.write(f, arcname=os.path.split(f)[1])

        self.FILE_TYPE = 0x00
        self.CONTENT_TYPE = 0x03
        self.CONTENT = zip_file.getvalue()
        self.CONTENT_LENGTH = len(self.CONTENT)
