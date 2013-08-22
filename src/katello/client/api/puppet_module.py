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


class PuppetModuleAPI(KatelloAPI):
    """
    Connection class to access puppet module calls
    """
    def puppet_module(self, module_id, repo_id):
        path = "/api/repositories/%s/puppet_modules/%s" % (repo_id, module_id)
        module = self.server.GET(path)[1]
        return module

    def puppet_modules_by_repo(self, repo_id):
        path = "/api/repositories/%s/puppet_modules" % repo_id
        module_list = self.server.GET(path)[1]
        return module_list

    def search(self, query, repo_id):
        path = "/api/repositories/%s/puppet_modules/search" % repo_id
        module_list = self.server.GET(path, {"search": query})[1]
        return module_list
