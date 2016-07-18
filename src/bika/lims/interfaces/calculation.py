# -*- coding: utf-8 -*-
from zope import schema

from collective.z3cform.datagridfield import DictRow
from plone.directives import form
from plone.supermodel import model
from zope.interface import Attribute

from bika.lims import messagefactory as _


class IInterimRowSchema(form.Schema):
    """A single row in the TestForm table
    """

    field_id = schema.TextLine(
        title=u"ID",
        required=True
    )

    field_title = schema.TextLine(
        title=u"Title",
        required=False
    )

    field_type = schema.Choice(
        title=_(u"Type"),
        description=_(u"Field type"),
        required=True,
        values=[_(u"Ingeger"),
                _(u"Floating point"),
                _(u"String"),
                _(u"Boolean")],
        default=u"Integer",
    )

    field_default = schema.TextLine(
        title=u"Default value",
        required=False
    )

    field_unit = schema.TextLine(
        title=u"Unit",
        required=False
    )

    field_hidden = schema.TextLine(
        title=u"Hidden field",
        required=False)

    field_apply_wide = schema.TextLine(
        title=u"Apply wide",
        required=False)


INTERIMROW_DEFAULT = [
    {'field_id': '',
     'field_title': '',
     'field_type': 'Integer',
     'field_default': '',
     'field_unit': '',
     'field_hidden': '',
     'field_apply_wide': '',
     }
]


class ICalculation(model.Schema):
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

    interim_fields = schema.List(
        title=_(u"Interim Fields"),
        description=_(
            u"Interim Fields define the inputs required by the calculation."
        ),
        value_type=DictRow(title=u"test", schema=IInterimRowSchema),
        required=True,
        default=INTERIMROW_DEFAULT
    )

    formula = schema.Text(
        title=_(u"Calculation Formula"),
        description=_(u"calculation_formula_description"),
    )

    dependent_services = Attribute("Dependent Services")
