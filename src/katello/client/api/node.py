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

class NodeAPI(KatelloAPI):

    def nodes(self):
        path = "/api/nodes/"
        nodes = self.server.GET(path)[1]
        return nodes

    def set_environments(self, node_id, environment_ids):
        data = { 
                'node': {
                   'environment_ids': environment_ids
                }
              }
        path = "/api/nodes/%s" % node_id
        return self.server.PUT(path, data)[1]

    def sync(self, node_id, env_id=None):
        data = {}
        if env_id is not None:
            data['environment_id'] = env_id
        path = "/api/nodes/%s/sync" % node_id
        return self.server.POST(path, data)[1]
