import os
import random
import sys
import datetime

from pyseeder.utils import PyseederException

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

def keygen(pub_key, priv_key, user_id, priv_key_password=None):
    """Generate new private key and certificate RSA_SHA512_4096"""
    # Generate our key
    key = rsa.generate_private_key(public_exponent=65537, key_size=4096,
                                            backend=default_backend())

    if priv_key_password:
        ea = serialization.BestAvailableEncryption(priv_key_password)
    else:
        ea = serialization.NoEncryption()

    # Write our key to disk for safe keeping
    with open(priv_key, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=ea,
        ))

    # Various details about who we are. For a self-signed certificate the
    # subject and issuer are always the same.
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "XX"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "XX"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "XX"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "I2P Anonymous Network"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "I2P"),
        x509.NameAttribute(NameOID.COMMON_NAME, user_id),
    ])

    cert = x509.CertificateBuilder() \
        .subject_name(subject) \
        .issuer_name(issuer) \
        .public_key(key.public_key()) \
        .not_valid_before(datetime.datetime.utcnow()) \
        .not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365*10)
        ) \
        .serial_number(random.randrange(1000000000, 2000000000)) \
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(key.public_key()),
            critical=False,
        ).sign(key, hashes.SHA512(), default_backend())

    with open(pub_key, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))


def get_signature(contents, priv_key, priv_key_password=None):
    """Calculate signature for prepared reseed file"""
    """Singing with NoneWithRSA algorithm: https://stackoverflow.com/a/68301530"""
    import rsa as pyrsa

    with open(priv_key, "rb") as kf:
        pk = pyrsa.PrivateKey.load_pkcs1(
            serialization.load_pem_private_key(
                kf.read(), password=priv_key_password, backend=default_backend()
            ).private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption()
            )
        )

    digest = hashes.Hash(hashes.SHA512(), default_backend())
    digest.update(contents)
    h = digest.finalize()

    keylength = pyrsa.pkcs1.common.byte_size(pk.n)
    padded = pyrsa.pkcs1._pad_for_signing(h, keylength)
    payload = pyrsa.pkcs1.transform.bytes2int(padded)
    encrypted = pk.blinded_encrypt(payload)
    sig = pyrsa.pkcs1.transform.int2bytes(encrypted, keylength)

    return sig
