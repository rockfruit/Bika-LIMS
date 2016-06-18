# -*- coding: utf-8 -*-
"""Setup tests for this package."""
import unittest

from bika.lims.testing import BIKA_LIMS_INTEGRATION_TESTING  # noqa
from plone import api


class TestSetup(unittest.TestCase):
    """Test that bika.lims is properly installed."""

    layer = BIKA_LIMS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if bika.lims is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'bika.lims'))

    def test_browserlayer(self):
        """Test that IBikaLIMSLayer is registered."""
        from bika.lims.interfaces import (
            IBikaLIMSLayer)
        from plone.browserlayer import utils
        self.assertIn(IBikaLIMSLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):
    layer = BIKA_LIMS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['bika.lims'])

    def test_product_uninstalled(self):
        """Test if bika.lims is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'bika.lims'))

    def test_browserlayer_removed(self):
        """Test that IBikaLIMSLayer is removed."""
        from bika.lims.interfaces import IBikaLIMSLayer
        from plone.browserlayer import utils
        self.assertNotIn(IBikaLIMSLayer, utils.registered_layers())
