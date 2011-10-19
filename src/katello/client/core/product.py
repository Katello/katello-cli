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
import datetime

from katello.client.core import repo
from katello.client.api.product import ProductAPI
from katello.client.api.repo import RepoAPI
from katello.client.api.filter import FilterAPI
from katello.client.core.repo import format_sync_state, format_sync_time
from katello.client.api.changeset import ChangesetAPI
from katello.client.config import Config
from katello.client.core.base import Action, Command
from katello.client.api.utils import get_environment, get_provider, get_product
from katello.client.core.utils import run_async_task_with_status, run_spinner_in_bg, wait_for_async_task, AsyncTask
from katello.client.core.utils import ProgressBar

try:
    import json
except ImportError:
    import simplejson as json

Config()



# base product action --------------------------------------------------------

class ProductAction(Action):

    def __init__(self):
        super(ProductAction, self).__init__()
        self.api = ProductAPI()
        self.repoapi = RepoAPI()
        self.csapi = ChangesetAPI()

# product actions ------------------------------------------------------------

class List(ProductAction):

    description = _('list known products')

    def setup_parser(self):
        self.parser.add_option('--org', dest='org',
                       help=_("organization name eg: foo.example.com (required)"))
        self.parser.add_option('--environment', dest='env',
                       help=_('environment name eg: production (default: Locker)'))
        self.parser.add_option('--provider', dest='prov',
                       help=_("provider name, lists provider's product in the Locker"))


    def check_options(self):
        self.require_option('org')


    def run(self):
        org_name = self.get_option('org')
        env_name = self.get_option('env')
        prov_name = self.get_option('prov')

        self.printer.addColumn('id')
        self.printer.addColumn('name')
        self.printer.addColumn('provider_id')
        self.printer.addColumn('provider_name')

        if prov_name:
            prov = get_provider(org_name, prov_name)
            if prov == None:
                return os.EX_DATAERR

            self.printer.setHeader(_("Product List For Provider %s") % (prov_name))
            prods = self.api.products_by_provider(prov["id"])

        else:
            env = get_environment(org_name, env_name)
            if env == None:
                return os.EX_DATAERR

            self.printer.setHeader(_("Product List For Organization %s, Environment '%s'") % (org_name, env["name"]))
            prods = self.api.products_by_env(env['id'])

        self.printer.printItems(prods)
        return os.EX_OK


# ------------------------------------------------------------------------------
class Sync(ProductAction):

    description = _('synchronize a product')

    def setup_parser(self):
        self.parser.add_option('--org', dest='org',
                               help=_("organization name eg: foo.example.com (required)"))
        self.parser.add_option('--name', dest='name',
                               help=_("product name (required)"))

    def check_options(self):
        self.require_option('org')
        self.require_option('name')

    def run(self):
        orgName     = self.get_option('org')
        prodName    = self.get_option('name')

        prod = get_product(orgName, prodName)
        if (prod == None):
            return os.EX_DATAERR


        task = AsyncTask(self.api.sync(prod["id"]))
        run_async_task_with_status(task, ProgressBar())

        if task.failed():
            errors = [json.loads(t["result"])['errors'][0] for t in task.get_hashes() if t['state'] == 'error']
            print _("Product [ %s ] failed to sync: %s" % (prodName, errors))
            return os.EX_DATAERR

        print _("Product [ %s ] synchronized" % prodName)
        return os.EX_OK


