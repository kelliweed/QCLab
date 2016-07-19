from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.layout.viewlets import ViewletBase


class AddStorageUnitsViewlet(ViewletBase):
    index = ViewPageTemplateFile("templates/addstorageunits_viewlet.pt")

    def render(self):
        return self.index()


class AddStorageUnitsSubmitHandler(BrowserView):
    """
    """

    def __call__(self):

        if "viewlet_submitted" in self.request.form:

            # Title and ID Templates
            titletemplate = self.request.form.get('titletemplate', None)
            idtemplate = self.request.form.get('idtemplate', None)
            if not (titletemplate and idtemplate):
                self.form_error(u'ID and Title template are both required.')
                return
            if not ('{id}' in titletemplate and '{id}' in idtemplate):
                self.form_error(u'ID and Title templates must contain {id} '
                                u'for ID sequence substitution')
                return

            # no validation on these
            temperature = self.request.form.get('temperature', '')
            department = self.request.form.get('department', None)
            address = self.request.form.get('address', None)

            # check for valid integer values
            try:
                seq_start = int(self.request.form.get('seq_start', None))
                storageunit_count = int(
                    self.request.form.get('storageunit_count', None))
            except:
                self.form_error(u'Sequence start and all counts must '
                                u'be integers')
                self.request.response.redirect(self.context.absolute_url())
                return

            # verify ID sequence start
            if seq_start < 1:
                self.form_error(u'Sequence Start may not be < 1')
                self.request.response.redirect(self.context.absolute_url())
                return

            # verify StorageUnit
            if storageunit_count < 1:
                self.form_error(u'Storage Unit count must not be < 1')
                self.request.response.redirect(self.context.absolute_url())
                return

            # Check that none of the IDs conflict with existing items
            ids = [x.id for x in self.context.objectValues('StorageUnit')]
            for x in range(storageunit_count):
                check = idtemplate.format(id=seq_start + x)
                if check in ids:
                    self.form_error(
                        u'The ID %s exists, cannot be created.' % check)
                    self.request.response.redirect(self.context.absolute_url())
                    return

            # Create the new storage unit items
            created_units = []
            for x in range(seq_start, storageunit_count+s):
                id = idtemplate.format(id=x)
                title = titletemplate.format(id=x)
                ob = api.content.create(
                    container=self.context, type="StorageUnit",
                    id=id, title=title)
                schema = ob.Schema()
                if temperature and 'Temperature' in schema:
                    ob.Schema()['Temperature'].set(ob, temperature)
                if department  and 'Department' in schema:
                    ob.Schema()['Department'].set(ob, temperature)
                if address  and 'Address' in schema:
                    ob.Schema()['Address'].set(ob, temperature)
                self.context.manage_renameObject(ob.id, id)
                created_units.append(ob)

            msg = u'%s Storage units created.' % len(created_units)
            self.context.plone_utils.addPortalMessage(msg)
            self.request.response.redirect(self.context.absolute_url())

    def form_error(self, msg):
        self.context.plone_utils.addPortalMessage(msg)
        self.request.response.redirect(self.context.absolute_url())
        return msg
