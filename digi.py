import os
import jinja2
import webapp2
import random
from google.appengine.api import mail
from google.appengine.api import users
from auth import getMovieDBKey
from google.appengine.ext import ndb

template_dir = os.path.join(os.path.dirname(__file__),'html')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
        extensions=['jinja2.ext.loopcontrols'],
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




class User(ndb.Model):
    userid = ndb.StringProperty()
    username = ndb.StringProperty()
    email = ndb.StringProperty()
    reputation = ndb.IntegerProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

class Code(ndb.Model):
    sellerid = ndb.StringProperty()
    title = ndb.StringProperty()
    price = ndb.FloatProperty()
    codeformat = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

class Review(ndb.Model):
    buyerid = ndb.StringProperty()
    sellerid = ndb.StringProperty()
    comment = ndb.StringProperty()
    rating = ndb.IntegerProperty()





class MainPage(Handler):
    def get(self):
        user = users.get_current_user()
        log_url = ""

        if user:
            log_url = users.create_logout_url('/')

        else:
            log_url = users.create_login_url('/')

        ultraviolet = ["The Godfather", "Lord of the Rings", "Casino Royale", "La La Land", "Sicario", "The Thing"]
        itunes = ["Whiplash", "The Dark Knight", "Inception", "Gone Girl", "Se7en", "Moonlight"]
        googleplay = ["Shark Tale", "Shrek", "Madagascar", "Antz", "Kung Fu Panda", "Shrek 2"]
        disney = ["Up", "Toy Story", "Beauty and the Beast", "Ratatouille", "Toy Story 3", "Bambi"]
        self.render("digi.html", ultraviolet=ultraviolet, itunes=itunes, googleplay=googleplay, disney=disney, user=user, log_url=log_url)


class MyProfilePage(Handler):
    def get(self):
        user = users.get_current_user()
        log_url = ""

        if user:
            log_url = users.create_logout_url('/')

            colors = ["green", "red", "blue", "yellow", "purple"]
            selling = ["Whiplash", "The Dark Knight", "Inception", "Gone Girl", "Se7en", "Moonlight"]
            self.render("myprofile.html", color=random.choice(colors), selling=selling, user=user, log_url=log_url)


class PostCodePage(Handler):
    def get(self):
        user = users.get_current_user()
        log_url = ""

        if user:
            log_url = users.create_logout_url('/')

        else:
            log_url = users.create_login_url('/')

        self.render("postcode.html", user=user, log_url=log_url)



application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/myprofile', MyProfilePage),
    ('/entercode', PostCodePage)
], debug=True)