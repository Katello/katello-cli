from katello.tests.core.action_test_utils import CLIOptionTestCase
from katello.client.core.system import Register

import katello.client.core.system


class RequiredCLIOptionsTests(CLIOptionTestCase):

    action = Register()

    disallowed_options = [
        ('--content_view=view1', '--org=ACME'),
        ('--name=raspbi'),
        ('--name=raspbi', '--env=Dev'),
        ('--org=ACME', '--name=raspbi', '--content_view=view1'),
    ]

    allowed_options = [
        ('--org=ACME', '--name=raspbi', '--content_view_id=1', '--env=Dev'),
        ('--org=ACME', '--activationkey=key1', '--name=raspbi'),
        ('--org=ACME', '--name=raspbi', '--content_view=view1', '--env=Dev'),
    ]

    def setUp(self):
        self.mock(katello.client.cli.base, 'get_katello_mode', self.mode)
        self.mock(katello.client.core.system, 'get_katello_mode', self.mode)
