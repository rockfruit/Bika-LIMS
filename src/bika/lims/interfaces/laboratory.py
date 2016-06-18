# -*- coding: utf-8 -*-
from zope import schema

from bika.lims import messagefactory as _
from bika.lims.interfaces.organisation import IOrganisation
from plone.supermodel import model


class ILaboratory(IOrganisation):
    """Lab Client
    """
    title = schema.TextLine(
        title=_(u"Name"),
        required=True,
    )
    model.fieldset('accreditation',
                   label=_(u"Accreditation"),
                   fields=['Confidence',
                           'Accredited',
                           'AccreditationBody',
                           'AccreditationBodyURL',
                           'Accreditation',
                           'AccreditationReference',
                           'AccreditationBodyLogo',
                           'AccreditationPageHeader',
                           ]
                   )
    Accredited = schema.Bool(
        title=_(u"Laboratory Accredited"),
        description=_(u"Check this box if your laboratory is accredited"),
        required=False
    )
    Confidence = schema.Int(
        title=_(u"Confidence Level %"),
        description=_(u"This value is reported at the bottom of all "
                      u"published results"),
        required=False
    )
    AccreditationBody = schema.TextLine(
        title=_(u"Accreditation Body"),
        description=_(u"Name of accreditation body, e.g. SANAS, APLAC, etc."),
        required=False
    )
    AccreditationBodyURL = schema.URI(
        title=_(u"Accreditation Body URL"),
        description=_(u"Web address for the accreditation body"),
        required=False
    )
    Accreditation = schema.TextLine(
        title=_(u"Accreditation"),
        description=_(u"The accreditation standard that applies, "
                      u"e.g. ISO 17025"),
        required=False
    )
    AccreditationReference = schema.URI(
        title=_(u"Accreditation Reference"),
        description=_(u"The reference code issued to the lab by the "
                      u"accreditation body"),
        required=False
    )
    AccreditationBodyLogo = namedfile.NamedBlobImage(
        title=_(u"Accreditation Logo"),
        description=_(
            u"Please upload the logo you are authorised to use on your "
            u"website and results reports by your accreditation body."),
        required=False
    )
    AccreditationPageHeader = schema.SourceText(
        title=_(u"Accreditation page header"),
        description=_(
            u"Enter the details of your lab's service accreditations here.  "
            u"The following fields are available: <br/>"
            u"&bull; lab_name<br/>"
            u"&bull; lab_country<br/>"
            u"&bull; confidence<br/>"
            u"&bull; accreditation_body<br/>"
            u"&bull; standard<br/>"
            u"&bull; reference<br/>"),
        default=u"<p>{lab_name} has been accredited as {standard} conformant "
                u"by {accreditation_body} ({reference}).</p>"
                u"<p>{accreditation_body} is the single national accreditation "
                u"body assessing testing and calibration laboratories for "
                u"compliance to the ISO/IEC 17025 standard.</p>",
        required=False
    )
