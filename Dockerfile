FROM python:alpine
LABEL maintainer="TRW <trw@acoby.de>" \
      org.label-schema.schema-version="1.0" \
      org.label-schema.name="nobod-cli" \
      org.label-schema.description="A simple container wrapper around a command line tool" \
      org.label-schema.url="https://github.com/acoby/nobod-cli" \
      org.label-schema.vendor="acoby GmbH"

COPY nobod-cli.py /usr/local/bin/nobod-cli
CMD ["/usr/local/bin/nobod-cli", "--help"]