# ------------------------------------------------------------------------------
class Status(ProductAction):

    description = _('status of product\'s synchronization')

    def setup_parser(self):
        self.parser.add_option('--org', dest='org',
                               help=_("organization name eg: foo.example.com (required)"))
        self.parser.add_option('--name', dest='name',
                               help=_("product name (required)"))

    def check_options(self):
        self.require_option('org')
        self.require_option('name')

    def run(self):
        orgName     = self.get_option('org')
        prodName    = self.get_option('name')

        prod = get_product(orgName, prodName)
        if (prod == None):
            return os.EX_DATAERR

        task = AsyncTask(self.api.last_sync_status(prod['id']))

        prod['last_sync'] = format_sync_time(prod['last_sync'])
        prod['sync_state'] = format_sync_state(prod['sync_state'])

        if task.is_running():
            pkgsTotal = task.total_count()
            pkgsLeft = task.items_left()
            prod['progress'] = ("%d%% done (%d of %d packages downloaded)" % (task.get_progress()*100, pkgsTotal-pkgsLeft, pkgsTotal))

        #TODO: last errors?

        self.printer.addColumn('id')
        self.printer.addColumn('name')
        self.printer.addColumn('provider_id')
        self.printer.addColumn('provider_name')

        self.printer.addColumn('last_sync')
        self.printer.addColumn('sync_state')
        self.printer.addColumn('progress', show_in_grep=False)

        self.printer.setHeader(_("Product Status"))
        self.printer.printItem(prod)
        return os.EX_OK


# ------------------------------------------------------------------------------
class Promote(ProductAction):

    description = _('promote a product to an environment')

    def setup_parser(self):
        self.parser.add_option('--org', dest='org',
                               help=_("organization name eg: foo.example.com (required)"))
        self.parser.add_option('--name', dest='name',
                               help=_("product name (required)"))
        self.parser.add_option('--environment', dest='env',
                               help=_("environment name (required)"))

    def check_options(self):
        self.require_option('org')
        self.require_option('name')
        self.require_option('env', '--environment')

    def run(self):
        orgName     = self.get_option('org')
        prodName    = self.get_option('name')
        envName     = self.get_option('env')

        env = get_environment(orgName, envName)
        if (env == None):
            return os.EX_DATAERR

        cset = self.csapi.create(orgName, env["id"], self.create_cs_name())
        try:
            patch = {}
            patch['+products'] = [prodName]
            cset = self.csapi.update_content(cset["id"], patch)

            task = self.csapi.promote(cset["id"])

            result = run_spinner_in_bg(wait_for_async_task, [task], message=_("Promoting the product, please wait... "))
            print _("Product [ %s ] promoted to environment [ %s ]" % (prodName, envName))

        finally:
            self.csapi.delete(cset["id"])
        return os.EX_OK

    def create_cs_name(self):
        curTime = datetime.datetime.now()
        return "product_promotion_"+str(curTime)

# ------------------------------------------------------------------------------
class Create(ProductAction):

    def __init__(self):
        super(Create, self).__init__()
        self.discoverRepos = repo.Discovery()

    description = _('create new product to a custom provider')

    def setup_parser(self):
        self.parser.add_option('--org', dest='org',
                               help=_("organization name eg: foo.example.com (required)"))
        self.parser.add_option('--provider', dest='prov',
                               help=_("provider name (required)"))
        self.parser.add_option('--name', dest='name',
                               help=_("product name (required)"))
        self.parser.add_option("--description", dest="description",
                               help=_("product description"))
        self.parser.add_option("--url", dest="url",
                               help=_("repository url eg: http://download.fedoraproject.org/pub/fedora/linux/releases/"))
        self.parser.add_option("--assumeyes", action="store_true", dest="assumeyes",
                               help=_("assume yes; automatically create candidate repositories for discovered urls (optional)"))


    def check_options(self):
        self.require_option('org')
        self.require_option('prov')
        self.require_option('name')

    def run(self):
        provName    = self.get_option('prov')
        orgName     = self.get_option('org')
        name        = self.get_option('name')
        description = self.get_option('description')
        url         = self.get_option('url')
        assumeyes   = self.get_option('assumeyes')

        return self.create_product_with_repos(provName, orgName, name, description, url, assumeyes)


    def create_product_with_repos(self, provName, orgName, name, description, url, assumeyes):
        prov = get_provider(orgName, provName)
        if prov == None:
            return os.EX_DATAERR

        prod = self.api.create(prov["id"], name, description)
        print _("Successfully created product [ %s ]") % name

        if url == None:
            return os.EX_OK

        repourls = self.discoverRepos.discover_repositories(orgName, url)
        self.printer.setHeader(_("Repository Urls discovered @ [%s]" % url))
        selectedurls = self.discoverRepos.select_repositories(repourls, assumeyes)
        self.discoverRepos.create_repositories(prod["id"], prod["name"], selectedurls)

        return os.EX_OK

