import transaction
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from Products.DataGridField import Column
from Products.DataGridField import DataGridField
from Products.DataGridField import DataGridWidget
from Products.DataGridField import DateColumn
from Products.DataGridField import LinesColumn
from Products.statusmessages.interfaces import IStatusMessage
from bika.lims import bikaMessageFactory as _, t
from bika.lims.browser.widgets.referencewidget import \
    ReferenceWidget as bReferenceWidget

from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import IARImport, IARImportHandler, IClient
from bika.lims.vocabularies import CatalogVocabulary
from bika.lims.workflow import skip
from plone.app.blob.field import BlobField
from zExceptions import Redirect
from zope.component import getMultiAdapter
from zope.interface import implements

RawData = BlobField(
    'RawData',
    searchable=True,
    widget=FileWidget(
        label=_("Original File"),
        description=_(
            "Store the original file data received from the "
            "user."),
        visible={'edit': 'invisible',
                 'view': 'visible', 'add': 'invisible'},
    ),
)

ClientName = StringField(
    'ClientName',
    searchable=True,
    widget=StringWidget(
        label=_("Client Name"),
        description=_("The name of the client specified in the input file. "
                      "This should always be the same as the client in which "
                      "this data is being imported."),
    ),
)

ClientID = StringField(
    'ClientID',
    searchable=True,
    widget=StringWidget(
        label=_("Client ID"),
        description=_("The ID matching the client name specified. "
                      "This should always match the client name, and also the "
                      "client in which this data is being imported."),
    ),
)

ClientOrderNumber = StringField(
    'ClientOrderNumber',
    searchable=True,
    widget=StringWidget(
        label=_('Client Order Number'),
    ),
)

ClientReference = StringField(
    'ClientReference',
    searchable=True,
    widget=StringWidget(
        label=_('Client Reference'),
    ),
)

ContactName = StringField(
    'ContactName',
    searchable=True,
    vocabulary='getClientContactFullnames',
    widget=StringWidget(
        label=_('Contact Name'),
        description=_('This must be the full name of a contact belonging to '
                      'this client.'),
    ),
)

CCContacts = DataGridField(
    'CCContacts',
    allow_insert=False,
    allow_delete=False,
    allow_reorder=False,
    allow_empty_rows=False,
    columns=('CCNamesReport',
             'CCEmailsReport',
             'CCNamesInvoice',
             'CCEmailsInvoice'),
    default=[{'CCNamesReport': [],
              'CCEmailsReport': [],
              'CCNamesInvoice': [],
              'CCEmailsInvoice': []
              }],
    widget=DataGridWidget(
        visible=False,
        columns={
            'CCNamesReport': LinesColumn('Report CC Contacts'),
            'CCEmailsReport': LinesColumn('Report CC Emails'),
            'CCNamesInvoice': LinesColumn('Invoice CC Contacts'),
            'CCEmailsInvoice': LinesColumn('Invoice CC Emails')
        }
    )
)

SamplePoint = ReferenceField(
    'SamplePoint',
    allowed_types='SamplePoint',
    relationship='ARImportSamplePoint',
    widget=bReferenceWidget(
        label=_("Sample Site"),
        description=_("Location where sample was taken"),
        visible={'edit': 'visible', 'view': 'visible'},
        catalog_name='bika_setup_catalog',
        base_query={'inactive_state': 'active'},
        showOn=True,
    ),
)

SampleType = ReferenceField(
    'SampleType',
    allowed_types='SampleType',
    relationship='ARImportSampleType',
    widget=bReferenceWidget(
        label=_("Media / SampleType"),
        description=_("Media or type of sample"),
        visible={'edit': 'visible', 'view': 'visible'},
        catalog_name='bika_setup_catalog',
        base_query={'inactive_state': 'active'},
        showOn=True,
    ),
)

