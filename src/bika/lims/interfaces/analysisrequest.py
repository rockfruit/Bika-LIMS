# -*- coding: utf-8 -*-
from zope import schema

from bika.lims import messagefactory as _
from bika.lims.interfaces.analysisservice import IAnalysisService
from bika.lims.interfaces.contact import IClientContact
from bika.lims.interfaces.sample import ISample
from plone.app.vocabularies.catalog import CatalogSource
from plone.supermodel import model
from z3c.relationfield import RelationChoice
from z3c.relationfield import RelationList


class IAnalysisRequest(model.Schema):
    """Analysis Request is the Client's interface for submitting samples
    and requesting analyses.
    """

    primary_contact = RelationChoice(
        title=_(u"Primary Contact"),
        description=_(u"All notifications and publications will be sent to "
                      u"this contact."),
        source=CatalogSource(object_provides=IClientContact.__identifier__),
        required=True,
    )

    cc_contacts = RelationList(
        title=_(u"Contacts to CC"),
        description=_(u"Publications will be sent to these contacts"),
        value_type=RelationChoice(
            title=u"Contact",
            source=CatalogSource(object_provides=IClientContact.__identifier__),
        ),
        unique=False,
    )

    cc_emails = schema.Text(
        title=_(u"CC Emails"),
        description=_(u"Publications will be sent to these email addresses."),
        required=False,
    )

    sample = RelationChoice(
        title=_(u"Sample"),
        description=_(u"Select an existing sample to create a secondary AR, "
                      u"or leave this field blank to register a new sample."),
        source=CatalogSource(object_provides=ISample.__identifier__),
        required=False,
    )

    services = RelationList(
        title=_(u"Analyses"),
        description=_(u"Selected analysis services to be performed on "
                      u"the sample"),
        value_type=RelationChoice(
            title=u"Analyses",
            source=CatalogSource(
                object_provides=IAnalysisService.__identifier__),
        ),
        unique=False,
    )


"""
ReferenceField('Batch',
ReferenceField('SamplingRound',
ReferenceField('SubGroup',
ReferenceField('Template',
ReferenceField('Profiles',
DateTimeField('DateSampled',
StringField('Sampler',
DateTimeField('SamplingDate',
ReferenceField('SampleType',
ReferenceField('Specification',
RecordsField('ResultsRange',
ReferenceField('PublicationSpecification',
ReferenceField('SamplePoint',
ReferenceField('StorageLocation',
StringField('ClientOrderNumber',
StringField('ClientReference',
StringField('ClientSampleID',
ReferenceField('SamplingDeviation',
ReferenceField('SampleCondition',
StringField('EnvironmentalConditions',
ReferenceField('DefaultContainerType',
BooleanField('ReportDryMatter',
BooleanField('InvoiceExclude',
ARAnalysesField('Analyses',
ReferenceField('Attachment',
ReferenceField('Invoice',
DateTimeField('DateReceived',
DateTimeField('DatePublished',
FixedPointField('MemberDiscount',
ReferenceField('ChildAnalysisRequest',
ReferenceField('ParentAnalysisRequest',
StringField('PreparationWorkflow',
HistoryAwareReferenceField('Priority',
TextField('ResultsInterpretation',
RecordsField('ResultsInterpretationDepts',
RecordsField('AnalysisServicesSettings',
TextField('Remarks',
"""
