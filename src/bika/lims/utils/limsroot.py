# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import IPloneSiteRoot
from bika.lims.interfaces.limsroot import ILimsRoot


def getLims(context):
    """Return the ILimsRoot instance that is the ancestor of context.
    """

    if ILimsRoot.providedBy(context):
        return context
    parent = context.__parent__
    while not IPloneSiteRoot.providedBy(parent) \
        and not ILimsRoot.providedBy(parent):
        parent = parent.__parent__
    if IPloneSiteRoot.providedBy(parent):
        return None
    if ILimsRoot.providedBy(parent):
        return parent
