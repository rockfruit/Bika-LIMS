# -*- coding: utf-8 -*-
from plone.app.vocabularies.catalog import CatalogSource
from plone.supermodel import model
from z3c.relationfield import RelationChoice
from z3c.relationfield import RelationList
from zope import schema

from bika.lims import messagefactory as _
from bika.lims.interfaces.samplepoint import ILabSamplePoint


class ISampleType(model.Schema):
    """Types of samples
    """
    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )
    SampleIDPrefix = schema.TextLine(
        title=_(u"Sample ID Prefix"),
        description=_(u"New samples of this type will have this prefix."),
        required=True,
        max_length=5,
    )
    RetentionPeriod = schema.Int(
        title=_(u"Retention Period"),
        description=_(
            u"The time (in hours) for which un-preserved samples of this "
            u"type can be kept before they expire.  Enter 0 to never expire."
        ),
        default=0,
        required=False,
    )
    Hazardous = schema.Bool(
        title=_(u"Hazardous"),
        description=_(u"Samples of this type should be treated as hazardous"),
        required=False,
    )
    SamplePoints = RelationList(
        title=_(u"Sample Points"),
        description=_(
            u"The list of sample points from which this sample type can be "
            u"collected.  If no sample points are selected, then all sample "
            u"points are available."
        ),
        value_type=RelationChoice(
            title=u"Sample Point",
            source=CatalogSource(
                object_provides=ILabSamplePoint.__identifier__),
        ),
        unique=True,
        required=False,
    )
