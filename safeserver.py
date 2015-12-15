from webapp2 import *   # "Extend" the module by importing everything
import webapp2          # Lets us refer to originals with webapp2 qualifier
from safestring import SafeString

# Wraps around webapp2's RequestHandler, only changing how query parameters
#   are returned.
class RequestHandler(webapp2.RequestHandler):
    def __init__(self, *args, **kwargs):
        webapp2.RequestHandler.__init__(self, *args, **kwargs)
        orig_get = self.request.get
        def get(self, *args, **kwargs):
            # Gets input the same way as expected, but wraps the return in
            #   a SafeString marked as unsafe
            rval = orig_get(self, *args, **kwargs)
            if isinstance(rval, (list, tuple)):
                return [SafeString(val, safe=False) for val in rval]
            return SafeString(rval, safe=False)
        self.request.get = get
