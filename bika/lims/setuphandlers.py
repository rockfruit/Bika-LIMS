# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INavigationSchema
from bika.lims.permissions import *
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


def setupRolesAndGroups(context):
    """Configure roles and groups
    """
    portal = context.getSite()
    if context.readDataFile('bika.lims.txt') is None:
        return

    # add roles
    prm = portal.acl_users.portal_role_manager
    for role in (
            'LabManager',
            'LabClerk',
            'Analyst',
            'Verifier',
            'Sampler',
            'Preserver',
            'Publisher',
            'Member',
            'Reviewer',
            'RegulatoryInspector',
            'Client'
    ):
        if role not in prm.listRoleIds():
            prm.addRole(role)
        # add roles to the portal
        portal._addRole(role)

    # Create groups
    portal_groups = portal.portal_groups
    groups = portal_groups.listGroupIds()
    addgroup = portal_groups.addGroup
    if 'LabManagers' not in groups:
        addgroup('LabManagers', title="Lab Managers",
                 roles=['Member', 'LabManager', ])
    if 'LabClerks' not in groups:
        addgroup('LabClerks', title="Lab Clerks",
                 roles=['Member', 'LabClerk'])
    if 'Analysts' not in groups:
        addgroup('Analysts', title="Lab Technicians",
                 roles=['Member', 'Analyst'])
    if 'Verifiers' not in groups:
        addgroup('Verifiers', title="Verifiers",
                 roles=['Verifier'])
    if 'Samplers' not in groups:
        addgroup('Samplers', title="Samplers",
                 roles=['Sampler'])
    if 'Preservers' not in groups:
        addgroup('Preservers', title="Preservers",
                 roles=['Preserver'])
    if 'Publishers' not in groups:
        addgroup('Publishers', title="Publishers",
                 roles=['Publisher'])
    if 'Clients' not in groups:
        addgroup('Clients', title="Clients",
                 roles=['Member', 'Client'])
    if 'Suppliers' not in groups:
        addgroup('Suppliers', title="Suppliers",
                 roles=['Member', ])
    if 'RegulatoryInspectors' not in groups:
        addgroup('RegulatoryInspectors', title="Regulatory Inspectors",
                 roles=['Member', 'RegulatoryInspector'])


def setupPermissions(context):
    """Configure default permissions for all folders
    """
    portal = context.getSite()
    if context.readDataFile('bika.lims.txt') is None:
        return
    mp = portal.manage_permission

    # LIMS may be added by admin users:
    mp(AddLIMS, ['Manager'], 0)

    # All other objects cannot be added at the root.
    mp(AddAliquot, [], 0)
    mp(AddAnalysisRequest, [], 0)
    mp(AddClient, [], 0)
    mp(AddContact, [], 0)
    mp(AddDepartment, [], 0)
    mp(AddLaboratory, [], 0)
    mp(AddSample, [], 0)
    mp(AddSamplePoint, [], 0)
    mp(AddSampleType, [], 0)

def setupVarious(context):
    portal = context.getSite()
    if context.readDataFile('bika.lims.txt') is None:
        return

    # Display 'LIMS' objects in the navigation
    registry = getUtility(IRegistry)
    settings = registry.forInterface(INavigationSchema, prefix="plone")
    settings.displayed_types = tuple(list(settings.displayed_types) + ['LIMS'])
