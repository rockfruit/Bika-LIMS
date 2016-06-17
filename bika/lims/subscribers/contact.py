# -*- coding: utf-8 -*-
from bika.lims.interfaces.contact import ILabContact, IClientContact
from bika.lims.utils.lims import getLims
from zope.interface import alsoProvides


def Added(contact, event):
    """I'll apply ILabContact or IClientContact interface to contacts, to
    allow us to neatly select them later based on their context.
    """

    contextpath = '/'.join(contact.__parent__.getPhysicalPath())
    lims = getLims(contact)
    limspath = '/'.join(lims.configuration.contacts.getPhysicalPath())
    if contextpath == limspath:
        alsoProvides(contact, ILabContact)
    else:
        alsoProvides(contact, IClientContact)
    contact.reindexObject(idxs=['object_provides'])