ActivitySampled = StringField(
    'ActivitySampled',
    searchable=True,
    widget=StringWidget(
        label=_('Activity Sampled'),
    ),
)

BatchTitle = StringField(
    'BatchTitle',
    searchable=True,
    widget=StringWidget(
        label=_('Work Order Title'),
        description=_('The title of the batch these items well be created in.'),
    ),
)

BatchDescription = StringField(
    'BatchDescription',
    searchable=True,
    widget=StringWidget(
        label=_('Work Order Description'),
        description=_('The description of the batch these items well be '
                      'created in.'),
    ),
)

BatchID = StringField(
    'BatchID',
    searchable=True,
    widget=StringWidget(
        label=_('Work Order ID'),
        description=_('The ID of the batch these items well be created in.'
                      'If a batch with this ID does not already exist, one '
                      'will be created.'),
    ),
)

ClientBatchID = StringField(
    'ClientBatchID',
    searchable=True,
    widget=StringWidget(
        label=_('Client Work Order ID'),
        description=_('The Client ID for this batch.'),
    ),
)

LabBatchComment = TextField(
    'LabBatchComment',
    searchable=True,
    widget=TextAreaWidget(
        label=_('Lab Batch Comment'),
    ),
)

ClientBatchComment = TextField(
    'ClientBatchComment',
    searchable=True,
    widget=TextAreaWidget(
        label=_('Client Batch Comment'),
    ),
)

Batch = ReferenceField(
    'Batch',
    allowed_types=('Batch',),
    relationship='ARImportBatch',
    widget=bReferenceWidget(
        label=_('Work Order'),
        description=_("If using an work order, select it here."),
        visible=True,
        catalog_name='bika_catalog',
        base_query={'review_state': 'open', 'cancellation_state': 'active'},
        showOn=True,
    ),
)

DateSampled = DateTimeField

# ItemData is used to display a gridwidget of all values that can be
# different for each imported item.  It includes all fields from all
# the objects that will finally be created
ItemData = DataGridField(
    'ItemData',
    allow_insert=True,
    allow_delete=True,
    allow_reorder=False,
    allow_empty_rows=False,
    allow_oddeven=True,
    columns=(
        'ClientSampleID',
        'AmountSampled',
        'Metric',
        'DateSampled',
        'Analyses',
        'Remarks',
    ),
    widget=DataGridWidget(
        label=_('Samples'),
        columns={
            'ClientSampleID': Column('Sample ID'),
            'AmountSampled': Column('Amount Sampled'),
            'Metric': Column('Metric'),
            'DateSampled': Column('Date Sampled'),
            'Analyses': LinesColumn('Analyses'),
            'Remarks': Column('Remarks'),
        }
    )
)

NrSamples = StringField(
    'NrSamples',
    widget=StringWidget(
        label=_('Number of samples'),
        visible=False
    ),
)

Errors = LinesField(
    'Errors',
    widget=LinesWidget(
        label=_('Errors'),
        rows=10,
    )
)

Valid = BooleanField(
    'Valid',
    default=False,
    widget=LinesWidget(
        visible=False,
    )
)

schema = BikaSchema.copy() + Schema((
    RawData,

    ClientName,
    ClientID,
    ClientOrderNumber,
    ClientReference,

    ContactName,
    CCContacts,

    SamplePoint,
    SampleType,
    ActivitySampled,

    BatchTitle,
    BatchDescription,
    BatchID,
    ClientBatchID,
    LabBatchComment,
    ClientBatchComment,
    Batch,

    ItemData,
    NrSamples,
    Errors,
    Valid
))

schema['title'].required = False
schema['title'].validators = ()
# Update the validation layer after change the validator in runtime
schema['title']._validationLayer()


