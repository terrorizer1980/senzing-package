#! /usr/bin/env python3

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
__updated__ = '2019-10-31'

SENZING_PRODUCT_ID = "5003"  # See https://github.com/Senzing/knowledge-base/blob/master/lists/senzing-product-ids.md
log_format = '%(asctime)s %(message)s'

# Working with bytes.

KILOBYTES = 1024
MEGABYTES = 1024 * KILOBYTES
GIGABYTES = 1024 * MEGABYTES

# The "configuration_locator" describes where configuration variables are in:
# 1) Command line options, 2) Environment variables, 3) Configuration files, 4) Default values

config = {}
configuration_locator = {
    "data_dir": {
        "default": "/opt/senzing/data",
        "env": "SENZING_DATA_DIR",
        "cli": "data-dir"
    },
    "debug": {
        "default": False,
        "env": "SENZING_DEBUG",
        "cli": "debug"
    },
    "g2_dir": {
        "default": "/opt/senzing/g2",
        "env": "SENZING_G2_DIR",
        "cli": "g2-dir"
    },
    "sleep_time_in_seconds": {
        "default": 0,
        "env": "SENZING_SLEEP_TIME_IN_SECONDS",
        "cli": "sleep-time-in-seconds"
    },
    "source_data_dir": {
        "default": "/opt/senzing-original/data/1.0.0",
        "env": "SENZING_SOURCE_DATA_DIR",
        "cli": "source-data-dir"
    },
    "source_g2_dir": {
        "default": "/opt/senzing-original/g2",
        "env": "SENZING_SOURCE_G2_DIR",
        "cli": "source-g2-dir"
    },
    "subcommand": {
        "default": None,
        "env": "SENZING_SUBCOMMAND",
    },
}

# Enumerate keys in 'configuration_locator' that should not be printed to the log.

keys_to_redact = [
    "password",
    ]

# -----------------------------------------------------------------------------
# Define argument parser
# -----------------------------------------------------------------------------


def get_parser():
    ''' Parse commandline arguments. '''

    subcommands = {
        'install': {
            "help": 'Example task #1.',
            "arguments": {
                "--debug": {
                    "dest": "debug",
                    "action": "store_true",
                    "help": "Enable debugging. (SENZING_DEBUG) Default: False"
                },
            },
        },
        'sleep': {
            "help": 'Do nothing but sleep. For Docker testing.',
            "arguments": {
                "--sleep-time-in-seconds": {
                    "dest": "sleep_time_in_seconds",
                    "metavar": "SENZING_SLEEP_TIME_IN_SECONDS",
                    "help": "Sleep time in seconds. DEFAULT: 0 (infinite)"
                },
            },
        },
        'version': {
            "help": 'Print version of program.',
        },
        'docker-acceptance-test': {
            "help": 'For Docker acceptance testing.',
        },
    }

    parser = argparse.ArgumentParser(prog="python-template.py", description="Example python skeleton. For more information, see https://github.com/Senzing/python-template")
    subparsers = parser.add_subparsers(dest='subcommand', help='Subcommands (SENZING_SUBCOMMAND):')

    for subcommand_key, subcommand_values in subcommands.items():
        subcommand_help = subcommand_values.get('help', "")
        subcommand_arguments = subcommand_values.get('arguments', {})
        subparser = subparsers.add_parser(subcommand_key, help=subcommand_help)
        for argument_key, argument_values in subcommand_arguments.items():
            subparser.add_argument(argument_key, **argument_values)

    return parser

# -----------------------------------------------------------------------------
# Message handling
# -----------------------------------------------------------------------------

# 1xx Informational (i.e. logging.info())
# 3xx Warning (i.e. logging.warning())
# 5xx User configuration issues (either logging.warning() or logging.err() for Client errors)
# 7xx Internal error (i.e. logging.error for Server errors)
# 9xx Debugging (i.e. logging.debug())


MESSAGE_INFO = 100
MESSAGE_WARN = 300
MESSAGE_ERROR = 700
MESSAGE_DEBUG = 900

