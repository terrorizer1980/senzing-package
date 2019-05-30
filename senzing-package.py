#! /usr/bin/env python

# -----------------------------------------------------------------------------
# senzing-package.py handles installation of the Senzing package.
# -----------------------------------------------------------------------------

import argparse
import grp
import json
import logging
import os
import pwd
import shutil
import signal
import sys
import tarfile
import time
import zipfile

__all__ = []
__version__ = "1.0.0"  # See https://www.python.org/dev/peps/pep-0396/
__date__ = '2019-03-27'
__updated__ = '2019-05-29'

SENZING_PRODUCT_ID = "5003"  # See https://github.com/Senzing/knowledge-base/blob/master/lists/senzing-product-ids.md
log_format = '%(asctime)s %(message)s'

# Working with bytes.

KILOBYTES = 1024
MEGABYTES = 1024 * KILOBYTES
GIGABYTES = 1024 * MEGABYTES

# The "configuration_locator" describes where configuration variables are in:
# 1) Command line options, 2) Environment variables, 3) Configuration files, 4) Default values

configuration_locator = {
    "debug": {
        "default": False,
        "env": "SENZING_DEBUG",
        "cli": "debug"
    },
    "full_db2_client": {
        "default": False,
        "env": "SENZING_FULL_DB2_CLIENT",
        "cli": "full-db2-client"
    },
    "senzing_dir": {
        "default": "/opt/senzing",
        "env": "SENZING_DIR",
        "cli": "senzing-dir"
    },
    "senzing_package": {
        "default": "downloads/Senzing_API.tgz",
        "env": "SENZING_PACKAGE",
        "cli": "senzing-package"
    },
    "sleep_time": {
        "default": 0,
        "env": "SENZING_SLEEP_TIME",
        "cli": "sleep-time"
    },
    "subcommand": {
        "default": None,
        "env": "SENZING_SUBCOMMAND",
    }
}

# -----------------------------------------------------------------------------
# Define argument parser
# -----------------------------------------------------------------------------


def get_parser():
    '''Parse commandline arguments.'''
    parser = argparse.ArgumentParser(prog="senzing-package.py", description="Senzing package management. For more information, see https://github.com/senzing/senzing-package")
    subparsers = parser.add_subparsers(dest='subcommand', help='Subcommands (SENZING_SUBCOMMAND):')

    subparser_1 = subparsers.add_parser('version', help='Print the version of senzing-package.py.')

    subparser_2 = subparsers.add_parser('sleep', help='Do nothing but sleep. For Docker testing.')
    subparser_2.add_argument("--sleep-time", dest="sleep_time", metavar="SENZING_SLEEP_TIME", help="Sleep time in seconds. DEFAULT: 0 (infinite)")

    subparser_3 = subparsers.add_parser('current-version', help='Show the version of the currently installed Senzing package.')
    subparser_3.add_argument("--senzing-dir", dest="senzing_dir", metavar="SENZING_DIR", help="Senzing directory.  DEFAULT: /opt/senzing")
    subparser_3.add_argument("--debug", dest="debug", action="store_true", help="Enable debugging. (SENZING_DEBUG) Default: False")

    subparser_4 = subparsers.add_parser('package-version', help='Show the version of the Senzing_API.tgz package.')
    subparser_4.add_argument("--senzing-package", dest="senzing_package", metavar="SENZING_PACKAGE", help="Path to Senzing package.  DEFAULT: downloads/Senzing_API.tgz")
    subparser_4.add_argument("--debug", dest="debug", action="store_true", help="Enable debugging. (SENZING_DEBUG) Default: False")

    subparser_5 = subparsers.add_parser('install', help='Backup existing directory and install to a clean directory.')
    subparser_5.add_argument("--senzing-dir", dest="senzing_dir", metavar="SENZING_DIR", help="Senzing directory.  DEFAULT: /opt/senzing")
    subparser_5.add_argument("--senzing-package", dest="senzing_package", metavar="SENZING_PACKAGE", help="Path to Senzing package.  DEFAULT: downloads/Senzing_API.tgz")
    subparser_5.add_argument("--full-db2-client", dest="full_db2_client", action="store_true", help="Include entire DB2 client. (SENZING_FULL_DB2_CLIENT) Default: False")
    subparser_5.add_argument("--debug", dest="debug", action="store_true", help="Enable debugging. (SENZING_DEBUG) Default: False")

    subparser_6 = subparsers.add_parser('delete', help='Delete existing directory.')
    subparser_6.add_argument("--senzing-dir", dest="senzing_dir", metavar="SENZING_DIR", help="Senzing directory.  DEFAULT: /opt/senzing")
    subparser_6.add_argument("--debug", dest="debug", action="store_true", help="Enable debugging. (SENZING_DEBUG) Default: False")

    subparser_7 = subparsers.add_parser('replace', help='Delete existing directory and install to a clean directory.')
    subparser_7.add_argument("--senzing-dir", dest="senzing_dir", metavar="SENZING_DIR", help="Senzing directory.  DEFAULT: /opt/senzing")
    subparser_7.add_argument("--senzing-package", dest="senzing_package", metavar="SENZING_PACKAGE", help="Path to Senzing package.  DEFAULT: downloads/Senzing_API.tgz")
    subparser_7.add_argument("--full-db2-client", dest="full_db2_client", action="store_true", help="Include entire DB2 client. (SENZING_FULL_DB2_CLIENT) Default: False")
    subparser_7.add_argument("--debug", dest="debug", action="store_true", help="Enable debugging. (SENZING_DEBUG) Default: False")

    subparser_10 = subparsers.add_parser('docker-acceptance-test', help='For Docker acceptance testing.')

    return parser

