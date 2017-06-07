# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.ATExtensions.field.records import RecordsField
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.utils import getToolByName
from bika.lims.browser.widgets import ServicesWidget
from bika.lims.browser.widgets import WorksheetTemplateLayoutWidget
from bika.lims.config import ANALYSIS_TYPES, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims import PMF, bikaMessageFactory as _
from zope.interface import implements
import sys

Layout = RecordsField(
    'Layout',
    schemata='Layout',
    required=1,
    type='templateposition',
    subfields=('pos', 'type', 'blank_ref', 'control_ref', 'dup'),
    required_subfields=('pos', 'type'),
    subfield_labels={'pos': _('Position'),
                     'type': _('Analysis Type'),
                     'blank_ref': _('Reference'),
                     'control_ref': _('Reference'),
                     'dup': _('Duplicate Of')},
    widget=WorksheetTemplateLayoutWidget(
        label=_("Worksheet Layout"),
        description=_(
            "Specify the size of the Worksheet, e.g. corresponding to a "
            "specific instrument's tray size. Then select an Analysis 'type' "
            "per Worksheet position. Where QC samples are selected, "
            "also select which Reference Sample should be used. If a "
            "duplicate analysis is selected, indicate which sample position "
            "it should be a duplicate of")
    )
)

Service = ReferenceField(
    'Service',
    schemata='Analyses',
    required=0,
    multiValued=1,
    allowed_types=('AnalysisService',),
    relationship='WorksheetTemplateAnalysisService',
    referenceClass=HoldingReference,
    widget=ServicesWidget(
        label=_("Analysis Service"),
        description=_(
            "Select which Analyses should be included on the Worksheet")
    )
)

RestrictToMethod = ReferenceField(
    'RestrictToMethod',
    schemata="Description",
    required=0,
    vocabulary_display_path_bound=sys.maxint,
    vocabulary='_getMethodsVoc',
    allowed_types=('Method',),
    relationship='WorksheetTemplateMethod',
    referenceClass=HoldingReference,
    widget=SelectionWidget(
        format='select',
        label=_("Method"),
        description=_(
            "Restrict the available analysis services and instrumentsto those "
            "with the selected method. In order to apply this change to the "
            "services list, you should save the change first.")
    )
)

Instrument = ReferenceField(
    'Instrument',
    schemata="Description",
    required=0,
    vocabulary_display_path_bound=sys.maxint,
    vocabulary='getInstruments',
    allowed_types=('Instrument',),
    relationship='WorksheetTemplateInstrument',
    referenceClass=HoldingReference,
    widget=ReferenceWidget(
        checkbox_bound=0,
        label=_("Instrument"),
        description=_("Select the preferred instrument")
    )
)

InstrumentTitle = ComputedField(
    'InstrumentTitle',
    expression="context.getInstrument().Title() "
               "if context.getInstrument() else ''",
    widget=ComputedWidget(
        visible=False
    )
)

schema = BikaSchema.copy() + Schema((
    Layout,
    Service,
    RestrictToMethod,
    Instrument,
    InstrumentTitle
))

schema['title'].schemata = 'Description'
schema['title'].widget.visible = True

schema['description'].schemata = 'Description'
schema['description'].widget.visible = True


class WorksheetTemplate(BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    security.declarePublic('getAnalysisTypes')
    def getAnalysisTypes(self):
        """ return Analysis type displaylist """
        return ANALYSIS_TYPES

    def getInstruments(self):
        cfilter = {'portal_type': 'Instrument', 'inactive_state': 'active'}
        if self.getRestrictToMethod():
            cfilter['getMethodUIDs'] = {
                                    "query": self.getRestrictToMethod().UID(),
                                    "operator": "or"}
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('', 'No instrument')] + [
            (o.UID, o.Title) for o in
            bsc(cfilter)]
        o = self.getInstrument()
        if o and o.UID() not in [i[0] for i in items]:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def getMethodUID(self):
        method = self.getRestrictToMethod()
        if method:
            return method.UID()
        return ''

    def _getMethodsVoc(self):
        """
        This function returns the registered methods in the system as a
        vocabulary.
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(i.UID, i.Title)
                 for i in bsc(portal_type='Method',
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        items.insert(0, ('', _("Not specified")))
        return DisplayList(list(items))

registerType(WorksheetTemplate, PROJECTNAME)
