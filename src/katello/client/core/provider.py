#
# Katello Organization actions
# Copyright (c) 2010 Red Hat, Inc.
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
from gettext import gettext as _
from urlparse import urlparse

from katello.client.api.provider import ProviderAPI
from katello.client.config import Config
from katello.client.core.base import Action, Command
from katello.client.core.utils import is_valid_record, get_abs_path, run_async_task_with_status, run_spinner_in_bg, AsyncTask
from katello.client.core.repo import format_sync_state, format_sync_time
from katello.client.core.utils import ProgressBar
from katello.client.api.utils import get_provider

try:
    import json
except ImportError:
    import simplejson as json

Config()

PROVIDER_TYPES = { 'redhat':   'Red Hat',
                   'custom':   'Custom'}


# base provider action =========================================================
class ProviderAction(Action):

    def __init__(self):
        super(ProviderAction, self).__init__()
        self.api = ProviderAPI()


# provider actions =============================================================
class List(ProviderAction):

    description = _('list all known providers')


    def setup_parser(self):
        self.parser.add_option('--org', dest='org',
                               help=_("organization name (required)"))

    def check_options(self):
        self.require_option('org')

    def run(self):
        orgName = self.get_option('org')

        provs = self.api.providers_by_org(orgName)

        self.printer.addColumn('id')
        self.printer.addColumn('name')
        self.printer.addColumn('provider_type', 'Type')
        self.printer.addColumn('repository_url', 'Url')
        #self.printer.addColumn('organization_id', 'Org Id')
        self.printer.addColumn('description', multiline=True)

        self.printer.setHeader(_("Provider List"))
        self.printer.printItems(provs)
        return os.EX_OK


# ==============================================================================
class Info(ProviderAction):

    description = _('list information about a provider')

    def setup_parser(self):
        # always provide --id option for create, even on registered clients
        self.parser.add_option('--name', dest='name',
                               help=_("provider name (required)"))
        self.parser.add_option('--org', dest='org',
                               help=_("organization name (required)"))

    def check_options(self):
        self.require_option('name')
        self.require_option('org')

    def run(self):
        provName = self.get_option('name')
        orgName  = self.get_option('org')

        prov = get_provider(orgName, provName)
        if prov != None:
            self.printer.addColumn('id')
            self.printer.addColumn('name')
            self.printer.addColumn('provider_type', 'Type')
            self.printer.addColumn('repository_url', 'Url')
            self.printer.addColumn('organization_id', 'Org Id')
            self.printer.addColumn('description', multiline=True)

            self.printer.setHeader(_("Provider Information"))
            self.printer.printItem(prov)
            return os.EX_OK
        else:
            return os.EX_DATAERR


# ==============================================================================
class Update(ProviderAction):

    @property
    def description(self):
        if self._create:
            return _('create a provider')
        else:
            return _('update a provider')


    def __init__(self, create = False):
        self._create = create
        super(Update, self).__init__()



    def setup_parser(self):
        self.parser.add_option('--name', dest='name',
                               help=_("provider name (required)"))
        self.parser.add_option("--description", dest="description",
                               help=_("provider description"))
        self.parser.add_option("--url", dest="url",
                               help=_("repository url eg: http://download.fedoraproject.org/pub/fedora/linux/releases/"))
        self.parser.add_option('--org', dest='org',
                               help=_("name of organization (required)"))

        if self._create:
            self.parser.add_option("--type", dest="type",
                                  help=_("""provider type, one of:
                                  \"redhat\"   for Red Hat,
                                  \"custom\"   for Generic Yum Collection (default)"""),
                                  choices=['redhat', 'custom'])
                                  #default='yum'
        else:
            self.parser.add_option('--new_name', dest='new_name',
                                  help=_("provider name"))


    def check_options(self):

        self.require_option('name')
        self.require_option('org')
        if self._create:
            self.require_option('type')

        if self.get_option('type') == 'redhat':
            self.require_option('url')

        if self.has_option('url'):
            url = self.get_option('url')
            url_parsed = urlparse(url)
            if not url_parsed.scheme in ["http","https"]:
                self.add_option_error(_('Option --url has to start with http:// or https://'))
            elif not url_parsed.netloc:
                self.add_option_error(_('Option --url is not in a valid format'))


    def create(self, name, orgName, description, provType, url):
        prov = self.api.create(name, orgName, description, provType, url)
        if is_valid_record(prov):
            print _("Successfully created provider [ %s ]") % prov['name']
            return True
        else:
            print _("Could not create provider [ %s ]") % prov['name']
            return False


    def update(self, name, orgName, newName, description, url):

        prov = get_provider(orgName, name)
        if prov != None:
            prov = self.api.update(prov["id"], newName, description, url)
            print _("Successfully updated provider [ %s ]") % prov['name']
            return True
        else:
            return False


    def run(self):
        provId      = self.get_option('id')
        name        = self.get_option('name')
        newName     = self.get_option('new_name')
        orgName     = self.get_option('org')
        description = self.get_option('description')
        url         = self.get_option('url')

        if self._create:
            provType = PROVIDER_TYPES[self.get_option('type')]
            if not self.create(name, orgName, description, provType, url):
                return os.EX_DATAERR
        else:
            if not self.update(name, orgName, newName, description, url):
                return os.EX_DATAERR

        return os.EX_OK


