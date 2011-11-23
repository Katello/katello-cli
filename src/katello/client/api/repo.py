# -*- coding: utf-8 -*-
#
# Copyright © 2011 Red Hat, Inc.
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

class RepoAPI(KatelloAPI):
    """
    Connection class to access repositories
    """
    def create(self, prod_id, name, url):
        repodata = {"product_id": prod_id,
                    "name": name,
                    "url": url}
        path = "/api/repositories/"
        return self.server.POST(path, repodata)[1]

    def repos_by_org_env(self, orgName, envId, includeDisabled=False):
        data = {
            "include_disabled": includeDisabled
        }
        path = "/api/organizations/%s/environments/%s/repositories" % (orgName, envId)
        result_list = self.server.GET(path, data)[1]
        return result_list

    def repos_by_env_product(self, envId, productId, name=None, includeDisabled=False):
        path = "/api/environments/%s/products/%s/repositories" % (envId, productId)

        search_params = {
            "include_disabled": includeDisabled
        }
        if name != None:
            search_params['name'] = name
            
        result_list = self.server.GET(path, search_params)[1]
        return result_list

    def repos_by_product(self, productId, includeDisabled=False):
        path = "/api/products/%s/repositories" % productId
        data = {
            "include_disabled": includeDisabled
        }
        result_list = self.server.GET(path, data)[1]
        return result_list

    def repo(self, repo_id):
        path = "/api/repositories/%s/" % repo_id
        data = self.server.GET(path)[1]
        return data


    def enable(self, repo_id, enable=True):
        data = {"enable": enable}
        path = "/api/repositories/%s/enable/" % repo_id
        return self.server.POST(path, data)[1]

    def delete(self, repoId):
        path = "/api/repositories/%s/" % repoId
        return self.server.DELETE(path)[1]

    def sync(self, repo_id):
        path = "/api/repositories/%s/sync" % repo_id
        data = self.server.POST(path)[1]
        return data

    def last_sync_status(self, repo_id):
        path = "/api/repositories/%s/sync" % repo_id
        data = self.server.GET(path)[1]
        return data

    def repo_discovery(self, org_name, url, repotype):
        discoverydata = {"url": url, "type": repotype}
        path = "/api/organizations/%s/repositories/discovery" % org_name
        return self.server.POST(path, discoverydata)[1]

    def repo_discovery_status(self, discoveryTaskId):
        path = "/api/repositories/discovery/%s" % discoveryTaskId
        return self.server.GET(path)[1]

    def packagegroups(self, repoid):
        path = "/api/repositories/%s/package_groups" % repoid
        return self.server.GET(path)[1]

    def packagegroup_by_id(self, repoid, groupId):
        path = "/api/repositories/%s/package_groups/" % repoid
        groups = self.server.GET(path, {"group_id": groupId})[1]
        if len(groups) == 0:
            return None
        else:
            return groups[0]

    def packagegroupcategories(self, repoid):
        path = "/api/repositories/%s/package_group_categories/" % repoid
        return self.server.GET(path)[1]

    def packagegroupcategory_by_id(self, repoid, categoryId):
        path = "/api/repositories/%s/package_group_categories/" % repoid
        categories = self.server.GET(path, {"category_id": categoryId})[1]
        if len(categories) == 0:
            return None
        else:
            return categories[0]
