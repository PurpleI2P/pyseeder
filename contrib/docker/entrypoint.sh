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
    I2PD_DIR="/i2pd_data"

    $COMMAND keygen --signer-id $SIGNER_ID --no-encrypt \
        --private-key $PRIVKEY_FILE --cert $CERT_FILE
    $COMMAND reseed --netdb $I2PD_DIR/netDb --signer-id $SIGNER_ID --no-encrypt \
        --private-key $PRIVKEY_FILE --outfile $RESEED_FILE
    $COMMAND serve --private-key $PRIVKEY_FILE --cert $CERT_FILE --file $RESEED_FILE
fi

