"""Action functions for argparser"""
import pyseeder.transport
import pyseeder.actions
from pyseeder.utils import PyseederException, check_readable, check_writable

def keygen(args):
    """Sub-command to generate keys"""
    for f in [args.cert, args.private_key]: check_writable(f)

    from pyseeder.crypto import keygen
    from getpass import getpass
    priv_key_password = getpass("Set private key password: ").encode("utf-8")
    keygen(args.cert, args.private_key, priv_key_password, args.signer_id)

def reseed(args):
    """Sub-command to generate reseed file"""
    check_writable(args.outfile)
    for f in [args.netdb, args.private_key]: check_readable(f)

    from pyseeder.su3file import SU3File
    priv_key_password = input().encode("utf-8")
    su3file = SU3File(args.signer_id)
    su3file.reseed(args.netdb)
    su3file.write(args.outfile, args.private_key, priv_key_password)

def transport_pull(args):
    """Sub-command for downloading su3 file"""
    import random
    random.shuffle(args.urls)

    for u in args.urls:
        if pyseeder.transport.download(u, args.outfile):
            return True

    raise PyseederException("Failed to download su3 file")

def transport_push(args):
    """Sub-command for uploading su3 file with transports"""
    check_readable(args.config)

    import configparser
    config = configparser.ConfigParser()
    config.read(args.config)
    pyseeder.transport.upload(args.file, config)

def serve(args):
    """Sub-command to start HTTPS reseed server"""
    for f in [args.private_key, args.cert, args.file]: check_readable(f)

    import pyseeder.server
    pyseeder.server.run_server(args.host, args.port, args.private_key,
            args.cert, args.file)
