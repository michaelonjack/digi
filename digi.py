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





colors = ["green", "red", "blue", "yellow", "purple"]
ULTRAVIOLET = 1
ITUNES = 2
GOOGLEPLAY = 3
DMA = 4






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
    movieid = ndb.StringProperty()
    price = ndb.FloatProperty()
    codeformat = ndb.IntegerProperty()
    title = ndb.StringProperty()
    posterurl = ndb.StringProperty()
    backdropurl = ndb.StringProperty()
    purchased = ndb.DateTimeProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

class Review(ndb.Model):
    buyerid = ndb.StringProperty()
    sellerid = ndb.StringProperty()
    comment = ndb.StringProperty()
    rating = ndb.IntegerProperty()


def getUser(user):
    matchedUser = User.query(User.userid == user.user_id()).fetch(1)

    # No user found, add the user to the database
    if len(matchedUser) == 0:
        newUser = User(userid=user.user_id(), username=user.nickname(), email=user.email(), reputation=0)
        newUser.put()
        return newUser

    return matchedUser[0]

def getCode(id):
    return Code.get_by_id(id)


def addCode(seller_id, movie_id, price, code_format, title, poster_url, backdrop_url):
    newCode = Code(sellerid=seller_id, movieid=movie_id, price=price, codeformat=code_format, title=title, posterurl=poster_url, backdropurl=backdrop_url, purchased=None)
    key = newCode.put()

def getCodesForFormat(_format):
    query = Code.query(Code.codeformat == _format).order(-Code.created)

    result = query.fetch(20)
    return result

def getCodesForSeller(sellerid):
    query = Code.query(Code.sellerid == sellerid).order(-Code.created)
    return query.fetch()







class MainPage(Handler):
    def get(self):
        user = users.get_current_user()
        log_url = ""

        if user:
            log_url = users.create_logout_url('/')

        else:
            log_url = users.create_login_url('/')

        ultraviolet = getCodesForFormat(ULTRAVIOLET)
        itunes = getCodesForFormat(ITUNES)
        googleplay = getCodesForFormat(GOOGLEPLAY)
        disney = getCodesForFormat(DMA)
        self.render("digi.html", ultraviolet=ultraviolet, itunes=itunes, googleplay=googleplay, disney=disney, user=user, log_url=log_url)


class MyProfilePage(Handler):
    def get(self):
        user = getUser(users.get_current_user())

        if user:
            log_url = users.create_logout_url('/')

            selling = getCodesForSeller(user.userid)
            self.render("myprofile.html", color=random.choice(colors), selling=selling, user=user, log_url=log_url)


class PostCodePage(Handler):
    def get(self):
        user = users.get_current_user()
        log_url = log_url = users.create_logout_url('/')

        self.render("postcode.html", user=user, log_url=log_url)

    def post(self):
        user = users.get_current_user()
        log_url = users.create_logout_url('/')

        seller_id = user.user_id()

        title = self.request.get("title")
        price = float(self.request.get("price"))
        code_format = int(self.request.get("format"))
        movie_id = self.request.get("movie-id")
        poster_url = self.request.get("poster-url");
        backdrop_url = self.request.get("backdrop-url");

        addCode(seller_id, movie_id, price, code_format, title, poster_url, backdrop_url)

        # return to account page
        selling = getCodesForSeller(user.user_id())
        self.redirect("/myprofile")


class CodePage(Handler):
    def get(self):
        codeid = int(self.request.get("id"))
        code = getCode(codeid)
        user = users.get_current_user()
        log_url = ""

        if user:
            log_url = users.create_logout_url('/')

        else:
            log_url = users.create_login_url('/')

        self.render("code.html", code=code, user=user, log_url=log_url)

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/myprofile', MyProfilePage),
    ('/entercode', PostCodePage),
    (r'/code.*', CodePage)
], debug=True)