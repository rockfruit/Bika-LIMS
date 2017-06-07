# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import json
from operator import itemgetter

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import DurationField
from bika.lims.browser.widgets import DurationWidget
from bika.lims.config import PRESERVATION_CATEGORIES, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from plone.protect import CheckAuthenticator

Category = StringField(
    'Category',
    default='lab',
    vocabulary=PRESERVATION_CATEGORIES,
    widget=SelectionWidget(
        format='flex',
        label=_("Preservation Category")
    )
)
RetentionPeriod = DurationField(
    'RetentionPeriod',
    widget=DurationWidget(
        label=_("Retention Period"),
        description=_(
            'Once preserved, the sample must be disposed of within this time '
            'period.  If not specified, the sample type retention period will '
            'be used.')
    )
)

schema = BikaSchema.copy() + Schema((
    Category,
    RetentionPeriod
))

schema['description'].widget.visible = True
schema['description'].schemata = 'default'


class Preservation(BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)


registerType(Preservation, PROJECTNAME)


class ajaxGetPreservations:
    catalog_name = 'bika_setup_catalog'
    contentFilter = {'portal_type': 'Preservation', 'inactive_state': 'active'}

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):

        CheckAuthenticator(self.request)
        searchTerm = 'searchTerm' in self.request and self.request[
            'searchTerm'].lower() or ''
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']

        # lookup objects from ZODB
        catalog = getToolByName(self.context, self.catalog_name)
        brains = catalog(self.contentFilter)
        brains = [p for p in brains if p.Title.lower().find(searchTerm) > -1] \
            if searchTerm else brains

        rows = [{'UID': p.UID,
                 'preservation_uid': p.UID,
                 'Preservation': p.Title,
                 'Description': p.Description}
                for p in brains]

        rows = sorted(rows, cmp=lambda x, y: cmp(x.lower(), y.lower()),
                      key=itemgetter(sidx and sidx or 'Preservation'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        start = (int(page) - 1) * int(nr_rows)
        end = int(page) * int(nr_rows)
        ret = {'page': page,
               'total': pages,
               'records': len(rows),
               'rows': rows[start:end]}
        return json.dumps(ret)
