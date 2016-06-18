# -*- coding: utf-8 -*-
from zope import schema

from bika.lims import messagefactory as _
from plone.app.vocabularies.catalog import CatalogSource
from plone.supermodel import model
from z3c.relationfield import RelationList, RelationChoice


class ISamplePoint(model.Schema):
    """The location that a sample was taken from
    """
    title = schema.TextLine(
        title=_(u"Name"),
        required=True,
    )
    SampleTypes = RelationList(
        title=_(u"Sample Types"),
        description=_(
            u"The list of sample types that can be collected at this sample "
            u"point.  If no sample types are selected, then all sample types "
            u"are available."
        ),
        value_type=RelationChoice(
            title=u"Sample Point",
            source=CatalogSource(
                object_provides='bika.lims.interfaces.sampletype.ISampleType'),
        ),
        unique=True,
        required=False,
    )


class ILabSamplePoint(ISamplePoint):
    """Sample points created in the LIMS configuration
    This is applied to new sample points by the ISamplePoint subscriber
    when SamplePoints are created
    """


class IClientSamplePoint(ISamplePoint):
    """Sample points created in the Client's configuration
    This is applied to new sample points by the ISamplePoint subscriber
    when SamplePoints are created
    """
