# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INavigationSchema
from Products.CMFPlone.interfaces import INonInstallable
from bika.lims.permissions import setup_default_permissions
from plone import api
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.interface import implementer

from bika.lims import messagefactory as _


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller"""
        return [
            'bika.lims:uninstall',
        ]


def setup_roles(context):
    """Configure roles
    """
    portal = context.getSite()
    if not context.readDataFile('bikalims_default.txt'):
        return

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
        portal._addRole(role)


def setup_groups(context):
    """Configure groups
    """
    portal = context.getSite()
    if not context.readDataFile('bikalims_default.txt'):
        return

    portal_groups = portal.portal_groups
    groups = portal_groups.listGroupIds()
    addgroup = portal_groups.addGroup
    if 'LabManagers' not in groups:
        addgroup('LabManagers',
                 title="Lab Managers",
                 roles=['Member', 'LabManager', ])
    if 'LabClerks' not in groups:
        addgroup('LabClerks',
                 title="Lab Clerks",
                 roles=['Member', 'LabClerk'])
    if 'Analysts' not in groups:
        addgroup('Analysts',
                 title="Lab Technicians",
                 roles=['Member', 'Analyst'])
    if 'Verifiers' not in groups:
        addgroup('Verifiers',
                 title="Verifiers",
                 roles=['Verifier'])
    if 'Samplers' not in groups:
        addgroup('Samplers',
                 title="Samplers",
                 roles=['Sampler'])
    if 'Preservers' not in groups:
        addgroup('Preservers',
                 title="Preservers",
                 roles=['Preserver'])
    if 'Publishers' not in groups:
        addgroup('Publishers',
                 title="Publishers",
                 roles=['Publisher'])
    if 'Clients' not in groups:
        addgroup('Clients',
                 title="Clients",
                 roles=['Member', 'Client'])
    if 'Suppliers' not in groups:
        addgroup('Suppliers',
                 title="Suppliers",
                 roles=['Member', ])
    if 'RegulatoryInspectors' not in groups:
        addgroup('RegulatoryInspectors',
                 title="Regulatory Inspectors",
                 roles=['Member', 'RegulatoryInspector'])


def setup_permissions(context):
    """Setup the default site root permissions
    """
    portal = context.getSite()
    if not context.readDataFile('bikalims_default.txt'):
        return

    setup_default_permissions(portal)


def uninstall(context):
    """Uninstall script"""
    if not context.readDataFile('bikalims_uninstall.txt'):
        return
    # Do something during the uninstallation of this package
    pass


def postInstall(context):
    portal = context.getSite()
    if not context.readDataFile('bikalims_default.txt'):
        return

    setup_roles(context)
    setup_groups(context)
    setup_permissions(context)

    create_lims(portal)
    add_to_displayed_types('LIMSRoot')


def add_to_displayed_types(typename):
    registry = getUtility(IRegistry)
    settings = registry.forInterface(INavigationSchema, prefix="plone")
    displayed_types = list(settings.displayed_types)
    if typename not in displayed_types:
        displayed_types.append('LIMSRoot')
        settings.displayed_types = tuple(displayed_types)


def create_lims(portal):
    if 'lims' not in portal:
        obj = api.content.create(portal, 'LIMSRoot', 'lims', _(u"LIMS"))
