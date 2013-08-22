import os

from katello.tests.core.content_upload.content_upload_data import CONTENT_UPLOADS
from katello.tests.core.action_test_utils import CLIOptionTestCase, CLIActionTestCase

import katello.client.core.repo
from katello.client.core.content_upload import ContentUpload

class RequiredCLIOptionsTests(CLIOptionTestCase):

    action = ContentUpload()

    disallowed_options = [
        ('--id=abc123', '--product=puppet', '--org=acme', ),
        ('--repo=fedora_17_x86_64', '--id=abc123', '--org=acme', ),
        ('--repo=fedora_17_x86_64', '--id=abc123', '--product=rpm', )
    ]

    allowed_options = [
        ('--repo_id=1', '--id=abc123', ),
        ('--repo=fedora_17_x86_64', '--id=abc123', '--product=rpm', '--org=acme', ),
        ('--repo=fedora_17_x86_64', '--id=abc123', '--product_id=5', '--org=acme', )
    ]


class ContentUploadTest(CLIActionTestCase):

    CONTENT_UPLOAD = CONTENT_UPLOADS[0]

    OPTIONS = {
        'upload_id': CONTENT_UPLOAD['upload_id'],
        'repo': 'fedora_17_x86_64',
        'product': 'rpm',
        'org': 'acme'
    }

    REPO_ID = 3

    def setUp(self):
        self.set_action(ContentUpload())
        self.set_module(katello.client.core.CONTENT_UPLOAD)
        self.mock_printer()

        self.mock_options(self.OPTIONS)

        self.mock(self.module, 'get_repo', {'id': self.REPO_ID})
        self.mock(self.action.api, 'CONTENT_UPLOAD', self.CONTENT_UPLOAD)

    def test_finds_org(self):
        self.run_action()
        self.action.api.CONTENT_UPLOAD.assert_called_once_with(self.CONTENT_UPLOAD['_id'], self.REPO_ID)

    def test_returns_ok(self):
        self.run_action(os.EX_OK)