class ListFilters(ProductAction):
    description = _('list filters of a product')

    def setup_parser(self):
        self.parser.add_option('--org', dest='org',
                               help=_("organization name eg: foo.example.com (required)"))
        self.parser.add_option('--name', dest='name',
                               help=_("product name (required)"))

    def check_options(self):
        self.require_option('org')
        self.require_option('name')

    def run(self):
        orgName     = self.get_option('org')
        prodName    = self.get_option('name')

        prod = get_product(orgName, prodName)
        if (prod == None):
            return os.EX_DATAERR

        filters = self.api.filters(prod['id'])
        self.printer.addColumn('name')
        self.printer.addColumn('description')
        self.printer.setHeader(_("Product Filters"))
        self.printer.printItems(filters)


        return os.EX_OK

class AddFilter(ProductAction):
    description = _('add a filter to a product')
    
    def __init__(self):
        super(AddFilter, self).__init__()
        self.filterAPI = FilterAPI()
    
    def setup_parser(self):
        self.parser.add_option('--org', dest='org',
                               help=_("organization name eg: foo.example.com (required)"))
        self.parser.add_option('--name', dest='name',
                               help=_("product name (required)"))
        self.parser.add_option('--filter', dest='filter',
                              help=_("filter name (required)"))

    def check_options(self):
        self.require_option('org')
        self.require_option('name')
        self.require_option('filter')

    def run(self):
        orgName     = self.get_option('org')
        prodName    = self.get_option('name')
        filterName  = self.get_option('filter')

        prod = get_product(orgName, prodName)
        if (prod == None):
            return os.EX_DATAERR
            
        if self.filterAPI.info(orgName, filterName) == None:
            return os.EX_DATAERR
            
        filters = self.api.filters(prod['id'])
        self.api.update_filters(prod['id'], [f['name'] for f in filters] + [filterName])
        
        print _("Added filter [ %s ] to product [ %s ]" % (filterName, prodName))
        return os.EX_OK

class DeleteFilter(ProductAction):
    description = _('delete a filter from a product')

    def __init__(self):
        super(DeleteFilter, self).__init__()
        self.filterAPI = FilterAPI()

    def setup_parser(self):
        self.parser.add_option('--org', dest='org',
                               help=_("organization name eg: foo.example.com (required)"))
        self.parser.add_option('--name', dest='name',
                               help=_("product name (required)"))
        self.parser.add_option('--filter', dest='filter',
                              help=_("filter name (required)"))

    def check_options(self):
        self.require_option('org')
        self.require_option('name')
        self.require_option('filter')

    def run(self):
        orgName     = self.get_option('org')
        prodName    = self.get_option('name')
        filterName  = self.get_option('filter')

        prod = get_product(orgName, prodName)
        if (prod == None):
            return os.EX_DATAERR

        if self.filterAPI.info(orgName, filterName) == None:
            return os.EX_DATAERR

        filters = self.api.filters(prod['id'])        
        existingFilterNames = [f['name'] for f in filters]

        if len(existingFilterNames) == 0:
            return os.EX_OK            
            
        self.api.update_filters(prod['id'], existingFilterNames)

        print _("Deleted filter [ %s ] from product [ %s ]" % (filterName, prodName))
        return os.EX_OK
    
# product command ------------------------------------------------------------

class Product(Command):

    description = _('product specific actions in the katello server')
