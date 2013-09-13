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
import rpm
import hashlib
import sys

# generate rpm metadata methods
# adapted from pulp_rpm/src/pulp_rpm/extension/admin/upload/package.py
# pylint: disable-all

RPMTAG_NOSOURCE = 1051
CHECKSUM_READ_BUFFER_SIZE = 65536


class InvalidRPMError(Exception):
    pass


def generate_rpm_data(rpm_filename):
    """
    For the given RPM, analyzes its metadata to generate the appropriate unit
    key and metadata fields, returning both to the caller.

    This is performed client side instead of in the importer to get around
    differences in RPMs between RHEL 5 and later versions of Fedora. We can't
    guarantee the server will be able to properly read the RPM so it is
    read client-side and the metadata passed in.

    The obvious caveat is that the format of the returned values must match
    what the importer would produce had this RPM been synchronized from an
    external source.

    @param rpm_filename: full path to the RPM to analyze
    @type  rpm_filename: str

    @return: tuple of unit key and unit metadata for the RPM
    @rtype:  tuple
    """

    # Expected metadata fields:
    # "vendor", "description", "buildhost", "license", "vendor", "requires", "provides", "relativepath", "filename"
    #
    # Expected unit key fields:
    # "name", "epoch", "version", "release", "arch", "checksumtype", "checksum"

    unit_key = dict()
    metadata = dict()

    # Read the RPM header attributes for use later
    ts = rpm.TransactionSet()
    ts.setVSFlags(rpm._RPMVSF_NOSIGNATURES)
    fd = os.open(rpm_filename, os.O_RDONLY)
    try:
        headers = ts.hdrFromFdno(fd)
        os.close(fd)
    except rpm.error:
        # Raised if the headers cannot be read
        os.close(fd)
        msg = _('The given file is not a valid RPM')
        raise InvalidRPMError(msg), None, sys.exc_info()[2]

    # -- Unit Key -----------------------

    # Checksum
    unit_key['checksumtype'] = 'sha256'  # hardcoded to this in v1 so leaving this way for now
    unit_key['checksum'] = _calculate_checksum(unit_key['checksumtype'], rpm_filename)

    # Name, Version, Release, Epoch
    for k in ['name', 'version', 'release', 'epoch']:
        unit_key[k] = headers[k]

    #   Epoch munging
    if unit_key['epoch'] is None:
        unit_key['epoch'] = str(0)
    else:
        unit_key['epoch'] = str(unit_key['epoch'])

    # Arch
    if headers['sourcepackage']:
        if RPMTAG_NOSOURCE in headers.keys():
            unit_key['arch'] = 'nosrc'
        else:
            unit_key['arch'] = 'src'
    else:
        unit_key['arch'] = headers['arch']

    # -- Unit Metadata ------------------

    metadata['relativepath'] = os.path.basename(rpm_filename)
    metadata['filename'] = os.path.basename(rpm_filename)

    # This format is, and has always been, incorrect. As of the new yum importer, the
    # plugin will generate these from the XML snippet because the API into RPM headers
    # is atrocious. This is the end game for this functionality anyway, moving all of
    # that metadata derivation into the plugin, so this is just a first step.
    # I'm leaving these in and commented to show how not to do it.
    # metadata['requires'] = [(r,) for r in headers['requires']]
    # metadata['provides'] = [(p,) for p in headers['provides']]

    metadata['buildhost'] = headers['buildhost']
    metadata['license'] = headers['license']
    metadata['vendor'] = headers['vendor']
    metadata['description'] = headers['description']

    return unit_key, metadata


def _calculate_checksum(checksum_type, filename):
    m = hashlib.new(checksum_type)
    f = open(filename, 'r')
    while 1:
        file_buffer = f.read(CHECKSUM_READ_BUFFER_SIZE)
        if not file_buffer:
            break
    m.update(file_buffer)
    f.close()
    return m.hexdigest()
