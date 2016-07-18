# -*- coding: utf-8 -*-
from plone.app.contenttypes import permissions

AddAliquot = "Bika LIMS: Add Aliquot"
AddAnalysisRequest = "Bika LIMS: Add Analysis Request"
AddAnalysisService = "Bika LIMS: Add Analysis Service"
AddCalculation = "Bika LIMS: Add Calculation"
AddClient = "Bika LIMS: Add Client"
AddContact = "Bika LIMS: Add Contact"
AddDepartment = "Bika LIMS: Add Department"
AddLIMSRoot = "Bika LIMS: Add LIMSRoot"
AddLaboratory = "Bika LIMS: Add Laboratory"
AddSample = "Bika LIMS: Add Sample"
AddSamplePoint = "Bika LIMS: Add Sample Point"
AddSampleType = "Bika LIMS: Add Sample Type"


def setup_default_permissions(portal):
    """Setup default portal rolemap
    """
    mp = portal.manage_permission
    mp(AddLIMSRoot, ['Manager'], 0)
    mp(AddAliquot, [], 0)
    mp(AddAnalysisRequest, [], 0)
    mp(AddAnalysisService, [], 0)
    mp(AddCalculation, [], 0)
    mp(AddClient, [], 0)
    mp(AddContact, [], 0)
    mp(AddDepartment, [], 0)
    mp(AddLaboratory, [], 0)
    mp(AddSample, [], 0)
    mp(AddSamplePoint, [], 0)
    mp(AddSampleType, [], 0)


def disallow_default_contenttypes(context):
    """Remove the default Plone content types' add permissions
    for all roles (including Manager) in the supplied context.
    Folders can be added anywhere...
    """
    mp = context.manage_permission
    mp(permissions.AddCollection, [], 0)
    mp(permissions.AddDocument, [], 0)
    mp(permissions.AddEvent, [], 0)
    mp(permissions.AddFile, [], 0)
    mp(permissions.AddImage, [], 0)
    mp(permissions.AddLink, [], 0)
    mp(permissions.AddNewsItem, [], 0)
