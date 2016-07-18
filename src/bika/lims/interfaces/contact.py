# -*- coding: utf-8 -*-
from zope import schema

from bika.lims import messagefactory as _
from bika.lims.interfaces.person import IPerson
from plone.autoform import directives
from plone.formwidget.autocomplete import AutocompleteMultiFieldWidget
from plone.supermodel import model


class IContact(IPerson):
    """Base for all types of Contacts
    """


class IClientContact(IContact):
    """Client Contact
    """

    model.fieldset('publicationpreference',
                   label=_(u"Publication preference"),
                   fields=['cc_contacts',
                           'attachments_permitted',
                           ]
                   )
    directives.widget(cc_contacts=AutocompleteMultiFieldWidget)

    cc_contacts = schema.List(
        title=_(u"Contacts to CC"),
        description=_(u"The selected contacts will be included when "
                      u"notifications and publications are sent."),
        value_type=schema.Choice(
            vocabulary='bika.lims.vocabularies.ClientContacts'
        ),
        required=False,
        unique=True,
    )

    attachments_permitted = schema.Bool(
        title=_(u"Results attachments permitted"),
        description=_(
            u"File attachments to results, e.g. microscope photos, will be "
            u"included in emails to recipients if this option is enabled"
        ),
        required=False,
    )


class ILabContact(IContact):
    """Lab Contact
    """
