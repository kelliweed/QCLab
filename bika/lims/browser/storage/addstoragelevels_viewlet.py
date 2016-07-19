from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.layout.viewlets import ViewletBase


class AddStorageLevelsViewlet(ViewletBase):
    index = ViewPageTemplateFile("templates/addstoragelevels_viewlet.pt")

    def render(self):
        return self.index()


class AddStorageLevelsSubmitHandler(BrowserView):
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
                return

            # verify ID sequence start
            if seq_start < 1:
                self.form_error(u'Sequence Start may not be < 1')
                self.request.response.redirect(self.context.absolute_url())
                return

            # verify StorageLevel
            if storagelevel_count < 1:
                self.form_error(u'Storage Level count must not be < 1')
                self.request.response.redirect(self.context.absolute_url())
                return

            # verify StorageLocation count
            if storagelocation_count < 0:
                self.form_error(u'Storagelocation count may not be < 0')
                self.request.response.redirect(self.context.absolute_url())
                return

            # verify storage_type interface selection
            storage_types = self.request.form.get('storage_type', [])
            if any([storage_types, storagelocation_count]) \
                    and not all([storage_types, storagelocation_count]):
                self.form_error(u'To create Storage locations in the new '
                                u'levels, at least one Storage Type must be '
                                u'selected.')
                self.request.response.redirect(self.context.absolute_url())
                return

            # Check that none of the IDs conflict with existing items
            ids = [x.id for x in self.context.objectValues('StorageLevel')]
            for x in range(storagelevel_count):
                check = idtemplate.format(id=seq_start + x)
                if check in ids:
                    self.form_error(
                        u'The ID %s exists, cannot be created.' % check)
                    self.request.response.redirect(self.context.absolute_url())
                    return

            # Create the new storage level items
            created_levels = []
            for x in range(seq_start, storagelevel_count):
                id = idtemplate.format(id=x+1)
                title = titletemplate.format(id=x+1)
                ob = api.content.create(
                    container=self.context, type="StorageLevel",
                    id=id, title=title)
                self.context.manage_renameObject(ob.id, id)
                created_levels.append(ob)

            # If required, create the StorageLocations inside the new levels.
            created_locations = []
            if storagelocation_count:
                for level in created_levels:
                    for x in range(storagelocation_count):
                        id = "pos-%s"%x
                        title = "Position %s"%x
                        ob = api.content.create(
                            container=level, type="StorageLocation",
                            id=id, title=title)
                        created_locations.append(ob)
                        import pdb;pdb.set_trace()
                        # Assign any selected storage type interfaces

            msg = u'%s Storage levels and %s storage locations created.' % (
                len(created_levels), len(created_locations))
            self.context.plone_utils.addPortalMessage(msg)
            self.request.response.redirect(self.context.absolute_url())


    def form_error(self, msg):
        self.context.plone_utils.addPortalMessage(msg)
        self.request.response.redirect(self.context.absolute_url())
        return msg
