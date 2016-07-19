from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.layout.viewlets import ViewletBase
from zope.dottedname.resolve import resolve
from zope.interface import alsoProvides


class AddStoragesViewlet(ViewletBase):
    index = ViewPageTemplateFile("templates/addstorages_viewlet.pt")

    def render(self):
        return self.index()


class AddStoragesSubmitHandler(BrowserView):
    """
    """

    def __call__(self):

        if "viewlet_submitted" in self.request.form:

            self.validate_form_inputs()

            titletemplate = self.request.form.get('titletemplate', None)
            idtemplate = self.request.form.get('idtemplate', None)
            seq_start = int(self.request.form.get('seq_start', None))
            storagelevel_count = int(
                self.request.form.get('storagelevel_count', None))
            storagelocation_count = int(
                self.request.form.get('storagelocation_count', None))
            storage_types = self.request.form.get('storage_types', [])

            levels = self.create_storage_levels(
                idtemplate, seq_start, storagelevel_count, titletemplate)

            locations = self.create_storage_locations(
                levels, storage_types, storagelocation_count)

            msg = u'%s Storage levels and %s storage locations created.' % (
                len(levels), len(locations))
            self.context.plone_utils.addPortalMessage(msg)
            self.request.response.redirect(self.context.absolute_url())

    def validate_form_inputs(self):

        titletemplate = self.request.form.get('titletemplate', None)
        idtemplate = self.request.form.get('idtemplate', None)
        if not (titletemplate and idtemplate):
            self.form_error(u'ID and Title template are both required.')
            raise RuntimeError
        if not ('{id}' in titletemplate and '{id}' in idtemplate):
            self.form_error(u'ID and Title templates must contain {id} '
                            u'for ID sequence substitution')
            raise RuntimeError
        try:
            seq_start = int(self.request.form.get('seq_start', None))
            storagelevel_count = int(
                self.request.form.get('storagelevel_count', None))
            storagelocation_count = int(
                self.request.form.get('storagelocation_count', None))
        except:
            self.form_error(u'Sequence start and all counts must '
                            u'be integers')
            self.request.response.redirect(self.context.absolute_url())
            raise RuntimeError

        # verify ID sequence start
        if seq_start < 1:
            self.form_error(u'Sequence Start may not be < 1')
            self.request.response.redirect(self.context.absolute_url())
            raise RuntimeError

        # verify StorageLevel
        if storagelevel_count < 1:
            self.form_error(u'Storage Level count must not be < 1')
            self.request.response.redirect(self.context.absolute_url())
            raise RuntimeError

        # verify StorageLocation count
        if storagelocation_count < 0:
            self.form_error(u'Storagelocation count may not be < 0')
            self.request.response.redirect(self.context.absolute_url())
            raise RuntimeError

        # verify storage_type interface selection
        storage_types = self.request.form.get('storage_types', [])
        if any([storage_types, storagelocation_count]) \
                and not all([storage_types, storagelocation_count]):
            self.form_error(u'To create Storage locations in the new '
                            u'levels, at least one Storage Type must be '
                            u'selected and the number of storage locations '
                            u'must be > 0')
            self.request.response.redirect(self.context.absolute_url())
            raise RuntimeError

        # Check that none of the IDs conflict with existing items
        ids = [x.id for x in self.context.objectValues('StorageLevel')]
        for x in range(storagelevel_count):
            check = idtemplate.format(id=seq_start + x)
            if check in ids:
                self.form_error(
                    u'The ID %s exists, cannot be created.' % check)
                self.request.response.redirect(self.context.absolute_url())
                raise RuntimeError

    def create_storage_locations(
            self, levels, storage_types, storagelocation_count):
        """If required, create the StorageLocations inside the new levels.
        """
        locations = []
        if storagelocation_count:
            for level in levels:
                for x in range(1, storagelocation_count + 1):
                    ob = api.content.create(
                        container=level, type="StorageLocation",
                        id="pos-%s" % x,
                        title="Position %s" % x)
                    self.set_inputs_into_schema(ob, storage_types)
                    locations.append(ob)
        return locations

    def create_storage_levels(
            self, idtemplate, seq_start, storagelevel_count, titletemplate):
        """Create the new storage level items
        """
        levels = []
        for x in range(seq_start, storagelevel_count + 1):
            id = idtemplate.format(id=x)
            title = titletemplate.format(id=x)
            ob = api.content.create(
                container=self.context, type="StorageLevel",
                id=id, title=title)
            self.context.manage_renameObject(ob.id, id)
            levels.append(ob)

        return levels

    def set_inputs_into_schema(self, ob, storage_types):
        # Set field values across each object if possible
        schema = ob.Schema()
        if storage_types and 'StorageTypes' in schema:
            ob.Schema()['StorageTypes'].set(ob, storage_types)
        self.alsoprovide_storage_interfaces(ob, storage_types)

    def alsoprovide_storage_interfaces(self, ob, storage_types):
        """Assign any selected storage type interfaces to this location.
        """
        for storage_type in storage_types:
            inter = resolve(storage_type)
            alsoProvides(ob, inter)

    def form_error(self, msg):
        self.context.plone_utils.addPortalMessage(msg)
        self.request.response.redirect(self.context.absolute_url())
