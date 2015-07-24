from Products.CMFPlone.utils import _createObjectByType
from bika.lims.utils import tmpID
from zExceptions import BadRequest
from zope.interface import alsoProvides
from bika.lims.reports.interfaces import *


class CreateReport(object):
	"""docstring for CreateReport"""
	def __init__(self, context, request=None):
		self.context = context
		self.request = request

	def __call__(self):
		if 'report' not in self.request:
			raise BadRequest("No report was specified in request!")
		report_type = self.request['report']		
		obj = _createObjectByType('ReportCollection', self.context, tmpID())

		obj.unmarkCreationFlag()
	#	productivity_reports = ['dailysamplesreceived', 'samplesreceivedvsreported', 'analysesperservice', 'analysespersampletype', \
    #     'analysesperclient', 'analysestats', 'analysestats_overtime', 'analysesperdepartment', 'analysesperformedpertotal', \
    #     'analysesattachments', 'dataentrydaybook']
		if report_type == 'productivity_dailysamplesreceived' :
			alsoProvides(obj, IDailySamplesReceived)
			obj.Schema().getField('query').set(obj,[
				{'i': 'DateReceived', 'o': 'plone.app.querystring.operation.date.today', 'v': ['', '']}
				])
		elif report_type == 'productivity_samplesreceivedvsreported' :
			alsoProvides(obj, ISamplesReceivedVsReported)
			obj.Schema().getField('query').set(obj,[
				{'i': 'DateReceived', 'o': 'plone.app.querystring.operation.date.today', 'v': ['', '']}
				])
		elif report_type == 'productivity_analysesperservice' :
			alsoProvides(obj, IAnalysesPerService)
			obj.Schema().getField('query').set(obj,[
				{'i': 'created', 'o': 'plone.app.querystring.operation.date.today'}, \
				{'i': 'DatePublished', 'o': 'plone.app.querystring.operation.date.today'}, \
				{'i': 'review_state', 'o': 'plone.app.querystring.operation.selection.is'}, \
				{'i': 'cancellation_state', 'o': 'plone.app.querystring.operation.selection.is'}, \
				{'i': 'worksheetanalysis_review_state', 'o': 'plone.app.querystring.operation.selection.is'} \
				])	
		self.request.response.redirect(obj.absolute_url())




		