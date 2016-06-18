# -*- coding: utf-8 -*-
from zope import schema

from bika.lims import messagefactory as _
from plone.schema import Email
from plone.supermodel import model
from zope.interface import Interface


class IPerson(Interface):
    """Doctor and Patient are based on this
    """
    Salutation = schema.TextLine(
        title=_(u"Salutation"),
        required=False,
    )
    Firstname = schema.TextLine(
        title=_(u"First name"),
        required=True,
    )
    Middlename = schema.TextLine(
        title=_(u"Middle name"),
        required=False,
    )
    Lastname = schema.TextLine(
        title=_(u"Last name"),
        required=False,
    )
    PhoneNumbers = schema.List(
        title=_(u"Phone numbers"),
        description=_(u"List of contact telephone and fax numbers"),
        value_type=schema.TextLine(),
        unique=True,
        required=False,
    )
    EmailAddress = Email(
        title=_(u"Email address"),
        description=_(u"Email address"),
        required=False,
    )
    JobTitle = schema.TextLine(
        title=_(u"Job title"),
        required=False,
    )

    model.fieldset('address',
                   label=_(u"Address"),
                   fields=['PhysicalAddress',
                           'PostalAddress',
                           'BillingAddress',
                           ]
                   )
    PhysicalAddress = schema.Text(
        title=_("Physical address"),
        required=False,
    )
    PostalAddress = schema.Text(
        title=_("Postal address"),
        required=False,
    )
    BillingAddress = schema.Text(
        title=_("Billing address"),
        required=False,
    )

    model.fieldset('logindetails',
                   label=_(u"Login Details"),
                   fields=['Username',
                           'Password',
                           ]
                   )
    Username = schema.TextLine(
        title=_(u"Username"),
        required=False,
    )
    Password = schema.Password(
        title=_(u"Password"),
        required=False,
    )
