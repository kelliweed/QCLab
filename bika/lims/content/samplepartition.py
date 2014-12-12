from AccessControl import ClassSecurityInfo
from bika.lims import logger
from bika.lims.browser.fields import DurationField
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import ISamplePartition
from bika.lims.workflow import doActionFor, isBasicTransitionAllowed, is_transition_allowed, filter_by_state, Actions, \
    StateFlow
from bika.lims.workflow import skip
from DateTime import DateTime
from datetime import timedelta
from Products.Archetypes.public import *
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATContentTypes.utils import DT2dt, dt2DT
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
    ReferenceField('Container',
        allowed_types=('Container',),
        relationship='SamplePartitionContainer',
        required=1,
        multiValued=0,
    ),
    ReferenceField('Preservation',
        allowed_types=('Preservation',),
        relationship='SamplePartitionPreservation',
        required=0,
        multiValued=0,
    ),
    BooleanField('Separate',
        default=False
    ),
    ReferenceField('Analyses',
        allowed_types=('Analysis',),
        relationship='SamplePartitionAnalysis',
        required=0,
        multiValued=1,
    ),
    DateTimeField('DatePreserved',
    ),
    StringField('Preserver',
        searchable=True
    ),
    DurationField('RetentionPeriod',
    ),
    ComputedField('DisposalDate',
        expression = 'context.disposal_date()',
        widget = ComputedWidget(
            visible=False,
        ),
    ),
)
)

schema['title'].required = False


class SamplePartition(BaseContent, HistoryAwareMixin):
    implements(ISamplePartition)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def _getCatalogTool(self):
        from bika.lims.catalog import getCatalog
        return getCatalog(self)

    def Title(self):
        """ Return the Sample ID as title """
        return safe_unicode(self.getId()).encode('utf-8')

    security.declarePublic('getAnalyses')

    def getAnalyses(self):
        """ return list of titles of analyses linked to this sample Partition """
        analyses = sorted(self.getBackReferences("AnalysisSamplePartition"))
        return analyses

    security.declarePublic('current_date')

    def current_date(self):
        """ return current date """
        return DateTime()

    security.declarePublic('disposal_date')

    def disposal_date(self):
        """ return disposal date """

        DateSampled = self.getDateSampled()

        # fallback to sampletype retention period
        st_retention = self.aq_parent.getSampleType().getRetentionPeriod()

        # but prefer retention period from preservation
        pres = self.getPreservation()
        pres_retention = pres and pres.getRetentionPeriod() or None

        rp = pres_retention and pres_retention or None
        rp = rp or st_retention

        td = timedelta(
            days='days' in rp and int(rp['days']) or 0,
            hours='hours' in rp and int(rp['hours']) or 0,
            minutes='minutes' in rp and int(rp['minutes']) or 0)

        dis_date = DateSampled and dt2DT(DT2dt(DateSampled) + td) or None
        return dis_date

    def guard_sample_prep_transition(self):
        if not isBasicTransitionAllowed(self):
            return False
        if self.aq_parent and self.aq_parent.getPreparationWorkflow():
            return True
        return False

    def workflow_do_action(self, action, workflow_id='review_state', notify_parent=True):
        """
        Transitions the state of the Sample Partition and its analysis linked (children). If the partition transition
        succeed, the method also notifies the action to the Sample (the parent) in order to escalate the action to
        siblings and other objects not directly related with this partition but that might be transitioned too.
        :param action: the transition id
        :param workflow_id: the workflow identifier. By default 'review_state'
        :param notify_parent: notify parent after the transition. By default, True.
        :return: True if the the transition of the partition has succeed. Otherwise, return False.
        """
        if skip(self, action) or not is_transition_allowed(self, action, workflow_id):
            return False

        # 1. Transition partition's children (analyses)
        analyses = self.getBackReferences('AnalysisSamplePartition')
        analyses = [an for an in analyses if is_transition_allowed(an, action, workflow_id)]
        for analysis in analyses:
            doActionFor(analysis, action)

        # 2. Transition the partition itself
        performed, msg = doActionFor(self, action)
        if not performed:
            # Something went wrong. Abort.
            return False

        # 3. Notify partition's parent (Sample)
        #    The parent is responsible of transitioning its own children. The sample partition must only be
        #    responsible of transitioning itself and its own children, but not its siblings.
        if notify_parent:
            self.aq_parent.notify_transition(self, action)

        return True


    def workflow_script_preserve(self):
        self.workflow_do_action(Actions.preserve)

    def workflow_transition_expire(self):
        self.setDateExpired(DateTime())
        self.reindexObject(idxs=[StateFlow.review, "getDateExpired", ])

    def workflow_script_sample(self):
        self.workflow_do_action(Actions.sample, StateFlow.sample)

    def workflow_script_to_be_preserved(self):
        self.workflow_do_action(Actions.to_be_preserved, StateFlow.review)

    def workflow_script_sample_due(self):
        self.workflow_do_action(Actions.sample_due, StateFlow.review)

    def workflow_script_receive(self):
        self.setDateReceived(DateTime())
        self.reindexObject(idxs=["getDateReceived", ])
        self.workflow_do_action(Actions.receive, StateFlow.review)

    def workflow_script_reinstate(self):
        if skip(self, "reinstate"):
            return
        sample = self.aq_parent
        workflow = getToolByName(self, 'portal_workflow')
        self.reindexObject(idxs=["cancellation_state", ])
        sample_c_state = workflow.getInfoFor(sample, 'cancellation_state')
        # if all sibling partitions are active, activate sample
        if not skip(sample, "reinstate", peek=True):
            cancelled = [sp for sp in sample.objectValues("SamplePartition")
                         if workflow.getInfoFor(sp, 'cancellation_state') == 'cancelled']
            if sample_c_state == 'cancelled' and not cancelled:
                workflow.doActionFor(sample, 'reinstate')

    def workflow_script_cancel(self):
        if skip(self, "cancel"):
            return
        sample = self.aq_parent
        workflow = getToolByName(self, 'portal_workflow')
        self.reindexObject(idxs=["cancellation_state", ])
        sample_c_state = workflow.getInfoFor(sample, 'cancellation_state')
        # if all sibling partitions are cancelled, cancel sample
        if not skip(sample, "cancel", peek=True):
            active = [sp for sp in sample.objectValues("SamplePartition")
                      if workflow.getInfoFor(sp, 'cancellation_state') == 'active']
            if sample_c_state == 'active' and not active:
                workflow.doActionFor(sample, 'cancel')

registerType(SamplePartition, PROJECTNAME)
