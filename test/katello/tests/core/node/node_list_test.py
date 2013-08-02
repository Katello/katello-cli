import unittest
from mock import Mock
import os
from katello.tests.core.action_test_utils import CLIOptionTestCase, CLIActionTestCase
from katello.tests.core.node import node_data

import katello.client.core.node
from katello.client.core.node import List, convert_org_hash

try:
    import json
except ImportError:
    import simplejson as json


class RequiredCLIOptionsTests(CLIOptionTestCase):

    action = List()

    disallowed_options = []

    allowed_options = []


class NodeListTest(CLIActionTestCase):

    def setUp(self):
        self.set_action(List())
        self.set_module(katello.client.core.node)

        self.mock_options({})
        self.mock_printer()
        nodes = node_data.NODES
        nodes[0]['org_environments'] = convert_org_hash(nodes[0]) 
        self.mock(self.action.api, 'nodes', node_data.NODES)

    def test_it_prints_nodes(self):
        self.mock_options({})
        self.run_action()
        self.action.printer.print_items.assert_called_with(node_data.NODES)
        self.action.printer.print_items.reset_mock()
