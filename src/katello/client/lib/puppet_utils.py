#
# Katello Repos actions
# Copyright 2013 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#
# Red Hat trademarks are not licensed under GPLv2. No permission is
# granted to use or replicate Red Hat trademarks that are incorporated
# in this software or its documentation.
#

import os
import sys
import tarfile
import re

# generate rpm metadata methods
# adapted from pulp_puppet_plugins/pulp_puppet/plugins/importers/metadata.py


class ExtractionException(Exception):
    """
    Root exception of all exceptions that can occur while extracting a module's
    metadata.
    """
    def __init__(self, module_filename):
        Exception.__init__(self, module_filename)
        self.module_filename = module_filename


class MissingModuleFile(ExtractionException):
    """
    Raised if the metadata file cannot be extracted from a module.
    """
    pass


class InvalidTarball(ExtractionException):
    """
    Raised if the tarball cannot be opened.
    """
    pass


def generate_puppet_data(filename):
    """
    Extracts the module's metadata file from the tarball. This call will attempt
    to only extract and read the metadata file itself, cleaning up the
    extracted file at the end.

    :raise InvalidTarball: if the module file cannot be opened
    :raise MissingModuleFile: if the module's metadata file cannot be found
    """
    temp_dir = os.path.dirname(filename)

    data = re.match('^(.+)?-(.+)?-(.+)?\.tar\.gz$', os.path.basename(filename))
    if data is None:
        raise ExtractionException(filename), None, sys.exc_info()[2]
    else:
        author = data.group(1)
        name = data.group(2)
        version = data.group(3)

    # Extract the module's metadata file itself
    metadata_file_path = '%s-%s-%s/%s' % (author, name, version,
                                          "metadata.json")

    try:
        tgz = tarfile.open(name=filename)
    except Exception, e:
        raise InvalidTarball(filename), None, sys.exc_info()[2]

    try:
        tgz.extract(metadata_file_path, path=temp_dir)
        tgz.close()
    except Exception, e:
        tgz.close()
        raise MissingModuleFile(filename), None, sys.exc_info()[2]

    # Read in the contents
    temp_filename = os.path.join(temp_dir, metadata_file_path)
    contents = _read_contents(temp_filename)
    unit_key = {"author": author, "name": name, "version": version}
    return unit_key, contents


def _read_contents(filename):
    """
    Simple utility to read in the contents of the given file, making sure to
    properly handle the file object.

    :return: contents of the given file
    """
    try:
        f = open(filename)
        contents = f.read()
        f.close()

        return contents
    finally:
        # Clean up the temporary file
        os.remove(filename)


def _find_file_in_dir(dir, filename):
    """
    Recursively checks the directory for the presence of a file with the given
    name.

    :param dir:
    :param filename:
    :return:
    """
    for found in os.listdir(dir):
        file_or_dir = os.path.join(dir, found)
        if os.path.isfile(file_or_dir):
            if found == filename:
                return dir
        else:
            sub_dir = _find_file_in_dir(file_or_dir, filename)

            if sub_dir is not None:
                return os.path.join(dir, sub_dir)
    else:
        return None

