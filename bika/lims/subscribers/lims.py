# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from bika.lims import messagefactory as _
from Products.CMFCore.permissions import ModifyPortalContent
from bika.lims.permissions import *
from plone import api


def Added(lims, event):
    """When a new LIMS is created, we must create it's folder structure and
    do some configuration.

    The order in which items are created here defines the default order
    of the site navigation.

    The permissions set here are inherited by children.
    """

    # Prevent anyone from adding a LIMS inside of a LIMS
    lims.manage_permission(AddLIMS, [], 0)

    # Create root folders and set their permissions
    # ---------------------------------------------
    for x in [
        ['Folder', 'clients', _(u"Clients")],
        ['Folder', 'samples', _(u"Samples")],
        ['Folder', 'analysisrequests', _(u"Analysis Requests")],
        ['Folder', 'configuration', _(u"Configuration")],
    ]:
        api.content.create(lims, x[0], x[1], x[2])

    mp = lims.clients.manage_permission
    mp(AddClient, ['Manager', 'LabManager'], 0)

    mp = lims.samples.manage_permission
    mp(AddSample, ['Manager', 'LabManager'], 0)

    mp = lims.analysisrequests.manage_permission
    mp(AddAnalysisRequest, ['Manager', 'LabManager'], 0)

    # Create configuration/* and set permissions
    # ------------------------------------------
    configuration = lims.configuration
    for x in [
        #['Laboratory', 'laboratory', _(u"Laboratory")],
        ['Folder', 'contacts', _(u"Contacts")],
        ['Folder', 'departments', _(u"Departments")],
        ['Folder', 'samplepoints', _(u"Sample Points")],
        ['Folder', 'sampletypes', _(u"Sample Types")],
    ]:
        api.content.create(configuration, x[0], x[1], x[2])

    mp = configuration.manage_permission
    mp(AddLaboratory, [], 0)

    mp = configuration.contacts.manage_permission
    mp(AddContact, ['Manager', 'LabManager', 'LabClerk'], 0)
    mp(ModifyPortalContent, ['Manager', 'LabManager', 'LabClerk'], 0)

    mp = configuration.departments.manage_permission
    mp(AddDepartment, ['Manager', 'LabManager'], 0)
    mp(ModifyPortalContent, ['Manager', 'LabManager'], 0)

    mp = configuration.samplepoints.manage_permission
    mp(AddSamplePoint, ['Manager', 'LabManager'], 0)
    mp(ModifyPortalContent, ['Manager', 'LabManager'], 0)

    mp = configuration.sampletypes.manage_permission
    mp(AddSampleType, ['Manager', 'LabManager'], 0)
    mp(ModifyPortalContent, ['Manager', 'LabManager'], 0)

