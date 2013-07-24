import unittest
from mock import Mock
import os

from katello.tests.core.action_test_utils import CLIOptionTestCase, CLIActionTestCase

from katello.tests.core.organization.organization_data  import ORGS, ATTACH_ALL_TASK

import katello.client.core.organization
from katello.client.core.organization import AttachAllSystems

class RequiredCLIOptionsTest(CLIOptionTestCase):
    # required: name

    action = AttachAllSystems()

    disallowed_options = [
        ()
    ]

    allowed_options = [
        ('--name=role1', )
    ]

class OrgAttachAllSystemsTest(CLIActionTestCase):

    ORG = ORGS[0]

    OPTIONS = {
        'name': ORG['name']
    }

    def setUp(self):
        self.set_action(AttachAllSystems())
        self.set_module(katello.client.core.organization)
        self.mock_printer()

        self.mock_options(self.OPTIONS)

        self.mock(self.action.api, 'attach_all_systems', ATTACH_ALL_TASK)

    def test_returns_ok(self):
        self.run_action(os.EX_OK)
