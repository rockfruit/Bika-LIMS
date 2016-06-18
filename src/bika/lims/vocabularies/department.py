# -*- coding: utf-8 -*-
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


class DepartmentsVocabulary():
    """Vocabulary factory for Departments
    """

    def __init__(self):
        pass

    def __call__(self, context):
        catalog = context.portal_catalog
        proxies = catalog({
            'object_provides': 'bika.lims.interfaces.department.IDepartment',
            'sort_on': 'sortable_title',
        })
        terms = [SimpleTerm(proxy.getObject(), title=proxy.Title)
                 for proxy in proxies]
        return SimpleVocabulary(terms)


DepartmentsVocabularyFactory = DepartmentsVocabulary()
