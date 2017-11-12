# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import urllib

import transaction
import zLOG
from DateTime import DateTime
from Products.ATContentTypes.utils import DT2dt
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.browser.fields.uidreferencefield import get_backreferences
from bika.lims.interfaces import IIdServer
from bika.lims.numbergenerator import INumberGenerator
from zope.component import getAdapters
from zope.component import getUtility
from zope.container.interfaces import INameChooser
from zope.interface import implements


class IDServerUnavailable(Exception):
    pass


def idserver_generate_id(context, prefix, batch_size=None):
    """ Generate a new id using external ID server.
    """
    plone = context.portal_url.getPortalObject()
    url = api.get_bika_setup().getIDServerURL()

    try:
        if batch_size:
            # GET
            f = urllib.urlopen('%s/%s/%s?%s' % (
                url,
                plone.getId(),
                prefix,
                urllib.urlencode({'batch_size': batch_size}))
            )
        else:
            f = urllib.urlopen('%s/%s/%s' % (url, plone.getId(), prefix))
        new_id = f.read()
        f.close()
    except:
        from sys import exc_info
        info = exc_info()
        msg = 'generate_id raised exception: {}, {} \n ID server URL: {}'
        msg = msg.format(info[0], info[1], url)
        zLOG.LOG('INFO', 0, '', msg)
        raise IDServerUnavailable(_('ID Server unavailable'))

    return new_id


def generateUniqueId(context, parent=False, portal_type=''):
    """ Generate pretty content IDs.
    """

    if portal_type == '':
        portal_type = context.portal_type

    def getLastCounter(context, config):
        if config.get('counter_type', '') == 'backreference':
            relationship = config['counter_reference']
            backrefs = get_backreferences(context, relationship)
            return len(backrefs) - 1
        elif config.get('counter_type', '') == 'contained':
            return len(context.objectItems(config['counter_reference'])) - 1
        else:
            raise RuntimeError('ID Server: missing values in configuration')

    number_generator = getUtility(INumberGenerator)
    # keys = number_generator.keys()
    # values = number_generator.values()
    # for i in range(len(keys)):
    #     print '%s : %s' % (keys[i], values[i])

    def getConfigByPortalType(config_map, portal_type):
        config_by_pt = {}
        for c in config_map:
            if c['portal_type'] == portal_type:
                config_by_pt = c
                break
        return config_by_pt

    config_map = api.get_bika_setup().getIDFormatting()
    config = getConfigByPortalType(
        config_map=config_map,
        portal_type=portal_type)
    if portal_type == "AnalysisRequest":
        variables_map = {
            'sampleId': context.getSample().getId(),
            'sample': context.getSample(),
            'year': DateTime().strftime("%Y")[2:],
        }
    elif portal_type == "SamplePartition":
        variables_map = {
            'sampleId': context.aq_parent.getId(),
            'sample': context.aq_parent,
            'year': DateTime().strftime("%Y")[2:],
        }
    elif portal_type == "Sample" and parent:
        config = getConfigByPortalType(
            config_map=config_map,
            portal_type='SamplePartition')  # Override
        variables_map = {
            'sampleId': context.getId(),
            'sample': context,
            'year': DateTime().strftime("%Y")[2:],
        }
    elif portal_type == "Sample":
        sampleDate = None
        sampleType = context.getSampleType().getPrefix()
        if context.getDateSampled():
            sampleDate = DT2dt(context.getDateSampled())
        else:
            # No Sample Date?
            logger.error("Sample {} has no sample date set".format(
                context.getId()))
            sampleDate = DT2dt(DateTime())

        variables_map = {
            'clientId': context.aq_parent.getClientID(),
            'sampleDate': sampleDate,
            'sampleType': api.normalize_filename(sampleType),
            'year': DateTime().strftime("%Y")[2:],
        }
    else:
        if not config:
            # Provide default if no format specified on bika_setup
            config = {
                'form': '%s-{seq}' % portal_type.lower(),
                'sequence_type': 'generated',
                'prefix': '%s' % portal_type.lower(),
            }
        variables_map = {
            'year': DateTime().strftime("%Y")[2:],
        }

    # Actual id construction starts here
    new_seq = 0
    form = config['form']
    if config['sequence_type'] == 'counter':
        new_seq = getLastCounter(
            context=variables_map[config['context']],
            config=config)
    elif config['sequence_type'] == 'generated':
        try:
            if config.get('split_length', None) == 0:
                prefix_config = '-'.join(form.split('-')[:-1])
                prefix = prefix_config.format(**variables_map)
            elif config.get('split_length', 0) > 0:
                prefix_config = form.split('-')[:config['split_length']]
                prefix_config = '-'.join(prefix_config)
                prefix = prefix_config.format(**variables_map)
            else:
                prefix = config['prefix']
            new_seq = number_generator(key=prefix)
        except KeyError, e:
            msg = "KeyError in GenerateUniqueId on %s: %s" % (
                str(config), e)
            raise RuntimeError(msg)
        except ValueError, e:
            msg = "ValueError in GenerateUniqueId on %s with %s: %s" % (
                str(config), str(variables_map), e)
            raise RuntimeError(msg)
    variables_map['seq'] = new_seq + 1
    result = form.format(**variables_map)
    return result


def renameAfterCreation(obj):
    """
    Renaming object right after it is created...
    In some cases we may want to override generate_id function. To do this,
    an adapter must be added (providing bika.lims.interfaces.IIdServer) for
    that content type.
    """
    # Check if the _bika_id was aready set
    bika_id = getattr(obj, "_bika_id", None)
    if bika_id is not None:
        return bika_id
    # Can't rename without a subtransaction commit when using portal_factory
    transaction.savepoint(optimistic=True)
    # The id returned should be normalized already
    new_id = None
    # Checking if an adapter exists for this content type. If yes, we will
    # get new_id from adapter.
    for name, adapter in getAdapters((obj, ), IIdServer):
        if new_id:
            logger.warn(('More than one ID Generator Adapter found for'
                         'content type -> %s') % obj.portal_type)
        new_id = adapter.generate_id(obj.portal_type)
    if not new_id:
        new_id = generateUniqueId(obj)

    parent = api.get_parent(obj)
    if new_id in parent.objectIds():
        # XXX We could do the check in a `while` loop and generate a new one.
        raise KeyError("The ID {} is already taken in the path {}".format(
            new_id, api.get_path(parent)))
    # rename the object to the new id
    parent.manage_renameObject(obj.id, new_id)

    return new_id


class AutoGenerateID(object):
    implements(INameChooser)

    def __init__(self, context):
        self.context = context

    def chooseName(self, name, object):
        bika_id = getattr(object, "_bika_id", None)
        if bika_id is None:
            new_id = generateUniqueId(object)
            object._bika_id = new_id
            bika_id = new_id
        return bika_id
