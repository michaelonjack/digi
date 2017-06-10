import os
import jinja2
import webapp2
import random
from google.appengine.api import mail
from auth import getMovieDBKey

template_dir = os.path.join(os.path.dirname(__file__),'html')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
        autoescape = True) #Jinja will now autoescape all html



# THREE FUNCTIONS FOR RENDERING BASIC TEMPLATES
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a,**kw)
    
    def render_str(self,template, **kw):
        t = jinja_env.get_template(template)
        return t.render(kw)

    def render(self,template,**kw):
        self.write(self.render_str(template,**kw))




class MainPage(Handler):
    def get(self):
        movies = ["Up", "Toy Story", "Beauty and the Beast", "Ratatouille", "Toy Story 3", "The Thing"]
        self.render("digi.html", movies=movies)



class ProfilePage(Handler):
    def get(self):
        colors = ["green", "red", "blue"]
        selling = ["Moana", "Frozen", "Finding Nemo", "Finding Dory", "Monsters University", "Lego Batman", "Whiplash", "La la land"]
        self.render("profile.html", color=random.choice(colors), selling=selling)


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/profile', ProfilePage)
], debug=True)