# ==============================================================================
class Delete(ProviderAction):

    description = _('delete a provider')

    def setup_parser(self):
        # always provide --name option for create, even on registered clients
        self.parser.add_option('--name', dest='name',
                               help=_("provider name (required)"))
        self.parser.add_option('--org', dest='org',
                               help=_("name of organization (required)"))

    def check_options(self):
        self.require_option('name')
        self.require_option('org')

    def run(self):
        provName = self.get_option('name')
        orgName  = self.get_option('org')

        prov = get_provider(orgName, provName)
        if prov != None:
            msg = self.api.delete(prov["id"])
            print msg
            return os.EX_OK
        else:
            return os.EX_DATAERR


# ==============================================================================
class Sync(ProviderAction):

    description = _('synchronize a provider')


    def setup_parser(self):
        self.parser.add_option('--name', dest='name',
                               help=_("provider name (required)"))
        self.parser.add_option('--org', dest='org',
                               help=_("name of organization (required)"))

    def check_options(self):
        self.require_option('name')
        self.require_option('org')

    def run(self):
        provName = self.get_option('name')
        orgName  = self.get_option('org')
        return self.sync_provider(provName, orgName)

    def sync_provider(self, providerName, orgName):
        prov = get_provider(orgName, providerName)
        if prov == None:
            return os.EX_DATAERR

        task = AsyncTask(self.api.sync(prov["id"]))
        result = run_async_task_with_status(task, ProgressBar())

        if task.failed():
            errors = [json.loads(t["result"])['errors'][0] for t in task.get_hashes() if t['state'] == 'error']
            print _("Provider [ %s ] failed to sync: %s" % (providerName, errors))
            return os.EX_DATAERR

        print _("Provider [ %s ] synchronized" % providerName)
        return os.EX_OK


# ------------------------------------------------------------------------------
class Status(ProviderAction):

    description = _('status of provider\'s synchronization')

    def setup_parser(self):
        self.parser.add_option('--name', dest='name',
                               help=_("provider name (required)"))
        self.parser.add_option('--org', dest='org',
                               help=_("name of organization (required)"))

    def check_options(self):
        self.require_option('org')
        self.require_option('name')

    def run(self):
        provName = self.get_option('name')
        orgName  = self.get_option('org')

        prov = get_provider(orgName, provName)
        if prov == None:
            return os.EX_DATAERR

        task = AsyncTask(self.api.last_sync_status(prov['id']))

        prov['last_sync'] = format_sync_time(prov['last_sync'])
        prov['sync_state'] = format_sync_state(prov['sync_state'])

        if task.is_running():
            pkgsTotal = task.total_count()
            pkgsLeft = task.items_left()
            prov['progress'] = ("%d%% done (%d of %d packages downloaded)" % (task.get_progress()*100, pkgsTotal-pkgsLeft, pkgsTotal))

        #TODO: last errors?

        self.printer.addColumn('id')
        self.printer.addColumn('name')

        self.printer.addColumn('last_sync')
        self.printer.addColumn('sync_state')
        self.printer.addColumn('progress', show_in_grep=False)

        self.printer.setHeader(_("Provider Status"))
        self.printer.printItem(prov)
        return os.EX_OK


# ==============================================================================
class ImportManifest(ProviderAction):

    description = _('import a manifest file')


    def setup_parser(self):
        self.parser.add_option('--name', dest='name',
                               help=_("provider name (required)"))
        self.parser.add_option('--org', dest='org',
                               help=_("name of organization (required)"))
        self.parser.add_option("--file", dest="file",
                               help=_("path to the manifest file (required)"))


    def check_options(self):
        self.require_option('name')
        self.require_option('org')
        self.require_option('file')


    def run(self):
        provName = self.get_option('name')
        orgName  = self.get_option('org')
        manifestPath = self.get_option('file')

        try:
            f = open(get_abs_path(manifestPath))
        except:
            print _("File %s does not exist" % manifestPath)
            return os.EX_IOERR

        prov = get_provider(orgName, provName)
        if prov != None:
            response = run_spinner_in_bg(self.api.import_manifest, (prov["id"], f), message=_("Importing manifest, please wait... "))
            f.close()
            print response
            return os.EX_OK
        else:
            f.close()
            return os.EX_DATAERR

# provider command =============================================================

class Provider(Command):

    description = _('provider specific actions in the katello server')
