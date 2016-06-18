# -*- coding: utf-8 -*-
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


class SamplesVocabulary():
    """Vocabulary factory for Samples
    """

    def __init__(self):
        pass

    def __call__(self, context):
        catalog = context.portal_catalog
        proxies = catalog({
            'object_provides': 'bika.lims.interfaces.sample.ISample',
            'sort_on': 'sortable_title',
        })
        terms = [SimpleTerm(proxy.getObject(), title=proxy.Title)
                 for proxy in proxies]
        return SimpleVocabulary(terms)


SamplesVocabularyFactory = SamplesVocabulary()
