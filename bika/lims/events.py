# -*- coding: utf-8 -*-

class LIMSCreatedEvent(object):
    """A LIMS root has been created.
    """

    def __init__(self, lims):
        self.lims = lims
