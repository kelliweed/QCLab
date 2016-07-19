from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.layout.viewlets import ViewletBase
from zExceptions import BadRequest


class AddStorageLevelsViewlet(ViewletBase):
    index = ViewPageTemplateFile("templates/addstoragelevels_viewlet.pt")

    def render(self):
        return self.index()


class AddStorageLevelsSubmitHandler(BrowserView):
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

            # verify ID sequence start/end
            try:
                seq_start = int(self.request.form.get('seq_start', 0))
                seq_end = int(self.request.form.get('seq_end', 0))
            except ValueError:
                self.form_error(u'sequence start and end must both be integers')
                self.request.response.redirect(self.context.absolute_url())
                return

            # verify start < end
            if seq_end <= seq_start:
                self.form_error(u'seqence end must be > sequence start')
                self.request.response.redirect(self.context.absolute_url())
                return

            # verify storage_type interface selection
            storage_types = self.request.form.get('storage_type', [])

            # Check that none of the IDs conflict with existing items
            ids = [x.id for x in self.context.objectValues('StorageLevel')]
            for x in range(seq_start, seq_end + 1):
                check = idtemplate.format(id=x)
                if check in ids:
                    self.form_error(
                        u'The ID %s exists, cannot be created.' % check)
                    self.request.response.redirect(self.context.absolute_url())
                    return

            # Create the new storage level items
            created_ids = []
            for x in range(seq_start, seq_end + 1):
                id = idtemplate.format(id=x)
                title = titletemplate.format(id=x)
                ob = api.content.create(
                    container=self.context, type="StorageLevel",
                    id=id,
                    title=title)
                self.context.manage_renameObject(ob.id, id)
                created_ids.append(id)

            # Assign any selected storage type interfaces
            msg = u'%s Storage levels created.' % len(created_ids)
            self.context.plone_utils.addPortalMessage(msg)
            self.request.response.redirect(self.context.absolute_url())

    def form_error(self, msg):
        self.context.plone_utils.addPortalMessage(msg)
        self.request.response.redirect(self.context.absolute_url())
        return msg
