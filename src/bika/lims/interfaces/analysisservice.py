# -*- coding: utf-8 -*-
from plone.supermodel import model
from zope import schema

from bika.lims import messagefactory as _


class IAnalysisService(model.Schema):
    """Analysis Service defines the tests available in the LIMS.
    """

    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    description = schema.Text(
        title=_(u"Description"),
        required=False,
    )

    result_unit = schema.TextLine(
        title=_(u"Result Unit"),
        description=_(
            u"This can be any of the SI units, plus a bunch of non-SI, bits, "
            u"dollars, and any combination of them. They can include the "
            u"standard SI prefixes.  You can also use your own unit strings "
            u"here, though the system will not be able to use these in "
            u"physical quantity calculations"),
        required=False,
    )

    result_decimal_precision = schema.Int(
        title=_(u"Result Decimal Precision"),
        description=_(
            u"Define the number of decimals to be used when the result is "
            u"printed as a decimal number."),
        required=False,
    )

    keyword = schema.TextLine(
        title=_(u"Analysis Keyword"),
        description=_(
            u"The unique keywords used to identify the analysis service in "
            u"calculations, instrument imports, and bulk AR requests."),
    )

    calculation = schema.Choice(
        title=_(u"Type of Aliquot"),
        description=_(u"Possible aliquot types are controlled by the sample "
                      u"type settings."),
        vocabulary="bika.lims.vocabularies.calculation.Calculations",
        required=False,
    )

"""
MaxTimeAllowed
DuplicateVariation
Accredited
PointOfCapture
Category
Price
BulkPrice
VATAmount
TotalPrice
VAT
CategoryTitle
CategoryUID
Department
DepartmentTitle
Uncertainties
PrecisionFromUncertainty
AllowManualUncertainty
ResultOptions
Separate
Preservation
Container
PartitionSetup
Hidden
CommercialID
ProtocolID
"""
