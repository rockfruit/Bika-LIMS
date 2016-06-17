# -*- coding: utf-8 -*-
from bika.lims import messagefactory as _
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile import field as namedfile
from plone.supermodel import model
from zope import schema
from zope.interface import alsoProvides


class IConfiguration(model.Schema):
    """Configuration items that are available for both LIMS and Client folders.
    """


alsoProvides(IConfiguration, IFormFieldProvider)
