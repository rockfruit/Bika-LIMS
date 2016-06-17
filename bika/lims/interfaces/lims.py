from bika.lims import messagefactory as _
from bika.lims.interfaces.organisation import IOrganisation
from plone.supermodel import model
from zope import schema


class ILIMS(model.Schema):
    """The LIMS root object.
    """
    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )
    model.fieldset('settings',
                   label=_(u"Settings"),
                   fields=['title',
                           ]
                   )
