FROM alpine:latest
LABEL authors "Darknet Villain <supervillain@riseup.net>"

ENV PYSEEDER_HOME="/home/pyseeder"
ENV DATA_DIR="${PYSEEDER_HOME}/data"

RUN mkdir -p "$PYSEEDER_HOME" "$DATA_DIR" "$DATA_DIR"/data "$DATA_DIR"/output \
    && adduser -S -h "$PYSEEDER_HOME" pyseeder \
    && chown -R pyseeder:nobody "$PYSEEDER_HOME" \
    && chmod -R 700 "$DATA_DIR"

RUN apk --no-cache add python3 py3-pip build-base git openssl-dev musl-dev python3-dev libffi-dev \
    && pip3 install --no-cache-dir https://github.com/PurpleI2P/pyseeder/zipball/master \
    && apk --purge del python3 py3-pip build-base git openssl-dev musl-dev python3-dev libffi-dev 

# 2. Adding required libraries to run i2pd to ensure it will run.
RUN apk --no-cache add python3 openssl

RUN mkdir /netDb

VOLUME "$DATA_DIR"

COPY entrypoint.sh /entrypoint.sh
RUN chmod a+x /entrypoint.sh

EXPOSE 8443

USER pyseeder

ENTRYPOINT [ "/entrypoint.sh" ]

