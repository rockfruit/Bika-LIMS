# -*- coding: utf-8 -*-
from Products.CMFCore.permissions import ModifyPortalContent
from plone import api
from zope.component import getMultiAdapter
from zope.event import notify

from bika.lims import messagefactory as _
from bika.lims.events import LIMSCreatedEvent
from bika.lims.permissions import *


def Added(lims, event):
    """When a new LIMS root is created, we must create it's folder structure
    and do some configuration.

    The order in which items are created here defines the default order
    of the site navigation.

    The permissions set here are inherited by children.
    """

    # Prevent anyone from adding a LIMSRoot inside of a LIMSRoot
    lims.manage_permission(AddLIMSRoot, [], 0)

    create_structure(lims)
    structure_permissions(lims)
    notify(LIMSCreatedEvent(lims))


def create_structure(lims):
    for x in [
        [lims, 'Folder', 'clients', _(u"Clients")],
        [lims, 'Folder', 'samples', _(u"Samples")],
        [lims, 'Folder', 'analysisrequests', _(u"Analysis Requests")],
        [lims, 'Folder', 'configuration', _(u"Configuration")],
    ]:
        obj = api.content.create(container=x[0], type=x[1], id=x[2], title=x[3])
        obj.setLayout('folder_contents')

    configuration = lims.configuration
    for x in [
        # [configuration, 'Laboratory', 'laboratory', _(u"Laboratory")],
        [configuration, 'Folder', 'aliquoting', _(u"Aliquoting")],
        [configuration, 'Folder', 'services', _(u"Analysis Services")],
        [configuration, 'Folder', 'contacts', _(u"Contacts")],
        [configuration, 'Folder', 'departments', _(u"Departments")],
        [configuration, 'Folder', 'samplepoints', _(u"Sample Points")],
        [configuration, 'Folder', 'sampletypes', _(u"Sample Types")],
    ]:
        obj = api.content.create(container=x[0], type=x[1], id=x[2], title=x[3])
        obj.setLayout('folder_contents')


def structure_permissions(lims):
    mp = lims.clients.manage_permission
    mp(AddClient, ['Manager', 'LabManager'], 0)

    mp = lims.samples.manage_permission
    mp(AddSample, ['Manager', 'LabManager'], 0)

    mp = lims.analysisrequests.manage_permission
    mp(AddAnalysisRequest, ['Manager', 'LabManager'], 0)

    mp = lims.configuration.manage_permission
    mp(AddLaboratory, [], 0)

    mp = lims.configuration.contacts.manage_permission
    mp(AddContact, ['Manager', 'LabManager', 'LabClerk'], 0)
    mp(ModifyPortalContent, ['Manager', 'LabManager', 'LabClerk'], 0)

    mp = lims.configuration.departments.manage_permission
    mp(AddDepartment, ['Manager', 'LabManager'], 0)
    mp(ModifyPortalContent, ['Manager', 'LabManager'], 0)

    mp = lims.configuration.samplepoints.manage_permission
    mp(AddSamplePoint, ['Manager', 'LabManager'], 0)
    mp(ModifyPortalContent, ['Manager', 'LabManager'], 0)

    mp = lims.configuration.sampletypes.manage_permission
    mp(AddSampleType, ['Manager', 'LabManager'], 0)
    mp(ModifyPortalContent, ['Manager', 'LabManager'], 0)
