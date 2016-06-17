# -*- coding: utf-8 -*-
from bika.lims import messagefactory as _
from plone.supermodel import model
from zope import schema


class ILIMS(model.Schema):
    """The LIMS root object.
    """
    model.fieldset('settings',
                   label=_(u"Settings"),
                   fields=['title',
                           ]
                   )
    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )
