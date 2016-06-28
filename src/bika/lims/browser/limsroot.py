# -*- coding: utf-8 -*-
# from bika.lims import messagefactory as _
# from bika.lims.interfaces.lims.interfaces import ILIMSRoot
# from collective.z3cform.datagridfield import DataGridFieldFactory
# from plone.dexterity.browser import add
# from plone.dexterity.browser import edit
# from z3c.form import field
# from z3c.form.interfaces import HIDDEN_MODE
#
#
# class EditForm(edit.DefaultEditForm):
#     label = _(u"Edit LIMS details")
#     description = _(u"You can edit the laboratory details below.")
#
#     fields = field.Fields(ILIMSRoot)
#     fields['PhoneNumbers'].widgetFactory = DataGridFieldFactory
#
#     def updateWidgets(self, prefix=None):
#         super(EditForm, self).updateWidgets(prefix)
#         self.widgets['PhoneNumbers'].allow_insert = False
#         self.widgets['PhoneNumbers'].allow_delete = True
#         self.widgets['PhoneNumbers'].auto_append = True
#         self.widgets['PhoneNumbers'].allow_reorder = False
#         # Hide column headers
#         self.widgets['PhoneNumbers'].columns[0]['mode'] = HIDDEN_MODE
#         self.widgets['PhoneNumbers'].columns[1]['mode'] = HIDDEN_MODE
#
#
# class AddForm(add.DefaultAddForm):
#     portal_type = 'LIMSRoot'
#
#     label = _(u"Create a new LIMS root folder")
#     description = _(u"After you complete some laboratory information in the "
#                     u"fields below, this folder will contain a LIMS system.")
#
#     fields = field.Fields(ILIMSRoot)
#     fields['PhoneNumbers'].widgetFactory = DataGridFieldFactory
#
#     def updateWidgets(self, prefix=None):
#         super(AddForm, self).updateWidgets(prefix)
#         self.widgets['PhoneNumbers'].allow_insert = False
#         self.widgets['PhoneNumbers'].allow_delete = True
#         self.widgets['PhoneNumbers'].auto_append = True
#         self.widgets['PhoneNumbers'].allow_reorder = False
#         # Hide column headers
#         self.widgets['PhoneNumbers'].columns[0]['mode'] = HIDDEN_MODE
#         self.widgets['PhoneNumbers'].columns[1]['mode'] = HIDDEN_MODE
#
#
# class AddView(add.DefaultAddView):
#     form = AddForm

from Products.Five import BrowserView
from plone import api

class ViewView(BrowserView):
   """
   """
   def fieldnames(self):
       import pdb;pdb.set_trace()
