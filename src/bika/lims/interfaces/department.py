# -*- coding: utf-8 -*-
from zope import schema

from plone.app.vocabularies.catalog import CatalogSource
from plone.supermodel import model
from z3c.relationfield import RelationChoice
from z3c.relationfield import RelationList

from bika.lims import messagefactory as _
from bika.lims.interfaces.contact import ILabContact


class IDepartment(model.Schema):
    """Lab departments
    """

    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    manager = RelationList(
        title=_(u"Manager"),
        value_type=RelationChoice(
            title=_(u"Manager"),
            source=CatalogSource(object_provides=ILabContact.__identifier__),
        ),
        unique=True,
        required=False,
    )
