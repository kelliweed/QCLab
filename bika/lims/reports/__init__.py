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

		if report_type == 'productivity_dailysamplesreceived' :
			alsoProvides(obj, IDailySamplesReceived)
			obj.Schema().getField('query').set(obj,[
				{'i': 'DateReceived', 'o': 'plone.app.querystring.operation.date.between', 'v': ['', '']}
				])
		self.request.response.redirect(obj.absolute_url())




		