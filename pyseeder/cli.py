#! /usr/bin/env python3
import os
import sys
import argparse
import logging

import pyseeder.transport
import pyseeder.actions
from pyseeder.utils import PyseederException

log = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--loglevel', default=logging.INFO, help="Log level",
            choices=[logging.CRITICAL, logging.ERROR, logging.WARNING,
                     logging.INFO, logging.DEBUG])

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
    kg_parser.add_argument("--cert", default=None,
            help="Certificate (example: data/user_at_mail.i2p.crt)")
    kg_parser.add_argument("--no-encryption", action="store_true",
            help="Disable private key encryption")
    kg_parser.set_defaults(func=pyseeder.actions.keygen)


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
    rs_parser.add_argument("--no-encryption", action="store_true",
            help="Disable private key encryption")
    rs_parser.set_defaults(func=pyseeder.actions.reseed)


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
    tpull_parser.set_defaults(func=pyseeder.actions.transport_pull)


    tpush_parser = subparsers.add_parser(
        "transport.push",
        description="Upload su3 file with transports",
        usage="%(prog)s --config transports.ini --file output/i2pseeds.su3"
    )
    tpush_parser.add_argument("--config", default="transports.ini",
            help="Transports config file (default: transports.ini)")
    tpush_parser.add_argument("-f", "--file", default="output/i2pseeds.su3",
            help=".su3 file (default: output/i2pseeds.su3)")
    tpush_parser.set_defaults(func=pyseeder.actions.transport_push)


    serve_parser = subparsers.add_parser(
        "serve",
        description="""Run HTTPS reseeding server
            (in production use nginx instead, please).
            Will ask for a private key password""",
        usage="""%(prog)s --port 8443 --host 127.0.0.1 \\
            --private-key data/priv_key.pem \\
            --cert data/user_at_mail.i2p.crt \\
            --file output/i2pseeds.su3"""
    )
    serve_parser.add_argument("--host", default="0.0.0.0",
            help="Host listening for clients (default: 0.0.0.0)")
    serve_parser.add_argument("--port", default=8443,
            help="Port listening for clients (default: 8443)")
    serve_parser.add_argument("--private-key", default="data/priv_key.pem",
            help="RSA private key (default: data/priv_key.pem)")
    serve_parser.add_argument("--cert", required=True,
            help="Certificate (example: data/user_at_mail.i2p.crt)")
    serve_parser.add_argument("-f", "--file", default="output/i2pseeds.su3",
            help=".su3 file (default: output/i2pseeds.su3)")
    serve_parser.set_defaults(func=pyseeder.actions.serve)


    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel,
            format='%(levelname)-8s %(message)s')

    if hasattr(args, "func"):
        try:
            args.func(args)
        except PyseederException as pe:
            log.critical("Pyseeder error: {}".format(pe))
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
