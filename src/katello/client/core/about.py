#
# Katello Organization actions
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

from katello.client.api.about import AboutAPI
from katello.client.core.base import BaseAction
from katello.client.lib.ui import printer


# base about action --------------------------------------------------------

class AboutAction(BaseAction):

    def __init__(self):
        super(AboutAction, self).__init__()
        self.api = AboutAPI()

# about actions ------------------------------------------------------------

class Status(AboutAction):

    description = _('status of the katello server and its subcomponents')

    def run(self):

        about_data = self.api.about()

        directory = about_data.get('Directory', None)

        if directory:
            about_data['Directory'] = directory['path']

        self.printer.add_column('Environment', _("Environment"))
        self.printer.add_column('Application', _("Application"))
        self.printer.add_column('Authentication', _("Authentication"))
        self.printer.add_column('Version', _("Version"))
        self.printer.add_column('Directory', _("Directory"))
        self.printer.add_column('Packages', _("Packages"), multiline=True, show_with=printer.VerboseStrategy)
        self.printer.add_column('Ruby', _("Ruby"))

        self.printer.set_header(_("About Katello Server"))

        return os.EX_OK