# -----------------------------------------------------------------------------
# Message handling
# -----------------------------------------------------------------------------

# 1xx Informational (i.e. logging.info())
# 2xx Warning (i.e. logging.warn())
# 4xx User configuration issues (either logging.warn() or logging.err() for Client errors)
# 5xx Internal error (i.e. logging.error for Server errors)
# 9xx Debugging (i.e. logging.debug())


message_dictionary = {
    "100": "senzing-" + SENZING_PRODUCT_ID + "{0:04d}I",
    "101": "Enter {0}",
    "102": "Exit {0}",
    "103": "Version: {0}  Updated: {1}",
    "104": "Sleeping {0} seconds.",
    "105": "Version {0} detected in {1}.",
    "106": "Version {0} detected in Senzing package '{1}'.",
    "107": "Archived {0} to {1}",
    "108": "{0} extracted to {1}",
    "109": "Deleting {0} at version {1}.",
    "110": "{0} deleted.",
    "111": "{0} copied to {1}.",
    "112": "{0} does not exist.",
    "131": "Sleeping infinitely.",
    "198": "For information on warnings and errors, see https://github.com/Senzing/stream-loader#errors",
    "199": "{0}",
    "200": "senzing-" + SENZING_PRODUCT_ID + "{0:04d}W",
    "201": "Cannot determine version. {0} does not exist.",
    "202": "Cannot move {0} to {1}.",
    "203": "Cannot extract {0} to {1}.",
    "204": "Cannot copy {0} to {1}.",
    "205": "Cannot extract {0}.",
    "206": "Cannot copy {0}.",
    "400": "senzing-" + SENZING_PRODUCT_ID + "{0:04d}E",
    "498": "Bad SENZING_SUBCOMMAND: {0}.",
    "499": "No processing done.",
    "500": "senzing-" + SENZING_PRODUCT_ID + "{0:04d}E",
    "501": "Error: {0} for {1}",
    "599": "Program terminated with error.",
    "900": "senzing-" + SENZING_PRODUCT_ID + "{0:04d}D",
    "999": "{0}",
}


def message(index, *args):
    index_string = str(index)
    template = message_dictionary.get(index_string, "No message for index {0}.".format(index_string))
    return template.format(*args)


def message_generic(generic_index, index, *args):
    index_string = str(index)
    return "{0} {1}".format(message(generic_index, index), message(index, *args))


def message_info(index, *args):
    return message_generic(100, index, *args)


def message_warn(index, *args):
    return message_generic(200, index, *args)


def message_error(index, *args):
    return message_generic(500, index, *args)


def message_debug(index, *args):
    return message_generic(900, index, *args)

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------


