# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

"""
    AnalysisRequests often use the same configurations.
    AnalysisProfile is used to save these common configurations (templates).
"""

from AccessControl import ClassSecurityInfo
from Products.ATExtensions.field import RecordsField
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import AnalysisProfileAnalysesWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IAnalysisProfile
from zope.interface import implements

ProfileKey = StringField(
    'ProfileKey',
    widget=StringWidget(
        label=_("Profile Keyword"),
        description=_(
            "The profile's keyword is used to uniquely identify it in import "
            "files. It has to be unique, and it may  not be the same as any "
            "Calculation Interim field ID."),
    )
)

Service = ReferenceField(
    'Service',
    schemata='Analyses',
    required=1,
    multiValued=1,
    allowed_types=('AnalysisService',),
    relationship='AnalysisProfileAnalysisService',
    widget=AnalysisProfileAnalysesWidget(
        label=_("Profile Analyses"),
        description=_(
            "The analyses included in this profile, grouped per category"),
    )
)

Remarks = TextField(
    'Remarks',
    searchable=True,
    default_content_type='text/plain',
    allowable_content_types=('text/plain',),
    default_output_type="text/plain",
    widget=TextAreaWidget(
        macro="bika_widgets/remarks",
        label=_("Remarks"),
        append_only=True,
    )
)

# Custom settings for the assigned analysis services
# https://jira.bikalabs.com/browse/LIMS-1324
# Fields:
#   - uid: Analysis Service UID
#   - hidden: True/False. Hide/Display in results reports
AnalysisServicesSettings = RecordsField(
    'AnalysisServicesSettings',
    required=0,
    subfields=('uid', 'hidden',),
    widget=ComputedWidget(visible=False),
)

CommercialID = StringField(
    'CommercialID',
    searchable=1,
    required=0,
    schemata='Accounting',
    widget=StringWidget(
        visible={'view': 'visible', 'edit': 'visible'},
        label=_('Commercial ID'),
        description=_("The profile's commercial ID for accounting purposes."),
    )
)

# When it's set, the system uses the analysis profile's price to quote and
# the system's VAT is overridden by the
# the analysis profile's specific VAT
UseAnalysisProfilePrice = BooleanField(
    'UseAnalysisProfilePrice',
    default=False,
    schemata='Accounting',
    widget=BooleanWidget(
        label=_("Use Analysis Profile Price"),
        description=_(
            "When it's set, the system uses the analysis profile's price to "
            "quote and the system's VAT is overridden by the analysis "
            "profile's specific VAT"),
    )
)

# The price will only be used if the checkbox "use analysis profiles' price"
# is set. This price will be used to quote the analyses instead of analysis
# service's price.
AnalysisProfilePrice = FixedPointField(
    'AnalysisProfilePrice',
    schemata="Accounting",
    default='0.00',
    widget=DecimalWidget(
        label=_("Price (excluding VAT)"),
        visible={'view': 'visible', 'edit': 'visible'},
    )
)

# When the checkbox "use analysis profiles' price" is set,
# the AnalysisProfilesVAT should override the system's VAT
AnalysisProfileVAT = FixedPointField(
    'AnalysisProfileVAT',
    schemata="Accounting",
    default='14.00',
    widget=DecimalWidget(
        label=_("VAT %"),
        description=_(
            "Enter percentage value eg. 14.0. This percentage is applied on "
            "the Analysis Profile only, overriding the systems VAT"),
        visible={'view': 'visible', 'edit': 'visible'},
    )
)

# This VAT amount is computed using the AnalysisProfileVAT instead of systems
#  VAT
VATAmount = ComputedField(
    'VATAmount',
    schemata="Accounting",
    expression='context.getVATAmount()',
    widget=ComputedWidget(
        label=_("VAT"),
        visible={'view': 'visible', 'edit': 'invisible'},
    )
)

TotalPrice = ComputedField(
    'TotalPrice',
    schemata="Accounting",
    expression='context.getTotalPrice()',
    widget=ComputedWidget(
        label=_("Total price"),
        visible={'edit': 'hidden', }
    )
)

schema = BikaSchema.copy() + Schema((
    ProfileKey,
    Service,
    Remarks,
    AnalysisServicesSettings,
    CommercialID,
    UseAnalysisProfilePrice,
    AnalysisProfilePrice,
    AnalysisProfileVAT,
    VATAmount,
    TotalPrice
))
schema['title'].widget.visible = True
schema['description'].widget.visible = True
IdField = schema['id']


class AnalysisProfile(BaseContent):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False
    implements(IAnalysisProfile)

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getClientUID(self):
        return self.aq_parent.UID()

    def getAnalysisServiceSettings(self, uid):
        """ Returns a dictionary with the settings for the analysis
            service that match with the uid provided.
            If there are no settings for the analysis service and
            profile, returns a dictionary with the key 'uid'
        """
        sets = [s for s in self.getAnalysisServicesSettings()
                if s.get('uid', '') == uid]
        return sets[0] if sets else {'uid': uid}

    def isAnalysisServiceHidden(self, uid):
        """ Checks if the analysis service that match with the uid
            provided must be hidden in results.
            If no hidden assignment has been set for the analysis in
            this profile, returns the visibility set to the analysis
            itself.
            Raise a TypeError if the uid is empty or None
            Raise a ValueError if there is no hidden assignment in this
                profile or no analysis service found for this uid.
        """
        if not uid:
            raise TypeError('None type or empty uid')
        sets = self.getAnalysisServiceSettings(uid)
        if 'hidden' not in sets:
            uc = getToolByName(self, 'uid_catalog')
            serv = uc(UID=uid)
            if serv and len(serv) == 1:
                return serv[0].getObject().getRawHidden()
            else:
                raise ValueError('%s is not valid' % uid)
        return sets.get('hidden', False)

    def getVATAmount(self):
        """ Compute AnalysisProfileVATAmount
        """
        price, vat = self.getAnalysisProfilePrice(), \
            self.getAnalysisProfileVAT()
        return float(price) * float(vat) / 100

    def getTotalPrice(self):
        """
        Computes the final price using the VATAmount and the subtotal price
        """
        price, vat = self.getAnalysisProfilePrice(), self.getVATAmount()
        return float(price) + float(vat)


registerType(AnalysisProfile, PROJECTNAME)
