import unittest
from mock import Mock
import os

from cli_test_utils import CLIOptionTestCase, CLIActionTestCase
import test_data

import katello.client.core.product
from katello.client.core.product import ListFilters



class RequiredCLIOptionsTests(CLIOptionTestCase):

    def setUp(self):
        self.set_action(ListFilters())
        self.mock_options()

    def test_missing_org_generates_error(self):
        self.assertRaises(Exception, self.action.process_options, ['list_filters', '--name=product_1'])

    def test_missing_product_generates_error(self):
        self.assertRaises(Exception, self.action.process_options, ['list_filters', '--org=ACME'])

    def test_no_error_if_org_and_product_provided(self):
        self.action.process_options(['list_filters', '--org=ACME', '--name=product_1'])
        self.assertEqual(len(self.action.optErrors), 0)


class ProductListFiltersTest(CLIActionTestCase):

    ORG = test_data.ORGS[0]
    PROD = test_data.PRODUCTS[0]

    OPTIONS = {
        'org': ORG['name'],
        'name': PROD['name']
    }

    def setUp(self):
        self.set_action(ListFilters())
        self.set_module(katello.client.core.product)
        self.mock_printer()

        self.mock_options(self.OPTIONS)

        self.mock(self.action.api, 'filters')
        self.mock(self.module, 'get_product', self.PROD)


    def tearDown(self):
        self.restore_mocks()

    def test_it_returns_with_error_if_no_product_was_found(self):
        self.module.get_product.return_value =  None
        self.action.run()
        self.assertEqual(self.action.run(), os.EX_DATAERR)

    def test_it_uses_product_list_filter_api(self):
        self.action.run()
        self.action.api.filters.assert_called_once_with(self.PROD['id'])
