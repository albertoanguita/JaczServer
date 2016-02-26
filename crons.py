import webapp2
from server import ServerApi

class RemoveOldClients(webapp2.RequestHandler):
    def get(self):
        """Set Announcement in Memcache."""
        ServerApi._remove_old_clients()
        self.response.set_status(204)



app = webapp2.WSGIApplication([
    ('/crons/remove_old_clients', RemoveOldClients),
], debug=True)
