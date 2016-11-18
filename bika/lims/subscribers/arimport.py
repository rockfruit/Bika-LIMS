def ARImportModifiedEventHandler(instance, event):

    instance.validateIt()


def ARImportItemModifiedEventHandler(instance, event):

    instance.aq_inner.aq_parent.validateIt()
