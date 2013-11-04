from unittest import TestCase

from katello.client.lib.puppet_utils import generate_puppet_data, validate_file_name
import os

MODULES_DIR = os.path.abspath(os.path.dirname(__file__)) + '/../../../files/puppet'

class PuppetUtilsTest(TestCase):

    def setUp(self):
        self.filename = os.path.join(MODULES_DIR, 'jdob-valid-1.0.0.tar.gz')

    def test_validate_file_name(self):
        self.assertFalse(validate_file_name("puppetlabs.tar.gz"))
        self.assertFalse(validate_file_name("puppetlabs-ntp.tar.gz"))
        self.assertFalse(validate_file_name("puppetlabs-ntp-2.0.1.tgz"))

        self.assertTrue(validate_file_name("puppetlabs-ntp-2.0.1.tar.gz"))
        self.assertTrue(validate_file_name("puppetlabs-ntp-2.0.1-beta4.tar.gz"))

    def test_generate_puppet_data(self):
        expected_unit_key = {'author': 'jdob', 'name': 'valid', 'version': '1.0.0'}
        unit_key, unit_metadata = generate_puppet_data(self.filename)

        self.assertEqual(unit_key, expected_unit_key)
        self.assertEqual(unit_metadata['description'], 'Valid Module Description')
        self.assertEqual(unit_metadata['license'], 'Apache License, Version 2.0')
        self.assertEqual(unit_metadata['project_page'], 'http://example.org/jdob-valid')
