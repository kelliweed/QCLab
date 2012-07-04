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
AddClient = 'BIKA: Add Client'
AddClientFolder = 'BIKA: Add ClientFolder'
AddMethod = 'BIKA: Add Method'
AddProvider = 'BIKA: Add Provider'
AddSample = 'BIKA: Add Sample'
AddSampleMatrix = 'BIKA: Add SampleMatrix'
AddSamplePartition = 'BIKA: Add SamplePartition'
AddSamplingDeviation = 'BIKA: Add SamplingDeviation'
AddProvider = 'BIKA: Add Provider'

# Default Archetypes Add Permission
ADD_CONTENT_PERMISSION = AddPortalContent

# Add Permissions for specific types, if required
ADD_CONTENT_PERMISSIONS = {
    'ARAnalysisSpec': AddAnalysisSpec,
    'AnalysisProfile': AddAnalysisProfile,
    'Analysis': AddAnalysis,
    'AnalysisRequest': AddAnalysisRequest,
    'Client': AddClient,
    'Method': AddMethod,
    'Provider': AddProvider,
    'Sample': AddSample,
    'SampleMatrix': AddSampleMatrix,
    'SamplePartition': AddSamplePartition,
    'SamplingDeviation': AddSamplingDeviation,
    'Provider': AddProvider,
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
ManageProviders = 'BIKA: Manage Providers'
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
