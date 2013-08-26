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

from katello.client.api.puppet_module import PuppetModuleAPI
from katello.client.cli.base import opt_parser_add_product, opt_parser_add_org, \
    opt_parser_add_environment, opt_parser_add_content_view
from katello.client.core.base import BaseAction, Command
from katello.client.api.utils import get_repo
from katello.client.lib.ui import printer
from katello.client.lib.ui.printer import batch_add_columns


# base puppet module action --------------------------------------------------------

class PuppetModuleAction(BaseAction):

    def __init__(self):
        super(PuppetModuleAction, self).__init__()
        self.api = PuppetModuleAPI()


# puppet module actions ------------------------------------------------------------
class Info(PuppetModuleAction):

    description = _('list information about a puppet module')

    def setup_parser(self, parser):
        parser.add_option('--id', dest='id',
                          help=_("puppet module ID (required)"))
        parser.add_option('--repo_id', dest='repo_id',
                          help=_("repository ID"))
        parser.add_option('--repo', dest='repo',
                          help=_("repository name (required unless repo_id is passed)"))
        opt_parser_add_org(parser, required=1)
        opt_parser_add_environment(parser, default="Library")
        opt_parser_add_product(parser)
        opt_parser_add_content_view(parser)

    def check_options(self, validator):
        validator.require('id')
        if not validator.exists('repo_id'):
            validator.require(('repo', 'org'))
            validator.require_at_least_one_of(('product', 'product_label', 'product_id'))
            validator.mutually_exclude('product', 'product_label', 'product_id')
            validator.mutually_exclude('view_name', 'view_label', 'view_id')

    def run(self):
        module_id = self.get_option('id')
        repo_id = self.get_option('repo_id')
        repo_name = self.get_option('repo')
        org_name = self.get_option('org')
        env_name = self.get_option('environment')
        prod_name = self.get_option('product')
        prod_label = self.get_option('product_label')
        prod_id = self.get_option('product_id')
        view_name = self.get_option('view_name')
        view_label = self.get_option('view_label')
        view_id = self.get_option('view_id')

        if not repo_id:
            repo = get_repo(org_name, repo_name, prod_name, prod_label, prod_id, env_name, False,
                            view_name, view_label, view_id)
            repo_id = repo["id"]

        module = self.api.puppet_module(module_id, repo_id)

        batch_add_columns(self.printer, {'_id': _("ID")}, {'name': _("Name")},
                          {'_storage_path': _("Path")}, {'license': _("License")},
                          {'project_page': _("Project page")}, {'version': _("Version")},
                          {'author': _("Author")})
        batch_add_columns(self.printer, {'description': _("Description")},
                          {'summary': _("Summary")}, multiline=True,
                          show_with=printer.VerboseStrategy)

        self.printer.set_header(_("Puppet Module Information"))
        self.printer.print_item(module)
        return os.EX_OK


# puppet_module actions ------------------------------------------------------------
class List(PuppetModuleAction):

    description = _('list puppet modules in a repository')

    def setup_parser(self, parser):
        parser.add_option('--repo_id', dest='repo_id',
                          help=_("repository ID"))
        parser.add_option('--repo', dest='repo',
                          help=_("repository name (required unless repo_id is passed)"))
        opt_parser_add_org(parser, required=1)
        opt_parser_add_environment(parser, default="Library")
        opt_parser_add_product(parser)
        opt_parser_add_content_view(parser)

    def check_options(self, validator):
        if not validator.exists('repo_id'):
            validator.require(('repo', 'org'))
            validator.require_at_least_one_of(('product', 'product_label', 'product_id'))
            validator.mutually_exclude('product', 'product_label', 'product_id')
            validator.mutually_exclude('view_name', 'view_label', 'view_id')

    def run(self):
        repo_id = self.get_repo_id()
        if not repo_id:
            return os.EX_DATAERR

        self.printer.set_header(_("Puppet Module List For Repo %s") % repo_id)

        puppet_modules = self.api.puppet_modules_by_repo(repo_id)
        self.print_puppet_modules(puppet_modules)

        return os.EX_OK

    def get_repo_id(self):
        repo_id = self.get_option('repo_id')
        repo_name = self.get_option('repo')
        org_name = self.get_option('org')
        env_name = self.get_option('environment')
        prod_name = self.get_option('product')
        prod_label = self.get_option('product_label')
        prod_id = self.get_option('product_id')
        view_name = self.get_option('view_name')
        view_label = self.get_option('view_label')
        view_id = self.get_option('view_id')

        if not repo_id:
            repo = get_repo(org_name, repo_name, prod_name, prod_label, prod_id, env_name, False,
                            view_name, view_label, view_id)
            if repo:
                repo_id = repo["id"]

        return repo_id

    def print_puppet_modules(self, puppet_modules):
        batch_add_columns(self.printer, {'_id': _("ID")}, {'name': _("Name")}, {'author': _("Author")},
                          {'version': _('Version')})
        self.printer.print_items(puppet_modules)


class Search(List):

    description = _('search puppet modules in a repository')

    def setup_parser(self, parser):
        super(Search, self).setup_parser(parser)
        parser.add_option('--query', dest='query', help=_("query string for \
                searching puppet modules' author, version, or name. e.g. 'http*','httpd'"))

    def check_options(self, validator):
        super(Search, self).check_options(validator)
        validator.require('query')

    def run(self):
        query = self.get_option('query')
        repo_id = self.get_repo_id()

        if not repo_id:
            return os.EX_DATAERR

        self.printer.set_header(_("Puppet Module List For Repo %(repo_id)s and Query %(query)s") %
                                {'repo_id': repo_id, 'query': query})

        puppet_modules = self.api.search(query, repo_id)
        self.print_puppet_modules(puppet_modules)
        return os.EX_OK


# puppet module command ------------------------------------------------------------

class PuppetModule(Command):

    description = _('puppet module specific actions in the katello server')
