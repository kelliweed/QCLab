from bika.lims import enum
from bika.lims import PMF
from bika.lims import logger
from bika.lims.interfaces import IJSONReadExtender
from bika.lims.utils import t
from Products.CMFCore.interfaces import IContentish
from zope.interface import Interface
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from zope.component import adapts
from zope.interface import implements
from bika.lims.jsonapi import get_include_fields


def skip(instance, action, peek=False, unskip=False):
    """Returns True if the transition is to be SKIPPED

        peek - True just checks the value, does not set.
        unskip - remove skip key (for manual overrides).

    called with only (instance, action_id), this will set the request variable preventing the
    cascade's from re-transitioning the object and return None.
    """

    uid = callable(instance.UID) and instance.UID() or instance.UID
    skipkey = "%s_%s" % (uid, action)
    if 'workflow_skiplist' not in instance.REQUEST:
        if not peek and not unskip:
            instance.REQUEST['workflow_skiplist'] = [skipkey, ]
    else:
        if skipkey in instance.REQUEST['workflow_skiplist']:
            if unskip:
                instance.REQUEST['workflow_skiplist'].remove(skipkey)
            else:
                return True
        else:
            if not peek and not unskip:
                instance.REQUEST["workflow_skiplist"].append(skipkey)


def doActionFor(instance, action_id):
    actionperformed = False
    message = ''
    workflow = getToolByName(instance, "portal_workflow")
    ex_state = workflow.getInfoFor(instance, 'review_state')
    if not skip(instance, action_id, peek=True) and ex_state != action_id:
        log_msg = "Transitioning %s from %s to %s" % (instance.portal_type, come_from, action_id)
        logger.debug(log_msg)
        try:
            workflow.doActionFor(instance, action_id)
            actionperformed = True
        except WorkflowException as e:
            logmsg = "Error while transitioning %s from %s to %s: %s" \
                     % (instance.portal_type,  ex_state, action_id, str(e))
            logger.error(logmsg)
            logger.error(log_msg)
    return actionperformed, message


def AfterTransitionEventHandler(instance, event):
    """This will run the workflow_script_* on any
    content type that has one.
    """
    # creation doesn't have a 'transition'
    if not event.transition:
        return
    key = 'workflow_script_' + event.transition.id
    method = getattr(instance, key, False)
    if method:
        method()


def get_workflow_actions(obj):
    """ Compile a list of possible workflow transitions for this object
    """

    def translate(id):
        return t(PMF(id + "_transition_title"))

    workflow = getToolByName(obj, 'portal_workflow')
    actions = [{"id": it["id"],
                "title": translate(it["id"])}
               for it in workflow.getTransitionsFor(obj)]

    return actions


def isBasicTransitionAllowed(context, permission=None):
    """Most transition guards need to check the same conditions:

    - Is the object active (cancelled or inactive objects can't transition)
    - Has the user a certain permission, required for transition.  This should
    normally be set in the guard_permission in workflow definition.

    """
    workflow = getToolByName(context, "portal_workflow")
    mtool = getToolByName(context, "portal_membership")
    if workflow.getInfoFor(context, "cancellation_state", "") == "cancelled" \
            or workflow.getInfoFor(context, "inactive_state", "") == "inactive" \
            or (permission and mtool.checkPermission(permission, context)):
        return False
    return True


def is_transition_allowed(instance, transition_id, workflow_id='review_state', permission=None):
    """ Checks if the current instance can be transitioned with transition_id specified. If permission is set, also
        checks if the current user has enough privileges to fire the transition.
    :param instance: the instance to be transitioned
    :param transition_id:  Transition identifier.
    :param workflow_id: Workflow identifier. By default, 'review_state'
    :param permission: permission required for this transition
    :return: True if transition allowed. False if transition not allowed
    """
    # Can't do anything to the object if it's cancelled
    if not isBasicTransitionAllowed(instance, permission):
        return False

    # Instance has the workflow?
    workflow = getToolByName(instance, 'portal_workflow')
    wfs = workflow.getWorkflowsFor(instance)
    wf = [wf for wf in wfs if wf.getId() == workflow_id]
    if len(wf) == 0:
        logger.debug("'%s' has no workflow '%s'" % (instance.portal_type, workflow_id))
        return False

    # The transition can be applied regarding to instance's current state?
    wf = wf[0]
    if not wf.isActionSupported(instance, transition_id):
        curr_state = wf.getInfoFor(instance, workflow_id)
        logger.debug("Transition '%s' not allowed for '%s' with state '%s'" % (transition_id, instance.portal_type,
                                                                               curr_state))
        return False

    # The transition can be applied regarding to permission?
    if permission:
        mtool = getToolByName(instance, "portal_membership")
        if not mtool.checkPermission(permission, instance):
            logger.debug("Transition '%s' not allowed for '%s'. Not enough privileges ('%s')" % (transition_id,
                                                                                                 instance.portal_type,
                                                                                                 permission))
            return False

    return True


