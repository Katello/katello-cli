import os

from katello.tests.core.content_upload.content_upload_data import CONTENT_UPLOADS
from katello.tests.core.action_test_utils import CLIOptionTestCase, CLIActionTestCase

import katello.client.core.repo
from katello.client.core.repo import ContentUpload


class RequiredCLIOptionsTests(CLIOptionTestCase):

    action = ContentUpload()

    disallowed_options = [
        ('--filepath=/tmp/bear-4.1-1.noarch.rpm', '--content_type=yum', ),
        ('--repo=fedora_17_x86_64', '--filepath=/tmp/bear-4.1-1.noarch.rpm', '--content_type=yum', '--org=acme', ),
        ('--repo=fedora_17_x86_64', '--filepath=/tmp/bear-4.1-1.noarch.rpm', '--content_type=yum', '--product=rpm', ),
        ('--filepath=/tmp/jdob-valid-1.1.0.tar.gz', '--content_type=puppet', ),
        ('--repo=pforge', '--filepath=/tmp/jdob-valid-1.1.0.tar.gz', '--content_type=puppet', '--org=acme', ),
        ('--repo=pforge', '--filepath=/tmp/jdob-valid-1.1.0.tar.gz', '--content_type=puppet', '--product=puppet', )
    ]

    allowed_options = [
        ('--repo_id=1', '--filepath=/tmp/bear-4.1-1.noarch.rpm', '--content_type=yum', ),
        ('--repo=fedora_17_x86_64', '--filepath=/tmp/bear-4.1-1.noarch.rpm', '--content_type=yum', '--product=rpm', '--org=acme', ),
        ('--repo=fedora_17_x86_64', '--filepath=/tmp/bear-4.1-1.noarch.rpm', '--content_type=yum', '--product_id=5', '--org=acme', ),
        ('--repo_id=5', '--filepath=/tmp/jdob-valid-1.1.0.tar.gz', '--content_type=puppet', ),
        ('--repo=pforge', '--filepath=/tmp/jdob-valid-1.1.0.tar.gz', '--content_type=puppet', '--product=puppet', '--org=acme', ),
        ('--repo=pforge', '--filepath=/tmp/jdob-valid-1.1.0.tar.gz', '--content_type=puppet', '--product_id=5', '--org=acme', )
    ]


class ContentUploadTest(CLIActionTestCase):
    def setUp(self):
        self.set_action(ContentUpload())
        self.set_module(katello.client.core.repo)
        self.mock_printer()
        self.mock(self.module, 'generate_puppet_data', [{}, {}])
        self.mock(self.module, 'generate_rpm_data', [{}, {}])
        self.mock(os.path, 'isfile', True)

    def test_yum_content_upload(self):
        content_upload = CONTENT_UPLOADS[0]

        options = {
            'upload_id': content_upload['upload_id'],
            'filepath': '/tmp/bear-4.1-1.noarch.rpm',
            'content_type': 'yum',
            'repo': 'fedora_17_x86_64',
            'product': 'rpm',
            'org': 'acme'
        }

        repo_id = 1
        self._setup_mocks(options, repo_id, content_upload)

        self.run_action()
        self.action.upload_api.create.assert_called_once_with(repo_id)
        self.module.generate_rpm_data.assert_called_once()
        self.action.send_content.assert_called_once_with(repo_id, content_upload["upload_id"], options["filepath"], None)
        self.action.upload_api.import_into_repo.assert_called_once()
        self.action.upload_api.delete.assert_called_once_with(repo_id, content_upload['upload_id'])

    def test_puppet_content_upload(self):
        content_upload = CONTENT_UPLOADS[1]

        options = {
            'upload_id': content_upload['upload_id'],
            'filepath': '/tmp/jdob-valid-1.1.0.tar.gz',
            'content_type': 'puppet',
            'repo': 'pforge',
            'product': 'puppet',
            'org': 'acme'
        }

        repo_id = 5
        self._setup_mocks(options, repo_id, content_upload)

        self.run_action()
        self.action.upload_api.create.assert_called_once_with(repo_id)
        self.module.generate_puppet_data.assert_called_once()
        self.action.send_content.assert_called_once_with(repo_id, content_upload["upload_id"], options["filepath"], None)
        self.action.upload_api.import_into_repo.assert_called_once()
        self.action.upload_api.delete.assert_called_once_with(repo_id, content_upload['upload_id'])

    def test_dir_content_upload(self):
        content_upload = CONTENT_UPLOADS[1]
        puppet_dir = os.path.join(os.getcwd(), 'test/files/puppet')

        options = {
            'upload_id': content_upload['upload_id'],
            'filepath': puppet_dir,
            'content_type': 'puppet',
            'repo': 'pforge',
            'product': 'puppet',
            'org': 'acme'
        }

        repo_id = 5
        self._setup_mocks(options, repo_id, content_upload)

        self.run_action()
        self.action.upload_api.create.assert_called_once_with(repo_id)
        self.module.generate_puppet_data.assert_called_once()
        self.action.send_content.assert_called_once_with(repo_id, content_upload["upload_id"], options["filepath"], None)
        self.action.upload_api.import_into_repo.assert_called_once()
        self.action.upload_api.delete.assert_called_once_with(repo_id, content_upload['upload_id'])

    def test_returns_ok(self):
        content_upload = CONTENT_UPLOADS[0]

        options = {
            'upload_id': content_upload['upload_id'],
            'filepath': '/tmp/bear-4.1-1.noarch.rpm',
            'content_type': 'yum',
            'repo': 'fedora_17_x86_64',
            'product': 'rpm',
            'org': 'acme'
        }

        repo_id = 1
        self._setup_mocks(options, repo_id, content_upload)
        self.run_action(os.EX_OK)

    def _setup_mocks(self, options, repo_id, content_upload):
        self.mock_options(options)
        self.mock(self.module, 'get_repo', {'id': repo_id})
        self.mock(self.action.upload_api, 'create', content_upload)
        self.mock(self.action, 'send_content', None)
        self.mock(self.action.upload_api, 'import_into_repo', content_upload)
        self.mock(self.action.upload_api, 'delete', content_upload)
