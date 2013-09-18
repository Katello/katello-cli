import unittest
import os

from katello.tests.core.action_test_utils import CLIOptionTestCase, CLIActionTestCase
from katello.tests.core.organization import organization_data
from katello.tests.core.system import system_data

import katello.client.core.system_group
from katello.client.core.system_group import RemoveSystems


class RequiredCLIOptionsTests(CLIOptionTestCase):
    #requires: organization, name, system uuids

    action = RemoveSystems()

    disallowed_options = [
        (),
        ('--org=ACME', ),
        ('--name=system_group_1',),
        ('--system_uuids=345'),
        ('--org=ACME', '--name=system_group_1'),
        ('--org=ACME', '--system_uuids=345'),
        ('--name=system_group_1', '--system_uuids=456')
    ]

    allowed_options = [
        ('--org=ACME', '--name=system', '--system_uuids=4948857'),
    ]


class SystemGroupRemoveSystemsTest(CLIActionTestCase):

    ORG = organization_data.ORGS[0]
    SYSTEM_GROUP = system_data.SYSTEM_GROUPS[1]
    SYSTEM_GROUP_SYSTEMS = system_data.SYSTEM_GROUP_SYSTEMS
    SYSTEMS = system_data.SYSTEMS

    OPTIONS = {
        'org': ORG['name'],
        'name': SYSTEM_GROUP['name'],
        'system_uuids' : [SYSTEMS[0]['uuid'], SYSTEMS[1]['uuid']]
    }

    def setUp(self):
        self.set_action(RemoveSystems())
        self.set_module(katello.client.core.system_group)
        self.mock_printer()

        self.mock_options(self.OPTIONS)

        self.mock(self.action.api, 'remove_systems', self.SYSTEM_GROUP)
        self.mock(self.module, 'get_system_group', self.SYSTEM_GROUP)
        self.mock(self.module, 'get_systems', self.SYSTEMS)
        self.mock(self.action.api, 'system_group_systems', self.SYSTEM_GROUP_SYSTEMS)

    def test_it_calls_system_group_remove_systems_api(self):
        self.action.run()
        self.action.api.remove_systems.assert_called_once_with(self.OPTIONS['org'], self.SYSTEM_GROUP['id'], self.OPTIONS['system_uuids'])

    def test_it_returns_error_when_removing_failed(self):
        self.mock(self.action.api, 'remove_systems', None)
        self.assertEqual(self.action.run(), os.EX_DATAERR)

    def test_it_success_on_successful_remove_of_systems(self):
        self.assertEqual(self.action.run(), os.EX_OK)
