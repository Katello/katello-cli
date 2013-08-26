import os

from katello.tests.core.puppet_module.puppet_module_data import PUPPET_MODULES
from katello.tests.core.action_test_utils import CLIOptionTestCase, CLIActionTestCase

import katello.client.core.puppet_module
from katello.client.core.puppet_module import Info


class RequiredCLIOptionsTests(CLIOptionTestCase):

    action = Info()

    disallowed_options = [
        ('--id=abc123', '--product=puppet', '--org=acme', ),
        ('--repo=pforge', '--id=abc123', '--org=acme', ),
        ('--repo=pforge', '--id=abc123', '--product=puppet', )
    ]

    allowed_options = [
        ('--repo_id=1', '--id=abc123', ),
        ('--repo=pforge', '--id=abc123', '--product=puppet', '--org=acme', ),
        ('--repo=pforge', '--id=abc123', '--product_id=5', '--org=acme', )
    ]


class PuppetInfoTest(CLIActionTestCase):

    PUPPET_MODULE = PUPPET_MODULES[0]

    OPTIONS = {
        'id': PUPPET_MODULE['_id'],
        'repo': 'pforge',
        'product': 'puppet',
        'org': 'acme'
    }

    REPO_ID = 5

    def setUp(self):
        self.set_action(Info())
        self.set_module(katello.client.core.puppet_module)
        self.mock_printer()

        self.mock_options(self.OPTIONS)

        self.mock(self.module, 'get_repo', {'id': self.REPO_ID})
        self.mock(self.action.api, 'puppet_module', self.PUPPET_MODULE)

    def test_finds_org(self):
        self.run_action()
        self.action.api.puppet_module.assert_called_once_with(self.PUPPET_MODULE['_id'], self.REPO_ID)

    def test_returns_ok(self):
        self.run_action(os.EX_OK)
