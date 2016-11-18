# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
import os

import App
from DateTime.DateTime import DateTime
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from bika.lims import bikaMessageFactory as _, logger
from bika.lims.browser import BrowserView, ulocalized_time
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.interfaces import IClient, IARImportHandler
from bika.lims.utils import tmpID
from bika.lims.workflow import getTransitionDate, doActionFor
from collective.progressbar.events import InitialiseProgressBar, \
    UpdateProgressEvent
from collective.progressbar.events import ProgressBar
from collective.progressbar.events import ProgressState
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.layout.globals.interfaces import IViewView
from plone.protect import CheckAuthenticator
from zope import event
from zope.component import getAdapter
from zope.event import notify
from zope.interface import alsoProvides
from zope.interface import implements


class ARImportsView(BikaListingView):
    implements(IViewView)

    def __init__(self, context, request):
        super(ARImportsView, self).__init__(context, request)
        request.set('disable_plone.rightcolumn', 1)
        alsoProvides(request, IContentListing)

        self.catalog = "portal_catalog"
        self.contentFilter = {
            'portal_type': 'ARImport',
            'cancellation_state': 'active',
            'sort_on': 'sortable_title',
        }
        self.context_actions = {}
        if IClient.providedBy(self.context):
            self.context_actions = {
                _('AR Import'): {
                    'url': 'arimport_add',
                    'icon': '++resource++bika.lims.images/add.png'}}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 50
        self.form_id = "arimports"

        self.icon = \
            self.portal_url + "/++resource++bika.lims.images/arimport_big.png"
        self.title = self.context.translate(_("Analysis Request Imports"))
        self.description = ""

        self.columns = {
            'Title': {'title': _('Title')},
            'Client': {'title': _('Client')},
            'Filename': {'title': _('Filename')},
            'Creator': {'title': _('Date Created')},
            'DateCreated': {'title': _('Date Created')},
            'DateValidated': {'title': _('Date Validated')},
            'DateImported': {'title': _('Date Imported')},
            'state_title': {'title': _('State')},
        }
        self.review_states = [
            {'id': 'default',
             'title': _('Pending'),
             'contentFilter': {'review_state': ['invalid', 'valid'],
                               'cancellation_state': 'active'
                               },
             'columns': ['Title',
                         'Creator',
                         'Filename',
                         'Client',
                         'DateCreated',
                         'DateValidated',
                         'DateImported',
                         'state_title']},
            {'id': 'imported',
             'title': _('Imported'),
             'contentFilter': {'review_state': 'imported',
                               'cancellation_state': 'active'
                               },
             'columns': ['Title',
                         'Creator',
                         'Filename',
                         'Client',
                         'DateCreated',
                         'DateValidated',
                         'DateImported']},
            {'id': 'cancelled',
             'title': _('Cancelled'),
             'contentFilter': {'review_state': ['invalid', 'valid', 'imported'],
                               'cancellation_state': 'cancelled'
                               },
             'columns': ['Title',
                         'Creator',
                         'Filename',
                         'Client',
                         'DateCreated',
                         'DateValidated',
                         'DateImported',
                         'state_title']},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['Title',
                         'Creator',
                         'Filename',
                         'Client',
                         'DateCreated',
                         'DateValidated',
                         'DateImported',
                         'state_title']},
        ]

    def folderitems(self, **kwargs):
        items = super(ARImportsView, self).folderitems()
        for x in range(len(items)):
            if 'obj' not in items[x]:
                continue
            obj = items[x]['obj']
            items[x]['Title'] = obj.title_or_id()
            if items[x]['review_state'] == 'invalid':
                items[x]['replace']['Title'] = "<a href='%s/edit'>%s</a>" % (
                    obj.absolute_url(), items[x]['Title'])
            else:
                items[x]['replace']['Title'] = "<a href='%s/view'>%s</a>" % (
                    obj.absolute_url(), items[x]['Title'])
            items[x]['Creator'] = obj.Creator()
            items[x]['Filename'] = obj.getFilename()
            parent = obj.aq_parent
            items[x]['Client'] = parent if IClient.providedBy(parent) else ''
            items[x]['replace']['Client'] = "<a href='%s'>%s</a>" % (
                parent.absolute_url(), parent.Title())
            items[x]['DateCreated'] = ulocalized_time(
                obj.created(), long_format=True, time_only=False, context=obj)
            date = getTransitionDate(obj, 'validate')
            items[x]['DateValidated'] = date if date else ''
            date = getTransitionDate(obj, 'import')
            items[x]['DateImported'] = date if date else ''

        return items


