from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATContentTypes.utils import DT2dt, dt2DT
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import DurationField
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IBatch
from datetime import timedelta
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
    StringField('BatchID',
        searchable=True,
        required=1,
        widget=StringWidget(
            label=_("Batch ID"),
        )
    ),
    ReferenceField('Doctor',
        required = 1,
        allowed_types = ('Doctor',),
        referenceClass = HoldingReference,
        relationship = 'BatchDoctor',
        widget=StringWidget(
            label=_("Doctor"),
        )
    ),
    ComputedField('DoctorUID',
        expression='context.getDoctor() and context.getDoctor().UID() or None',
        widget=ComputedWidget(
            visible=False,
        ),
    ),
    ReferenceField('Patient',
        required=0,
        multiValued=0,
        allowed_types = ('Patient',),
        referenceClass = HoldingReference,
        relationship = 'BatchPatient',
        widget=StringWidget(
            label=_('Patient'),
        ),
    ),
    ComputedField('PatientUID',
        expression='context.getPatient() and context.getPatient().UID() or None',
        widget=ComputedWidget(
            visible=False,
        ),
    ),
    ReferenceField('AnalysisRequests',
        allowed_types=('AnalysisRequest',),
        relationship='BatchAnalysisRequests',
        multiValued=1,
    ),
    TextField('Remarks',
        searchable=True,
        default_content_type='text/x-web-intelligent',
        allowable_content_types=('text/x-web-intelligent',),
        default_output_type="text/html",
        widget=TextAreaWidget(
            macro="bika_widgets/remarks",
            label=_('Remarks'),
            append_only=True,
        ),
    ),
),
)

schema['title'].required = False
schema['title'].widget.visible = False
schema['description'].widget.visible = True
schema['AnalysisRequests'].widget.visible = False

schema.moveField('BatchID', before='description')
schema.moveField('description', after='Patient')

class Batch(BaseContent):
    implements(IBatch)
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
        """ Return the BatchID or id as title """
        res = self.getBatchID()
        return str(res).encode('utf-8')

registerType(Batch, PROJECTNAME)
