# -*- coding: utf-8 -*-
from bika.lims.interfaces.samplepoint import ILabSamplePoint, IClientSamplePoint
from bika.lims.utils.lims import getLims
from zope.interface import alsoProvides


def Added(samplepoint, event):
    """I'll apply ILabSamplePoint or IClientSamplePoint interface to sample
    points, to allow us to neatly select them later based on their context.
    """

    contextpath = '/'.join(samplepoint.__parent__.getPhysicalPath())
    lims = getLims(samplepoint)
    limspath = '/'.join(lims.configuration.samplepoints.getPhysicalPath())
    if contextpath == limspath:
        alsoProvides(samplepoint, ILabSamplePoint)
    else:
        alsoProvides(samplepoint, IClientSamplePoint)
    samplepoint.reindexObject(idxs=['object_provides'])
