# -*- coding: utf-8 -*-
from zope import schema

from bika.lims import messagefactory as _
from plone.supermodel import model


class ILIMSRoot(model.Schema):
    """The LIMS root object.
    """

    model.fieldset('settings',
                   label=_(u"Settings"),
                   fields=['title']
                   )

    title = schema.TextLine(
        title=_(u"Title"),
        default=u"LIMS",
        required=True,
    )
