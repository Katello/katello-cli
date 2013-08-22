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
    def create(self):
        path = "/api/content_uploads/"
        return self.server.POST(path)[1]

    def upload_bits(self, upload_id, offset, filepath):
        path = "/api/content_uploads/%s/%s/upload_bits/" % upload_id % offset
        return self.server.PUT(path, filepath)[1]

    def import_into_repo(self, repo_id, unit_type_id, upload_id, unit_key, unit_metadata):
        data = {
                'upload_request': {
                   'unit_type_id': unit_type_id,
                   'upload_id': upload_id,
                   'unit_key': unit_key,
                   'unit_metadata': unit_metadata
                }
              }
        path = "/api/repositories/%s/import_into_repo/" % repo_id
        return self.server.POST(path, data)[1]

    def delete(self, upload_id):
        path = "/api/content_uploads/%s/"  % upload_id
        return self.server.DELETE(path)[1]

    def list(self):
        path = " /api/content_uploads/"
        return self.server.GET(path)[1]

