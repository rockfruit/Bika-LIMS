# -*- coding: utf-8 -*-
from bika.lims.interfaces.samplepoint import ILabSamplePoint, IClientSamplePoint
from bika.lims.utils.limsroot import getLims
from zope.interface import alsoProvides


def Added(sample, event):
    """Sample has been added, set some permissions
    """

    lims = getLims(sample)
    mp = sample.manage_permission
    mp(AddAliquot, ['Manager', 'LabManager', 'LabClerk', 'Owner'], 0)