class ARImport(BaseFolder):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False
    implements(IARImport)
    _at_rename_after_creation = True

    security.declarePublic('current_date')

    def current_date(self):
        """ return current date """
        return DateTime()

    def _renameAfterCreation(self, check_auto_id=False):
        renameAfterCreation(self)

    def workflow_before_validate(self):
        handler = getMultiAdapter((self, self.REQUEST),
                                  interface=IARImportHandler)
        handler.validate()
        # valid = self.Schema()['Valid'].get(self)
        # if not valid:
        #     # Store the data that's been changed...
        #     transaction.commit()
        #
        #     # but abort the workflow state change...
        #     raise Redirect(self.absolute_url() + "/edit")
        #     # self.REQUEST.response.write(
        #     #     '<script>document.location.href="{}/edit"</script>'.format(
        #     #         self.absolute_url()))
        # raise Redirect(self.absolute_url())

    def at_post_edit_script(self):
        workflow = getToolByName(self, 'portal_workflow')
        trans_ids = [t['id'] for t in workflow.getTransitionsFor(self)]
        if 'validate' in trans_ids:
            handler = getMultiAdapter((self, self.REQUEST),
                                      interface=IARImportHandler)
            handler.validate()
            if self.getValid():
                wf = getToolByName(self, 'portal_workflow')
                wf.doActionFor(self, "validate")
                if wf.getInfoFor(self, "review_state") == 'valid':
                    msg = _("Valid and ready to import.")
                    return IStatusMessage(self.REQUEST).addStatusMessage(msg)

    def workflow_script_import(self):
        """ submit arimport batch for import.  This implies that the data
            has been parsed and found valid, and won't work until it has.
        """
        if not skip(self, 'import', peek=True):
            # I do not know why this transition is invoked multiple times.
            # To prevent this, just add us to the workflow_skiplist.
            skip(self, 'arimport')
            handler = getMultiAdapter((self, self.REQUEST),
                                      interface=IARImportHandler)
            handler.validate()
            if self.getValid():
                handler.import_items()
                url = self.absolute_url().split("?")[0] + "/base_view"
                script = '<script>document.location.href="{}"' \
                         '</script>'.format(url)
                self.REQUEST.response.write(script)
                msg = _("Import finished, objects have been created!")
                IStatusMessage(self.REQUEST).addStatusMessage(msg)
                transaction.commit()
                raise Redirect(url)

    def Vocabulary_SamplePoint(self):
        vocabulary = CatalogVocabulary(self)
        vocabulary.catalog = 'bika_setup_catalog'
        folders = [self.bika_setup.bika_samplepoints]
        if IClient.providedBy(self.aq_parent):
            folders.append(self.aq_parent)
        return vocabulary(allow_blank=True, portal_type='SamplePoint')

    def Vocabulary_SampleMatrix(self):
        vocabulary = CatalogVocabulary(self)
        vocabulary.catalog = 'bika_setup_catalog'
        return vocabulary(allow_blank=True, portal_type='SampleMatrix')

    def Vocabulary_SampleType(self):
        vocabulary = CatalogVocabulary(self)
        vocabulary.catalog = 'bika_setup_catalog'
        folders = [self.bika_setup.bika_sampletypes]
        if IClient.providedBy(self.aq_parent):
            folders.append(self.aq_parent)
        return vocabulary(allow_blank=True, portal_type='SampleType')

    def Vocabulary_ContainerType(self):
        vocabulary = CatalogVocabulary(self)
        vocabulary.catalog = 'bika_setup_catalog'
        return vocabulary(allow_blank=True, portal_type='ContainerType')

    def Vocabulary_Priority(self):
        vocabulary = CatalogVocabulary(self)
        vocabulary.catalog = 'bika_setup_catalog'
        return vocabulary(allow_blank=True, portal_type='ARPriority')

    def getClientContactFullnames(self):
        contacts = self.aq_parent.objectValues('Contact')
        items = []
        for contact in contacts:
            key = contact.getId()
            value = contact.getFullname()
            items.append((key, t(value)))
        return DisplayList(items)


atapi.registerType(ARImport, PROJECTNAME)
