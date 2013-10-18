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

from katello.client.core.base import BaseAction, Command
from katello.client.api.node import NodeAPI
from katello.client.api.utils import get_node, get_environment
from katello.client.cli.base import opt_parser_add_node, opt_parser_add_org
from katello.client.lib.ui.progress import run_spinner_in_bg, wait_for_async_task
from katello.client.lib.ui.formatters import format_node_sync_errors
from katello.client.lib.async import AsyncTask, evaluate_task_status


# base node action =========================================================
class NodeAction(BaseAction):

    def __init__(self):
        super(NodeAction, self).__init__()
        self.api = NodeAPI()

def convert_org_hash(node):
    orgs = {}
    for env in node['environments']:
        org_name = env['org_name']
        if not orgs.has_key(org_name):
            orgs[org_name] = []
        orgs[org_name].append(env['name'])
    org_string = ""
    for org_name, env_list in orgs.iteritems():
        org_string += "%s: " % org_name
        org_string += "[%s]" % ','.join(env_list)
        org_string += "  "
    return org_string

# node actions =============================================================
class List(NodeAction):

    description = _('list all known nodes')

    def setup_parser(self, parser):
        "No parser needed"
    def check_options(self, validator):
        "No validation needed"

    def run(self):
        nodes = self.api.nodes()
        for node in nodes:
            node['org_environments'] = convert_org_hash(node)

        self.printer.add_column('id', _("ID"))
        self.printer.add_column('name', _("Name"))
        self.printer.add_column('org_environments', _("Environments"))

        self.printer.set_header(_("Node List"))
        self.printer.print_items(nodes)
        return os.EX_OK


class Sync(NodeAction):

    description = _('Sync a node')

    def setup_parser(self, parser):
        opt_parser_add_node(parser)
        opt_parser_add_org(parser, required=0)
        parser.add_option("--environment", dest="env_name",
                          help=_("Environment name to sync, (optional)"))

    def check_options(self, validator):
        validator.require_at_least_one_of(('name', 'id'))
        validator.mutually_exclude('name', 'id')
        validator.require_all_or_none(('env_name', 'org'))

    def run(self):
        node_id = self.get_option("id")
        node_name = self.get_option("name")

        org_name = self.get_option('org')
        env_name = self.get_option('env_name')
        env_id = None
        message = _("Syncing node, please wait... ")
        if env_name is not None:
            env = get_environment(org_name, env_name)
            env_id = env['id']
            message = _("Syncing environment %s to node, please wait...") % env['name']

        node_id = get_node(node_name, node_id)['id']
        sync_tasks = self.api.sync(node_id, env_id)
        task = AsyncTask(sync_tasks)
        run_spinner_in_bg(wait_for_async_task, [task], message=message)

        return evaluate_task_status(task,
            ok =     _("Sync of environment [ %s ] completed successfully.") % env_name,
            failed = _("Sync of environment [ %s ] failed") % env_name,
            error_formatter = format_node_sync_errors
        )

class BaseUpdate(NodeAction):

    def setup_parser(self, parser):
        opt_parser_add_node(parser)
        opt_parser_add_org(parser, required=1)
        parser.add_option("--environment", dest="env_name", help=_("Environment name"))
 

    def check_options(self, validator):
        validator.require_at_least_one_of(('name', 'id'))
        validator.mutually_exclude('name', 'id')
        validator.require('org')
        validator.require('env_name')

    def run(self):
        node_id = self.get_option("id")
        node_name = self.get_option("name")

        node = get_node(node_name, node_id)

        org_name = self.get_option('org')
        env_name = self.get_option('env_name')
        env = get_environment(org_name, env_name)
        self.process(node, env)

    def process(self, node, env):
        """
          NOOP
        """

class AddEnvironment(BaseUpdate):

    description = _('add an environment')

    def process(self, node, env):
        env_ids = node['environment_ids']
        env_id = env['id']
        if not env_id in env_ids:
            self.api.set_environments(node['id'], env_ids + [env_id])
        else:
            print _("Node already subscribed to environment %s.") % env['name']

class RemoveEnvironment(BaseUpdate):
 
    description = _('remove an environment')

    def process(self, node, env):
        env_ids = node['environment_ids']
        env_id = env['id']
        if env_id in env_ids:
            env_ids.remove(env_id)
            self.api.set_environments(node['id'], env_ids)
        else:
            print _("Node not subscribed to environment %s.") % env['name']


class Node(Command):

    description = _('node specific actions in the katello server')

