# -*- coding: utf-8 -*-
from zope import schema

from plone.schema import Email
from plone.supermodel import model
from zope.interface import Interface

from bika.lims import messagefactory as _


class IPerson(Interface):
    """All person things
    """
    first_name = schema.TextLine(
        title=_(u"First name"),
        required=True,
    )

    middle_name = schema.TextLine(
        title=_(u"Middle name"),
        required=False,
    )

    last_name = schema.TextLine(
        title=_(u"Last name"),
        required=False,
    )

    phone_numbers = schema.List(
        title=_(u"Phone numbers"),
        description=_(u"List of contact telephone and fax numbers"),
        value_type=schema.TextLine(),
        unique=True,
        required=False,
    )

    email_address = Email(
        title=_(u"Email address"),
        description=_(u"Email address"),
        required=False,
    )

    job_title = schema.TextLine(
        title=_(u"Job title"),
        required=False,
    )

    model.fieldset('address',
                   label=_(u"Address"),
                   fields=['physical_address',
                           'postal_address',
                           'billing_address',
                           ]
                   )

    physical_address = schema.Text(
        title=_("Physical address"),
        required=False,
    )

    postal_address = schema.Text(
        title=_("Postal address"),
        required=False,
    )

    billing_address = schema.Text(
        title=_("Billing address"),
        required=False,
    )

    model.fieldset('logindetails',
                   label=_(u"Login Details"),
                   fields=['username',
                           'password',
                           ]
                   )

    username = schema.TextLine(
        title=_(u"Username"),
        required=False,
    )

    password = schema.Password(
        title=_(u"Password"),
        required=False,
    )
