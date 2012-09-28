from bika.lims.browser import BrowserView
import re
import sys
import json
from bika.lims.idserver import generateUniqueId
from bika.lims.utils import changeWorkflowState

class Add(BrowserView):
    """Add a new AR and associated Sample and Analyses.
    The function accepts a JSON variable in the request:
    input_string: {
        clientname*: client Title
        ar_id: new AR id
        Contact*: client contact Fullname
        ClientOrderNumber
        SampleType*: Title
        SamplePoint: Title
        SamplingDate*: String
        ClientReference: String
        ClientSampleID: String
    }
    * = required.

    On success, returns the ID of the created ID.
    On error, returns a string.
    """

    def __call__(self):

        try:
            values = json.loads(self.request['input_string'])
        except:
            return "Input JSON cannot be loaded"

        try:
            client = self.portal_catalog(
                portal_type='Client',
                title=values['clientname'])[0].getObject()
        except:
            return "Client not found"

        wftool = self.portal_workflow

        # add Sample
        SamplingWorkflowEnabled =\
            self.context.bika_setup.getSamplingWorkflowEnabled()
        _id = client.invokeFactory('Sample', id = 'tmp')
        sample = client[_id]
        sample.edit(
            ClientSampleID = values.get('ClientSampleID', ''),
            SamplePoint = values.get('SamplePoint', ''),
            SampleType = values.get['SampleType'],
            SamplingDate = values.get['SamplingDate'],
            SamplingWorkflowEnabled = False,
        )
        sample.processForm()
        if SamplingWorkflowEnabled:
            wftool.doActionFor(sample, 'sampling_workflow')
        else:
            wftool.doActionFor(sample, 'no_sampling_workflow')

        # Single partition
        _id = sample.invokeFactory('SamplePartition', id = 'tmp')
        part = sample[_id]
        if SamplingWorkflowEnabled:
            wftool.doActionFor(sample, 'sampling_workflow')
        else:
            wftool.doActionFor(sample, 'no_sampling_workflow')

        # add AR
        client.invokeFactory('AnalysisRequest', id = 'tmp')
        ar = client[_id]
        ar.edit(
            Sample = sample.UID(),
            **dict(values)
        )
        ar.processForm()
        # re-set AR id
        ar.reindexObject(idxs=['id',])
        if SamplingWorkflowEnabled:
            wftool.doActionFor(sample, 'sampling_workflow')
        else:
            wftool.doActionFor(sample, 'no_sampling_workflow')

        return ar.getId()

class Results(BrowserView):
    """Returns all verified results in an AR as a JSON string.
    """

    def __call__(self):

        try:
            values = json.loads(self.request['input_string'])
        except:
            return "Input JSON cannot be loaded"

        proxy = bc(portal_type = 'AnalysisRequest',
                   getClientSampleIDid = ar_id)[0]
        ar = proxy.getObject()
        analyses = ar.getAnalyses(full_objects = True)

        for analysis in analyses:
            review_state = wf.getInfoFor(analysis, 'review_state')
            print "%s/%s: %s (%s)" % (ar_id,
                                 analysis.Title(),
                                 analysis.getResult(),
                                 review_state)
