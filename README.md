# senzing-package

## Overview

The [senzing-package.py](senzing-package.py) python script
copies `data/` and `g2/` directories to new locations.
The `senzing/senzing-package` docker image is a wrapper for use in docker formations (e.g. docker-compose, kubernetes).
Baked into `senzing/senzing-package` is the installed `senzingdata-v1` and `senzingapi` packages.

The dockerized version, `store/senzing/senzing-package`, is at
[hub.docker.com/_/senzing-package](https://hub.docker.com/_/senzing-package).
For more information, scroll down to [Accept docker image](#accept-docker-image).

To see all of the subcommands, run:

```console
$ ./senzing-package.py
usage: python-template.py [-h]
                          {install,sleep,version,docker-acceptance-test} ...

Example python skeleton. For more information, see
https://github.com/Senzing/python-template

positional arguments:
  {install,sleep,version,docker-acceptance-test}
                        Subcommands (SENZING_SUBCOMMAND):
    install             Copy source data and g2 directories to a target.
    sleep               Do nothing but sleep. For Docker testing.
    version             Print version of program.
    docker-acceptance-test
                        For Docker acceptance testing.

optional arguments:
  -h, --help            show this help message and exit
```

To see the options for a subcommand, run commands like:

```console
./senzing-package.py install --help
```

### Related artifacts

1. [DockerHub](https://hub.docker.com/_/senzing-package)
1. [Helm Chart](https://github.com/Senzing/charts/tree/master/charts/senzing-package)

### Contents

1. [Expectations](#expectations)
    1. [Space](#space)
    1. [Time](#time)
    1. [Background knowledge](#background-knowledge)
1. [Demonstrate using Docker](#demonstrate-using-docker)
    1. [Accept docker image](#accept-docker-image)
    1. [Configuration](#configuration)
    1. [Demonstrate using Docker](#demonstrate-using-docker)
1. [Develop](#develop)
    1. [Prerequisite software](#prerequisite-software)
    1. [Clone repository](#clone-repository)
    1. [Build docker image for development](#build-docker-image-for-development)
1. [Examples](#examples)
1. [Errors](#errors)
1. [References](#references)

## Expectations

### Space

This repository and demonstration require 6 GB free disk space.

### Time

Budget 40 minutes to get the demonstration up-and-running, depending on CPU and network speeds.

### Background knowledge

This repository assumes a working knowledge of:

1. [Docker](https://github.com/Senzing/knowledge-base/blob/master/WHATIS/docker.md)

## Demonstrate using Docker

### Accept docker image

The use of the [store/senzing/senzing-package](https://hub.docker.com/_/senzing-package)
docker image requires acceptance of an End User License agreement (EULA).
To accept the license:

1. Visit [hub.docker.com/_/senzing-package](https://hub.docker.com/_/senzing-package).
1. Login to DockerHub.
1. On [hub.docker.com/_/senzing-package](https://hub.docker.com/_/senzing-package), click "Proceed to Checkout" button.
1. Check boxes for agreeing and acknowledging
1. Click "Get Content" button.
1. Verify image can be pulled from "Docker Store".  Example:

   ```console
   sudo docker pull store/senzing/senzing-package:0.0.1
   ```

### Configuration

Configuration values specified by environment variable or command line parameter.

- **[SENZING_DATA_DIR](https://github.com/Senzing/knowledge-base/blob/master/lists/environment-variables.md#senzing_data_dir)**
- **[SENZING_DEBUG](https://github.com/Senzing/knowledge-base/blob/master/lists/environment-variables.md#senzing_debug)**
- **[SENZING_G2_DIR](https://github.com/Senzing/knowledge-base/blob/master/lists/environment-variables.md#senzing_g2_dir)**
- **[SENZING_LOG_LEVEL](https://github.com/Senzing/knowledge-base/blob/master/lists/environment-variables.md#senzing_log_level)**
- **[SENZING_NETWORK](https://github.com/Senzing/knowledge-base/blob/master/lists/environment-variables.md#senzing_network)**
- **[SENZING_RUNAS_USER](https://github.com/Senzing/knowledge-base/blob/master/lists/environment-variables.md#senzing_runas_user)**
- **[SENZING_SLEEP_TIME](https://github.com/Senzing/knowledge-base/blob/master/lists/environment-variables.md#senzing_sleep_time)**
- **[SENZING_SUBCOMMAND](https://github.com/Senzing/knowledge-base/blob/master/lists/environment-variables.md#senzing_subcommand)**

1. To determine which configuration parameters are use for each `<subcommand>`, run:

    ```console
    ./senzing-package.py <subcommand> --help
    ```

### Demonstrate using Docker

1. :pencil2: Set environment variables.  Example:

    ```console
    export SENZING_SUBCOMMAND=install
    export SENZING_DATA_DIR=/opt/my-senzing/data
    export SENZING_G2_DIR=/opt/my-senzing/g2
    ```

#### Docker network

:thinking: **Optional:**  Use if docker container is part of a docker network.

1. List docker networks.
   Example:

    ```console
    sudo docker network ls
    ```

1. :pencil2: Specify docker network.
   Choose value from NAME column of `docker network ls`.
   Example:

    ```console
    export SENZING_NETWORK=*nameofthe_network*
    ```

1. Construct parameter for `docker run`.
   Example:

    ```console
    export SENZING_NETWORK_PARAMETER="--net ${SENZING_NETWORK}"
    ```

#### Docker user

:thinking: **Optional:**  The docker container runs as "USER 1001".
Use if a different userid (UID) is required.

1. :pencil2: Manually identify user.
   User "0" is root.
   Example:

    ```console
    export SENZING_RUNAS_USER="0"
    ```

   Another option, use current user.
   Example:

    ```console
    export SENZING_RUNAS_USER=$(id -u)
    ```

1. Construct parameter for `docker run`.
   Example:

    ```console
    export SENZING_RUNAS_USER_PARAMETER="--user ${SENZING_RUNAS_USER}"
    ```

#### Run docker container

1. Run docker container.
   Example:

    ```console
    sudo docker run \
      ${SENZING_RUNAS_USER_PARAMETER} \
      ${SENZING_NETWORK_PARAMETER} \
      --env SENZING_SUBCOMMAND="${SENZING_SUBCOMMAND}" \
      --rm \
      --volume ${SENZING_DATA_DIR}:/opt/senzing/data \
      --volume ${SENZING_G2_DIR}:/opt/senzing/g2 \
      senzing/senzing-package
    ```

## Develop

### Prerequisite software

The following software programs need to be installed:

1. [git](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-git.md)
1. [make](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-make.md)
1. [docker](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-docker.md)

### Clone repository

For more information on environment variables,
see [Environment Variables](https://github.com/Senzing/knowledge-base/blob/master/lists/environment-variables.md).

1. Set these environment variable values:

    ```console
    export GIT_ACCOUNT=senzing
    export GIT_REPOSITORY=senzing-package
    export GIT_ACCOUNT_DIR=~/${GIT_ACCOUNT}.git
    export GIT_REPOSITORY_DIR="${GIT_ACCOUNT_DIR}/${GIT_REPOSITORY}"
    ```

1. Follow steps in [clone-repository](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/clone-repository.md) to install the Git repository.

### Build docker image for development

1. **Option #1:** Using `docker` command and GitHub.

    ```console
    sudo docker build --tag senzing/template https://github.com/senzing/senzing-package.git
    ```

1. **Option #2:** Using `docker` command and local repository.

    ```console
    cd ${GIT_REPOSITORY_DIR}
    sudo docker build --tag senzing/senzing-package .
    ```

1. **Option #3:** Using `make` command.

    ```console
    cd ${GIT_REPOSITORY_DIR}
    sudo make docker-build
    ```

    Note: `sudo make docker-build-development-cache` can be used to create cached docker layers.

## Examples

## Errors

1. See [docs/errors.md](docs/errors.md).

## References
