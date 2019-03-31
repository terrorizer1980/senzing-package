ARG BASE_IMAGE=debian:9
FROM ${BASE_IMAGE}

ENV REFRESHED_AT=2019-03-22

LABEL Name="senzing/senzing-package" \
      Version="1.0.0"

# Install packages via apt.

RUN apt-get update \
 && apt-get -y install \
    python \
 && rm -rf /var/lib/apt/lists/*

# Copy into the app directory.

COPY ./senzing-package.py /app/
COPY ./downloads/ /app/downloads/

# Override parent docker image.

WORKDIR /app
ENTRYPOINT /app/senzing-package.py
CMD [""]
