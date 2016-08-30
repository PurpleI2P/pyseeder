#! /usr/bin/env python3
import os, os.path
import sys
from getpass import getpass
import argparse

from pyseeder.crypto import keygen
from pyseeder.su3file import SU3File
import pyseeder.transport

from pyseeder.utils import PyseederException

def keygen_action(args):
    """Sub-command to generate keys"""
    priv_key_password = getpass("Set private key password: ").encode("utf-8")
    keygen(args.cert, args.private_key, priv_key_password, args.signer_id)

def reseed_action(args):
    """Sub-command to generate reseed file"""
    priv_key_password = input().encode("utf-8")
    su3file = SU3File(args.signer_id)
    su3file.reseed(args.netdb)
    su3file.write(args.outfile, args.private_key, priv_key_password)

def transport_pull_action(args):
    """Sub-command for downloading su3 file"""
    import random
    random.shuffle(args.urls)

    for u in args.urls:
        if pyseeder.transport.download(u, args.outfile):
            return True

    raise PyseederException("Failed to download su3 file")

def transport_push_action(args):
    """Sub-command for uploading su3 file with transports"""
    if not os.path.isfile(args.config):
        raise PyseederException("Can't read transports config file")

    import configparser
    config = configparser.ConfigParser()
    config.read(args.config)
    pyseeder.transport.upload(args.file, config)

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="actions",
            help="Command to execute")

    kg_parser = subparsers.add_parser(
        "keygen",
        description="Generates keypair for your reseed",
        usage="""
%(prog)s --cert data/user_at_mail.i2p.crt \\
        --private-key data/priv_key.pem --signer-id user@mail.i2p""" 
    )
    kg_parser.add_argument("--signer-id", required=True,
            help="Identifier of certificate (example: user@mail.i2p)")
    kg_parser.add_argument("--private-key", default="data/priv_key.pem",
            help="RSA private key (default: data/priv_key.pem)")
    kg_parser.add_argument("--cert", required=True, 
            help="Certificate (example: output/user_at_mail.i2p.crt)")
    kg_parser.set_defaults(func=keygen_action)


    rs_parser = subparsers.add_parser(
        "reseed",
        description="Creates su3 reseed file",
        usage="""
echo $YOUR_PASSWORD | %(prog)s --netdb /path/to/netDb \\
        --private-key data/priv_key.pem --outfile output/i2pseeds.su3 \\
        --signer-id user@mail.i2p"""
    )
    rs_parser.add_argument("--signer-id", required=True, 
            help="Identifier of certificate (example: user@mail.i2p)")
    rs_parser.add_argument("--private-key", default="data/priv_key.pem",
            help="RSA private key (default: data/priv_key.pem)")
    rs_parser.add_argument("-o", "--outfile", default="output/i2pseeds.su3",
            help="Output file (default: output/i2pseeds.su3)")
    rs_parser.add_argument("--netdb", required=True, 
            help="Path to netDb folder (example: ~/.i2pd/netDb)")
    rs_parser.set_defaults(func=reseed_action)


    tpull_parser = subparsers.add_parser(
        "transport.pull",
        description="Download su3 file from random reseed server",
        usage="""
%(prog)s --urls https://reseed.i2p-projekt.de/ \\
                https://reseed.i2p.vzaws.com:8443/ \\
        --outfile output/i2pseeds.su3"""
    )
    tpull_parser.add_argument("--urls", default=pyseeder.transport.RESEED_URLS,
            nargs="*", help="""Reseed URLs separated by space, default are
            mainline I2P (like https://reseed.i2p-projekt.de/)""")
    tpull_parser.add_argument("-o", "--outfile", default="output/i2pseeds.su3",
            help="Output file (default: output/i2pseeds.su3)")
    tpull_parser.set_defaults(func=transport_pull_action)


    tpush_parser = subparsers.add_parser(
        "transport.push",
        description="Upload su3 file with transports",
        usage="%(prog)s --config transports.ini --file output/i2pseeds.su3"
    )
    tpush_parser.add_argument("--config", default="transports.ini",
            help="Transports config file (default: transports.ini)")
    tpush_parser.add_argument("-f", "--file", default="output/i2pseeds.su3",
            help=".su3 file (default: output/i2pseeds.su3)")
    tpush_parser.set_defaults(func=transport_push_action)

    args = parser.parse_args()
    if hasattr(args, "func"):
        try:
            args.func(args)
        except PyseederException as pe:
            print("Pyseeder error: {}".format(pe))
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
