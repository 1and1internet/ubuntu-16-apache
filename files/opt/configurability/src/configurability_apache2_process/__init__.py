"""
Configurability script module: Process which configures apache2.

The process method

 -==========================================================================-
    Written for python 2.7 because it is included with Ubuntu 16.04 and I
      wanted to avoid requiring that python 3 also be installed.
 -==========================================================================-
"""

import os
import os.path
import logging
import re

# noinspection PyUnresolvedReferences
from configurability import custom_files

logger = logging.getLogger(__name__)


# noinspection PyBroadException,PyUnboundLocalVariable
def process(name, config, directory, config_translator=None):
    """
    Configures Apache 2 based on the input configuration.

    Supports Document Root and Gzip settings.

    :param name: Name of this section of the configuration
    :param config: The configuration dictionary for this section
    :param directory: The directory in which the input files are mounted
    :param config_translator: Optional callable method for preprocessing config items
    :return:
    """
    for required_key in [
        'configuration_file_name'
    ]:
        if required_key not in config:
            raise Exception(
                'Required key %s not present in %s section of internal configuration'
                % (name, required_key)
            )
    logger.info('Configuring %s' % name)

    try:
        custom_values, file_format = custom_files.read_custom_file(
            os.path.join(directory, config['configuration_file_name'])
        )
    except Exception as file_reading_exception:
        logger.error(str(file_reading_exception))  # don't log the full stack trace
        logger.info('Not configuring %s (not a critical failure)' % name)
        return  # abort but don't fail

    assert custom_values is not None and isinstance(custom_values, dict)

    if config_translator:
        for key, value in custom_values.iteritems():
            custom_values[key] = config_translator.process(key, value)

    apache2_directory = os.path.join('etc', 'apache2')

    sites_enabled_directory = os.path.join(apache2_directory, 'sites-enabled')
    conf_enabled_directory = os.path.join(apache2_directory, 'conf-enabled')
    mods_enabled_directory = os.path.join(apache2_directory, 'mods-enabled')

    document_root_key = 'DOCUMENT_ROOT'
    document_root_default = 'html'

    if document_root_key.lower() in custom_values:
        document_root = custom_values[document_root_key.lower()]

        document_root_path = os.path.join('var', 'www', document_root)
        if not os.path.exists(document_root_path):
            os.makedirs(document_root_path)

        regex = re.compile('\${?%s}?' % document_root_key)

        if os.environ.get(document_root_key, document_root_default) not in [document_root, document_root_default]:
            raise Exception('Legacy %s variable is present with a conflicting value' % document_root_key)

        #
        #  Update the on disk well known location so that other scripts
        #  which need to know the document root can look it up.
        #
        with open(os.path.join('etc', document_root_key), 'w') as file_handle:
            file_handle.write("%s\n" % document_root)

        #
        # Update the apache configuration
        #
        for target_directory in [sites_enabled_directory, conf_enabled_directory, mods_enabled_directory]:
            for file_path in os.listdir(target_directory):
                full_file_path = os.path.join(target_directory, file_path)
                if os.path.isfile(full_file_path):
                    write_needed = False
                    with open(full_file_path, 'r') as file_handle:
                        lines = file_handle.readlines()
                        for index, line in enumerate(lines):
                            lines[index] = regex.sub(document_root, lines[index])
                            write_needed = write_needed or lines[index] != line
                    if write_needed:
                        with open(full_file_path, 'w') as file_handle:
                            file_handle.writelines(lines)

        logger.info('%13s = %s' % (document_root_key, document_root))

    gzip_key = 'gzip'
    if gzip_key in custom_values:

        gzip = True

        if custom_values['gzip'].strip().upper() != 'OFF':
            gzip_level = custom_values[gzip_key]
        else:
            gzip = False

        #
        #  Update the apache configuration
        #
        for file_path in os.listdir(mods_enabled_directory):
            if file_path not in ['deflate.conf', 'deflate.load']:
                continue
            full_file_path = os.path.join(mods_enabled_directory, file_path)

            if not gzip:
                # Remove the configuration to disable gzip
                os.unlink(full_file_path)

            if gzip and file_path.endswith('.conf'):
                # Add the level directive to the bottom of the configuration
                with open(full_file_path, 'a') as file_handle:
                    file_handle.write(
                        "DeflateCompressionLevel %s\n" % gzip_level
                    )

        logger.info('%13s = %s' % (gzip_key.upper(), gzip_level))
