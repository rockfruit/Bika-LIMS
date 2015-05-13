from Products.CMFPlone.interfaces import IWorkflowChain
from Products.CMFPlone.workflow import ToolWorkflowChain
from bika.lims.utils import changeWorkflowState
from Products.CMFCore.utils import getToolByName
from zope.interface import implementer


@implementer(IWorkflowChain)
def SamplePrepWorkflowChain(ob, wftool):
    """Responsible for inserting the optional sampling preparation workflow
    into the workflow chain for objects with ISamplePrepWorkflow

    This is only done if the object is in 'sample_prep' state in the
    primary workflow (review_state).
    """
    # use catalog to retrieve review_state: getInfoFor causes recursion loop
    chain = list(ToolWorkflowChain(ob, wftool))
    bc = getToolByName(ob, 'bika_catalog')
    proxies = bc(UID=ob.UID())
    if not proxies or proxies[0].review_state != 'sample_prep':
        return chain
    sampleprep_workflow = ob.getPreparationWorkflow()
    if sampleprep_workflow:
        chain.append(sampleprep_workflow)
    return tuple(chain)


def SamplePrepTransitionEventHandler(instance, event):
    """Sample preparation is considered complete when the sampleprep workflow
    reaches a state which has no exit transitions.

    If the stateis state's ID is the same as any AnalysisRequest primary workflow ID,
    then the AnalysisRequest will be sent directly to that state.

    If the final state's ID is not found in the AR workflow, the AR will be
    transitioned to 'sample_received'.
    """
    # creation doesn't have a 'transition'
    if not event.transition:
        return
    if not event.new_state.getTransitions():
        wftool = getToolByName(instance, 'portal_workflow')
        primary_wf_name = list(ToolWorkflowChain(instance, wftool))[0]
        primary_wf_states = wftool.getWorkflowById(primary_wf_name).states.keys()
        if event.new_state.id in primary_wf_states:
            # final state name matches review_state in primary workflow:
            dst_state = event.new_state.id
        else:
            # fallback state:
            dst_state = 'sample_received'
        changeWorkflowState(instance, primary_wf_name, dst_state)