message_dictionary = {
    "100": "senzing-" + SENZING_PRODUCT_ID + "{0:04d}I",
    "130": "Version {0} detected in {1}.",
    "131": "Version {0} detected in Senzing package '{1}'.",
    "132": "Archived {0} to {1}",
    "133": "{0} extracted to {1}",
    "134": "Deleting {0} at version {1}.",
    "135": "{0} deleted.",
    "136": "{0} copied to {1}.",
    "137": "{0} does not exist.",
    "292": "Configuration change detected.  Old: {0} New: {1}",
    "293": "For information on warnings and errors, see https://github.com/Senzing/stream-loader#errors",
    "294": "Version: {0}  Updated: {1}",
    "295": "Sleeping infinitely.",
    "296": "Sleeping {0} seconds.",
    "297": "Enter {0}",
    "298": "Exit {0}",
    "299": "{0}",
    "300": "senzing-" + SENZING_PRODUCT_ID + "{0:04d}W",
    "301": "Cannot determine version. {0} does not exist.",
    "302": "Cannot move {0} to {1}.",
    "303": "Cannot extract {0} to {1}.",
    "304": "Cannot copy {0} to {1}.",

    "499": "{0}",
    "500": "senzing-" + SENZING_PRODUCT_ID + "{0:04d}E",
    "695": "Unknown database scheme '{0}' in database url '{1}'",
    "696": "Bad SENZING_SUBCOMMAND: {0}.",
    "697": "No processing done.",
    "698": "Program terminated with error.",
    "699": "{0}",
    "700": "senzing-" + SENZING_PRODUCT_ID + "{0:04d}E",
    "885": "License has expired.",
    "886": "G2Engine.addRecord() bad return code: {0}; JSON: {1}",
    "888": "G2Engine.addRecord() G2ModuleNotInitialized: {0}; JSON: {1}",
    "889": "G2Engine.addRecord() G2ModuleGenericException: {0}; JSON: {1}",
    "890": "G2Engine.addRecord() Exception: {0}; JSON: {1}",
    "891": "Original and new database URLs do not match. Original URL: {0}; Reconstructed URL: {1}",
    "892": "Could not initialize G2Product with '{0}'. Error: {1}",
    "893": "Could not initialize G2Hasher with '{0}'. Error: {1}",
    "894": "Could not initialize G2Diagnostic with '{0}'. Error: {1}",
    "895": "Could not initialize G2Audit with '{0}'. Error: {1}",
    "896": "Could not initialize G2ConfigMgr with '{0}'. Error: {1}",
    "897": "Could not initialize G2Config with '{0}'. Error: {1}",
    "898": "Could not initialize G2Engine with '{0}'. Error: {1}",
    "899": "{0}",
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
    return message_generic(MESSAGE_INFO, index, *args)


def message_warning(index, *args):
    return message_generic(MESSAGE_WARN, index, *args)


def message_error(index, *args):
    return message_generic(MESSAGE_ERROR, index, *args)


def message_debug(index, *args):
    return message_generic(MESSAGE_DEBUG, index, *args)


def get_exception():
    ''' Get details about an exception. '''
    exception_type, exception_object, traceback = sys.exc_info()
    frame = traceback.tb_frame
    line_number = traceback.tb_lineno
    filename = frame.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, line_number, frame.f_globals)
    return {
        "filename": filename,
        "line_number": line_number,
        "line": line.strip(),
        "exception": exception_object,
        "type": exception_type,
        "traceback": traceback,
    }

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------


def get_configuration(args):
    ''' Order of precedence: CLI, OS environment variables, INI file, default. '''
    result = {}

    # Copy default values into configuration dictionary.

    for key, value in list(configuration_locator.items()):
        result[key] = value.get('default', None)

    # "Prime the pump" with command line args. This will be done again as the last step.

    for key, value in list(args.__dict__.items()):
        new_key = key.format(subcommand.replace('-', '_'))
        if value:
            result[new_key] = value

    # Copy OS environment variables into configuration dictionary.

    for key, value in list(configuration_locator.items()):
        os_env_var = value.get('env', None)
        if os_env_var:
            os_env_value = os.getenv(os_env_var, None)
            if os_env_value:
                result[key] = os_env_value

    # Copy 'args' into configuration dictionary.

    for key, value in list(args.__dict__.items()):
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

    booleans = [
        'debug'
    ]
    for boolean in booleans:
        boolean_value = result.get(boolean)
        if isinstance(boolean_value, str):
            boolean_value_lower_case = boolean_value.lower()
            if boolean_value_lower_case in ['true', '1', 't', 'y', 'yes']:
                result[boolean] = True
            else:
                result[boolean] = False

    # Special case: Change integer strings to integers.

    integers = [
        'sleep_time_in_seconds'
    ]
    for integer in integers:
        integer_string = result.get(integer)
        result[integer] = int(integer_string)

    return result


