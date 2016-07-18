# -*- coding: utf-8 -*-
from zope import schema

from bika.lims import messagefactory as _
from plone.schema import Email
from plone.supermodel import model


class IOrganisation(model.Schema):
    """Base fields for all organisation types
    """

    phone_number = schema.TextLine(
        title=_(u"Phone number"),
        required=False,
    )

    email_address = Email(
        title=_(u"Email address"),
        required=False,
    )

    website = schema.URI(
        title=_(u"Website"),
        required=False,
    )

    model.fieldset('Address',
                   label=_(u"Address"),
                   fields=['physical_address',
                           'postal_address',
                           'billing_address',
                           ]
                   )

    physical_address = schema.Text(
        title=_(u"Physical address"),
        required=False,
    )

    postal_address = schema.Text(
        title=_(u"Postal address"),
        required=False,
    )

    billing_address = schema.Text(
        title=_(u"Billing address"),
        required=False,
    )

    model.fieldset('banking',
                   label=_(u"Banking details"),
                   fields=['account_type',
                           'account_name',
                           'account_number',
                           'bank_name',
                           'bank_branch',
                           'swift_code',
                           'tax_number',
                           ]
                   )

    account_type = schema.TextLine(
        title=_(u"Account type"),
        required=False,
    )

    account_name = schema.TextLine(
        title=_(u"Account name"),
        required=False,
    )

    account_number = schema.TextLine(
        title=_(u"Account number"),
        required=False,
    )

    bank_name = schema.TextLine(
        title=_(u"Bank name"),
        required=False,
    )

    bank_branch = schema.TextLine(
        title=_(u"Bank branch"),
        required=False,
    )

    swift_code = schema.TextLine(
        title=_(u"SWIFT code"),
        required=False,
    )

    tax_number = schema.TextLine(
        title=_(u"Tax number"),
        required=False,
    )
