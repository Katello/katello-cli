import unittest
from mock import Mock
import os
from katello.tests.core.action_test_utils import CLIOptionTestCase, CLIActionTestCase
from katello.tests.core.node import node_data
from katello.tests.core.repo import repo_data
from katello.tests.core.organization import organization_data

import katello.client.core.node
from katello.client.core.node import Sync 

try:
    import json
except ImportError:
    import simplejson as json


class RequiredCLIOptionsTests(CLIOptionTestCase):

    action = Sync()

    disallowed_options = [
                          ('--name=node.test', '--org=Foo'),
                          ('--name=node.test', '--environment=Dev')
                         ]

    allowed_options = [
                       ('--name=node.test', '--environment=Dev', '--org=Foo')
                      ]


class NodeSyncTest(CLIActionTestCase):

    ORG = organization_data.ORGS[0]
    ENV = organization_data.ENVS[0]
    NODE = node_data.NODES[0]
    ALL_ENV_OPTIONS = { 'node': 'node.test' }

    ENV_OPTIONS = {
                    'node': NODE['name'],
                    'org' : ORG['name'],
                    'env_name': ENV['name']
                  }

    def setUp(self):
        self.set_action(Sync())
        self.set_module(katello.client.core.node)

        self.mock(self.action.api, 'sync', repo_data.SYNC_RESULT_WITHOUT_ERROR)
        self.mock(self.module, 'get_environment', self.ENV)
        self.mock(self.module, 'get_node', self.NODE)
        self.mock(self.module, 'run_spinner_in_bg')
        self.mock(self.module, 'wait_for_async_task')

        self.mock_printer()

    def test_it_syncs_with_env_id(self):
        self.mock_options(self.ENV_OPTIONS)
        self.run_action()       
        self.action.api.sync.assert_called_once_with(self.NODE['id'], self.ENV['id'])
        self.module.get_environment.assert_called_once_with(self.ORG['name'], self.ENV['name'])

    def test_it_syncs_without_env_id(self):
        self.mock_options(self.ALL_ENV_OPTIONS)
        self.run_action()       
        self.action.api.sync.assert_called_once_with(self.NODE['id'], None)

