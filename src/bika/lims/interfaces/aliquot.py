# -*- coding: utf-8 -*-
from datetime import datetime
from plone.supermodel import model
from zope import schema

from bika.lims import messagefactory as _


def currentTime():
    return datetime.now()


class IAliquot(model.Schema):
    """Object that can hold other aliquots, or be an aliquot
    """
    PourDate = schema.Datetime(
        title=_(u"Date of Aliquot Pour"),
        description=_(u"Date of Aliquot Pour"),
        defaultFactory=currentTime,
        required=True,
    )
    FluidType = schema.Choice(
        title=_(u"Type of Aliquot"),
        description=_(u"Possible aliquot types are controlled by the sample "
                      u"type settings."),
        default=u"Serum",
        required=True,
    )
    Use = schema.Choice(
        title=_(u"Use of Aliquot"),
        description=_(u"Use of Aliquot Bulk or Working"),
        values=[_(u"Bulk"),
                _(u"Working"),
                _(u"Quality Control"),
                _(u"Other")],
        default=u"Bulk",
        required=True,
    )
    Department = schema.Choice(
        title=_(u"Department"),
        description=_(u"Department Expected to use Aliquot"),
        vocabulary="bika.lims.vocabularies.Departments",
        required=True,
    )
    StorageLocation = schema.TextLine(
        title=_(u"Storage Location of Aliquot"),
        description=_(u"Storage Location of Aliquot"),
        required=False,
    )
    Volume = schema.Float(
        title=_(u"Volume of Material in uL"),
        description=_(u"volume of Material in uL"),
        required=True,
    )
