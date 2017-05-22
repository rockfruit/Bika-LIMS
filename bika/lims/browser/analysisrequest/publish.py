# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
import csv
from email.mime.base import MIMEBase

import StringIO
from bika.lims import bikaMessageFactory as _, t
from bika.lims import logger
from bika.lims.browser import BrowserView
from bika.lims.config import POINTS_OF_CAPTURE
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import IResultOutOfRange
from bika.lims.utils import isnumber
from bika.lims.utils import to_utf8, encode_header
from bika.lims.utils import to_utf8, formatDecimalMark, format_supsub
from bika.lims.utils.analysis import format_uncertainty
from bika.lims.utils.pdf import attachPdf, createPdf
from bika.lims.vocabularies import getARReportTemplates
from DateTime import DateTime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.Utils import formataddr
from operator import itemgetter
from pkg_resources import resource_filename
from plone.registry.interfaces import IRegistry
from plone.resource.utils import iterDirectoriesOfType, queryResourceDirectory
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import safe_unicode, _createObjectByType
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from smtplib import SMTPServerDisconnected, SMTPRecipientsRefused
from zope.component import getAdapters, getUtility

from plone.registry import Record
from plone.registry import field
from plone import api

import App
import os
import re
import tempfile
import time
import traceback


class AnalysisRequestPublishView(BrowserView):
    template = ViewPageTemplateFile("templates/analysisrequest_publish.pt")
    _ars = []
    _arsbyclient = []
    _current_ar_index = 0
    _current_arsbyclient_index = 0
    _publish = False

    def __init__(self, context, request, publish=False):
        super(AnalysisRequestPublishView, self).__init__(context, request)
        self._publish = publish
        self._ars = [self.context]
        # Simple caching hack.  Various templates can allow these functions
        # to be called many thousands of times for relatively simple reports.
        # To prevent bad code from causing this, we cache all analysis data
        # here.
        self._cache = {
            '_analysis_data': {},
            '_qcanalyses_data': {},
            '_ar_data': {}
        }

    @property
    def _DEFAULT_TEMPLATE(self):
        registry = getUtility(IRegistry)
        return registry.get(
            'bika.lims.analysisrequest.default_arreport_template', 'default.pt')

    def next_certificate_number(self):
        """Get a new certificate id.  These are throwaway IDs, until the
        publication is actually done.  So each preview gives us a new ID.
        """
        key = 'bika.lims.current_coa_number'
        registry = getUtility(IRegistry)
        if key not in registry:
            registry.records[key] = \
                Record(field.Int(title=u"Current COA number"), 0)
        val = api.portal.get_registry_record(key) + 1
        api.portal.set_registry_record(key, val)
        year = str(time.localtime(time.time())[0])[-2:]
        return "COA%s-%05d"%(year, int(val))

    def current_certificate_number(self):
        """Return the last written ID from the registry
        """
        key = 'bika.lims.current_coa_number'
        val = api.portal.get_registry_record(key)
        year = str(time.localtime(time.time())[0])[-2:]
        return "COA%s-%05d"%(year, int(val))

    def __call__(self):
        if self.context.portal_type == 'AnalysisRequest':
            self._ars = [self.context]
        elif self.context.portal_type == 'AnalysisRequestsFolder' \
            and self.request.get('items',''):
            uids = self.request.get('items').split(',')
            uc = getToolByName(self.context, 'uid_catalog')
            self._ars = sorted([obj.getObject() for obj in uc(UID=uids)],
                               key=itemgetter('id'))
        else:
            #Do nothing
            self.destination_url = self.request.get_header("referer",
                                   self.context.absolute_url())

        # Group ARs by client
        groups = {}
        for ar in self._ars:
            idclient = ar.aq_parent.id
            if idclient not in groups:
                groups[idclient] = [ar]
            else:
                groups[idclient].append(ar)
        self._arsbyclient = [group for group in groups.values()]

        # Report may want to print current date
        self.current_date = self.ulocalized_time(DateTime(), long_format=True)

        # Do publish?
        if self.request.form.get('publish', '0') == '1':
            self.publishFromPOST()
        else:
            return self.template()

    def showOptions(self):
        """ Returns true if the options top panel will be displayed
            in the template
        """
        return self.request.get('pub', '1') == '1';

    def getAvailableFormats(self):
        """ Returns the available formats found in templates/reports
        """
        return getARReportTemplates()

    def getAnalysisRequests(self):
        """ Returns a dict with the analysis requests to manage
        """
        return self._ars

    def getAnalysisRequestsCount(self):
        """ Returns the number of analysis requests to manage
        """
        return len(self._ars)

    def getGroupedAnalysisRequestsCount(self):
        """ Returns the number of groups of analysis requests to manage when
            a multi-ar template is selected. The ARs are grouped by client
        """
        return len(self._arsbyclient)

    def getAnalysisRequestObj(self):
        """ Returns the analysis request objects to be managed
        """
        return self._ars[self._current_ar_index]

    def getAnalysisRequest(self, analysisrequest=None):
        """ Returns the dict for the Analysis Request specified. If no AR set,
            returns the current analysis request
        """
        return self._ar_data(analysisrequest) if analysisrequest \
                else self._ar_data(self._ars[self._current_ar_index])

    def getAnalysisRequestGroup(self):
        """ Returns the current analysis request group to be managed
        """
        return self._arsbyclient[self._current_arsbyclient_index]

    def getAnalysisRequestGroupData(self):
        """ Returns an array that contains the dicts (ar_data) for each
            analysis request from the current group
        """
        return [self._ar_data(ar) for ar in self.getAnalysisRequestGroup()]

    def _nextAnalysisRequest(self):
        """ Move to the next analysis request
        """
        if self._current_ar_index < len(self._ars):
            self._current_ar_index += 1

    def _nextAnalysisRequestGroup(self):
        """ Move to the next analysis request group
        """
        if self._current_arsbyclient_index < len(self._arsbyclient):
            self._current_arsbyclient_index += 1

    def _renderTemplate(self):
        """ Returns the html template to be rendered in accordance with the
            template specified in the request ('template' parameter)
        """
        templates_dir = 'templates/reports'
        embedt = self.request.form.get('template', self._DEFAULT_TEMPLATE)
        if embedt.find(':') >= 0:
            prefix, template = embedt.split(':')
            templates_dir = queryResourceDirectory('reports', prefix).directory
            embedt = template
        embed = ViewPageTemplateFile(os.path.join(templates_dir, embedt))
        return embedt, embed(self)

    def getReportTemplate(self):
        """ Returns the html template for the current ar and moves to
            the next ar to be processed. Uses the selected template
            specified in the request ('template' parameter)
        """
        reptemplate = ""
        embedt = ""
        try:
            embedt, reptemplate = self._renderTemplate()
        except:
            tbex = traceback.format_exc()
            arid = self._ars[self._current_ar_index].id
            reptemplate = "<div class='error-report'>%s - %s '%s':<pre>%s</pre></div>" % (arid, _("Unable to load the template"), embedt, tbex)
        self._nextAnalysisRequest()
        return reptemplate

    def getGroupedReportTemplate(self):
        """ Returns the html template for the current group of ARs and moves to
            the next group to be processed. Uses the selected template
            specified in the request ('template' parameter)
        """
        reptemplate = ""
        embedt = ""
        try:
            embedt, reptemplate = self._renderTemplate()
        except:
            tbex = traceback.format_exc()
            reptemplate = "<div class='error-report'>%s '%s':<pre>%s</pre></div>" % (_("Unable to load the template"), embedt, tbex)
        self._nextAnalysisRequestGroup()
        return reptemplate

    def getReportStyle(self):
        """ Returns the css style to be used for the current template.
            If the selected template is 'default.pt', this method will
            return the content from 'default.css'. If no css file found
            for the current template, returns empty string
        """
        template = self.request.form.get('template', self._DEFAULT_TEMPLATE)
        content = ''
        if template.find(':') >= 0:
            prefix, template = template.split(':')
            resource = queryResourceDirectory('reports', prefix)
            css = '{0}.css'.format(template[:-3])
            if css in resource.listDirectory():
                content = resource.readFile(css)
        else:
            this_dir = os.path.dirname(os.path.abspath(__file__))
            templates_dir = os.path.join(this_dir, 'templates/reports/')
            path = '%s/%s.css' % (templates_dir, template[:-3])
            with open(path, 'r') as content_file:
                content = content_file.read()
        return content

    def isSingleARTemplate(self):
        seltemplate = self.request.form.get('template', self._DEFAULT_TEMPLATE)
        seltemplate = seltemplate.split(':')[-1].strip()
        return not seltemplate.lower().startswith('multi')

    def isQCAnalysesVisible(self):
        """ Returns if the QC Analyses must be displayed
        """
        return self.request.form.get('qcvisible', '0').lower() in ['true', '1']

    def isHiddenAnalysesVisible(self):
        """ Returns true if hidden analyses are visible
        """
        return self.request.form.get('hvisible', '0').lower() in ['true', '1']

    def isLandscape(self):
        """ Returns if the layout is landscape
        """
        return self.request.form.get('landscape', '0').lower() in ['true', '1']

    def explode_data(self, data, padding=''):
        out = ''
        for k,v in data.items():
            if type(v) is dict:
                pad = '%s&nbsp;&nbsp;&nbsp;&nbsp;' % padding
                exploded = self.explode_data(v,pad)
                out = "%s<br/>%s'%s':{%s}" % (out, padding, str(k), exploded)
            elif type(v) is list:
                out = "%s<br/>%s'%s':[]" % (out, padding, str(k))
            elif type(v) is str:
                out = "%s<br/>%s'%s':''" % (out, padding, str(k))
        return out

    def _ar_data(self, ar, excludearuids=[]):
        """ Creates an ar dict, accessible from the view and from each
            specific template.
        """
        if ar.UID() in self._cache['_ar_data']:
            return self._cache['_ar_data'][ar.UID()]
        data = {'obj': ar}
        # data = {'obj': ar,
        #         'id': ar.getRequestID(),
        #         'client_order_num': ar.getClientOrderNumber(),
        #         'client_reference': ar.getClientReference(),
        #         'client_sampleid': ar.getClientSampleID(),
        #         'adhoc': ar.getAdHoc(),
        #         'composite': ar.getComposite(),
        #         'report_drymatter': ar.getReportDryMatter(),
        #         'invoice_exclude': ar.getInvoiceExclude(),
        #         'date_received': self.ulocalized_time(ar.getDateReceived(), long_format=1),
        #         'member_discount': ar.getMemberDiscount(),
        #         'date_sampled': self.ulocalized_time(
        #             ar.getDateSampled(), long_format=1),
        #         'date_published': self.ulocalized_time(DateTime(), long_format=1),
        #         'invoiced': ar.getInvoiced(),
        #         'late': ar.getLate(),
        #         'subtotal': ar.getSubtotal(),
        #         'vat_amount': ar.getVATAmount(),
        #         'totalprice': ar.getTotalPrice(),
        #         'invalid': ar.isInvalid(),
        #         'url': ar.absolute_url(),
        #         'remarks': to_utf8(ar.getRemarks()),
        #         'footer': to_utf8(self.context.bika_setup.getResultFooter()),
        #         'prepublish': False,
        #         'child_analysisrequest': None,
        #         'parent_analysisrequest': None,
        #         'resultsinterpretation':ar.getResultsInterpretation()}

        # # Sub-objects
        # excludearuids.append(ar.UID())
        # puid = ar.getRawParentAnalysisRequest()
        # if puid and puid not in excludearuids:
        #     data['parent_analysisrequest'] = self._ar_data(ar.getParentAnalysisRequest(), excludearuids)
        # cuid = ar.getRawChildAnalysisRequest()
        # if cuid and cuid not in excludearuids:
        #     data['child_analysisrequest'] = self._ar_data(ar.getChildAnalysisRequest(), excludearuids)
        #
        # wf = getToolByName(ar, 'portal_workflow')
        # allowed_states = ['verified', 'published']
        # data['prepublish'] = wf.getInfoFor(ar, 'review_state') not in allowed_states
        #
        # data['contact'] = self._contact_data(ar)
        # data['client'] = self._client_data(ar)
        # data['sample'] = self._sample_data(ar)
        # data['batch'] = self._batch_data(ar)
        # data['specifications'] = self._specs_data(ar)
        # data['analyses'] = self._analyses_data(ar, ['verified', 'published'])
        # data['qcanalyses'] = self._qcanalyses_data(ar, ['verified', 'published'])
        # data['points_of_capture'] = sorted(set([an['point_of_capture'] for an in data['analyses']]))
        # data['categories'] = sorted(set([an['category'] for an in data['analyses']]))
        # data['haspreviousresults'] = len([an['previous_results'] for an in data['analyses'] if an['previous_results']]) > 0
        # data['hasblanks'] = len([an['reftype'] for an in data['qcanalyses'] if an['reftype'] == 'b']) > 0
        # data['hascontrols'] = len([an['reftype'] for an in data['qcanalyses'] if an['reftype'] == 'c']) > 0
        # data['hasduplicates'] = len([an['reftype'] for an in data['qcanalyses'] if an['reftype'] == 'd']) > 0
        #
        # # Categorize analyses
        # data['categorized_analyses'] = {}
        # data['department_analyses'] = {}
        # for an in data['analyses']:
        #     poc = an['point_of_capture']
        #     cat = an['category']
        #     pocdict = data['categorized_analyses'].get(poc, {})
        #     catlist = pocdict.get(cat, [])
        #     catlist.append(an)
        #     pocdict[cat] = catlist
        #     data['categorized_analyses'][poc] = pocdict
        #
        #     # Group by department too
        #     anobj = an['obj']
        #     dept = anobj.getService().getDepartment() if anobj.getService() else None
        #     if dept:
        #         dept = dept.UID()
        #         dep = data['department_analyses'].get(dept, {})
        #         dep_pocdict = dep.get(poc, {})
        #         dep_catlist = dep_pocdict.get(cat, [])
        #         dep_catlist.append(an)
        #         dep_pocdict[cat] = dep_catlist
        #         dep[poc] = dep_pocdict
        #         data['department_analyses'][dept] = dep
        #
        # # Categorize qcanalyses
        # data['categorized_qcanalyses'] = {}
        # for an in data['qcanalyses']:
        #     qct = an['reftype']
        #     poc = an['point_of_capture']
        #     cat = an['category']
        #     qcdict = data['categorized_qcanalyses'].get(qct, {})
        #     pocdict = qcdict.get(poc, {})
        #     catlist = pocdict.get(cat, [])
        #     catlist.append(an)
        #     pocdict[cat] = catlist
        #     qcdict[poc] = pocdict
        #     data['categorized_qcanalyses'][qct] = qcdict
        #
        # data['reporter'] = self._reporter_data(ar)
        # data['managers'] = self._managers_data(ar)
        #
        # portal = self.context.portal_url.getPortalObject()
        # data['portal'] = {'obj': portal,
        #                   'url': portal.absolute_url()}
        # data['laboratory'] = self._lab_data()
        #
        # #results interpretation
        # ri = {}
        # if (ar.getResultsInterpretationByDepartment(None)):
        #     ri[''] = ar.getResultsInterpretationByDepartment(None)
        # depts = ar.getDepartments()
        # for dept in depts:
        #     ri[dept.Title()] = ar.getResultsInterpretationByDepartment(dept)
        # data['resultsinterpretationdepts'] = ri
        #
        # self._cache['_ar_data'][ar.UID()] = data
        return data

    def _batch_data(self, ar):
        data = {}
        batch = ar.getBatch()
        if batch:
            data = {'obj': batch,
                    'id': batch.id,
                    'url': batch.absolute_url(),
                    'title': to_utf8(batch.Title()),
                    'date': batch.getBatchDate(),
                    'client_batchid': to_utf8(batch.getClientBatchID()),
                    'remarks': to_utf8(batch.getRemarks())}

            uids = batch.Schema()['BatchLabels'].getAccessor(batch)()
            uc = getToolByName(self.context, 'uid_catalog')
            data['labels'] = [to_utf8(p.getObject().Title()) for p in uc(UID=uids)]

        return data

    def _sample_data(self, ar):
        data = {}
        sample = ar.getSample()
        if sample:
            data = {'obj': sample,
                    'id': sample.id,
                    'url': sample.absolute_url(),
                    'client_sampleid': sample.getClientSampleID(),
                    'date_sampled': sample.getDateSampled(),
                    'sampling_date': sample.getSamplingDate(),
                    'sampler': self._sampler_data(sample),
                    'date_received': sample.getDateReceived(),
                    'composite': sample.getComposite(),
                    'date_expired': sample.getDateExpired(),
                    'date_disposal': sample.getDisposalDate(),
                    'date_disposed': sample.getDateDisposed(),
                    'adhoc': sample.getAdHoc(),
                    'remarks': sample.getRemarks() }
        return data

    def _sampler_data(self, sample=None):
        data = {}
        if not sample or not sample.getSampler():
            return data
        sampler = sample.getSampler()
        mtool = getToolByName(self, 'portal_membership')
        member = mtool.getMemberById(sampler)
        if member:
            mfullname = member.getProperty('fullname')
            memail = member.getProperty('email')
            mhomepage = member.getProperty('home_page')
            pc = getToolByName(self, 'portal_catalog')
            c = pc(portal_type='Contact', getUsername=member.id)
            c = c[0].getObject() if c else None
            cfullname = c.getFullname() if c else None
            cemail = c.getEmailAddress() if c else None
            data = {'id': member.id,
                    'fullname': to_utf8(cfullname) if cfullname else to_utf8(mfullname),
                    'email': cemail if cemail else memail,
                    'business_phone': c.getBusinessPhone() if c else '',
                    'business_fax': c.getBusinessFax() if c else '',
                    'home_phone': c.getHomePhone() if c else '',
                    'mobile_phone': c.getMobilePhone() if c else '',
                    'job_title': to_utf8(c.getJobTitle()) if c else '',
                    'department': to_utf8(c.getDepartment()) if c else '',
                    'physical_address': to_utf8(c.getPhysicalAddress()) if c else '',
                    'postal_address': to_utf8(c.getPostalAddress()) if c else '',
                    'home_page': to_utf8(mhomepage)}
        return data

    def _sample_type(self, sample=None):
        data = {}
        sampletype = sample.getSampleType() if sample else None
        if sampletype:
            data = {'obj': sampletype,
                    'id': sampletype.id,
                    'title': sampletype.Title(),
                    'url': sampletype.absolute_url()}
        return data

    def _sample_point(self, sample=None):
        samplepoint = sample.getSamplePoint() if sample else None
        data = {}
        if samplepoint:
            data = {'obj': samplepoint,
                    'id': samplepoint.id,
                    'title': samplepoint.Title(),
                    'url': samplepoint.absolute_url()}
        return data

    def format_address(self, address):
        if address:
            _keys = ['address', 'city', 'district', 'state', 'zip', 'country']
            _list = ["<div>%s</div>" % address.get(v) for v in _keys
                     if address.get(v)]
            return ''.join(_list)
        return ''

    def _lab_address(self, lab):
        lab_address = lab.getPostalAddress() \
                      or lab.getBillingAddress() \
                      or lab.getPhysicalAddress()
        return self.format_address(lab_address)

    def _lab_data(self):
        portal = self.context.portal_url.getPortalObject()
        lab = self.context.bika_setup.laboratory

        return {'obj': lab,
                'title': to_utf8(lab.Title()),
                'url': to_utf8(lab.getLabURL()),
                'address': to_utf8(self._lab_address(lab)),
                'confidence': lab.getConfidence(),
                'accredited': lab.getLaboratoryAccredited(),
                'accreditation_body': to_utf8(lab.getAccreditationBody()),
                'accreditation_logo': lab.getAccreditationBodyLogo(),
                'logo': "%s/logo_print.png" % portal.absolute_url()}

    def _contact_data(self, ar):
        data = {}
        contact = ar.getContact()
        if contact:
            data = {'obj': contact,
                    'fullname': to_utf8(contact.getFullname()),
                    'email': to_utf8(contact.getEmailAddress()),
                    'pubpref': contact.getPublicationPreference()}
        return data

    def _client_address(self, client):
        client_address = client.getPostalAddress()
        if not client_address:
            # Data from the first contact
            contact = self.getAnalysisRequest().getContact()
            if contact and contact.getBillingAddress():
                client_address = contact.getBillingAddress()
            elif contact and contact.getPhysicalAddress():
                client_address = contact.getPhysicalAddress()
        return self.format_address(client_address)

    def _client_data(self, ar):
        data = {}
        client = ar.aq_parent
        if client:
            data['obj'] = client
            data['id'] = client.id
            data['url'] = client.absolute_url()
            data['name'] = to_utf8(client.getName())
            data['phone'] = to_utf8(client.getPhone())
            data['fax'] = to_utf8(client.getFax())

            data['address'] = to_utf8(self._client_address(client))
        return data

    def _specs_data(self, ar):
        data = {}
        specs = ar.getPublicationSpecification()
        if not specs:
            specs = ar.getSpecification()

        if specs:
            data['obj'] = specs
            data['id'] = specs.id
            data['url'] = specs.absolute_url()
            data['title'] = to_utf8(specs.Title())
            data['resultsrange'] = specs.getResultsRangeDict()

        return data

    def _analyses_data(self, ar, analysis_states=['verified', 'published']):
        analyses = []
        dm = ar.aq_parent.getDecimalMark()
        batch = ar.getBatch()
        workflow = getToolByName(self.context, 'portal_workflow')
        showhidden = self.isHiddenAnalysesVisible()
        for an in ar.getAnalyses(full_objects=True,
                                 review_state=analysis_states):

            # Omit hidden analyses?
            if not showhidden:
                serv = an.getService()
                asets = ar.getAnalysisServiceSettings(serv.UID())
                if asets.get('hidden'):
                    # Hide analysis
                    continue

            # Build the analysis-specific dict
            andict = self._analysis_data(an, dm)

            # Are there previous results for the same AS and batch?
            andict['previous'] = []
            andict['previous_results'] = ""
            if batch:
                keyword = an.getKeyword()
                bars = [bar for bar in batch.getAnalysisRequests() \
                            if an.aq_parent.UID() != bar.UID() \
                            and keyword in bar]
                for bar in bars:
                    pan = bar[keyword]
                    pan_state = workflow.getInfoFor(pan, 'review_state')
                    if pan.getResult() and pan_state in analysis_states:
                        pandict = self._analysis_data(pan)
                        andict['previous'].append(pandict)

                andict['previous'] = sorted(andict['previous'], key=itemgetter("capture_date"))
                andict['previous_results'] = ", ".join([str(p['formatted_result']) for p in andict['previous'][-5:]])

            analyses.append(andict)
        return analyses

    def _analysis_data(self, analysis, decimalmark=None):
        if analysis.UID() in self._cache['_analysis_data']:
            return self._cache['_analysis_data'][analysis.UID()]

        keyword = analysis.getKeyword()
        service = analysis.getService()
        andict = {'obj': analysis,
                  'id': analysis.id,
                  'title': analysis.Title(),
                  'keyword': keyword,
                  'scientific_name': service.getScientificName(),
                  'accredited': service.getAccredited(),
                  'point_of_capture': to_utf8(POINTS_OF_CAPTURE.getValue(service.getPointOfCapture())),
                  'category': to_utf8(service.getCategoryTitle()),
                  'result': analysis.getResult(),
                  'isnumber': isnumber(analysis.getResult()),
                  'unit': to_utf8(service.getUnit()),
                  'formatted_unit': format_supsub(to_utf8(service.getUnit())),
                  'capture_date': analysis.getResultCaptureDate(),
                  'request_id': analysis.aq_parent.getId(),
                  'formatted_result': '',
                  'uncertainty': analysis.getUncertainty(),
                  'formatted_uncertainty': '',
                  'retested': analysis.getRetested(),
                  'remarks': to_utf8(analysis.getRemarks()),
                  'resultdm': to_utf8(analysis.getResultDM()),
                  'outofrange': False,
                  'type': analysis.portal_type,
                  'reftype': analysis.getReferenceType() \
                            if hasattr(analysis, 'getReferenceType')
                            else None,
                  'worksheet': None,
                  'specs': {},
                  'formatted_specs': ''}

        if analysis.portal_type == 'DuplicateAnalysis':
            andict['reftype'] = 'd'

        ws = analysis.getBackReferences('WorksheetAnalysis')
        andict['worksheet'] = ws[0].id if ws and len(ws) > 0 else None
        andict['worksheet_url'] = ws[0].absolute_url if ws and len(ws) > 0 else None
        andict['refsample'] = analysis.getSample().id \
                            if analysis.portal_type == 'Analysis' \
                            else '%s - %s' % (analysis.aq_parent.id, analysis.aq_parent.Title())

        if analysis.portal_type == 'ReferenceAnalysis':
            # The analysis is a Control or Blank. We might use the
            # reference results instead other specs
            uid = analysis.getServiceUID()
            specs = analysis.aq_parent.getResultsRangeDict().get(uid, {})

        else:
            # Get the specs directly from the analysis. The getResultsRange
            # function already takes care about which are the specs to be used:
            # AR, client or lab.
            specs = analysis.getResultsRange()

        andict['specs'] = specs
        scinot = self.context.bika_setup.getScientificNotationReport()
        fresult =  analysis.getFormattedResult(specs=specs, sciformat=int(scinot), decimalmark=decimalmark)

        # We don't use here cgi.encode because results fields must be rendered
        # using the 'structure' wildcard. The reason is that the result can be
        # expressed in sci notation, that may include <sup></sup> html tags.
        # Please note the default value for the 'html' parameter from
        # getFormattedResult signature is set to True, so the service will
        # already take into account LDLs and UDLs symbols '<' and '>' and escape
        # them if necessary.
        andict['formatted_result'] = fresult;

        fs = ''
        if specs.get('min', None) and specs.get('max', None):
            fs = '%s - %s' % (specs['min'], specs['max'])
        elif specs.get('min', None):
            fs = '> %s' % specs['min']
        elif specs.get('max', None):
            fs = '< %s' % specs['max']
        andict['formatted_specs'] = formatDecimalMark(fs, decimalmark)
        andict['formatted_uncertainty'] = format_uncertainty(analysis, analysis.getResult(), decimalmark=decimalmark, sciformat=int(scinot))

        # Out of range?
        if specs:
            adapters = getAdapters((analysis, ), IResultOutOfRange)
            bsc = getToolByName(self.context, "bika_setup_catalog")
            for name, adapter in adapters:
                ret = adapter(specification=specs)
                if ret and ret['out_of_range']:
                    andict['outofrange'] = True
                    break
        self._cache['_analysis_data'][analysis.UID()]  = andict
        return andict

    def _qcanalyses_data(self, ar, analysis_states=['verified', 'published']):
        if ar.UID() in self._cache['_qcanalyses_data']:
            return self._cache['_qcanalyses_data'][ar.UID()]
        analyses = []
        batch = ar.getBatch()
        workflow = getToolByName(self.context, 'portal_workflow')
        for an in ar.getQCAnalyses(review_state=analysis_states):

            # Build the analysis-specific dict
            andict = self._analysis_data(an)

            # Are there previous results for the same AS and batch?
            andict['previous'] = []
            andict['previous_results'] = ""

            analyses.append(andict)
        analyses.sort(lambda x, y: cmp(x.get('title').lower(), y.get('title').lower()))
        self._cache['_qcanalyses_data'][ar.UID()] = analyses
        return analyses

    def _reporter_data(self, ar):
        data = {}
        member = self.context.portal_membership.getAuthenticatedMember()
        if member:
            username = member.getUserName()
            data['username'] = username
            data['fullname'] = to_utf8(self.user_fullname(username))
            data['email'] = to_utf8(self.user_email(username))

            c = [x for x in self.bika_setup_catalog(portal_type='LabContact')
                 if x.getObject().getUsername() == username]
            if c:
                sf = c[0].getObject().getSignature()
                if sf:
                    data['signature'] = sf.absolute_url() + "/Signature"

        return data

    def _managers_data(self, ar):
        managers = {'ids': [], 'dict': {}}
        departments = {}
        ar_mngrs = ar.getResponsible()
        for id in ar_mngrs['ids']:
            new_depts = ar_mngrs['dict'][id]['departments'].split(',')
            if id in managers['ids']:
                for dept in new_depts:
                    if dept not in departments[id]:
                        departments[id].append(dept)
            else:
                departments[id] = new_depts
                managers['ids'].append(id)
                managers['dict'][id] = ar_mngrs['dict'][id]

        mngrs = departments.keys()
        for mngr in mngrs:
            final_depts = ''
            for dept in departments[mngr]:
                if final_depts:
                    final_depts += ', '
                final_depts += to_utf8(dept)
            managers['dict'][mngr]['departments'] = final_depts

        return managers

    def publishFromPOST(self):
        """The handler for the Publish button in the report preview page.
        """
        html = self.request.form.get('html')
        style = self.request.form.get('style')
        uids = self.request.form.get('uid').split(':')
        template = self.request.form.get('template', '')
        reporthtml = "<html><head>%s</head><body><div id='report'>%s</body></html>" % (style, html)
        publishedars = []
        if 'multi_' in template.lower():
            publishedars = self.publishFromHTML(
                uids, safe_unicode(reporthtml).encode('utf-8'))
        else:
            for uid in uids:
                ars = self.publishFromHTML(
                    uid, safe_unicode(reporthtml).encode('utf-8'))
                publishedars.extend(ars)
        return publishedars

    def localize_images(self, html):
        """Replace manually the image URLs that can't be traversed,
        with filesystem paths
        """
        path = resource_filename('bika.lims', 'skins/bika/logo_print.png')
        html = re.sub(r"""http.*logo_print[^'"]+""",
                       "file://" + path, html)

        path = resource_filename('bika.lims', 'browser/images/accredited.png')
        html = re.sub(r"""http.*accredited[^'"]+""",
                       "file://" + path, html)

        return html

    def publishFromHTML(self, ar_uids, results_html):
        """ar_uids can be a single UID or a list of AR uids.  The resulting
        ARs will be published together (ie, sent as a single outbound email)
        and the entire report will be saved in each AR's published-results
        tab.
        """
        debug_mode = App.config.getConfiguration().debug_mode
        wf = getToolByName(self.context, 'portal_workflow')

        # The AR can be published only and only if allowed
        uc = getToolByName(self.context, 'uid_catalog')
        ars = [p.getObject() for p in uc(UID=ar_uids)]
        if not ars:
            return []

        results_html = self.localize_images(results_html)
        # Create the pdf report for the supplied HTML.
        pdf_report = createPdf(results_html, False)
        # PDF written to debug file?
        if debug_mode:
            pdf_fn = tempfile.mktemp(suffix=".pdf")
            logger.info("Writing PDF for {} to {}".format(
                ', '.join([ar.Title() for ar in ars]), pdf_fn))
            open(pdf_fn, 'wb').write(pdf_report)

        for ar in ars:
            # Generate in each relevant AR, a new ARReport
            reportid = ar.generateUniqueId('ARReport')
            report = _createObjectByType("ARReport", ar, reportid)
            report.edit(
                AnalysisRequest=ar.UID(),
                Pdf=pdf_report,
                Html=results_html,
            )
            report.unmarkCreationFlag()
            renameAfterCreation(report)
            # Modify the workflow state of each AR that's been published
            status = wf.getInfoFor(ar, 'review_state')
            transitions = {'verified': 'publish', 'published': 'republish'}
            transition = transitions.get(status, 'prepublish')
            try:
                wf.doActionFor(ar, transition)
            except WorkflowException:
                pass

        # compose and send email.
        # The managers of the departments for which the current AR has
        # at least one AS must receive always the pdf report by email.
        # https://github.com/bikalabs/Bika-LIMS/issues/1028
        lab = ars[0].bika_setup.laboratory
        mime_msg = MIMEMultipart('related')
        mime_msg['Subject'] = "Published results for %s" % \
                              ",".join([ar.Title() for ar in ars])
        mime_msg['From'] = formataddr(
            (encode_header(lab.getName()), lab.getEmailAddress()))
        mime_msg.preamble = 'This is a multi-part MIME message.'
        msg_txt = MIMEText(results_html, _subtype='html')
        mime_msg.attach(msg_txt)

        to = []
        to_emails = []

        mngrs = []
        for ar in ars:
            resp = ar.getResponsible()
            if 'dict' in resp and resp['dict']:
                for mngrid,mngr in resp['dict'].items():
                    if mngr['email'] not in [m['email'] for m in mngrs]:
                        mngrs.append(mngr)
        for mngr in mngrs:
            name = mngr['name']
            email = mngr['email']
            to.append(formataddr((encode_header(name), email)))

        # Send report to recipients
        for ar in ars:
            recips = self.get_recipients(ar)
            for recip in recips:
                if 'email' not in recip.get('pubpref', []) \
                        or not recip.get('email', ''):
                    continue
                title = encode_header(recip.get('title', ''))
                email = recip.get('email')
                if email not in to_emails:
                    to.append(formataddr((title, email)))
                    to_emails.append(email)

        # Create the new mime_msg object, cause the previous one
        # has the pdf already attached
        mime_msg = MIMEMultipart('related')
        mime_msg['Subject'] = "Published results for %s" % \
                              ",".join([ar.Title() for ar in ars])
        mime_msg['From'] = formataddr(
        (encode_header(lab.getName()), lab.getEmailAddress()))
        mime_msg.preamble = 'This is a multi-part MIME message.'
        msg_txt = MIMEText(results_html, _subtype='html')
        mime_msg.attach(msg_txt)
        mime_msg['To'] = ",".join(to)

        # Attach the pdf to the email
        fn = "_".join([ar.Title() for ar in ars])
        attachPdf(mime_msg, pdf_report, fn)

        # ALS hack.  Create the CSV they desire here now
        csvdata = self.create_als_csv(ars)
        # Attach to email
        part = MIMEBase('text', "csv")
        fn = self.current_certificate_number()
        part.add_header(
            'Content-Disposition', 'attachment; filename="{}.csv"'.format(fn))
        part.set_payload(csvdata)
        mime_msg.attach(part)

        msg_string = mime_msg.as_string()

        try:
            host = getToolByName(ars[0], 'MailHost')
            host.send(msg_string, immediate=True)
        except SMTPServerDisconnected as msg:
            logger.warn("SMTPServerDisconnected: %s." % msg)
        except SMTPRecipientsRefused as msg:
            raise WorkflowException(str(msg))

        return ars

    def create_als_csv(self, ars):
        analyses = []
        for ar in ars:
            analyses.extend(ar.getAnalyses(full_objects=True))
        #
        fieldnames = [
            "LRN",
            "Date",
            "Constituent",
            "Value",
            "Product Description",
            "Orig site"]
        #
        output = StringIO.StringIO()
        dw = csv.DictWriter(output, fieldnames=fieldnames)
        dw.writerow(dict((fn, fn) for fn in fieldnames))
        #
        for analysis in analyses:
            ar = analysis.aq_parent
            sample = ar.getSample()
            sid = sample.getClientSampleID()
            if not sid:
                sid = sample.getId()
            point = sample.getSamplePoint().Title() \
                if sample.getSamplePoint() else ''
            date = analysis.getResultCaptureDate()
            date = self.ulocalized_time(date, long_format=True)
            row = {
                "LRN": sid,
                "Date": date,
                "Constituent": analysis.getService().getKeyword(),
                "Value": analysis.getFormattedResult(),
                "Product Description": sample.getSampleType().Title(),
                "Orig site": point,
            }
            dw.writerow(row)
        return output.getvalue()

    def publish(self):
        """ Publish the AR report/s. Generates a results pdf file
            associated to each AR, sends an email with the report to
            the lab manager and sends a notification (usually an email
            with the PDF attached) to the AR's contact and CCs.
            Transitions each published AR to statuses 'published',
            'prepublished' or 'republished'.
            Returns a list with the AR identifiers that have been
            published/prepublished/republished (only those 'verified',
            'published' or at least have one 'verified' result).
        """
        if len(self._ars) > 1:
            published_ars = []
            for ar in self._ars:
                arpub = AnalysisRequestPublishView(ar, self.request, publish=True)
                ar = arpub.publish()
                published_ars.extend(ar)
            published_ars = [par.id for par in published_ars]
            return published_ars

        results_html = safe_unicode(self.template()).encode('utf-8')
        return self.publishFromHTML(results_html)

    def get_recipients(self, ar):
        """ Returns a list with the recipients and all its publication prefs
        """
        recips = []

        # Contact and CC's
        contact = ar.getContact()
        if contact:
            recips.append({'title': to_utf8(contact.Title()),
                           'email': contact.getEmailAddress(),
                           'pubpref': contact.getPublicationPreference()})
        for cc in ar.getCCContact():
            recips.append({'title': to_utf8(cc.Title()),
                           'email': cc.getEmailAddress(),
                           'pubpref': contact.getPublicationPreference()})

        return recips

    def get_mail_subject(self, ar):
        """ Returns the email subject in accordance with the client
            preferences
        """
        client = ar.aq_parent
        subject_items = client.getEmailSubject()
        ai = co = cr = cs = False
        if 'ar' in subject_items:
            ai = True
        if 'co' in subject_items:
            co = True
        if 'cr' in subject_items:
            cr = True
        if 'cs' in subject_items:
            cs = True
        ais = []
        cos = []
        crs = []
        css = []
        blanks_found = False
        if ai:
            ais.append(ar.getRequestID())
        if co:
            if ar.getClientOrderNumber():
                if not ar.getClientOrderNumber() in cos:
                    cos.append(ar.getClientOrderNumber())
            else:
                blanks_found = True
        if cr or cs:
            sample = ar.getSample()
        if cr:
            if sample.getClientReference():
                if not sample.getClientReference() in crs:
                    crs.append(sample.getClientReference())
            else:
                blanks_found = True
        if cs:
            if sample.getClientSampleID():
                if not sample.getClientSampleID() in css:
                    css.append(sample.getClientSampleID())
            else:
                blanks_found = True
        line_items = []
        if ais:
            ais.sort()
            li = t(_('ARs: ${ars}', mapping={'ars': ', '.join(ais)}))
            line_items.append(li)
        if cos:
            cos.sort()
            li = t(_('Orders: ${orders}', mapping={'orders': ', '.join(cos)}))
            line_items.append(li)
        if crs:
            crs.sort()
            li = t(_('Refs: ${references}', mapping={'references':', '.join(crs)}))
            line_items.append(li)
        if css:
            css.sort()
            li = t(_('Samples: ${samples}', mapping={'samples': ', '.join(css)}))
            line_items.append(li)
        tot_line = ' '.join(line_items)
        if tot_line:
            subject = t(_('Analysis results for ${subject_parts}',
                          mapping={'subject_parts':tot_line}))
            if blanks_found:
                subject += (' ' + t(_('and others')))
        else:
            subject = t(_('Analysis results'))
        return subject, tot_line

    def sorted_by_sort_key(self, category_keys):
        """ Sort categories via catalog lookup on title. """
        bsc = getToolByName(self.context, "bika_setup_catalog")
        analysis_categories = bsc(portal_type="AnalysisCategory", sort_on="sortable_title")
        sort_keys = dict([(b.Title, "{:04}".format(a)) for a, b in enumerate(analysis_categories)])
        return sorted(category_keys, key=lambda title, sk=sort_keys: sk.get(title))

    def getAnaysisBasedTransposedMatrix(self, ars):
        """ Returns a dict with the following structure:
            {'category_1_name':
                {'service_1_title':
                    {'service_1_uid':
                        {'service': <AnalysisService-1>,
                         'ars': {'ar1_id': [<Analysis (for as-1)>,
                                           <Analysis (for as-1)>],
                                 'ar2_id': [<Analysis (for as-1)>]
                                },
                        },
                    },
                {'service_2_title':
                     {'service_2_uid':
                        {'service': <AnalysisService-2>,
                         'ars': {'ar1_id': [<Analysis (for as-2)>,
                                           <Analysis (for as-2)>],
                                 'ar2_id': [<Analysis (for as-2)>]
                                },
                        },
                    },
                ...
                },
            }
        """
        analyses = {}
        for ar in ars:
            ans = [an.getObject() for an in ar.getAnalyses()]
            for an in ans:
                service = an.getService()
                cat = service.getCategoryTitle()
                if cat not in analyses:
                    analyses[cat] = {
                        service.title: {
                            'service': service,
                            'accredited': service.getAccredited(),
                            'ars': {ar.id: an.getFormattedResult()}
                        }
                    }
                elif service.title not in analyses[cat]:
                    analyses[cat][service.title] = {
                        'service': service,
                        'accredited': service.getAccredited(),
                        'ars': {ar.id: an.getFormattedResult()}
                    }
                else:
                    d = analyses[cat][service.title]
                    d['ars'][ar.id] = an.getFormattedResult()
                    analyses[cat][service.title]=d
        return analyses

    def getAnaysisBasedTransposedCatMethMatrix(self, ars):
        """ Returns a dict with the following structure:
        {cat_title: {meth_title: [analysis, analysis, analysis]}}
        """
        catmeths = {}
        for ar in ars:
            ans = [an.getObject() for an in ar.getAnalyses()]
            for an in ans:
                # First setup catmeths heirarchy for this analysis
                cat = an.getCategoryTitle()
                meth = an.getMethod().Title() if an.getMethod() else ''
                if cat not in catmeths:
                    catmeths[cat] = {}
                if meth not in catmeths[cat]:
                    catmeths[cat][meth] = []
                # Then add analysis to catmeths/cat/meth
                titles = [a.getService().Title() for a in catmeths[cat][meth]]
                if an.getService().Title() not in titles:
                    catmeths[cat][meth].append(an)

        return catmeths
