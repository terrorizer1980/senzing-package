# senzing-package

## Overview

The [senzing-package.py](senzing-package.py) python script manages installing `Senzing_API.tgz`.
The `senzing/senzing-package` docker image is a wrapper for use in docker formations (e.g. docker-compose, kubernetes).

The dockerized version, `store/senzing/senzing-package`, is at
[hub.docker.com/_/senzing-package](https://hub.docker.com/_/senzing-package).
For more information, scroll down to [Accept docker image](#accept-docker-image).

To see all of the subcommands, run:

```console
$ ./senzing-package.py --help
usage: senzing-package.py [-h]
                          {install,replace,delete,installed-version,package-version,version,sleep,docker-acceptance-test}
                          ...

Senzing package management. For more information, see
https://github.com/senzing/senzing-package

positional arguments:
  {install,replace,delete,installed-version,package-version,version,sleep,docker-acceptance-test}
                        Subcommands (SENZING_SUBCOMMAND):
    install             Backup existing directory and install to a clean
                        directory.
    replace             Delete existing directory and install to a clean
                        directory.
    delete              Delete existing directory.
    installed-version   Show the version of the currently installed Senzing
                        package.
    package-version     Show the version of the Senzing_API.tgz package.
    version             Print the version of senzing-package.py.
    sleep               Do nothing but sleep. For Docker testing.
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

1. [Using Command Line](#using-command-line)
    1. [Install](#install)
    1. [Demonstrate](#demonstrate)
1. [Using Docker](#using-docker)
    1. [Expectations](#expectations)
    1. [Build docker image](#build-docker-image)
    1. [Configuration](#configuration)
    1. [Run docker container](#run-docker-container)
1. [Develop](#develop)
    1. [Prerequisite software](#prerequisite-software)
    1. [Clone repository](#clone-repository)
    1. [Downloads](#downloads)
    1. [Build docker image for development](#build-docker-image-for-development)
1. [Examples](#examples)
1. [Errors](#errors)

## Using Command Line

### Install

### Demonstrate

## Using Docker

### Expectations

#### Space

This repository and demonstration require 6 GB free disk space.

#### Time

Budget 40 minutes to get the demonstration up-and-running, depending on CPU and network speeds.

#### Background knowledge

This repository assumes a working knowledge of:

1. [Docker](https://github.com/Senzing/knowledge-base/blob/master/WHATIS/docker.md)

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

### Build docker image

See [Develop](#develop).

### Configuration

* **SENZING_DEBUG** -
  Enable debug information. Values: 0=no debug; 1=debug. Default: 0.
* **SENZING_DIR** -
  Path on the local system where
  [Senzing_API.tgz](https://s3.amazonaws.com/public-read-access/SenzingComDownloads/Senzing_API.tgz)
  has been extracted.
  Default: `/opt/senzing`
* **SENZING_PACKAGE** -
  Full path name to Senzing_API.tgz.  Default: `downloads/Senzing_API.tgz`.
* **SENZING_SLEEP_TIME_IN_SECONDS** -
  Number of seconds to sleep when using `sleep` subcommand.  Usually used for debugging.  Default: 0 (infinite).
* **SENZING_SUBCOMMAND** -
  Identify the subcommand to be run. See `senzing-package.py --help` for complete list.

1. To determine which configuration parameters are use for each `<subcommand>`, run:

    ```console
    ./senzing-package.py <subcommand> --help
    ```

### Run docker container

#### Demonstrate stand-alone

1. :pencil2: Set environment variables.  Example:

    ```console
    export SENZING_SUBCOMMAND=install
    export SENZING_DIR=/opt/senzing
    ```

1. Run the docker container.  Example:

    ```console
    sudo docker run \
      --env SENZING_SUBCOMMAND="${SENZING_SUBCOMMAND}" \
      --rm \
      --volume ${SENZING_DIR}:/opt/senzing \
      senzing/senzing-package
    ```

#### Demonstrate in docker-compose

1. :pencil2: Determine docker network.  Example:

    ```console
    sudo docker network ls

    # Choose value from NAME column of docker network ls
    export SENZING_NETWORK=nameofthe_network
    ```

1. :pencil2: Set environment variables.  Example:

    ```console
    export SENZING_SUBCOMMAND=install
    export SENZING_DIR=/opt/senzing
    ```

1. Run the docker container.  Example:

    ```console
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

1. Follow steps in [clone-repository](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/clone-repository.md) to install the Git repository.

1. After the repository has been cloned, be sure the following are set:

    ```console
    export GIT_ACCOUNT_DIR=~/${GIT_ACCOUNT}.git
    export GIT_REPOSITORY_DIR="${GIT_ACCOUNT_DIR}/${GIT_REPOSITORY}"
    ```

### Downloads

#### Download Senzing_API.tgz

1. Visit [Downloading Senzing_API.tgz](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/create-senzing-dir.md#downloading-senzing_apitgz)
1. Download `Senzing_API.tgz` to ${GIT_REPOSITORY_DIR}/[downloads](./downloads) directory.

#### Download ibm_data_server_driver_for_odbc_cli_linuxx64_v11.1.tar.gz

1. Visit [Download initial Version 11.1 clients and drivers](http://www-01.ibm.com/support/docview.wss?uid=swg21385217)
    1. Click on "[IBM Data Server Driver for ODBC and CLI (CLI Driver)](http://www.ibm.com/services/forms/preLogin.do?source=swg-idsoc97)" link.
    1. Select :radio_button:  "IBM Data Server Driver for ODBC and CLI (Linux AMD64 and Intel EM64T)"
    1. Click "Continue" button.
    1. Choose download method and click "Download now" button.
    1. Download `ibm_data_server_driver_for_odbc_cli_linuxx64_v11.1.tar.gz` to ${GIT_REPOSITORY_DIR}/[downloads](./downloads) directory.

#### Download v11.1.4fp4a_jdbc_sqlj.tar.gz

1. Visit [DB2 JDBC Driver Versions and Downloads](http://www-01.ibm.com/support/docview.wss?uid=swg21363866)
    1. In DB2 Version 11.1 > JDBC 3.0 Driver version, click on "3.72.52" link for "v11.1 M4 FP4 iFix1"
    1. Click on "DSClients--jdbc_sqlj-11.1.4.4-FP004a" link.
    1. Click on "v11.1.4fp4a_jdbc_sqlj.tar.gz" link to download.
    1. Download `v11.1.4fp4a_jdbc_sqlj.tar.gz` to ${GIT_REPOSITORY_DIR}/[downloads](./downloads) directory.

### Build docker image for development

1. Option #1 - Using docker command and local repository.

    ```console
    cd ${GIT_REPOSITORY_DIR}
    sudo docker build --tag senzing/senzing-package .
    ```

1. Option #2 - Using make command.

    ```console
    cd ${GIT_REPOSITORY_DIR}
    sudo make docker-build
    ```

    Note: `sudo make docker-build-base` can be used to create cached docker layers.

## Examples

## Errors

1. See [docs/errors.md](docs/errors.md).
