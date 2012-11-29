"""	All permissions are defined here.
	They are also defined in permissions.zcml.
	The two files must be kept in sync.

    bika.lims.__init__ imports * from this file, so
    bika.lims.PermName or bika.lims.permissions.PermName are
    both valid.

"""
from Products.CMFCore.permissions import AddPortalContent

# Add Permissions:
# ----------------
AddAnalysisProfile = 'BIKA: Add AnalysisProfile'
AddARTemplate = 'BIKA: Add ARTemplate'
AddAnalysis = 'BIKA: Add Analysis'
AddAnalysisRequest = 'BIKA: Add Analysis Request'
AddAnalysisSpec = 'BIKA: Add AnalysisSpec'
AddBatch = 'BIKA: Add Batch'
AddClient = 'BIKA: Add Client'
AddClientFolder = 'BIKA: Add ClientFolder'
AddMethod = 'BIKA: Add Method'
AddPatient = 'BIKA: Add Patient'
AddDoctor = 'BIKA: Add Doctor'
AddSample = 'BIKA: Add Sample'
AddSamplePoint = 'BIKA: Add SamplePoint'
AddSampleMatrix = 'BIKA: Add SampleMatrix'
AddSamplePartition = 'BIKA: Add SamplePartition'
AddSamplingDeviation = 'BIKA: Add SamplingDeviation'
AddAetiologicAgent = 'BIKA: Add AetiologicAgent'
AddTreatment = 'BIKA: AddTreatment'
AddDrug = 'BIKA: Add Drug'
AddImmunization = 'BIKA: Add Immunization'
AddVaccinationCenter = 'BIKA: Add VaccinationCenter'
AddSymptom = 'BIKA: Add Symptom'
AddDrugProhibition = 'BIKA: Add DrugProhibition'

# Default Archetypes Add Permission
ADD_CONTENT_PERMISSION = AddPortalContent

# Add Permissions for specific types, if required
ADD_CONTENT_PERMISSIONS = {
    'ARAnalysisSpec': AddAnalysisSpec,
    'AnalysisProfile': AddAnalysisProfile,
    'Analysis': AddAnalysis,
    'AnalysisRequest': AddAnalysisRequest,
    'Batch': AddBatch,
    'Client': AddClient,
    'Method': AddMethod,
    'Doctor': AddDoctor,
    'Patient': AddPatient,
    'Sample': AddSample,
    'SampleMatrix': AddSampleMatrix,
    'SamplePartition': AddSamplePartition,
    'SamplingDeviation': AddSamplingDeviation,
    'AetiologicAgent': AddAetiologicAgent,
    'Treatment': AddTreatment,
    'Drug': AddDrug,
    'Immunization': AddImmunization,
    'VaccinationCenter': AddVaccinationCenter,
    'Symptom': AddSymptom,
    'DrugProhibition': AddDrugProhibition,
}

# Very Old permissions:
# ---------------------
DispatchOrder = 'BIKA: Dispatch Order'
ManageARImport = 'BIKA: Manage ARImport'
ManageAnalysisRequests = 'BIKA: Manage Analysis Requests'
ManageBika = 'BIKA: Manage Bika'
ManageClients = 'BIKA: Manage Clients'
ManageOrders = 'BIKA: Manage Orders'
ManagePricelists = 'BIKA: Manage Pricelists'
ManagePatients = 'BIKA: Manage Patients'
ManageDoctors = 'BIKA: Manage Doctors'
ManageReference = 'BIKA: Manage Reference'
ManageReferenceSuppliers = 'BIKA: Manage Reference Suppliers'
ManageSamples = 'BIKA: Manage Samples'
PostInvoiceBatch = 'BIKA: Post Invoice batch'

# this is for creating and transitioning worksheets
ManageWorksheets = 'BIKA: Manage Worksheets'
# this is for adding/editing/exporting analyses on worksheets
EditWorksheet = 'BIKA: Edit Worksheet'
RejectWorksheet = 'BIKA: Reject Worksheet'

# New or changed permissions:
# ---------------------------
SampleSample = 'BIKA: Sample Sample'
PreserveSample = 'BIKA: Preserve Sample'
ReceiveSample = 'BIKA: Receive Sample'
ExpireSample = 'BIKA: Expire Sample'
DisposeSample = 'BIKA: Dispose Sample'
ImportAnalysis = 'BIKA: Import Analysis'
Retract = "BIKA: Retract"
Verify = 'BIKA: Verify'
VerifyOwnResults = 'BIKA: Verify own results'
PublishAR = 'BIKA: Publish'
EditSample = 'BIKA: Edit Sample'
EditAR = 'BIKA: Edit AR'
ResultsNotRequested = 'BIKA: Results not requested'
ManageInvoices = 'BIKA: Manage Invoices'
ViewResults = 'BIKA: View Results'
EditResults = 'BIKA: Edit Results'
EditFieldResults = 'BIKA: Edit Field Results'
CancelAndReinstate = 'BIKA: Cancel and reinstate'