def validate_configuration(config):
    ''' Check aggregate configuration from commandline options, environment variables, config files, and defaults. '''

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
        logging.warning(user_warning_message)

    # Log error messages.

    for user_error_message in user_error_messages:
        logging.error(user_error_message)

    # Log where to go for help.

    if len(user_warning_messages) > 0 or len(user_error_messages) > 0:
        logging.info(message_info(293))

    # If there are error messages, exit.

    if len(user_error_messages) > 0:
        exit_error(697)


def redact_configuration(config):
    ''' Return a shallow copy of config with certain keys removed. '''
    result = config.copy()
    for key in keys_to_redact:
        try:
            result.pop(key)
        except:
            pass
    return result

# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------


def create_signal_handler_function(args):
    ''' Tricky code.  Uses currying technique. Create a function for signal handling.
        that knows about "args".
    '''

    def result_function(signal_number, frame):
        logging.info(message_info(298, args))
        sys.exit(0)

    return result_function


def bootstrap_signal_handler(signal, frame):
    sys.exit(0)


def entry_template(config):
    ''' Format of entry message. '''
    debug = config.get("debug", False)
    config['start_time'] = time.time()
    if debug:
        final_config = config
    else:
        final_config = redact_configuration(config)
    config_json = json.dumps(final_config, sort_keys=True)
    return message_info(297, config_json)


def exit_template(config):
    ''' Format of exit message. '''
    debug = config.get("debug", False)
    stop_time = time.time()
    config['stop_time'] = stop_time
    config['elapsed_time'] = stop_time - config.get('start_time', stop_time)
    if debug:
        final_config = config
    else:
        final_config = redact_configuration(config)
    config_json = json.dumps(final_config, sort_keys=True)
    return message_info(298, config_json)


def exit_error(index, *args):
    ''' Log error message and exit program. '''
    logging.error(message_error(index, *args))
    logging.error(message_error(698))
    sys.exit(1)


def exit_silently():
    ''' Exit program. '''
    sys.exit(0)


def get_config():
    return config

# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------


def XX_common_prolog(config):
    '''Common steps for most do_* functions.'''
    validate_configuration(config)
    logging.info(entry_template(config))


def XX_delete_sentinel_files(config):
    '''Delete the sentinel file used to signal that processing was done.'''
    senzing_dir = config.get('senzing_dir')
    files = [
        "{0}/docker-runs.sentinel".format(senzing_dir),
        "{0}/mysql-init.sentinel".format(senzing_dir)
    ]

    # Delete files.

    for file in files:
        try:
            os.remove(file)
            logging.info(message_info(135, senzing_g2_dir))
        except:
            pass


def XX_file_ownership(config):
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


def XX_get_installed_version(config):
    '''Get version of Senzing seen in senzing_dir.'''
    result = None
    senzing_dir = config.get('senzing_dir')
    version_file = "{0}/g2/data/g2BuildVersion.json".format(senzing_dir)

    # Read version file.

    try:
        with open(version_file) as version_json_file:
            version_dictionary = json.load(version_json_file)
            result = version_dictionary.get('VERSION')
            logging.info(message_info(130, result, version_file))
    except:
        logging.info(message_warn(301, version_file))

    return result


def XX_get_senzing_directories(config):
    '''Get directories within /opt/senzing.'''
    senzing_dir = config.get('senzing_dir')
    return [
        "{0}/g2".format(senzing_dir),
        "{0}/db2".format(senzing_dir)
    ]

# -----------------------------------------------------------------------------
# Archive functions
# -----------------------------------------------------------------------------


def XX_archive_path(source, installed_version):
    '''Move source to a backup path.'''

    # Construct backup name.

    target = source
    if installed_version:
        target = "{0}-{1}".format(target, installed_version)
    target = "{0}.{1}".format(target, int(time.time()))

    # Move path.

    try:
        shutil.move(source, target)
        logging.info(message_info(132, source, target))
    except:
        logging.info(message_warn(302, source, target))


