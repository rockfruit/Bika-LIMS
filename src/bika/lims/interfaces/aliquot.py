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

    date_created = schema.Datetime(
        title=_(u"Date Created"),
        defaultFactory=currentTime,
        required=True,
    )

    aliquot_type = schema.Choice(
        title=_(u"Type of Aliquot"),
        description=_(u"Possible aliquot types are controlled by the sample "
                      u"type settings."),
        vocabulary="bika.lims.vocabularies.aliquot.AliquotTypes",
        required=True,
    )

    purpose = schema.Choice(
        title=_(u"Use of Aliquot"),
        description=_(
            u"Use of Aliquot<br><ul>"
            u"<li>Working aliquot for analysis</li>"
            u"<li>Bulk aliquot for storage</li>"
            u"<li>Quality Control aliquot</li>"),
        values=[_(u"Working"),
                _(u"Bulk"),
                _(u"Quality Control"),
                _(u"Other")],
        default=u"Working",
        required=True,
    )

    department = schema.Choice(
        title=_(u"Department"),
        description=_(u"Department Expected to use Aliquot"),
        vocabulary="bika.lims.vocabularies.Departments",
        required=True,
    )

    storage_location = schema.TextLine(
        title=_(u"Storage Location of Aliquot"),
        description=_(u"Storage Location of Aliquot"),
        required=False,
    )

    physical_quantity = schema.Float(
        title=_(u"Physical quantity of material"),
        description=_(u"Specify with SI units, eg: 1uL, 1', 20g, or 1 kg."),
        required=True,
    )
