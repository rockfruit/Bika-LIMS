from bika.lims import logger
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

version = '1.1.2'  # Remember version number in metadata.xml and setup.py
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

    # The assignment of the whole Calculation object in a metadata column
    # was causing a "TypeError: Can't pickle objects in acquisition wrappers".
    # getCalculation was only used in analyses listing and can be safely
    # replaced by getCalculationUID, cause is only used to determine if a
    # calculation is required to compute the result value
    # https://github.com/senaite/bika.lims/issues/322
    ut.delColumn(CATALOG_ANALYSIS_LISTING, 'getCalculation')
    ut.addColumn(CATALOG_ANALYSIS_LISTING, 'getCalculationUID')
    ut.refreshCatalogs()

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True
