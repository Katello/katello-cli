import unittest
import os
from mock import Mock
from copy import deepcopy

from katello.tests.core.action_test_utils import CLIOptionTestCase, CLIActionTestCase

from katello.tests.core.about import about_data

import katello.client.core.about
from katello.client.core.about import Status

class AboutTest(CLIActionTestCase):


    def setUp(self):
        self.set_action(Status())
        self.set_module(katello.client.core.about)

        self.mock(self.action.api, 'about', about_data.ABOUT_STATUS)
        self.mock_printer()

    def test_calls_the_api(self):
        self.run_action()
        self.action.api.about.assert_called_once()

    def test_it_returns_correct_error_code(self):
        self.run_action(os.EX_OK)

    def test_status_for_admin_user(self):
        self.check_server_status()
        self.assertEqual(about_data.ABOUT_STATUS, self.action.api.about())

    def test_status_for_non_admin_user(self):
        self.check_server_status(False)
        self.assertNotEqual(about_data.ABOUT_STATUS, self.action.api.about())

    def check_server_status(self, is_admin=True):
        status = deepcopy(about_data.ABOUT_STATUS)

        if not is_admin:
            status.pop('Environment')
            status.pop('Directory')
            status.pop('Authentication')
            status.pop('Ruby')

        self.mock(self.action.api, 'about', status)

