# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import DateTimeField, ReferenceWidget, Schema
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from plone.app.blob.field import FileField

# It comes from blob
AttachmentFile = FileField(
    'AttachmentFile',
    widget=atapi.FileWidget(
        label=_("Attachment")
    )
)

AttachmentType = UIDReferenceField(
    'AttachmentType',
    required=0,
    allowed_types=('AttachmentType',),
    widget=ReferenceWidget(
        label=_("Attachment Type")
    )
)

AttachmentKeys = atapi.StringField(
    'AttachmentKeys',
    searchable=True,
    widget=atapi.StringWidget(
        label=_("Attachment Keys")
    )
)

DateLoaded = DateTimeField(
    'DateLoaded',
    required=1,
    default_method='current_date',
    widget=DateTimeWidget(
        label=_("Date Loaded")
    )
)

schema = BikaSchema.copy() + Schema((
    AttachmentFile,
    AttachmentType,
    AttachmentKeys,
    DateLoaded
))

schema['id'].required = False
schema['title'].required = False


class Attachment(atapi.BaseFolder):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """ Return the Id """
        return safe_unicode(self.getId()).encode('utf-8')

    def getRequest(self):
        """Return the AR to which this is linked.  There is a short time 
        between creation and linking when it is not linked
        """
        tool = getToolByName(self, REFERENCE_CATALOG)
        backrefs = tool.getBackReferences(self, 'AnalysisRequestAttachment')
        uids = [uid for uid in backrefs]
        if len(uids) == 1:
            reference = uids[0]
            ar = tool.lookupObject(reference.sourceUID)
            return ar
        else:
            backrefs = tool.getBackReferences(self, 'AnalysisAttachment')
            uids = [uid for uid in backrefs]
            if len(uids) == 1:
                reference = uids[0]
                analysis = tool.lookupObject(reference.sourceUID)
                ar = analysis.aq_parent
                return ar
        return None

    def getRequestID(self):
        """ Return the ID of the request to which this is linked """
        ar = self.getRequest()
        if ar:
            return ar.getRequestID()
        return None

    def getAttachmentTypeUID(self):
        attachment_type = self.getAttachmentType()
        if attachment_type:
            return attachment_type.UID()
        return ''

    def getClientUID(self):
        return self.aq_parent.UID()

    def getAnalysis(self):
        """ Return the analysis to which this is linked """
        """  it may not be linked to an analysis """
        tool = getToolByName(self, REFERENCE_CATALOG)
        backrefs = tool.getBackReferences(self, 'AnalysisAttachment')
        uids = [uid for uid in backrefs]
        if len(uids) == 1:
            reference = uids[0]
            analysis = tool.lookupObject(reference.sourceUID)
            return analysis
        return None

    def getParentState(self):
        """ Return the review state of the object - analysis or AR """
        """ to which this is linked """
        workflow = getToolByName(self, 'portal_workflow')
        tool = getToolByName(self, REFERENCE_CATALOG)
        backrefs = tool.getBackReferences(self, 'AnalysisAttachment')
        uids = [uid for uid in backrefs]
        parent = False
        if len(uids) == 1:
            reference = uids[0]
            parent = tool.lookupObject(reference.sourceUID)
        else:
            backrefs = tool.getBackReferences(self, 'AnalysisRequestAttachment')
            uids = [uid for uid in backrefs]
            if len(uids) == 1:
                reference = uids[0]
                parent = tool.lookupObject(reference.sourceUID)
        if parent:
            return workflow.getInfoFor(parent, 'review_state', '')
        return ''


atapi.registerType(Attachment, PROJECTNAME)
