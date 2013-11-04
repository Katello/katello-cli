from unittest import TestCase

from katello.client.lib.rpm_utils import generate_rpm_data
import os

MODULES_DIR = os.path.abspath(os.path.dirname(__file__)) + '/../../../files/rpm'

class rpmUtilsTest(TestCase):

    def setUp(self):
        self.filename = os.path.join(MODULES_DIR, 'bear-4.1-1.noarch.rpm')

    def test_generate_rpm_data(self):
        unit_key, unit_metadata = generate_rpm_data(self.filename)
        self.assertEqual(unit_key['name'], 'bear')
        self.assertEqual(unit_key['release'], '1')
        self.assertEqual(unit_key['version'], '4.1')
        self.assertEqual(unit_key['arch'], 'noarch')
        self.assertEqual(unit_metadata['filename'], 'bear-4.1-1.noarch.rpm')
        self.assertEqual(unit_metadata['license'], 'GPLv2')
        self.assertEqual(unit_metadata['vendor'], None)
