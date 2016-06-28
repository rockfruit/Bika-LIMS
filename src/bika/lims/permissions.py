# -*- coding: utf-8 -*-
from plone.app.contenttypes import permissions

AddAliquot = "Bika LIMS: Add Aliquot"
AddAnalysisRequest = "Bika LIMS: Add Analysis Request"
AddClient = "Bika LIMS: Add Client"
AddContact = "Bika LIMS: Add Contact"
AddDepartment = "Bika LIMS: Add Department"
AddLIMSRoot = "Bika LIMS: Add LIMSRoot"
AddLaboratory = "Bika LIMS: Add Laboratory"
AddSample = "Bika LIMS: Add Sample"
AddSamplePoint = "Bika LIMS: Add Sample Point"
AddSampleType = "Bika LIMS: Add Sample Type"


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
