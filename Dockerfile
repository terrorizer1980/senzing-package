ARG BASE_IMAGE=debian:9
FROM ${BASE_IMAGE}

ENV REFRESHED_AT=2019-04-30

LABEL Name="senzing/senzing-package" \
      Maintainer="support@senzing.com" \
      Version="1.0.0"

HEALTHCHECK CMD ["/app/healthcheck.sh"]

# Install packages via apt.

RUN apt-get update \
 && apt-get -y install \
    python \
 && rm -rf /var/lib/apt/lists/*

# Copy files from repository.

COPY ./rootfs /
COPY ./senzing-package.py /app/
COPY ./downloads/ /app/downloads/

# Runtime execution.

WORKDIR /app
ENTRYPOINT /app/senzing-package.py
CMD [""]
