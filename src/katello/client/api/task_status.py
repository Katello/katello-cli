# -*- coding: utf-8 -*-
#
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

from katello.client.api.base import KatelloAPI
from katello.client.server import ServerRequestError


class TaskStatusAPI(KatelloAPI):
    def status(self, taskUuid):
        path = "/api/tasks/%s" % str(taskUuid)
        try:
            task = self.server.GET(path)[1]
        except ServerRequestError:
            task = None
        return task

    def tasks_by_org(self, org):
        path = "/api/organizations/%s/tasks" % str(org)
        tasks = self.server.GET(path)[1]
        return tasks

class SystemTaskStatusAPI(KatelloAPI):
    def status(self, taskUuid):
        path = "/api/systems/tasks/%s" % str(taskUuid)
        return self.server.GET(path)[1]
