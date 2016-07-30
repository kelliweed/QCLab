from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.layout.viewlets import ViewletBase
from zope.dottedname.resolve import resolve
from zope.interface import alsoProvides
from zope.schema import ValidationError

from bika.lims.browser.storage import getStorageTypes


class AddStorageLevelsViewlet(ViewletBase):
    index = ViewPageTemplateFile("templates/addstoragelevels_viewlet.pt")

    def storage_types(self):
        """Return UI-friendly formatted version of getStorageTypes() output
        """
        return getStorageTypes(dotted_names=True)

    def render(self):
        # If there are any storage_locations present in this folder,
        # Then we will not allow adding of Storage Levels (and vice-versa).
        storage_locations = self.context.objectValues('StorageLocation')
        if storage_locations:
            return ""
        else:
            return self.index()


class AddStorageLevelsSubmitHandler(BrowserView):
    """
    """

    def __call__(self):

        if "viewlet_submitted" in self.request.form:

            try:
                self.validate_form_inputs()
            except ValidationError as e:
                self.form_error(e.message)
                return

            # Validation is complete, now set local variables from form inputs.
            form = self.request.form
            titletemplate = form.get('titletemplate', None)
            idtemplate = form.get('idtemplate', None)
            seq_start = int(form.get('seq_start', None))
            storagelevel_count = int(form.get('storagelevel_count', None))
            storagelocation_count = int(form.get('storagelocation_count', None))
            storage_types = form.get('storage_types', [])

            # Create required storage levels
            levels = self.create_storage_levels(
                idtemplate, seq_start, storagelevel_count, titletemplate)

            # Create required storage locations
            locations = self.create_storage_locations(
                levels, storagelocation_count)

            if storagelocation_count:
                # If storage types are selected, and storage locations have been
                # created, then I will apply these storage types to the new
                # locations.
                for location in locations:
                    self.set_storage_types(location, storage_types)
            else:
                # If storage types are selected, and no storage locations are
                # created, then I will apply the storage types directly to the
                # storage levels created above.
                for level in levels:
                    self.set_storage_types(level, storage_types)

            msg = u'%s Storage levels and %s storage locations created.' % (
                len(levels), len(locations))
            self.context.plone_utils.addPortalMessage(msg)
            self.request.response.redirect(self.context.absolute_url())

    def validate_form_inputs(self):

        form = self.request.form

        titletemplate = form.get('titletemplate', None)
        idtemplate = form.get('idtemplate', None)
        if not (titletemplate and idtemplate):
            raise ValidationError(u'ID and Title template are both required.')
        if not ('{id}' in titletemplate and '{id}' in idtemplate):
            raise ValidationError(u'ID and Title templates must contain {id} '
                                  u'for ID sequence substitution')
        try:
            seq_start = int(form.get('seq_start', None))
            storagelevel_count = int(form.get('storagelevel_count', None))
            storagelocation_count = int(form.get('storagelocation_count', None))
            # Could be set to "", but that's valid sometimes in this case
            if not storagelocation_count:
                storagelocation_count = 0
        except:
            raise ValidationError(
                u'Sequence start and all counts must be integers')

        # verify ID sequence start
        if seq_start < 1:
            raise ValidationError(u'Sequence Start may not be < 1')

        # verify StorageLevel
        if storagelevel_count < 1:
            raise ValidationError(u'Storage Level count must not be < 1')

        # verify StorageLocation count
        if storagelocation_count < 0:
            raise ValidationError(u'Storagelocation count may not be < 0')

        # verify storage_type interface selection
        storage_types = form.get('storage_types', [])
        if storagelocation_count and not storage_types:
            raise ValidationError(
                u'To create Storage locations in the new levels, at least one '
                u'Storage Type must be selected.')

        # Check that none of the IDs conflict with existing items
        ids = [x.id for x in self.context.objectValues('StorageLevel')]
        for x in range(storagelevel_count):
            check = idtemplate.format(id=seq_start + x)
            if check in ids:
                raise ValidationError(
                    u'The ID %s exists, cannot be created.' % check)

    @staticmethod
    def create_storage_locations(levels, storagelocation_count):
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
                    locations.append(ob)
        return locations

    def create_storage_levels(
            self, idtemplate, seq_start, storagelevel_count, titletemplate):
        """Create the new storage level items
        """
        levels = []
        for x in range(seq_start, storagelevel_count + 1):
            ob = api.content.create(
                container=self.context, type="StorageLevel",
                id=idtemplate.format(id=x), title=titletemplate.format(id=x))
            self.context.manage_renameObject(ob.id, idtemplate.format(id=x))
            levels.append(ob)

        return levels

    def set_storage_types(self, ob, storage_types):
        """Set field values across each object if possible
        """
        # If it's only one type, then the Plone form hands us a single string.
        # If multiple types are selected, then Plone form hands us a list.
        if isinstance(storage_types, basestring):
            storage_types = [storage_types]

        schema = ob.Schema()
        if storage_types and 'StorageTypes' in schema:
            ob.Schema()['StorageTypes'].set(ob, storage_types)
        self.provide_storagetype_interfaces(ob, storage_types)

    @staticmethod
    def provide_storagetype_interfaces(ob, storage_types):
        """Assign any selected storage type interfaces to this location.
        The storage type interfaces are passed here as dotted names, and
        must be resolved.
        """
        for storage_type in storage_types:
            inter = resolve(storage_type)
            alsoProvides(ob, inter)

    def form_error(self, msg):
        self.context.plone_utils.addPortalMessage(msg)
        self.request.response.redirect(self.context.absolute_url())
