# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import IPloneSiteRoot
from bika.lims.interfaces.lims import ILIMS


def getLims(context):
    """Return the ILIMS instance that is the ancestor of context.
    """

    if ILIMS.providedBy(context):
        return context
    parent = context.__parent__
    while not (IPloneSiteRoot.providedBy(parent) or ILIMS.providedBy(parent)):
        parent = parent.__parent__
    if IPloneSiteRoot.providedBy(parent):
        return None
    if ILIMS.providedBy(parent):
        return parent
