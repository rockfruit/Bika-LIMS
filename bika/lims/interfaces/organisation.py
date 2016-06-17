# -*- coding: utf-8 -*-
from bika.lims import messagefactory as _
from plone.schema import Email
from plone.supermodel import model
from zope import schema


class IOrganisation(model.Schema):
    """Base fields for all organisation types
    """
    PhoneNumber = schema.TextLine(
        title=_(u"Phone number"),
        required=False,
    )
    EmailAddress = Email(
        title=_(u"Email address"),
        required=False,
    )
    URI = schema.URI(
        title=_(u"Website"),
        required=False,
    )

    model.fieldset('Address',
                   label=_(u"Address"),
                   fields=['PhysicalAddress',
                           'PostalAddress',
                           'BillingAddress',
                           ]
                   )
    PhysicalAddress = schema.Text(
        title=_(u"Physical address"),
        required=False,
    )
    PostalAddress = schema.Text(
        title=_(u"Postal address"),
        required=False,
    )
    BillingAddress = schema.Text(
        title=_(u"Billing address"),
        required=False,
    )

    model.fieldset('banking',
                   label=_(u"Banking details"),
                   fields=['AccountType',
                           'AccountName',
                           'AccountNumber',
                           'BankName',
                           'BankBranch',
                           'TaxNumber',
                           ]
                   )
    AccountType = schema.TextLine(
        title=_(u"Account type"),
        required=False,
    )
    AccountName = schema.TextLine(
        title=_(u"Account name"),
        required=False,
    )
    AccountNumber = schema.TextLine(
        title=_(u"Account number"),
        required=False,
    )
    BankName = schema.TextLine(
        title=_(u"Bank name"),
        required=False,
    )
    BankBranch = schema.TextLine(
        title=_(u"Bank branch"),
        required=False,
    )
    TaxNumber = schema.TextLine(
        title=_(u"Tax number"),
        required=False,
    )