def get_configuration(args):
    ''' Order of precedence: CLI, OS environment variables, INI file, default.'''
    result = {}

    # Copy default values into configuration dictionary.

    for key, value in configuration_locator.items():
        result[key] = value.get('default', None)

    # "Prime the pump" with command line args. This will be done again as the last step.

    for key, value in args.__dict__.items():
        new_key = key.format(subcommand.replace('-', '_'))
        if value:
            result[new_key] = value

    # Copy OS environment variables into configuration dictionary.

    for key, value in configuration_locator.items():
        os_env_var = value.get('env', None)
        if os_env_var:
            os_env_value = os.getenv(os_env_var, None)
            if os_env_value:
                result[key] = os_env_value

    # Copy 'args' into configuration dictionary.

    for key, value in args.__dict__.items():
        new_key = key.format(subcommand.replace('-', '_'))
        if value:
            result[new_key] = value

    # Special case: Remove variable of less priority.

    if result.get('project_filespec') and result.get('project_filename'):
        result.pop('project_filename')  # Remove key

    # Special case: subcommand from command-line

    if args.subcommand:
        result['subcommand'] = args.subcommand

    # Special case: Change boolean strings to booleans.

    booleans = ['debug']
    for boolean in booleans:
        boolean_value = result.get(boolean)
        if isinstance(boolean_value, str):
            boolean_value_lower_case = boolean_value.lower()
            if boolean_value_lower_case in ['true', '1', 't', 'y', 'yes']:
                result[boolean] = True
            else:
                result[boolean] = False

    # Special case: Change integer strings to integers.

    integers = ['sleep_time']
    for integer in integers:
        integer_string = result.get(integer)
        result[integer] = int(integer_string)

    return result


def validate_configuration(config):
    '''Check aggregate configuration from commandline options, environment variables, config files, and defaults.'''

    user_warning_messages = []
    user_error_messages = []

#     if not config.get('g2_database_url'):
#         user_error_messages.append(message_error(401))

    # Perform subcommand specific checking.

    subcommand = config.get('subcommand')

    if subcommand in ['XXX', 'YYY', 'ZZZ']:

        if not config.get('ld_library_path'):
            user_error_messages.append(message_error(414))

    # Log warning messages.

    for user_warning_message in user_warning_messages:
        logging.warn(user_warning_message)

    # Log error messages.

    for user_error_message in user_error_messages:
        logging.error(user_error_message)

    # Log where to go for help.

    if len(user_warning_messages) > 0 or len(user_error_messages) > 0:
        logging.info(message_info(198))

    # If there are error messages, exit.

    if len(user_error_messages) > 0:
        exit_error(499)

# -----------------------------------------------------------------------------
# Archive functions
# -----------------------------------------------------------------------------


def archive_path(source, current_version):
    '''Move source to a backup path.'''

    # Construct backup name.

    target = source
    if current_version:
        target = "{0}-{1}".format(target, current_version)
    target = "{0}.{1}".format(target, int(time.time()))

    # Move path.

    try:
        shutil.move(source, target)
        logging.info(message_info(107, source, target))
    except:
        logging.info(message_warn(202, source, target))


def archive_paths(config):
    '''Archive all paths by moving to a new pathname.
       Note: Can't just archive senzing_dir (/opt/senzing)
       because it may be an attached volume in a docker image.
    '''

    # Synthesize variables.

    current_version = get_current_version(config)
    senzing_directories = get_senzing_directories(config)

    # Archive paths.

    for senzing_directory in senzing_directories:
        if os.path.exists(senzing_directory):
            archive_path(senzing_directory, current_version)

# -----------------------------------------------------------------------------
# Install functions
# -----------------------------------------------------------------------------


def copy_directory(config, manifest):
    '''Extract a TGZ file.'''
    source = manifest.get("source")
    target = manifest.get("target")

    try:
        shutil.copytree(source, target, symlinks=True)
        logging.info(message_info(111, source, target))
    except:
        logging.info(message_warn(204, source, target))


def install_tgz(config, manifest):
    '''Extract a TGZ file.'''
    source = manifest.get("source")
    target = manifest.get("target")
    try:
        with tarfile.open(source) as compressed_file:
            compressed_file.extractall(path=target)
            logging.info(message_info(108, source, target))
    except:
        logging.info(message_warn(203, source, target))


def install_file(config, manifest):
    '''Install single file.  But first, backup original file.'''
    source = manifest.get("source")
    target = manifest.get("target")
    target_backup = "{0}.{1}".format(target, int(time.time()))
    try:
        shutil.move(target, target_backup)
        logging.info(message_info(107, target, target_backup))
        shutil.copyfile(source, target)
        logging.info(message_info(111, source, target))
    except:
        logging.info(message_warn(204, source, target))


def install_zip(config, manifest):
    '''Extract a ZIP file.'''
    source = manifest.get("source")
    target = manifest.get("target")
    try:
        with zipfile.ZipFile(source, 'r') as compressed_file:
            compressed_file.extractall(target)
            logging.info(message_info(108, source, target))
    except:
        logging.info(message_warn(203, source, target))


