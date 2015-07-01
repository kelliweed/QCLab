from zope.publisher.browser import BrowserView

class ContentListingView(BrowserView):
    """docstring for ContentListingView"""
    def __call__(self, **kw):
    	import pdb
    	pdb.set_trace()
        return self.index(**kw)
		