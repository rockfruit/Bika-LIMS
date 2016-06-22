# -*- coding: utf-8 -*-
from collective.z3cform.datagridfield import DictRow
from plone.app.vocabularies.catalog import CatalogSource
from plone.directives import form
from z3c.relationfield import RelationChoice
from z3c.relationfield import RelationList
from zope import schema

from bika.lims import messagefactory as _
from bika.lims.interfaces.samplepoint import ILabSamplePoint


class IAliquotTypesRow(form.Schema):
    """A single row in the Aliquot Types table
    """
    title = schema.TextLine(
        title=_(u"Type Title"),
        description=_(u"Display Name"),
        required=True
    )
    idTemplate = schema.TextLine(
        title=_(u"ID template"),
        description=_(u"A template for naming new aliquots of this type"),
        readonly=False
    )
    minimumVolume = schema.TextLine(
        title=_(u"Minimum Volume"),
        description=_(u"Specify with SI units, eg: 1cm/2, 1', 20g, or 1kg."),
        readonly=False
    )
    AutoCount = schema.Int(
        title=_(u"Auto Create"),
        description=_(u"These aliquots will be automatically created"),
        default=0,
        readonly=False
    )


ALIQUOT_TYPES_DEFAULT = [
    {'title': 'Bulk',
     'idTemplate': '{sample_id:s}-001',
     'MinimumVolume': '',
     'AutoCount': 1,
     }
]


class ISampleType(form.Schema):
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
            u"type can be kept before they expire.  Enter 0 if these samples "
            u"never expire."
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
            u"collected.  If no sample points are selected, then all "
            u"sample points are available."
        ),
        value_type=RelationChoice(
            title=_(u"Sample Point"),
            source=CatalogSource(
                object_provides=ILabSamplePoint.__identifier__),
        ),
        unique=True,
        required=False,
    )
    AliquotTypes = schema.List(
        title=_(u"Aliquot Types"),
        value_type=DictRow(title=u"test", schema=IAliquotTypesRow),
        required=False,
    )
    # values=[_(u"Serum"),
    #         _(u"Plasma"),
    #         _(u"CSF"),
    #         _(u"Whole Blood")],
