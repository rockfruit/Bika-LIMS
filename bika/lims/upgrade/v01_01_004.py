from Products.CMFCore.utils import getToolByName
from bika.lims import logger
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

version = '1.1.4'  # Remember version number in metadata.xml and setup.py
profile = 'profile-{0}:default'.format(product)


@upgradestep(product, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(product)

    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ver_from, version))
        # The currently installed version is more recent than the target
        # version of this upgradestep
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ver_from, version))

    # Attachments must be present in a catalog, otherwise the idserver
    # will fall apart.  https://github.com/senaite/bika.lims/issues/323
    at = getToolByName(portal, 'archetype_tool')
    at.setCatalogsByType('Attachment', ['portal_catalog'])

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True