def filter_by_state(instances, states, workflow_id='review_state'):
    """ Filters the instances according to the source_states
    :param instances: array of instances to filter
    :param states: array of instance states to be filtered by
    :param workflow_id: workflow identifier. By default, 'review_state'
    :return:The list of matching instances
    """
    matches = []
    for instance in instances:
        workflow = getToolByName(instance, 'portal_workflow')
        if workflow.getInfoFor(instance, workflow_id) in states:
            matches.append(instance)

    return matches

def get_states(instance, workflow_id='review_state'):
    """  Returns the states registered in the system for the instance and workflow specified
    :param instance: the instance for which the states should be retrieved
    :param workflow_id: workflow identifier. By default, 'review_state'
    :return: dictionary of states and transitions
    """
    workflow = getToolByName(instance, 'portal_workflow')
    wfs = workflow.getWorkflowsFor(instance)
    wf = [wf for wf in wfs if wf.getId() == workflow_id]
    if len(wf) == 0:
        return []

    wf = wf[0]
    wf.get
    if not wf.isActionSupported(instance, transition_id):
        curr_state = wf.getInfoFor(instance, workflow_id)
        logger.debug("Transition '%s' not allowed for '%s' with state '%s'" % (transition_id, instance.portal_type,
                                                                               curr_state))
        return False


def get_further_states(instance, state, workflow_id='review_state'):
    """ Returns all the states that follows directly, or indirectly the specified state.
        For example, for an instance 'Sample' and state 'sampled', the method will return the states 'to_be_preserved',
        'sample_due' and 'sample_received', but 'sample_registered' and 'to_be_sampled' will be excluded.
    :param instance: the instance for which the states should be retrieved
    :param state: the target state
    :param workflow_id: workflow identifier. By default, 'review_state'
    :return: list of states after the state specified, in accordance with the type of the instance and the workflow id
    """


def get_previous_states(instance, state, workflow_id='review_state'):
    """ The opposite of get_further_states. For an instance 'Sample' and state 'sampled', the method will return the
        states 'sample_registered' and 'to_be_sampled', but 'to_be_preserved', 'sample_due' and 'sample_received' will
        be excluded.
    :param instance: the instance for which the states should be retrieved
    :param state: the target state
    :param workflow_id: workflow identifier. By default, 'review_state'
    :return: list of states before the state specified, in accordance with the type of the instance and the workflow id
    """
    all_states = get_states(instance, workflow_id)
    return all_states.keys() - get_further_states(instance, state, workflow_id) - [state]


def getCurrentState(obj, stateflowid):
    """ The current state of the object for the state flow id specified
        Return empty if there's no workflow state for the object and flow id
    """
    wf = getToolByName(obj, 'portal_workflow')
    return wf.getInfoFor(obj, stateflowid, '')

# Enumeration of the available status flows
StateFlow = enum(review='review_state',
                 inactive='inactive_state',
                 cancellation='cancellation_state')

# Enumeration of the different available states from the inactive flow
InactiveState = enum(active='active')

# Enumeration of the different states can have a batch
BatchState = enum(open='open',
                  closed='closed',
                  cancelled='cancelled')

BatchTransitions = enum(open='open',
                        close='close')

CancellationState = enum(active='active',
                         cancelled='cancelled')

CancellationTransitions = enum(cancel='cancel',
                               reinstate='reinstate')

# Enumeration of states for review_state
States = enum(to_be_preserved='to_be_preserved',
              to_be_sampled='to_be_sampled')

# Enumeration of actions
Actions = enum(preserve='preserve',
               to_be_preserved='to_be_preserved',
               sample_due='sample_due',
               receive='receive',
               reinstate='reinstate')


class JSONReadExtender(object):

    """- Adds the list of possible transitions to each object, if 'transitions'
    is specified in the include_fields.
    """

    implements(IJSONReadExtender)

    def __init__(self, context):
        self.context = context

    def __call__(self, request, data):
        include_fields = get_include_fields(request)
        if not include_fields or "transitions" in include_fields:
            data['transitions'] = get_workflow_actions(self.context)
