# -*- coding: utf-8 -*-

# Copyright © 2010 Red Hat, Inc.
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

import os

from katello.client.cli.base import KatelloCLI


class AdminCLI(KatelloCLI):

    def setup_credentials(self):
        """
        Use the super-class credentials, then fall back to auth login
        credentials if present.
        """
        super(AdminCLI, self).setup_credentials()
        #if self._server.has_credentials_set():
        #    return
        #login = Login()
        #certfile = login.crtpath()
        #keyfile = login.keypath()
        #if os.access(certfile, os.R_OK) and os.access(keyfile, os.R_OK):
        #    self._server.set_ssl_credentials(certfile, keyfile)
