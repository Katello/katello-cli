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

from katello.client.api.task_status import TaskStatusAPI
from katello.client.core.base import BaseAction, Command
from katello.client.api.utils import ApiDataError
from katello.client.cli.base import opt_parser_add_org
from katello.client.lib.control import system_exit
from katello.client.lib.ui.formatters import format_date

# base task action ----------------------------------------------------------------

class TaskAction(BaseAction):

    STATES = ["waiting", "running", "error", "finished", "canceled", "timed_out"]

    def __init__(self):
        super(TaskAction, self).__init__()
        self.api = TaskStatusAPI()

# task actions --------------------------------------------------------------------

class List(TaskAction):

    description = _("get a list of tasks")

    def setup_parser(self, parser):
        opt_parser_add_org(parser, required=1)
        parser.add_option("--state", dest="state",
                          help=(_("task state (%s)") % (", ".join(self.STATES))))
        parser.add_option("--type", dest="task_type",
                          help=(_("task type eg: content_view_refresh")))

    def check_options(self, validator):
        validator.require('org')
        if (self.get_option("state") and self.get_option("state") not in self.STATES):
            state = self.get_option("state")
            system_exit(os.EX_DATAERR, _("State '%(state)s' not valid. It must be in [%(options)s].") %
                        {'state': state, 'options': ", ".join(self.STATES)})

    def run(self):
        org_name = self.get_option('org')
        state = self.get_option('state')
        task_type = self.get_option('task_type')

        tasks = self.api.tasks_by_org(org_name)

        if state:
            tasks = filter(lambda t: t['state'] == state, tasks)
        if task_type:
            tasks = filter(lambda t: t['task_type'] == task_type, tasks)

        self.printer.add_column('uuid', _("UUID"))
        self.printer.add_column('state', _("State"))
        self.printer.add_column('task_type', _("Type"))
        self.printer.add_column('start_time', _("Start Time"), formatter=format_date)
        self.printer.add_column('finish_time', _("Finish Time"), formatter=format_date)

        self.printer.set_header(_("Task Status"))
        self.printer.print_items(tasks)
        return os.EX_OK

class Status(TaskAction):

    description = _("get a task's status")

    def setup_parser(self, parser):
        parser.add_option("--uuid", dest='uuid',
                          help=_("task uuid eg: c9668eda-096b-445d-b96d (required)"))

    def check_options(self, validator):
        validator.require(('uuid'))

    def run(self):
        uuid = self.get_option('uuid')

        task = self.api.status(uuid)
        if task is None:
            raise ApiDataError(_("Could not find task [ %s ].") % uuid)

        self.printer.add_column('uuid', _("UUID"))
        self.printer.add_column('state', _("State"))
        self.printer.add_column('task_type', _("Type"))
        self.printer.add_column('progress', _("Progress"))
        self.printer.add_column('start_time', _("Start Time"), formatter=format_date)
        self.printer.add_column('finish_time', _("Finish Time"), formatter=format_date)
        self.printer.add_column('task_owner_id', _("Owner ID"))
        self.printer.add_column('task_owner_type', _("Owner Type"))
        self.printer.set_header(_("Task Status"))
        self.printer.print_item(task)
        return os.EX_OK

# task command --------------------------------------------------------------------

class Task(Command):

    description = _('commands for retrieving task information')
