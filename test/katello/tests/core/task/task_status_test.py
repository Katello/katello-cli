from katello.tests.core.action_test_utils import CLIOptionTestCase, CLIActionTestCase

import katello.client.core.task
from katello.client.core.task import Status


class RequiredCLIOptionsTests(CLIOptionTestCase):

    action = Status()

    disallowed_options = [
        (),
        ('--org=ACME', '--uuid=abc123', )
    ]

    allowed_options = [
        ('--uuid=abc123', ),
    ]


class TaskListTest(CLIActionTestCase):

    UUID = 'abc123'
    OPTIONS = {'uuid': UUID}

    def setUp(self):
        self.set_action(Status())
        self.set_module(katello.client.core.task)
        self.mock_printer()

        self.mock_options(self.OPTIONS)

        self.mock(self.action.api, 'status', [])

    def tearDown(self):
        self.restore_mocks()

    def test_it_uses_lists_api(self):
        self.run_action()
        self.action.api.status.assert_called_once_with(self.UUID)