def install_files(config):
    '''Install all files based on what is in the 'downloads' directory.'''

    senzing_dir = config.get('senzing_dir')
    manifests = [
        {
            'source': config.get('senzing_package'),
            'target': senzing_dir,
            'function': install_tgz
        }, {
            'source': "/opt/IBM/db2",
            'target': "{0}/db2".format(senzing_dir),
            'function': copy_directory
        }
    ]

    # Tricky code. The function called is specified in the manifest.

    for manifest in manifests:
        source = manifest.get("source")
        if os.path.exists(source):
            manifest.get("function")(config, manifest)
        else:
            logging.info(message_info(112, source))


def delete_files(config):
    '''Delete all files by removing directories trees.'''
    current_version = get_current_version(config)
    senzing_directories = get_senzing_directories(config)
    for senzing_directory in senzing_directories:
        if os.path.exists(senzing_directory):
            logging.info(message_info(109, senzing_directory, current_version))
            shutil.rmtree(senzing_directory)
            logging.info(message_info(110, senzing_directory))

# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------


def bootstrap_signal_handler(signal, frame):
    sys.exit(0)


def create_signal_handler_function(args):
    '''Tricky code.  Uses currying technique. Create a function for signal handling.
       that knows about "args".
    '''

    def result_function(signal_number, frame):
        logging.info(message_info(102, args))
        sys.exit(0)

    return result_function


def delete_sentinal_files(config):
    '''Delete the sentinal file used to signal that processing was done.'''
    senzing_dir = config.get('senzing_dir')
    files = [
        "{0}/docker-runs.sentinel".format(senzing_dir)
    ]

    # Delete files.

    for file in files:
        try:
            os.remove(file)
            logging.info(message_info(110, senzing_g2_dir))
        except:
            pass


def entry_template(config):
    '''Format of entry message.'''
    config['start_time'] = time.time()

    # FIXME: Redact sensitive info:  Example: database password.

    config_json = json.dumps(config, sort_keys=True)
    return message_info(101, config_json)


def exit_template(config):
    '''Format of exit message.'''
    stop_time = time.time()
    config['stop_time'] = stop_time
    config['elapsed_time'] = stop_time - config.get('start_time', stop_time)

    # FIXME: Redact sensitive info:  Example: database password.

    config_json = json.dumps(config, sort_keys=True)
    return message_info(102, config_json)


def exit_error(index, *args):
    '''Log error message and exit program.'''
    logging.error(message_error(index, *args))
    logging.error(message_error(599))
    sys.exit(1)


def exit_silently():
    '''Exit program.'''
    sys.exit(0)


def file_ownership(config):
    '''Modify file ownership (i.e. chown).'''
    senzing_dir = config.get('senzing_dir')

    # Determine ownership of senzing_dir.

    stat_info = os.stat(senzing_dir)
    user_id = stat_info.st_uid
    group_id = stat_info.st_gid

    # Adjust file ownership.

    senzing_directories = get_senzing_directories(config)
    for senzing_directory in senzing_directories:
        for dirpath, dirnames, filenames in os.walk(senzing_directory):
            for dname in dirnames:
                try:
                    os.chown(os.path.join(dirpath, dname), user_id, group_id)
                except:
                    continue
            for fname in filenames:
                try:
                    os.chown(os.path.join(dirpath, fname), user_id, group_id)
                except:
                    continue


def get_current_version(config):
    '''Get version of Senzing seen in senzing_dir.'''
    result = None
    senzing_dir = config.get('senzing_dir')
    version_file = "{0}/g2/data/g2BuildVersion.json".format(senzing_dir)

    # Read version file.

    try:
        with open(version_file) as version_json_file:
            version_dictionary = json.load(version_json_file)
            result = version_dictionary.get('VERSION')
            logging.info(message_info(105, result, version_file))
    except:
        logging.info(message_warn(201, version_file))

    return result


def get_senzing_directories(config):
    '''Get directories within /opt/senzing.'''
    senzing_dir = config.get('senzing_dir')
    return [
        "{0}/g2".format(senzing_dir),
        "{0}/db2".format(senzing_dir)
    ]


def common_prolog(config):
    '''Common steps for most do_* functions.'''
    validate_configuration(config)
    logging.info(entry_template(config))

# -----------------------------------------------------------------------------
# do_* functions
#   Common function signature: do_XXX(args)
# -----------------------------------------------------------------------------


def do_current_version(args):
    '''Get current version of Senzing API.'''

    # Get context from CLI, environment variables, and ini files.

    config = get_configuration(args)

    # Prolog.

    common_prolog(config)

    # Perform action.

    get_current_version(config)

    # Epilog.

    logging.info(exit_template(config))


