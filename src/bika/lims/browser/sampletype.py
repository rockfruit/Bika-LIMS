# -*- coding: utf-8 -*-
from collective.z3cform.datagridfield import DataGridFieldFactory
from plone.dexterity.browser import add
from plone.dexterity.browser import edit
from z3c.form import field

from bika.lims import messagefactory as _
from bika.lims.interfaces.sampletype import ISampleType


class EditForm(edit.DefaultEditForm):
    label = _(u"Edit Sample Type")
    description = ""

    fields = field.Fields(ISampleType)
    fields['aliquot_types'].widgetFactory = DataGridFieldFactory

    def updateWidgets(self, prefix=None):
        super(EditForm, self).updateWidgets(prefix)
        self.widgets['aliquot_types'].allow_insert = True
        self.widgets['aliquot_types'].allow_delete = True
        self.widgets['aliquot_types'].auto_append = True
        self.widgets['aliquot_types'].allow_reorder = True
        # Hide column headers - causes display issue, wish it worked.
        # self.widgets['aliquot_types'].columns[0]['mode'] = HIDDEN_MODE
        # self.widgets['aliquot_types'].columns[1]['mode'] = HIDDEN_MODE


class AddForm(add.DefaultAddForm):
    portal_type = 'SampleType'

    label = _(u"Adds Sample Type")
    description = ""

    fields = field.Fields(ISampleType)
    fields['aliquot_types'].widgetFactory = DataGridFieldFactory

    def updateWidgets(self, prefix=None):
        super(AddForm, self).updateWidgets(prefix)
        self.widgets['aliquot_types'].allow_insert = True
        self.widgets['aliquot_types'].allow_delete = True
        self.widgets['aliquot_types'].auto_append = True
        self.widgets['aliquot_types'].allow_reorder = True
        # Hide column headers - causes display issue, wish it worked.
        # self.widgets['aliquot_types'].columns[0]['mode'] = HIDDEN_MODE
        # self.widgets['aliquot_types'].columns[1]['mode'] = HIDDEN_MODE


class AddView(add.DefaultAddView):
    form = AddForm
