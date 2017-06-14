# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

""" An AnalysisRequest report, containing the report itself in pdf and html
    format. Also, includes information about the date when was published, from
    who, the report recipients (and their emails) and the publication mode
"""
from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordsField
from Products.Archetypes import atapi
from Products.Archetypes.public import BaseFolder
from Products.Archetypes.public import Schema
from Products.Archetypes.public import StringField
from Products.Archetypes.references import HoldingReference
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import DateTimeField, UIDReferenceField
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from plone.app.blob.field import BlobField

AnalysisRequest = UIDReferenceField(
    'AnalysisRequest',
    allowed_types=('AnalysisRequest',),
    referenceClass=HoldingReference,
    required=1
)

Pdf = BlobField(
    'Pdf',
)

SMS = StringField(
    'SMS',
)

Recipients = RecordsField(
    'Recipients',
    type='recipients',
    subfields=(
        'UID', 'Username', 'Fullname', 'EmailAddress',
        'PublicationModes'),
)

DatePrinted = DateTimeField(
    'DatePrinted',
    mode="rw",
    widget=DateTimeWidget(
        label=_("Date Printed"),
        visible={'edit': 'visible',
                 'view': 'visible'
                 }
    )
)

schema = BikaSchema.copy() + Schema((
    AnalysisRequest,
    Pdf,
    SMS,
    Recipients,
    DatePrinted
))

schema['id'].required = False
schema['title'].required = False


class ARReport(BaseFolder):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)


atapi.registerType(ARReport, PROJECTNAME)
