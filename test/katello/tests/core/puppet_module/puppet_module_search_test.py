import os

from katello.tests.core.puppet_module.puppet_module_data import PUPPET_MODULES
from katello.tests.core.action_test_utils import CLIOptionTestCase, CLIActionTestCase

import katello.client.core.puppet_module
from katello.client.core.puppet_module import Search


class RequiredCLIOptionsTests(CLIOptionTestCase):

    action = Search()

    disallowed_options = [
        ('--repo=pforge', '--product=puppet', ),
        ('--repo_id=1', '--id=abc123', '--query=htt*', ),
        ('--repo=pforge', '--product=puppet', '--org=acme', ),
        ('--repo_id=1', )
    ]

    allowed_options = [
        ('--repo_id=1', '--query=htt*', ),
        ('--repo=pforge', '--product=puppet', '--org=acme', '--query=htt*', ),
        ('--repo=pforge', '--product_id=5', '--org=acme', '--query=htt*', )
    ]


class PuppetSearchTest(CLIActionTestCase):

    QUERY = 'htt*'

    OPTIONS = {
        'repo': 'pforge',
        'product': 'puppet',
        'org': 'acme',
        'query': QUERY
    }

    REPO_ID = 5

    def setUp(self):
        self.set_action(Search())
        self.set_module(katello.client.core.puppet_module)
        self.mock_printer()

        self.mock_options(self.OPTIONS)

        self.mock(self.module, 'get_repo', {'id': self.REPO_ID})
        self.mock(self.action.api, 'search', PUPPET_MODULES)

    def test_finds_org(self):
        self.run_action()
        self.action.api.search.assert_called_once_with(self.QUERY, self.REPO_ID)

    def test_returns_ok(self):
        self.run_action(os.EX_OK)
