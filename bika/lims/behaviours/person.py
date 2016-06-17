# -*- coding: utf-8 -*-
from plone.app.content.interfaces import INameFromTitle
from zope.component import adapts
from zope.interface import implements
from zope.interface import Interface


class INameFromFullname(Interface):
    """Interface to activate NameFromFullname behaviour
    """


class NameFromFullname(object):
    """Set the ID and Title of IPerson from the combined Firstname and Lastname
    """
    implements(INameFromTitle)
    adapts(INameFromFullname)

    def __new__(cls, context):
        person_title = u'%s %s' % (
            context.Firstname, context.Lastname if context.Lastname else '')
        person_id = person_title.replace(' ', '-').lower()
        context.setTitle(person_title)
        inst = super(NameFromFullname, cls).__new__(cls)
        inst.title = person_id
        return inst
