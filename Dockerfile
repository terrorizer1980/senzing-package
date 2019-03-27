ARG BASE_IMAGE=debian:9
FROM ${BASE_IMAGE}

ENV REFRESHED_AT=2019-03-22

LABEL Name="senzing/senzing-package" \
      Version="1.0.0"

# Install packages via apt.

# RUN apt-get update \
#  && apt-get -y install \
#     librdkafka-dev \
#  && rm -rf /var/lib/apt/lists/*

# Perform PIP installs.

# RUN pip install \
#     configparser \
#     confluent-kafka \
#     psutil

# Copy into the app directory.

COPY ./senzing-package /app/

# Override parent docker image.

WORKDIR /app
ENTRYPOINT ["/app/senzing-package.py"]
CMD [""]
