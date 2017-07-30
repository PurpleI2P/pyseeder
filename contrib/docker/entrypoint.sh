#!/bin/sh
COMMAND="pyseeder"

if [ "$1" = "--help" ]; then
    $COMMAND --help
else
    # TODO
    # make configurable SIGNER_ID and cert, key etc

    DATA_DIR="/home/pyseeder/data"
    SIGNER_ID="test@mail.i2p"
    PRIVKEY_FILE="$DATA_DIR/data/private_key.pem"
    CERT_FILE=` echo $DATA_DIR/data/$SIGNER_ID.crt | sed 's/@/_at_/' `
    RESEED_FILE="$DATA_DIR/output/i2pseeds.su3"
    NETDB_DIR="/i2pd_data/netDb"
    if [ ! -d $NETDB_DIR ]; then
	    NETDB_DIR="/netDb"
    fi

    $COMMAND keygen --signer-id $SIGNER_ID --no-encrypt \
        --private-key $PRIVKEY_FILE --cert $CERT_FILE
    $COMMAND reseed --netdb $NETDB_DIR --signer-id $SIGNER_ID --no-encrypt \
        --private-key $PRIVKEY_FILE --outfile $RESEED_FILE
    $COMMAND serve --private-key $PRIVKEY_FILE --cert $CERT_FILE --file $RESEED_FILE
fi

