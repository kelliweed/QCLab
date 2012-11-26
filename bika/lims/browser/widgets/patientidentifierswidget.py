from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import PMF, bikaMessageFactory as _
from bika.lims.browser import BrowserView

class PatientIdentifiersView(BrowserView):
    template = ViewPageTemplateFile("patient_identifiers.pt")

    def __init__(self, context, request, fieldvalue, allow_edit):
        self.context = context
        self.request = request
        self.fieldvalue = fieldvalue
        self.allow_edit = allow_edit

    def __call__(self):
        return self.template()
    
    def hasIdentifiers(self):
        return len(self.context.getPatientIdentifiers())>0
    

class PatientIdentifiersWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "bika_widgets/patientidentifierswidget",
        'helper_js': ("bika_widgets/patientidentifierswidget.js",),
        'helper_css': ("bika_widgets/patientidentifierswidget.css",),
    })

    security = ClassSecurityInfo()
    security.declarePublic('process_form')

    def process_form(self, instance, field, form, empty_marker=None, emptyReturnsMarker=False):
        value = len(instance.getPatientIdentifiers())>0 and instance.getPatientIdentifiers() or []
        if 'PID_clear' in form:
            value = []
            
        elif 'PID_delete' in form:
            valueout = []
            for i in range(len(value)):
                if not ('PID_SelectItem-%s'%i in form):
                    valueout.append(value[i])
            value = valueout
            
        elif 'PID_submitted' in form:
            bsc = getToolByName(instance, 'bika_setup_catalog')
            for i in range(len(form.get('PID_IdentifierTypeUID', []))):
                U = form['PID_IdentifierTypeUID'][i]
                T = form['PID_IdentifierType'][i]
                I = form['PID_Identifier'][i]
                
                # Only add the element if the Identifier Type exists
                itlist = bsc(portal_type='IdentifierType', title=T)
                if itlist:
                    value.append({'IdentifierTypeUID':U, 'IdentifierType': T, 'Identifier': I })
        return value, {}

    security.declarePublic('PatientIdentifiers')

    def PatientIdentifiers(self, field, allow_edit=False):
        fieldvalue = getattr(field, field.accessor)()
        view = PatientIdentifiersView(self,
                                self.REQUEST,
                                fieldvalue=fieldvalue,
                                allow_edit=allow_edit)
        return view()

registerWidget(PatientIdentifiersWidget,
               title=_('Patient identifiers'),
               description=_("Patient additional identifiers"),)
