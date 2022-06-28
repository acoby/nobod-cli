FROM python:alpine
LABEL maintainer="TRW <trw@acoby.de>" \
      org.label-schema.schema-version="1.0" \
      org.label-schema.name="nobod-cli" \
      org.label-schema.description="A simple container wrapper around a command line tool" \
      org.label-schema.url="https://github.com/acoby/nobod-cli" \
      org.label-schema.vendor="acoby GmbH"

ENV TZ Europe/Berlin

COPY nobod-cli.py /usr/local/bin/nobod-cli

RUN apk add --no-cache --update git openssh-keygen && \
    adduser -u 5000 -h /repository -D worker && \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install netaddr passlib requests && \
    chmod 755 /usr/local/bin/nobod-cli

USER worker

CMD ["/usr/local/bin/nobod-cli", "--help"]
