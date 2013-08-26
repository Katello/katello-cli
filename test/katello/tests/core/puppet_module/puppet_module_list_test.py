import os

from katello.tests.core.puppet_module.puppet_module_data import PUPPET_MODULES
from katello.tests.core.action_test_utils import CLIOptionTestCase, CLIActionTestCase

import katello.client.core.puppet_module
from katello.client.core.puppet_module import List


class RequiredCLIOptionsTests(CLIOptionTestCase):

    action = List()

    disallowed_options = [
        ('--product=puppet', '--org=acme', ),
        ('--repo=pforge', '--org=acme', ),
        ('--repo=pforge', '--product=puppet', ),
        ('--repo_id=1', '--id=abc123', ),
    ]

    allowed_options = [
        ('--repo_id=1', ),
        ('--repo=pforge', '--product=puppet', '--org=acme', ),
        ('--repo=pforge', '--product_id=5', '--org=acme', )
    ]


class PuppetListTest(CLIActionTestCase):

    OPTIONS = {
        'repo': 'pforge',
        'product': 'puppet',
        'org': 'acme'
    }

    REPO_ID = 5

    def setUp(self):
        self.set_action(List())
        self.set_module(katello.client.core.puppet_module)
        self.mock_printer()

        self.mock_options(self.OPTIONS)

        self.mock(self.module, 'get_repo', {'id': self.REPO_ID})
        self.mock(self.action.api, 'puppet_modules_by_repo', PUPPET_MODULES)

    def test_finds_org(self):
        self.run_action()
        self.action.api.puppet_modules_by_repo.assert_called_once_with(self.REPO_ID)

    def test_returns_ok(self):
        self.run_action(os.EX_OK)
