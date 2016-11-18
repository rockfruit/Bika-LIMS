import transaction
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from Products.DataGridField import CheckboxColumn
from Products.DataGridField import Column
from Products.DataGridField import DataGridField
from Products.DataGridField import DataGridWidget
from Products.DataGridField import DateColumn
from Products.DataGridField import LinesColumn
from Products.DataGridField import SelectColumn
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets.referencewidget import \
    ReferenceWidget as bReferenceWidget

from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import IARImport, IARImportHandler
from plone.app.blob.field import BlobField
from zope.component import getAdapter
from zope.interface import implements

Filename = StringField(
    'Filename',
    widget=StringWidget(
        label=_('Original Filename'),
        visible=True
    ),
)

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
ParsedData = BlobField(
    'ParsedData',
    searchable=True,
    widget=FileWidget(
        label=_("Parsed file data"),
        description=_(
            "This field is populated only when parsing is "
            "complete."),
        visible={'edit': 'invisible',
                 'view': 'visible', 'add': 'invisible'},
    ),
)

NrSamples = StringField(
    'NrSamples',
    widget=StringWidget(
        label=_('Number of samples'),
        visible=True
    ),
)

ClientName = StringField(
    'ClientName',
    searchable=True,
    widget=StringWidget(
        label=_("Client Name"),
    ),
)

ClientID = StringField(
    'ClientID',
    searchable=True,
    widget=StringWidget(
        label=_('Client ID'),
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

Contact = ReferenceField(
    'Contact',
    allowed_types=('Contact',),
    relationship='ARImportContact',
    default_method='getContactUIDForUser',
    widget=ReferenceWidget(
        label=_('Primary Contact'),
        size=20,
        visible=True,
        base_query={'inactive_state': 'active'},
        showOn=True,
        popup_width='300px',
        colModel=[{'columnName': 'UID', 'hidden': True},
                  {'columnName': 'Fullname', 'width': '100',
                   'label': _('Name')}],
    ),
)

Batch = ReferenceField(
    'Batch',
    allowed_types=('Batch',),
    relationship='ARImportBatch',
    widget=bReferenceWidget(
        label=_('Batch'),
        visible=True,
        catalog_name='bika_catalog',
        base_query={'review_state': 'open', 'cancellation_state': 'active'},
        showOn=True,
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
        columns={
            'CCNamesReport': LinesColumn('Report CC Contacts'),
            'CCEmailsReport': LinesColumn('Report CC Emails'),
            'CCNamesInvoice': LinesColumn('Invoice CC Contacts'),
            'CCEmailsInvoice': LinesColumn('Invoice CC Emails')
        }
    )
)

SampleData = DataGridField(
    'SampleData',
    allow_insert=True,
    allow_delete=True,
    allow_reorder=False,
    allow_empty_rows=False,
    allow_oddeven=True,
    columns=('ClientSampleID',
             'SamplingDate',
             'DateSampled',
             'SamplePoint',
             'SampleMatrix',
             'SampleType',  # not a schema field!
             'ContainerType',  # not a schema field!
             'ReportDryMatter',
             'Priority',
             'Analyses',  # not a schema field!
             'Profiles'  # not a schema field!
             ),
    widget=DataGridWidget(
        label=_('Samples'),
        columns={
            'ClientSampleID': Column('Sample ID'),
            'SamplingDate': DateColumn('Sampling Date'),
            'DateSampled': DateColumn('Date Sampled'),
            'SamplePoint': SelectColumn(
                'Sample Point', vocabulary='Vocabulary_SamplePoint'),
            'SampleMatrix': SelectColumn(
                'Sample Matrix', vocabulary='Vocabulary_SampleMatrix'),
            'SampleType': SelectColumn(
                'Sample Type', vocabulary='Vocabulary_SampleType'),
            'ContainerType': SelectColumn(
                'Container', vocabulary='Vocabulary_ContainerType'),
            'ReportDryMatter': CheckboxColumn('Dry'),
            'Priority': SelectColumn(
                'Priority', vocabulary='Vocabulary_Priority'),
            'Analyses': LinesColumn('Analyses'),
            'Profiles': LinesColumn('Profiles'),
        }
    )
)

Errors = LinesField(
    'Errors',
    widget=LinesWidget(
        label=_('Errors'),
        rows=10,
    )
)

schema = BikaSchema.copy() + Schema((
    Filename,
    RawData,
    ParsedData,
    NrSamples,
    ClientName,
    ClientID,
    ClientOrderNumber,
    ClientReference,
    Contact,
    CCContacts,
    Batch,
    SampleData,
    Errors,
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

    # def Title(self):
    #    """ Return the id as title """
    #    return safe_unicode(self.getId()).encode('utf-8')

    security.declarePublic('current_date')

    def current_date(self):
        """ return current date """
        return DateTime()

    def _renameAfterCreation(self, check_auto_id=False):
        renameAfterCreation(self)

    # workflow methods
    #
    def workflow_script_submit(self):
        """ submit arimport batch for import.  This implies that the data
            has been parsed and found valid, and won't work until it has.
        """
        if self.getParsedData():
            adapter = getAdapter(self, interface=IARImportHandler,
                                 name="ARImportHandler")(self.REQUEST, self)
            adapter.import_parsed_data()
            transaction.commit()
        url_script = '<script>document.location.href="%s"</script>'.format(
            self.absolute_url()
        )
        self.REQUEST.response.write(url_script)

    def validateIt(self):
        """Called when ARImportItemModifiedEventHandler or
        ARImportModifiedEventHandler events are fired.
        Returns boolean
        """

        if not self.Schema()['RawData'].get(self):
            return False
        adapter = getAdapter(self, interface=IARImportHandler,
                             name="ARImportHandler")(self.REQUEST, self)
        return adapter.validate_arimport()

    security.declarePublic('getContactUIDForUser')

    def _findProfileKey(self, key):
        profiles = self.bika_setup_catalog(
            portal_type='AnalysisProfile')
        found = False
        for brain in profiles:
            if brain.getObject().getProfileKey() == key:
                return brain.getObject()


atapi.registerType(ARImport, PROJECTNAME)
