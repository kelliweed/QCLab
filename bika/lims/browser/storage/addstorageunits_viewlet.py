from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.layout.viewlets import ViewletBase
from zope.schema import ValidationError


class AddStorageUnitsViewlet(ViewletBase):
    index = ViewPageTemplateFile("templates/addstorageunits_viewlet.pt")

    def render(self):
        return self.index()


class AddStorageUnitsSubmitHandler(BrowserView):
    """
    """

    def __call__(self):

        if "viewlet_submitted" in self.request.form:

            try:
                self.validate_form_inputs()
            except ValidationError:
                return

            titletemplate = self.request.form.get('titletemplate', None)
            idtemplate = self.request.form.get('idtemplate', None)
            # no validation on these
            temperature = self.request.form.get('temperature', '')
            department = self.request.form.get('department', None)
            address = self.request.form.get('address', None)
            seq_start = int(self.request.form.get('seq_start', None))
            storageunit_count = int(
                self.request.form.get('storageunit_count', None))

            created_units = self.create_storage_units(address, department,
                                                      idtemplate, seq_start,
                                                      storageunit_count,
                                                      temperature,
                                                      titletemplate)

            msg = u'%s Storage units created.' % len(created_units)
            self.context.plone_utils.addPortalMessage(msg)
            self.request.response.redirect(self.context.absolute_url())

    def create_storage_units(self, address, department, idtemplate, seq_start,
                             storageunit_count, temperature, titletemplate):
        """Create the new storage unit items
        """
        created_units = []
        for x in range(seq_start, storageunit_count + 1):
            ob = api.content.create(
                container=self.context, type="StorageUnit",
                id=idtemplate.format(id=x),
                title=titletemplate.format(id=x))
            self.set_inputs_into_schema(
                address, department, ob, temperature)
            self.context.manage_renameObject(ob.id, idtemplate.format(id=x), )
            created_units.append(ob)
        return created_units

    def validate_form_inputs(self):
        # Title and ID Templates
        titletemplate = self.request.form.get('titletemplate', None)
        idtemplate = self.request.form.get('idtemplate', None)
        if not (titletemplate and idtemplate):
            self.form_error(u'ID and Title template are both required.')
            raise ValidationError
        if not ('{id}' in titletemplate and '{id}' in idtemplate):
            self.form_error(u'ID and Title templates must contain {id} '
                            u'for ID sequence substitution')
            raise ValidationError

        # check for valid integer values
        try:
            seq_start = int(self.request.form.get('seq_start', None))
            storageunit_count = int(
                self.request.form.get('storageunit_count', None))
        except:
            self.form_error(u'Sequence start and all counts must '
                            u'be integers')
            self.request.response.redirect(self.context.absolute_url())
            raise ValidationError

        # verify ID sequence start
        if seq_start < 1:
            self.form_error(u'Sequence Start may not be < 1')
            self.request.response.redirect(self.context.absolute_url())
            raise ValidationError

        # verify StorageUnit
        if storageunit_count < 1:
            self.form_error(u'Storage Unit count must not be < 1')
            self.request.response.redirect(self.context.absolute_url())
            raise ValidationError

        # Check that none of the IDs conflict with existing items
        ids = [x.id for x in self.context.objectValues('StorageUnit')]
        for x in range(storageunit_count):
            check = idtemplate.format(id=seq_start + x)
            if check in ids:
                self.form_error(
                    u'The ID %s exists, cannot be created.' % check)
                self.request.response.redirect(self.context.absolute_url())
                raise ValidationError

    def set_inputs_into_schema(self, address, department, ob, temperature):
        # Set field values across each object if possible
        schema = ob.Schema()
        if temperature and 'Temperature' in schema:
            ob.Schema()['Temperature'].set(ob, temperature)
        if department and 'Department' in schema:
            ob.Schema()['Department'].set(ob, temperature)
        if address and 'Address' in schema:
            ob.Schema()['Address'].set(ob, temperature)

    def form_error(self, msg):
        self.context.plone_utils.addPortalMessage(msg)
        self.request.response.redirect(self.context.absolute_url())