def do_delete(args):
    '''Delete the installed Senzing_API.tgz .'''

    # Get context from CLI, environment variables, and ini files.

    config = get_configuration(args)

    # Prolog.

    common_prolog(config)

    # Perform action.

    delete_files(config)
    delete_sentinal_files(config)

    # Epilog.

    logging.info(exit_template(config))


def do_docker_acceptance_test(args):
    '''Sleep.'''

    # Get context from CLI, environment variables, and ini files.

    config = get_configuration(args)

    # Prolog.

    logging.info(entry_template(config))

    # Epilog.

    logging.info(exit_template(config))


def do_install(args):
    '''Install Senzing_API.tgz package. Backup existing version.'''

    # Get context from CLI, environment variables, and ini files.

    config = get_configuration(args)

    # Prolog.

    common_prolog(config)

    # Perform action.

    archive_paths(config)
    delete_sentinal_files(config)
    install_files(config)
    file_ownership(config)

    # Epilog.

    logging.info(exit_template(config))


def do_package_version(args):
    '''Get version in Senzing_API.tgz package.'''

    # Get context from CLI, environment variables, and ini files.

    config = get_configuration(args)

    # Prolog.

    common_prolog(config)

    # Pull values from configuration.

    senzing_package = config.get('senzing_package')

    # Synthesize variables

    version_file = "g2/data/g2BuildVersion.json"

    # Read version file in tarball.

    try:
        with tarfile.open(senzing_package) as senzing_package_file:
            version_json_file = senzing_package_file.extractfile(version_file)
            version_dictionary = json.load(version_json_file)
            logging.info(message_info(106, version_dictionary.get('VERSION'), senzing_package))

    except:
        logging.info(message_warn(201, senzing_package))

    # Epilog.

    logging.info(exit_template(config))


def do_replace(args):
    '''Install Senzing_API.tgz package. Do not backup existing version.'''

    # Get context from CLI, environment variables, and ini files.

    config = get_configuration(args)

    # Prolog.

    common_prolog(config)

    # Perform action.

    delete_files(config)
    delete_sentinal_files(config)
    install_files(config)
    file_ownership(config)

    # Epilog.

    logging.info(exit_template(config))


def do_sleep(args):
    '''Sleep.  Used for debugging.'''

    # Get context from CLI, environment variables, and ini files.

    config = get_configuration(args)

    # Prolog.

    logging.info(entry_template(config))

    # Pull values from configuration.

    sleep_time = config.get('sleep_time')

    # Sleep

    if sleep_time > 0:
        logging.info(message_info(104, sleep_time))
        time.sleep(sleep_time)

    else:
        sleep_time = 3600
        while True:
            logging.info(message_info(131))
            time.sleep(sleep_time)

    # Epilog.

    logging.info(exit_template(config))


def do_version(args):
    '''Log version information.'''

    logging.info(message_info(103, __version__, __updated__))

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


if __name__ == "__main__":

    # Configure logging. See https://docs.python.org/2/library/logging.html#levels

    log_level_map = {
        "notset": logging.NOTSET,
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "fatal": logging.FATAL,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }

    log_level_parameter = os.getenv("SENZING_LOG_LEVEL", "info").lower()
    log_level = log_level_map.get(log_level_parameter, logging.INFO)
    logging.basicConfig(format=log_format, level=log_level)

    # Trap signals temporarily until args are parsed.

    signal.signal(signal.SIGTERM, bootstrap_signal_handler)
    signal.signal(signal.SIGINT, bootstrap_signal_handler)

    # Parse the command line arguments.

    subcommand = os.getenv("SENZING_SUBCOMMAND", None)
    parser = get_parser()
    if len(sys.argv) > 1:
        args = parser.parse_args()
        subcommand = args.subcommand
    elif subcommand:
        args = argparse.Namespace(subcommand=subcommand)
    else:
        parser.print_help()
        if len(os.getenv("SENZING_DOCKER_LAUNCHED", "")):
            subcommand = "sleep"
            args = argparse.Namespace(subcommand=subcommand)
            do_sleep(args)
        exit_silently()

    # Catch interrupts. Tricky code: Uses currying.

    signal_handler = create_signal_handler_function(args)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Transform subcommand from CLI parameter to function name string.

    subcommand_function_name = "do_{0}".format(subcommand.replace('-', '_'))

    # Test to see if function exists in the code.

    if subcommand_function_name not in globals():
        logging.warn(message_warn(498, subcommand))
        parser.print_help()
        exit_silently()

    # Tricky code for calling function based on string.

    globals()[subcommand_function_name](args)
