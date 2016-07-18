# -*- coding: utf-8 -*-
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


class AliquotTypesVocabulary():
    """Vocabulary factory for Contacts
    """

    def __init__(self):
        pass

    def __call__(self, context):
        catalog = context.portal_catalog
        proxies = catalog({
            'object_provides': 'bika.lims.interfaces.contact.IContact',
            'sort_on': 'sortable_title',
        })
        terms = [SimpleTerm(proxy.getObject(), title=proxy.Title)
                 for proxy in proxies]
        return SimpleVocabulary(terms)


AliquotTypesFactory = AliquotTypesVocabulary()


class ClientAliquotTypes():
    """Vocabulary factory showing only Client Contacts.
    """

    def __init__(self):
        pass

    def __call__(self, context):
        catalog = context.portal_catalog
        proxies = catalog({
            'object_provides': 'bika.lims.interfaces.contact.IClientContact',
            'sort_on': 'sortable_title',
        })
        terms = [SimpleTerm(proxy.getObject(), title=proxy.Title)
                 for proxy in proxies]
        return SimpleVocabulary(terms)


ClientAliquotTypesFactory = ClientAliquotTypes()


class LabAliquotTypes():
    """Vocabulary factory showing only Lab Contacts
    """

    def __init__(self):
        pass

    def __call__(self, context):

        terms = [SimpleTerm(proxy.getObject(), title=proxy.Title)
                 for proxy in proxies]
        return SimpleVocabulary(terms)


LabAliquotTypesFactory = LabAliquotTypes()
