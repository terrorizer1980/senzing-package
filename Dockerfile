ARG BASE_IMAGE=debian:10
FROM ${BASE_IMAGE}

ENV REFRESHED_AT=2019-11-01

LABEL Name="senzing/senzing-package" \
      Maintainer="support@senzing.com" \
      Version="1.12.1"

HEALTHCHECK CMD ["/app/healthcheck.sh"]

# Install packages via apt.

RUN apt update \
 && apt -y install \
    apt-transport-https \
    curl \
    gnupg \
    python3 \
    python3-distutils \
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

# Install system packages.

ARG SENZING_ACCEPT_EULA=NO
ENV SENZING_ACCEPT_EULA=${SENZING_ACCEPT_EULA}
RUN env
RUN echo "---------------" \
 && env \
 && echo "---------------" \
 && apt -y install senzingdata-v1 senzingapi

# Move files.

RUN mv /opt/senzing /opt/senzing-source

# Copy files from repository.

COPY ./rootfs /
COPY ./senzing-package.py /app/

# Runtime execution.

ENV SENZING_DOCKER_LAUNCHED=true

WORKDIR /app
ENTRYPOINT ["/app/senzing-package.py"]
