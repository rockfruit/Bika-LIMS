# -*- coding: utf-8 -*-
from Products.CMFCore.permissions import ModifyPortalContent

from bika.lims.permissions import AddAnalysisRequest
from bika.lims.permissions import AddClient
from bika.lims.permissions import AddContact
from bika.lims.permissions import AddSample
from bika.lims.permissions import AddSamplePoint
from plone import api


def Added(client, event):
    """When a new Client is created, we must create it's folder structure and
    do some configuration.

    The order in which items are created here defines the default order
    of the site navigation.

    The permissions set here are inherited by children.
    """

    # Prevent anyone from adding a Client inside of a Client
    client.manage_permission(AddClient, [], 0)

    # Create client/* folders and set permissions
    # -------------------------------------------
    for x in [
        ['samples', 'Samples'],
        ['analysisrequests', 'Analysis Requests'],
        ['configuration', 'Configuration'],
    ]:
        instance = api.content.create(client, 'Folder', x[0], x[1])

    mp = client.samples.manage_permission
    mp(AddSample, ['Manager', 'LabManager', 'LabClerk', 'Owner'], 0)
    mp(ModifyPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Owner'], 0)

    mp = client.analysisrequests.manage_permission
    mp(AddAnalysisRequest, ['Manager', 'LabManager', 'LabClerk', 'Owner'], 0)
    mp(ModifyPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Owner'], 0)

    # Create client/configuration/* and set permissions
    # -------------------------------------------------
    folder = client.configuration
    for x in [
        ['contacts', 'Contacts'],
        ['samplepoints', 'Sample Points'],
    ]:
        instance = api.content.create(folder, 'Folder', x[0], x[1])

    mp = folder.contacts.manage_permission
    mp(AddContact, ['Manager', 'LabManager', 'LabClerk', 'Owner'], 0)
    mp(ModifyPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Owner'], 0)

    mp = folder.samplepoints.manage_permission
    mp(AddSamplePoint, ['Manager', 'LabManager', 'LabClerk', 'Owner'], 0)
    mp(ModifyPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Owner'], 0)
