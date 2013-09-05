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


class ContentUploadAPI(KatelloAPI):
    """
    Connection class to access content upload requests
    """

    def create(self, repo_id):
        path = "/api/repositories/%s/content_uploads" % repo_id
        return self.server.POST(path)[1]

    def upload_bits(self, repo_id, upload_id, offset, content):
        data = {
            'offset': str(offset),
            'content': content
        }
        path = "/api/repositories/%s/content_uploads/%s/upload_bits/" % (repo_id, upload_id)
        return self.server.PUT(path, data, multipart=True)[1]

    def import_into_repo(self, repo_id, upload_id, unit_key, unit_metadata):
        data = {
            'unit_key': unit_key,
            'unit_metadata': unit_metadata
        }
        path = "/api/repositories/%s/content_uploads/%s/import_into_repo/" % \
            (repo_id, upload_id)
        return self.server.POST(path, data)[1]

    def delete(self, repo_id, upload_id):
        path = "/api/repositories/%s/content_uploads/%s/" % (repo_id, upload_id)
        return self.server.DELETE(path)[1]
