from katello.tests.core.action_test_utils import CLIOptionTestCase, CLIActionTestCase

import katello.client.core.task
from katello.client.core.task import List


class RequiredCLIOptionsTests(CLIOptionTestCase):

    action = List()

    disallowed_options = [
        ('--name=view1', ),
        ('--state=waiting', )
    ]

    allowed_options = [
        ('--org=ACME', ),
        ('--org=ACME', '--state=waiting', ),
        ('--org=ACME', '--state=waiting', '--type=content_view_refresh', )
    ]


class TaskListTest(CLIActionTestCase):

    ORG = 'some_org'
    STATE = 'waiting'
    OPTIONS = {'org': ORG, 'state': STATE}

    def setUp(self):
        self.set_action(List())
        self.set_module(katello.client.core.task)
        self.mock_printer()

        self.mock_options(self.OPTIONS)

        self.mock(self.action.api, 'tasks_by_org', [])

    def tearDown(self):
        self.restore_mocks()

    def test_it_uses_lists_api(self):
        self.run_action()
        self.action.api.tasks_by_org.assert_called_once_with(self.ORG)
