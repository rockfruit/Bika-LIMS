# -*- coding: utf-8 -*-
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope.interface import alsoProvides


class IConfiguration(model.Schema):
    """Configuration items that are available for both LIMS and Client folders.
    """


alsoProvides(IConfiguration, IFormFieldProvider)
