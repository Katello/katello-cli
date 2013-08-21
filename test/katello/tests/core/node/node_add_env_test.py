import unittest
from mock import Mock
import os
from katello.tests.core.action_test_utils import CLIOptionTestCase, CLIActionTestCase
from katello.tests.core.node import node_data
from katello.tests.core.organization import organization_data

import katello.client.core.node
from katello.client.core.node import AddEnvironment 

try:
    import json
except ImportError:
    import simplejson as json


class RequiredCLIOptionsTests(CLIOptionTestCase):

    action = AddEnvironment()

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
        self.NODE['environment_ids'] = []
        self.set_action(AddEnvironment())
        self.set_module(katello.client.core.node)

        self.mock(self.module, 'get_environment', self.ENV)
        self.mock(self.module, 'get_node', self.NODE)
        self.mock_printer()

    def test_it_adds_env(self):
        self.mock_options(self.ENV_OPTIONS)
        self.mock(self.action.api, 'set_environments') 
        self.run_action()       
        self.action.api.set_environments.assert_called_once_with(self.NODE['id'], [self.ENV['id']])
        self.module.get_environment.assert_called_once_with(self.ORG['name'], self.ENV['name'])