def XX_archive_paths(config):
    '''Archive all paths by moving to a new pathname.
       Note: Can't just archive senzing_dir (/opt/senzing)
       because it may be an attached volume in a docker image.
    '''

    # Synthesize variables.

    installed_version = get_installed_version(config)
    senzing_directories = get_senzing_directories(config)

    # Archive paths.

    for senzing_directory in senzing_directories:
        if os.path.exists(senzing_directory):
            archive_path(senzing_directory, installed_version)

# -----------------------------------------------------------------------------
# Install functions
# -----------------------------------------------------------------------------


def copy_directory(config, manifest):
    '''Extract a TGZ file.'''
    source = manifest.get("source")
    target = manifest.get("target")

    try:
        shutil.copytree(source, target, symlinks=True)
        logging.info(message_info(136, source, target))
    except:
        logging.info(message_warn(304, source, target))


def XX_install_tgz(config, manifest):
    '''Extract a TGZ file.'''
    source = manifest.get("source")
    target = manifest.get("target")
    try:
        with tarfile.open(source) as compressed_file:
            compressed_file.extractall(path=target)
            logging.info(message_info(133, source, target))
    except:
        logging.info(message_warn(303, source, target))


def XX_install_file(config, manifest):
    '''Install single file.  But first, backup original file.'''
    source = manifest.get("source")
    target = manifest.get("target")
    target_backup = "{0}.{1}".format(target, int(time.time()))
    try:
        shutil.move(target, target_backup)
        logging.info(message_info(132, target, target_backup))
        shutil.copyfile(source, target)
        logging.info(message_info(136, source, target))
    except:
        logging.info(message_warn(304, source, target))


def XX_install_zip(config, manifest):
    '''Extract a ZIP file.'''
    source = manifest.get("source")
    target = manifest.get("target")
    try:
        with zipfile.ZipFile(source, 'r') as compressed_file:
            compressed_file.extractall(target)
            logging.info(message_info(133, source, target))
    except:
        logging.info(message_warn(303, source, target))


def XX_install_files(config):
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
            logging.info(message_info(137, source))


def XX_delete_files(config):
    '''Delete all files by removing directories trees.'''
    installed_version = get_installed_version(config)
    senzing_directories = get_senzing_directories(config)
    for senzing_directory in senzing_directories:
        if os.path.exists(senzing_directory):
            logging.info(message_info(134, senzing_directory, installed_version))
            shutil.rmtree(senzing_directory)
            logging.info(message_info(135, senzing_directory))

# -----------------------------------------------------------------------------
# do_* functions
#   Common function signature: do_XXX(args)
# -----------------------------------------------------------------------------


def do_docker_acceptance_test(args):
    ''' For use with Docker acceptance testing. '''

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

    source_data_dir = config.get('data_dir')
    target_data_dir = config.get('source_data_dir')
    source_g2_dir = config.get('source_g2_dir')
    target_g2_dir = config.get('g2_dir')

    # Prolog.

    validate_configuration(config)
    logging.info(entry_template(config))

    # Perform action.

    source = "/opt/senzing-original/data/1.0.0"
    target = "/opt/senzing/data"
    try:
        shutil.copytree(source, target, symlinks=True)
        logging.info(message_info(136, source, target))
    except:
        logging.info(message_warn(304, source, target))

    source = "/opt/senzing-original/g2"
    target = "/opt/senzing/g2"
    try:
        shutil.copytree(source, target, symlinks=True)
        logging.info(message_info(136, source, target))
    except:
        logging.info(message_warn(304, source, target))

    # Epilog.

    logging.info(exit_template(config))


def do_sleep(args):
    ''' Sleep.  Used for debugging. '''

    # Get context from CLI, environment variables, and ini files.

    config = get_configuration(args)

    # Prolog.

    logging.info(entry_template(config))

    # Pull values from configuration.

    sleep_time_in_seconds = config.get('sleep_time_in_seconds')

    # Sleep.

    if sleep_time_in_seconds > 0:
        logging.info(message_info(296, sleep_time_in_seconds))
        time.sleep(sleep_time_in_seconds)

    else:
        sleep_time_in_seconds = 3600
        while True:
            logging.info(message_info(295))
            time.sleep(sleep_time_in_seconds)

    # Epilog.

    logging.info(exit_template(config))


def do_version(args):
    ''' Log version information. '''

    logging.info(message_info(294, __version__, __updated__))

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
        logging.warning(message_warning(596, subcommand))
        parser.print_help()
        exit_silently()

    # Tricky code for calling function based on string.

    globals()[subcommand_function_name](args)