class ClientARImportsView(ARImportsView):
    def __init__(self, context, request):
        super(ClientARImportsView, self).__init__(context, request)
        self.contentFilter['path'] = {
            'query': '/'.join(context.getPhysicalPath())
        }

        self.review_states = [
            {'id': 'default',
             'title': _('Pending'),
             'contentFilter': {'review_state': ['invalid', 'valid']},
             'columns': ['Title',
                         'Creator',
                         'Filename',
                         'DateCreated',
                         'DateValidated',
                         'DateImported',
                         'state_title']},
            {'id': 'imported',
             'title': _('Imported'),
             'contentFilter': {'review_state': 'imported'},
             'columns': ['Title',
                         'Creator',
                         'Filename',
                         'DateCreated',
                         'DateValidated',
                         'DateImported',
                         'state_title']},
            {'id': 'cancelled',
             'title': _('Cancelled'),
             'contentFilter': {
                 'review_state': ['initial', 'invalid', 'valid', 'imported'],
                 'cancellation_state': 'cancelled'
             },
             'columns': ['Title',
                         'Creator',
                         'Filename',
                         'DateCreated',
                         'DateValidated',
                         'DateImported',
                         'state_title']},
        ]


class ClientARImportAddView(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile('templates/arimport_add_form.pt')

    def __init__(self, context, request):
        super(ClientARImportAddView, self).__init__(context, request)
        alsoProvides(request, IContentListing)

    def debug_mode(self):
        return App.config.getConfiguration().debug_mode

    def __call__(self):
        CheckAuthenticator(self.request.form)

        if self.request.form.get('submitted', False):

            csvfile = self.request.form.get('csvfile')
            rawdata = csvfile.read()
            fullfilename = csvfile.filename
            fullfilename = fullfilename.split('/')[-1]
            filename = fullfilename.split('.')[0]

            # Create the arimport object
            arimport = _createObjectByType("ARImport", self.context, tmpID())
            arimport.processForm()
            arimport.setTitle(self.mkTitle(filename))
            arimport.Schema()['RawData'].set(arimport, rawdata)

            # This can be overridden in other packages, so that client code
            # can control the arimport processing
            # See also IARImportSchema
            adapter = getAdapter(self, interface=IARImportHandler,
                                 name="ARImportHandler")(self.request, arimport)

            # attempt to validate and parse form data into arimport fields
            adapter.parse_raw_data()
            adapter.validate_arimport()

            url = arimport.absolute_url() + "/view"
            return self.request.response.redirect(url)

        else:

            return self.template()

    def mkTitle(self, filename):
        pc = getToolByName(self.context, 'portal_catalog')
        nr = 1
        while True:
            newname = '%s-%s' % (os.path.splitext(filename)[0], nr)
            existing = pc(portal_type='ARImport', title=newname)
            if not existing:
                return newname
            nr += 1


class ImportHandler():
    """Create a custom version of this in an addon to override the behaviours of
    ARImports.
    """
    implements(IARImportHandler)

    def __init__(self, context):
        self.context = context
        self.request = None
        self.arimport = None
        self.data = []

    def __call__(self, request, arimport):
        self.request = request
        self.arimport = arimport
        return self

    def parse_raw_data(self):
        """Create ARImport and ARImportItem and set schema fields from the
        raw data.
        Handled instead by the import function.
        """
        csvfile = self.request.form.get('csvfile')
        fullfilename = csvfile.filename
        fullfilename = fullfilename.split('/')[-1]
        filename = fullfilename.split('.')[0]

        log = []

        client = r[0].getObject()
        reader = self.arimport.Schema()['RawData'].get(self.arimport)
        samples = []
        sample_headers = None
        batch_headers = None
        batch_remarks = []
        row_count = 0
        for n, row in enumerate(reader):
            row_count = row_count + 1
            if not row:
                continue
            # a new batch starts
            if row_count == 1:
                if row[0] == 'Header':
                    continue
                else:
                    msg = '%s invalid batch header' % row
                    self.data['errors'].append(msg)
                    return None, msg
            elif row_count == 2:
                msg = None
                if row[1] != 'Import':
                    msg = 'Invalid batch header - Import required in cell B2'
                    self.data['errors'].append(msg)
                    return None, msg
                entered_name = fullfilename.split('.')[0]
                if not row[2] or entered_name.lower() != row[2].lower():
                    msg = 'Filename, %s, does not match entered filename, %s' \
                          % (filename, row[2])
                    self.data['errors'].append(msg)
                    return None, msg

                batch_headers = row[0:]
                title = filename
                idx = 1
                while title in [i.Title() for i in client.objectValues()]:
                    title = '%s-%s' % (filename, idx)
                    idx += 1
                continue
            elif row_count == 3:
                sample_headers = row[10:]
                continue
            elif row_count in [4, 5, 6]:
                continue
            # otherwise add to list of sample
            samples.append(row)
        if not row_count:
            msg = 'Invalid batch header'
            self.data['errors'].append(msg)
            return None, msg

        self.progressbar_init("Reading and verifying file data")

        for n, sample in enumerate(samples):
            next_num = tmpID()
            item_remarks = []
            self.progressbar_progress(n, len(samples))
            analyses = []
            for i in range(10, len(sample)):
                if sample[i] != '1':
                    continue
                analyses.append(sample_headers[(i - 10)])
            if len(analyses) > 0:
                aritem_id = '%s_%s' % ('aritem', (str(next_num)))
                aritem = _createObjectByType("ARImportItem", self.arimport,
                                             aritem_id)
                aritem.edit(
                    SampleName=sample[0],
                    ClientRef=sample[1],
                    SampleDate=sample[2],
                    SampleType=sample[3],
                    SampleMatrix=sample[4],
                    PickingSlip=sample[5],
                    ContainerType=sample[6],
                    ReportDryMatter=sample[7],
                    Priority=sample[8],
                )

                aritem.setRemarks(item_remarks)
                aritem.setAnalyses(analyses)

        cc_names_report = ','.join(
            [i.strip() for i in batch_headers[6].split(';')]) \
            if (batch_headers and len(batch_headers) > 7) else ""
        cc_emails_report = ','.join(
            [i.strip() for i in batch_headers[7].split(';')]) \
            if batch_headers and len(batch_headers) > 8 else ""
        cc_emails_invoice = ','.join(
            [i.strip() for i in batch_headers[8].split(';')]) \
            if batch_headers and len(batch_headers) > 9 else ""

        try:
            numOfSamples = int(batch_headers[12])
        except:
            numOfSamples = 0
        self.arimport.edit(
            FileName=batch_headers[2],
            ClientTitle=batch_headers[3],
            ClientID=batch_headers[4],
            ContactID=batch_headers[5],
            CCNamesReport=cc_names_report,
            CCEmailsReport=cc_emails_report,
            CCEmailsInvoice=cc_emails_invoice,
            OrderID=batch_headers[9],
            QuoteID=batch_headers[10],
            SamplePoint=batch_headers[11],
            NumberSamples=numOfSamples,
            Remarks=batch_remarks,
            Analyses=sample_headers,
            DateImported=DateTime(),
        )
        self.arimport._renameAfterCreation()

    def import_parsed_data(self, arimport):
        """Create and update objects from the parsed data
        # This one cheats, and does a bunch of validation stuff.
        """

        uc = arimport.uid_catalog

        ars = []
        samples = []
        client = arimport.aq_parent
        contact_obj = None
        cc_contact_obj = None

        valid_batch = False

        # validate contact
        for contact in client.objectValues('Contact'):
            if contact.getUsername() == arimport.getContactID():
                contact_obj = contact
            if arimport.getCCContactID() == None:
                if contact_obj != None:
                    break
            else:
                if contact.getUsername() == arimport.getCCContactID():
                    cc_contact_obj = contact
                    if contact_obj != None:
                        break

        if contact_obj == None:
            valid_batch = False

        # get Keyword to ServiceId Map
        services = {}
        service_uids = {}

        for service in arimport.bika_setup_catalog(
                portal_type='AnalysisService'):
            obj = service.getObject()
            keyword = obj.getKeyword()
            if keyword:
                services[keyword] = '%s:%s' % (obj.UID(), obj.getPrice())
            service_uids[obj.UID()] = '%s:%s' % (obj.UID(), obj.getPrice())

        samplepoints = arimport.bika_setup_catalog(
            portal_type='SamplePoint',
            Title=arimport.getSamplePoint())
        if not samplepoints:
            valid_batch = False

        profiles = {}
        aritems = arimport.objectValues('ARImportItem')

        request = arimport.REQUEST
        title = 'Submitting AR Import'
        # Initialize the Progress Bar
        self.progressbar_init("Importing File")

        item_count = len(aritems)
        prefix = 'Sample'
        for n, aritem in enumerate(aritems):
            # set up analyses
            ar_profile = None
            analyses = []

            for profilekey in aritem.getAnalysisProfile():
                this_profile = None
                if not profiles.has_key(profilekey):
                    profiles[profilekey] = []
                    # there is no profilekey index
                    l_prox = arimport._findProfileKey(profilekey)
                    if l_prox:
                        profiles[profilekey] = \
                            [s.UID() for s in l_prox.getService()]
                        this_profile = l_prox
                    else:
                        # TODO This will not find it!!
                        # there is no profilekey index
                        c_prox = arimport.bika_setup_catalog(
                            portal_type='AnalysisProfile',
                            getClientUID=client.UID(),
                            getProfileKey=profilekey)
                        if c_prox:
                            obj = c_prox[0].getObject()
                            profiles[profilekey] = \
                                [s.UID() for s in obj.getService()]
                            this_profile = obj

                if ar_profile is None:
                    ar_profile = obj
                else:
                    ar_profile = None
                profile = profiles[profilekey]
                for analysis in profile:
                    if not service_uids.has_key(analysis):
                        service = uc.lookupObject(analysis)
                        keyword = service.getKeyword()
                        service_uids[obj.UID()] = '%s:%s' % (
                            obj.UID(), obj.getPrice())
                        if keyword:
                            services[keyword] = '%s:%s' % (
                                obj.UID(), obj.getPrice())

                    if service_uids.has_key(analysis):
                        if not service_uids[analysis] in analyses:
                            analyses.append(service_uids[analysis])
                    else:
                        valid_batch = False

            for analysis in aritem.getAnalyses(full_objects=True):
                if not services.has_key(analysis):
                    for service in arimport.bika_setup_catalog(
                            portal_type='AnalysisService',
                            getKeyword=analysis):
                        obj = service.getObject()
                        services[analysis] = '%s:%s' % (
                            obj.UID(), obj.getPrice())
                        service_uids[obj.UID()] = '%s:%s' % (
                            obj.UID(), obj.getPrice())

                if services.has_key(analysis):
                    analyses.append(services[analysis])
                else:
                    valid_batch = False

            sampletypes = arimport.portal_catalog(
                portal_type='SampleType',
                sortable_title=aritem.getSampleType().lower(),
            )
            if not sampletypes:
                valid_batch = False
                return
            sampletypeuid = sampletypes[0].getObject().UID()

            samplematrices = arimport.bika_setup_catalog(
                portal_type='SampleMatrix',
                sortable_title=aritem.getSampleMatrix().lower(),
            )
            if not samplematrices:
                valid_batch = False
                return
            samplematrixuid = samplematrices[0].getObject().UID()

            if aritem.getSampleDate():
                date_items = aritem.getSampleDate().split('/')
                sample_date = DateTime(
                    int(date_items[2]), int(date_items[0]), int(date_items[1]))
            else:
                sample_date = None

            sample_id = '%s-%s' % (prefix, tmpID())
            sample = _createObjectByType("Sample", client, sample_id)
            sample.unmarkCreationFlag()
            sample.edit(
                SampleID=sample_id,
                ClientReference=aritem.getClientRef(),
                ClientSampleID=aritem.getClientSid(),
                SampleType=aritem.getSampleType(),
                SampleMatrix=aritem.getSampleMatrix(),
                DateSampled=sample_date,
                SamplingDate=sample_date,
                DateReceived=DateTime(),
                Remarks=aritem.getClientRemarks(),
            )
            sample._renameAfterCreation()
            sample.setSamplePoint(arimport.getSamplePoint())
            sample.setSampleID(sample.getId())
            event.notify(ObjectInitializedEvent(sample))
            sample.at_post_create_script()
            sample_uid = sample.UID()
            samples.append(sample_id)
            aritem.setSample(sample_uid)

            priorities = arimport.bika_setup_catalog(
                portal_type='ARPriority',
                sortable_title=aritem.Priority.lower(),
            )
            if len(priorities) < 1:
                logger.warning(
                    'Invalid Priority: validation should have prevented this')
                priority = ''
            else:
                priority = priorities[0].getObject()

            ar_id = tmpID()
            ar = _createObjectByType("AnalysisRequest", client, ar_id)
            report_dry_matter = False

            ar.unmarkCreationFlag()
            ar.edit(
                RequestID=ar_id,
                Contact=arimport.getContact(),
                CCContact=arimport.getCCContact(),
                CCEmails=arimport.getCCEmailsInvoice(),
                ClientOrderNumber=arimport.getOrderID(),
                ReportDryMatter=report_dry_matter,
                Profile=ar_profile,
                Analyses=analyses,
                Remarks=aritem.getClientRemarks(),
                Priority=priority,
            )
            ar.setSample(sample_uid)
            sample = ar.getSample()
            ar.setSampleType(sampletypeuid)
            ar.setSampleMatrix(samplematrixuid)
            ar_uid = ar.UID()
            aritem.setAnalysisRequest(ar_uid)
            ars.append(ar_id)
            ar._renameAfterCreation()
            self.progressbar_progress(n + 1, item_count)
            arimport._add_services_to_ar(ar, analyses)

        arimport.setDateApplied(DateTime())
        arimport.reindexObject()

    def validate_arimport(self, instance):
        """Validation assumes the form_data has been parsed, and that
        the fields of the ARImport have been populated.

        Return true if all field values are valid.
        """
        pc = getToolByName(instance, 'portal_catalog')
        bsc = getToolByName(instance, 'bika_setup_catalog')
        client = instance.aq_parent
        batch_remarks = []
        valid_batch = True
        uid = instance.UID()
        batches = pc({
            'portal_type': 'ARImport',
            'path': {'query': '/'.join(client.getPhysicalPath())},
        })
        for brain in batches:
            if brain.UID == uid:
                continue
            batch = brain.getObject()
            if batch.getOrderID() != instance.getOrderID():
                continue
            if batch.getStatus():
                # then a previous valid batch exists
                batch_remarks.append(
                    '\n' + 'Duplicate order %s' % instance.getOrderID())
                valid_batch = False
                break

        # validate client
        if instance.getClientID() != client.getClientID():
            batch_remarks.append(
                '\n' + 'Client ID should be %s' % client.getClientID())
            valid_batch = False

        # validate contact
        contact_found = False
        cc_contact_found = False

        if instance.getContact():
            contact_found = True
        else:
            contactid = instance.getContactID()
            for contact in client.objectValues('Contact'):
                if contact.getUsername() == contactid:
                    instance.edit(Contact=contact)
                    contact_found = True
                    # break

        if instance.getCCContact():
            cc_contact_found = True
        else:
            if instance.getCCContactID():
                cccontact_uname = instance.getCCContactID()
                for contact in client.objectValues('Contact'):
                    if contact.getUsername() == cccontact_uname:
                        instance.edit(CCContact=contact)
                        cc_contact_found = True
                        break

        cccontact_uname = instance.getCCContactID()

        if not contact_found:
            batch_remarks.append('\n' + 'Contact invalid')
            valid_batch = False
        if cccontact_uname != None and \
                        cccontact_uname != '':
            if not cc_contact_found:
                batch_remarks.append('\n' + 'CC contact invalid')
                valid_batch = False

        # validate sample point
        samplepoint = instance.getSamplePoint()
        if samplepoint != None:
            points = pc(portal_type='SamplePoint',
                        Title=samplepoint)

        sampletypes = \
            [p.Title for p in pc(portal_type="SampleType")]
        samplematrices = \
            [p.Title for p in bsc(portal_type="SampleMatrix")]
        containertypes = \
            [p.Title for p in bsc(portal_type="ContainerType")]
        service_keys = []
        dependant_services = {}

        services = bsc(portal_type="AnalysisService",
                       inactive_state='active')
        for brain in services:
            service = brain.getObject()
            service_keys.append(service.getKeyword())
            calc = service.getCalculation()
            if calc:
                dependencies = calc.getDependentServices()
                if dependencies:
                    dependant_services[service.getKeyword()] = dependencies
        aritems = instance.objectValues('ARImportItem')
        for aritem in aritems:
            item_remarks = []
            valid_item = True
            # validate sample type
            if aritem.getSampleType() not in sampletypes:
                batch_remarks.append('\n%s: Sample type %s invalid' % (
                    aritem.getSampleName(), aritem.getSampleType()))
                item_remarks.append(
                    '\nSample type %s invalid' % (aritem.getSampleType()))
                valid_item = False
            if aritem.getSampleMatrix() not in samplematrices:
                batch_remarks.append('\n%s: Sample Matrix %s invalid' % (
                    aritem.getSampleName(), aritem.getSampleMatrix()))
                item_remarks.append(
                    '\nSample Matrix %s invalid' % (aritem.getSampleMatrix()))
                valid_item = False
            # validate container type
            if aritem.getContainerType() not in containertypes:
                batch_remarks.append(
                    '\n%s: Container type %s invalid' % (
                        aritem.getSampleName(), aritem.getContainerType()))
                item_remarks.append(
                    '\nContainer type %s invalid' % (aritem.getContainerType()))
                valid_item = False
            # validate Sample Date
            try:
                date_items = aritem.getSampleDate().split('/')
                test_date = DateTime(int(date_items[2]), int(date_items[1]),
                                     int(date_items[0]))
            except:
                valid_item = False
                batch_remarks.append('\n' + '%s: Sample date %s invalid' % (
                    aritem.getSampleName(), aritem.getSampleDate()))
                item_remarks.append(
                    '\n' + 'Sample date %s invalid' % (aritem.getSampleDate()))

            # validate Priority
            invalid_priority = False
            try:
                priorities = instance.bika_setup_catalog(
                    portal_type='ARPriority',
                    sortable_title=aritem.Priority.lower(),
                )
                if len(priorities) < 1:
                    invalid_priority = True
            except:
                invalid_priority = True

            if invalid_priority:
                valid_item = False
                batch_remarks.append('\n' + '%s: Priority %s invalid' % (
                    aritem.getSampleName(), aritem.Priority))
                item_remarks.append('\n' + 'Priority %s invalid' % (
                    aritem.Priority))

            analyses = aritem.getAnalysisProfile()
            if len(analyses) == 0:
                valid_item = False
                item_remarks.append('\n%s: No Profile provided' \
                                    % aritem.getSampleName())
                batch_remarks.append('\n%s: No Profile provided' \
                                     % aritem.getSampleName())
            elif len(analyses) > 1:
                valid_item = False
                item_remarks.append('\n%s: Only one Profile allowed' \
                                    % aritem.getSampleName())
                batch_remarks.append('\n%s: Only one Profile allowed' \
                                     % aritem.getSampleName())
            else:
                if not instance._findProfileKey(analyses[0]):
                    valid_item = False
                    item_remarks.append('\n%s: unknown Profile %s' \
                                        % (aritem.getSampleName(),
                                           analyses[0]))
                    batch_remarks.append('\n%s: unknown Profile %s' \
                                         % (aritem.getSampleName(),
                                            analyses[0]))

            aritem.setRemarks(item_remarks)
            # print item_remarks
            if not valid_item:
                valid_batch = False
        if instance.getNumberSamples() != len(aritems):
            valid_batch = False
            self.statusmessage('\nNumber of samples specified {} does not '
                               'match number of samples listed {}'.format(
                instance.getNumberSamples(), len(aritems)))
        instance.edit(
            Remarks=batch_remarks,
            Status=valid_batch)
        # print batch_remarks
        return valid_batch

    def _add_services_to_ar(self, ar, analyses):
        # Add Services
        service_uids = [i.split(':')[0] for i in analyses]
        new_analyses = ar.setAnalyses(service_uids)
        ar.setRequestID(ar.getId())
        ar.reindexObject()
        event.notify(ObjectInitializedEvent(ar))
        ar.at_post_create_script()

        SamplingWorkflowEnabled = \
            ar.bika_setup.getSamplingWorkflowEnabled()
        wftool = getToolByName(self, 'portal_workflow')

        # Create sample partitions
        parts = [{'services': [],
                  'container': [],
                  'preservation': '',
                  'separate': False}]
        sample = ar.getSample()
        parts_and_services = {}
        for _i in range(len(parts)):
            p = parts[_i]
            part_prefix = sample.getId() + "-P"
            if '%s%s' % (part_prefix, _i + 1) in sample.objectIds():
                parts[_i]['object'] = sample['%s%s' % (part_prefix, _i + 1)]
                parts_and_services['%s%s' % (part_prefix, _i + 1)] = \
                    p['services']
            else:
                part = _createObjectByType("SamplePartition", sample, tmpID())
                parts[_i]['object'] = part
                container = None
                preservation = p['preservation']
                parts[_i]['prepreserved'] = False
                part.unmarkCreationFlag()
                part.edit(
                    Container=container,
                    Preservation=preservation,
                )
                part._renameAfterCreation()
                if SamplingWorkflowEnabled:
                    wftool.doActionFor(part, 'sampling_workflow')
                else:
                    wftool.doActionFor(part, 'no_sampling_workflow')
                parts_and_services[part.id] = p['services']

        if SamplingWorkflowEnabled:
            wftool.doActionFor(ar, 'sampling_workflow')
        else:
            wftool.doActionFor(ar, 'no_sampling_workflow')

        # Add analyses to sample partitions
        # XXX jsonapi create AR: right now, all new analyses are linked to
        # the first samplepartition
        if new_analyses:
            analyses = list(part.getAnalyses())
            analyses.extend(new_analyses)
            part.edit(
                Analyses=analyses,
            )
            for analysis in new_analyses:
                analysis.setSamplePartition(part)

        # If Preservation is required for some partitions,
        # and the SamplingWorkflow is disabled, we need
        # to transition to to_be_preserved manually.
        if not SamplingWorkflowEnabled:
            to_be_preserved = []
            sample_due = []
            lowest_state = 'sample_due'
            for p in sample.objectValues('SamplePartition'):
                if p.getPreservation():
                    lowest_state = 'to_be_preserved'
                    to_be_preserved.append(p)
                else:
                    sample_due.append(p)
            for p in to_be_preserved:
                doActionFor(p, 'to_be_preserved')
            for p in sample_due:
                doActionFor(p, 'sample_due')
            doActionFor(sample, lowest_state)
            for analysis in ar.objectValues('Analysis'):
                doActionFor(analysis, lowest_state)
            doActionFor(ar, lowest_state)

    def getContactUIDForUser(self):
        """ get the UID of the contact associated with the authenticated
            user
        """
        user = self.REQUEST.AUTHENTICATED_USER
        user_id = user.getUserName()
        r = self.portal_catalog(
            portal_type='Contact',
            getUsername=user_id
        )
        if len(r) == 1:
            return r[0].UID

    def getCCContactUIDForUser(self):
        """ get the UID of the cc contact associated with the authenticated
            user
        """
        user = self.request.AUTHENTICATED_USER
        user_id = user.getUserName()
        r = self.portal_catalog(
            portal_type='Contact',
            getUsername=user_id
        )
        if len(r) == 1:
            return r[0].UID

    def progressbar_init(self, title):
        """Progress Bar
        """
        bar = ProgressBar(self.context, self.request, title,
                          description='')
        notify(InitialiseProgressBar(bar))

    def progressbar_progress(self, n, total):
        """Progres Bar Progress
        """
        progress_index = float(n) / float(total) * 100.0
        progress = ProgressState(self.request, progress_index)
        notify(UpdateProgressEvent(progress))

    def statusmessage(self, msg, facility="info"):
        """Add a statusmessage to the response
        """
        return IStatusMessage(self.request).addStatusMessage(msg, facility)
