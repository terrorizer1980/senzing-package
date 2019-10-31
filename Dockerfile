ARG BASE_IMAGE=debian:10
FROM ${BASE_IMAGE}

ENV REFRESHED_AT=2019-11-01

LABEL Name="senzing/senzing-package" \
      Maintainer="support@senzing.com" \
      Version="1.13.0"

HEALTHCHECK CMD ["/app/healthcheck.sh"]

# Install packages via apt.

RUN apt update \
 && apt -y install \
    apt-transport-https \
    curl \
    gnupg \
    sudo \
    wget

# Install Senzing repository index.

RUN curl \
    --output /senzingrepo_1.0.0-1_amd64.deb \
    https://senzing-production-apt.s3.amazonaws.com/senzingrepo_1.0.0-1_amd64.deb \
 && apt -y install \
    /senzingrepo_1.0.0-1_amd64.deb \
 && apt update \
 && rm /senzingrepo_1.0.0-1_amd64.deb

# Copy files from repository.

COPY ./rootfs /
COPY ./senzing-package.py /app/

# Install system packages

ENV SENZING_ACCEPT_EULA=I_ACCEPT_THE_SENZING_EULA
RUN apt -y install senzingdata-v1 senzingapi

# Move files.

RUN mv /opt/senzing     /opt/senzing-original \
 && mv /etc/opt/senzing /etc/opt/senzing-original \
 && mv /var/opt/senzing /var/opt/senzing-original \

WORKDIR /app
ENTRYPOINT ["/app/senzing-package.py"]
