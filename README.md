# senzing-package

## Overview

The [senzing-package.py](senzing-package.py) python script manages installing `Senzing_API.tgz`.
The `senzing/senzing-package` docker image is a wrapper for use in docker formations (e.g. docker-compose, kubernetes).

To see all of the subcommands, run:

```console
$ ./senzing-package.py --help
usage: senzing-package.py [-h]
                          {version,sleep,current-version,package-version,install,delete,replace}
                          ...

Senzing package management. For more information, see
https://github.com/senzing/senzing-package

positional arguments:
  {version,sleep,current-version,package-version,install,delete,replace}
                        Subcommands (SENZING_SUBCOMMAND):
    version             Print the version of senzing-package.py.
    sleep               Do nothing but sleep. For Docker testing.
    current-version     Show the version of the currently installed Senzing
                        package.
    package-version     Show the version of the Senzing_API.tgz package.
    install             Backup existing directory and install to a clean
                        directory.
    delete              Delete existing directory.
    replace             Delete existing directory and install to a clean
                        directory.

optional arguments:
  -h, --help            show this help message and exit
```

### Contents

1. [Using Command Line](#using-command-line)
    1. [Install](#install)
    1. [Demonstrate](#demonstrate)
1. [Using Docker](#using-docker)
    1. [Build docker image](#build-docker-image)
    1. [Configuration](#configuration)
    1. [Run docker image](#run-docker-image)
1. [Develop](#develop)
    1. [Prerequisite software](#prerequisite-software)
    1. [Clone repository](#clone-repository)
    1. [Downloads](#downloads)
    1. [Build docker image for development](#build-docker-image-for-developmen
1. [Examples](#examples)
1. [Errors](errors)

## Using Command Line

### Install

### Demonstrate

## Using Docker

### Build docker image

See [Develop](#develop).

### Configuration

- **SENZING_SUBCOMMAND** -
  Identify the subcommand to be run. See `stream-loader.py --help` for complete list.
  
1. To determine which configuration parameters are use for each `<subcommand>`, run:

    ```console
    ./senzing-package.py <subcommand> --help
    ```

### Run docker image

#### Demonstrate stand-alone

1. Run the docker container. Example:

    ```console
    export SENZING_SUBCOMMAND=install
    export SENZING_DIR=/opt/senzing

    sudo docker run \
      --env SENZING_SUBCOMMAND="${SENZING_SUBCOMMAND}" \
      --rm \
      --volume ${SENZING_DIR}:/opt/senzing \
      senzing/senzing-package
    ```

#### Demonstrate in docker-compose

1. Determine docker network:

    ```console
    docker network ls

    # Choose value from NAME column of docker network ls
    export SENZING_NETWORK=nameofthe_network
    ```

1. Run the docker container. Example:

    ```console
    export SENZING_SUBCOMMAND=install
    export SENZING_DIR=/opt/senzing

    sudo docker run \
      --env SENZING_SUBCOMMAND="${SENZING_SUBCOMMAND}" \
      --net ${SENZING_NETWORK} \
      --rm \
      --volume ${SENZING_DIR}:/opt/senzing \
      senzing/senzing-package
    ```

## Develop

### Prerequisite software

The following software programs need to be installed:

1. [git](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-git.md)
1. [make](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-make.md)
1. [docker](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-docker.md)

### Clone repository

1. Set these environment variable values:

    ```console
    export GIT_ACCOUNT=senzing
    export GIT_REPOSITORY=senzing-package
    ```

   Then follow steps in [clone-repository](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/clone-repository.md).

1. After the repository has been cloned, be sure the following are set:

    ```console
    export GIT_ACCOUNT_DIR=~/${GIT_ACCOUNT}.git
    export GIT_REPOSITORY_DIR="${GIT_ACCOUNT_DIR}/${GIT_REPOSITORY}"
    ```

### Downloads

#### Download Senzing_API.tgz

1. Visit [Downloading Senzing_API.tgz](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/create-senzing-dir.md#downloading-senzing_apitgz)
1. Download `Senzing_API.tgz` to ${GIT_REPOSITORY_DIR}/[downloads](./downloads) directory.

### Build docker image for development

1. Variation #1 - Using `make` command.

    ```console
    cd ${GIT_REPOSITORY_DIR}
    sudo make docker-build
    ```

    Note: `sudo make docker-build-base` can be used to create cached docker layers.

1. Variation #2 - Using `docker` command.

    ```console
    export DOCKER_IMAGE_NAME=senzing/senzing-package

    cd ${GIT_REPOSITORY_DIR}
    sudo docker build --tag ${DOCKER_IMAGE_NAME} .
    ```

## Examples

## Errors

1. See [docs/errors.md](docs/errors.md).