# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import IPloneSiteRoot
from bika.lims.interfaces.limsroot import ILIMSRoot


def getLims(context):
    """Return the ILIMSRoot instance that is the ancestor of context.
    """

    if ILIMSRoot.providedBy(context):
        return context
    parent = context.__parent__
    while not IPloneSiteRoot.providedBy(parent) \
        and not ILIMSRoot.providedBy(parent):
        parent = parent.__parent__
    if IPloneSiteRoot.providedBy(parent):
        return None
    if ILIMSRoot.providedBy(parent):
        return parent
