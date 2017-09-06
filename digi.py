import os
import jinja2
import webapp2
import random
import logging
from google.appengine.api import mail
from google.appengine.api import users
from auth import getMovieDBKey
from google.appengine.ext import ndb
from urllib import urlencode
from urllib2 import urlopen, Request

template_dir = os.path.join(os.path.dirname(__file__),'html')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
        extensions=['jinja2.ext.loopcontrols'],
        autoescape = True) #Jinja will now autoescape all html





colors = ["green", "red", "blue", "yellow", "purple"]
all_formats = ["", "Ultraviolet", "iTunes", "Google Play", "DMA"]
ULTRAVIOLET = 1
ITUNES = 2
GOOGLEPLAY = 3
DMA = 4

all_quality = ["", "SD", "HD", "UHD"]
SD = 1
HD = 2
UHD = 3

all_types = ["", "Movie", "Television", "Collection"]
MOVIE = 1
TELEVISION = 2
COLLECTION = 3


VALIDATOR = 0


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
    quality = ndb.IntegerProperty()
    codetype = ndb.IntegerProperty()
    title = ndb.StringProperty()
    code = ndb.StringProperty()
    posterurl = ndb.StringProperty()
    backdropurl = ndb.StringProperty()
    season = ndb.IntegerProperty()
    purchased = ndb.DateTimeProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

class Review(ndb.Model):
    buyerid = ndb.StringProperty()
    sellerid = ndb.StringProperty()
    createdby = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    comment = ndb.StringProperty()
    rating = ndb.IntegerProperty()

class Transaction(ndb.Expando):
    # Attributes defined here are referenced in other parts of the application.
    # Using the ndb.Expando type allows us to add additional Attributes later on.
    dateSent = ndb.DateTimeProperty(auto_now_add=True)
    transaction_id = ndb.StringProperty()
    payment_status = ndb.StringProperty()
    custom = ndb.StringProperty()
    verified = ndb.BooleanProperty()

    @classmethod
    def transaction_exists(cls, id, status):
        match = Transaction.query(ndb.AND(Transaction.transaction_id == id, Transaction.payment_status == status, Transaction.verified == True)).fetch()
        if match:
            return True
        else:
            return False


def getUser(userid):
    matchedUser = User.query(User.userid == userid).fetch(1)

    # No user found
    if len(matchedUser) == 0:
        return None

    return matchedUser[0]

def getUserByUsername(username):
    query = User.query(User.username == username)
    result = query.fetch()

    if(len(result) > 0):
        return result[0]
    else:
        return None

def getReviewsForUser(userid):
    query = Review.query((Review.sellerid == userid or Review.buyerid == userid) and Review.createdby != userid).order(+Review.createdby).order(-Review.created)
    results = query.fetch()
    return results

def getUserByEmail(email):
    query = User.query(User.email == email)
    result = query.fetch()

    if(len(result) > 0):
        return result[0]
    else:
        return None

def addUser(user):
    newUser = User(userid=user.user_id(), username=user.nickname(), email=user.email(), reputation=0)
    newUser.put()
    return newUser

def getCode(id):
    return Code.get_by_id(id)

def getCodesByName(name):
    query = Code.query(Code.title == name).order(+Code.price)
    results = query.fetch()
    return results 

def addReview(sellerid, buyerid, createdby, comment, rating):
    newReview = Review(sellerid=sellerid, buyerid=buyerid, createdby=createdby, comment=comment, rating=rating)
    newReview.put()
    return newReview


def addCode(seller_id, movie_id, price, code_format, code_type, quality, title, poster_url, backdrop_url, season, code):
    newCode = Code(sellerid=seller_id, 
                    movieid=movie_id, 
                    price=price, 
                    codeformat=code_format,
                    codetype=code_type, 
                    quality=quality, 
                    title=title, 
                    posterurl=poster_url, 
                    backdropurl=backdrop_url,
                    season=season,
                    code=code, 
                    purchased=None)

    key = newCode.put()

def getRecentCodesForFormat(_format):
    query = Code.query(Code.codeformat == _format).order(-Code.created)

    result = query.fetch(10)
    return result

def getAllCodesForFormat(_format):
    query = Code.query(Code.codeformat == _format).order(+Code.price)

    result = query.fetch()
    return result

def getAllCodes():
    return Code.query().order(+Code.price).fetch()

def getCodesForSeller(sellerid):
    query = Code.query(Code.sellerid == sellerid).order(-Code.created)
    return query.fetch()






def verify_ipn(data):
    # prepares provided data set to inform PayPal we wish to validate the response
    data["cmd"] = "_notify-validate"
    params = urlencode(data)
 
    # sends the data and request to the PayPal Sandbox
    req = Request("""https://www.paypal.com/cgi-bin/webscr""", params)
    req.add_header("Content-type", "application/x-www-form-urlencoded")
    # reads the response back from PayPal
    response = urlopen(req)
    status = response.read()
 
    # If not verified
    if not status == "VERIFIED":
        return False
 
    # if not the correct currency
    if not data["mc_currency"] == "USD":
        return False
 
    # otherwise...
    return True







class MainPage(Handler):
    def get(self):
        user = users.get_current_user()
        log_url = ""

        if user:
            log_url = users.create_logout_url('/')

        else:
            log_url = users.create_login_url('/')

        ultraviolet = getRecentCodesForFormat(ULTRAVIOLET)
        itunes = getRecentCodesForFormat(ITUNES)
        googleplay = getRecentCodesForFormat(GOOGLEPLAY)
        disney = getRecentCodesForFormat(DMA)
        self.render("digi.html", 
                    ultraviolet=ultraviolet, 
                    itunes=itunes, 
                    googleplay=googleplay, 
                    disney=disney, 
                    user=user, 
                    log_url=log_url)

    def post(self):
        query = self.request.get("query")
        self.redirect("/search?q=" + query + "&page=1")



class SearchResultsPage(Handler):
    def get(self):
        query = self.request.get("q")
        all_codes = getAllCodes()
        codes = []
        for code in all_codes:
            if query.lower() in code.title.lower():
                codes.append(code) 
        #codes = getCodesByName(query)

        page = int(self.request.get("page"))
        user = users.get_current_user()
        numpages = len(codes)/16 + (1 if len(codes)%16 > 0 else 0)
        codes = codes[(16*page-16):(16*page)]
        log_url = ""

        if user:
            log_url = users.create_logout_url('/')

        else:
            log_url = users.create_login_url('/')

        self.render("searchresults.html", 
                    codes=codes,
                    formats=all_formats,
                    query=query,
                    currpage=page,
                    numpages=numpages,
                    user=user, 
                    log_url=log_url)

    def post(self):
        query = self.request.get("query")
        self.redirect("/search?q=" + query + "&page=1")


class MyProfilePage(Handler):
    def get(self):
        user = getUser(users.get_current_user().user_id())
        if user is None:
            user = addUser(users.get_current_user())
        
        log_url = users.create_logout_url('/')

        selling = getCodesForSeller(user.userid)
        self.render("myprofile.html", 
                    color=random.choice(colors), 
                    selling=selling,
                    formats=all_formats, 
                    user=user, 
                    log_url=log_url)

    def post(self):
        query = self.request.get("query")
        self.redirect("/search?q=" + query + "&page=1")


class OtherProfilePage(Handler):
    def get(self):
        otheruserid = self.request.get("id")
        otheruser = getUser(otheruserid)
        currentuser = users.get_current_user()
        
        if currentuser:
            currentuser = getUser(currentuser.user_id())
            log_url = users.create_logout_url('/')

        else:
            log_url = users.create_login_url('/')

        selling = getCodesForSeller(otheruser.userid)
        self.render("otherprofile.html",
                    color=random.choice(colors), 
                    selling=selling,
                    formats=all_formats, 
                    currentuser=currentuser, 
                    otheruser=otheruser, 
                    log_url=log_url)

    def post(self):
        query = self.request.get("query")
        self.redirect("/search?q=" + query + "&page=1")


class PostCodePage(Handler):
    def get(self):
        user = users.get_current_user()
        log_url = log_url = users.create_logout_url('/')

        self.render("postcode.html", 
                    user=user, 
                    log_url=log_url)

    def post(self):
        user = users.get_current_user()
        log_url = users.create_logout_url('/')

        seller_id = user.user_id()

        title = self.request.get("title")
        price = float(self.request.get("price"))
        code = self.request.get("code")
        code_format = int(self.request.get("format"))
        code_type = int(self.request.get("type"))
        quality = int(self.request.get("quality"))
        movie_id = self.request.get("movie-id")
        poster_url = self.request.get("poster-url")
        backdrop_url = self.request.get("backdrop-url")
        season = int(self.request.get("season"))

        addCode(seller_id, movie_id, 
                price, code_format, 
                code_type, quality, 
                title, poster_url, 
                backdrop_url, season, code)

        # return to account page
        selling = getCodesForSeller(user.user_id())
        self.redirect("/myprofile")


class CodePage(Handler):
    def get(self):
        codeid = int(self.request.get("id"))
        code = getCode(codeid)
        user = users.get_current_user()
        seller = getUser(code.sellerid)
        log_url = ""

        if user:
            log_url = users.create_logout_url('/')

        else:
            log_url = users.create_login_url('/')

        self.render("code.html", 
                    code=code,
                    quality=all_quality, 
                    seller=seller,
                    all_formats=all_formats, 
                    user=user, 
                    log_url=log_url)

    def post(self):
        buyer = getUser( users.get_current_user().user_id() )
        codeid = int(self.request.get("codeid"))
        code = getCode(codeid)
        seller = getUser(code.sellerid)

        # The user who submit the form is the seller of the code
        # This means we're performing a DELETE operation; not a BUY operation
        if code.sellerid == buyer.userid:
            code.key.delete()
            self.redirect("/myprofile")

        # Users should never get to this state but if they do redirect to home
        else:
            self.redirect("/")


class CodePurchasedPage(Handler):
    def post(self):
        post_data = self.request.POST.copy()
        buyer = getUser( self.request.get("buyerid") )
        codeid = int(self.request.get("codeid"))
        code = getCode(codeid)
        
        seller = None
        if code:
            seller = getUser(code.sellerid)

        # Create a new Transaction instance for this deal
        payment = Transaction(receiver_email = post_data['receiver_email'],
                            transaction_id = post_data['txn_id'],
                            transaction_type = post_data['txn_type'],
                            payment_type = post_data['payment_type'],
                            payment_status = post_data['payment_status'],
                            amount = post_data['mc_gross'],
                            currency = post_data['mc_currency'],
                            payer_email = post_data['payer_email'],
                            first_name = post_data['first_name'],
                            last_name = post_data['last_name'],
                            verified = False)


        # Check if the transaction has already been recorded in the DB
        if Transaction.transaction_exists(payment.transaction_id, payment.payment_status):
            # This transaction has already been verified and processed.
            logging.debug('Transaction already exists')


        # Check if the transaction is verified by PayPal
        elif verify_ipn(post_data):

            # Once the IPN has been verified by PayPal, verify the transaction
            payment.verified = True
            # Enter transaction into the DB
            payment.put()

            # The seller has the code saved in the DB so it is eligible for automatic delivery
            if code is not None and code.code is not None and code.code != "":

                # Send message to the seller
                subject = "Kodala: " + buyer.username + " has purchased your " + code.title + " (" + str(all_formats[code.codeformat]) + ") digital code" 
                message = ("Hi, " + seller.username + "\n\n" + buyer.username + " has purchased your " + code.title + " (" + str(all_formats[code.codeformat]) + ") digital code.\n\n" +
                            "Payment has been sent to " + seller.email + "\n" +
                            "Since your code was saved to Kodala, it has already been delivered to the buyer and your listing for this code has been removed.\n" + 
                            "You can leave the buyer feedback on their profile at https://kodala.codes/profile?id=" + buyer.userid)
                
                mail.send_mail(sender="kodalacodes@gmail.com",
                            to=seller.email,
                            subject=subject,
                            body=message)


                # Send message to the buyer
                subject = "Kodala: Here's your digital code!" 
                message = ("Hi, " + buyer.username + "\n\n" +  
                            "Here's your code for " + code.title + " (" + str(all_formats[code.codeformat]) + ") : \n\n" + code.code + "\n\n" +
                            "After reeedming your code you can contact or leave the seller feedback on their profile at https://kodala.codes/profile?id=" + code.sellerid)
                mail.send_mail(sender="kodalacodes@gmail.com",
                            to=buyer.email,
                            subject=subject,
                            body=message)

                # Delete the code from the database now that it has been purchased
                code.key.delete()

            # The code is NOT saved in the DB. Manual delivery required
            else:

                # Send message to the seller
                subject = "Kodala: Your digital code has been purchased!" 
                message = ("Hi, " + seller.username + "\n\n" + buyer.username + " has purchased your " + code.title + " (" + str(all_formats[code.codeformat]) + ") digital code.\n\n" +
                            "Payment has been sent to " + seller.email + "\n" +
                            "Since your code was not saved to Kodala, you will need to manually send the code to the buyer at their contact address of " + buyer.email + "\n" + 
                            "You can leave the buyer feedback on their profile at https://kodala.codes/profile?id=" + buyer.userid + "\n\n" +
                            "Don't forget to send your code!")
                mail.send_mail(sender="kodalacodes@gmail.com",
                            to=seller.email,
                            subject=subject,
                            body=message)


                # Send message to the buyer
                subject = "Kodala: Payment sent!" 
                message = ("Hi, " + buyer.username + "\n\n" +  
                            "Your payment to " + seller.username + " has been sent. Expect an email from the seller with your code soon!\n\n" +
                            "You can contact or leave the seller feedback on their profile at https://kodala.codes/profile?id=" + code.sellerid)
                mail.send_mail(sender="kodalacodes@gmail.com",
                            to=buyer.email,
                            subject=subject,
                            body=message)


        else:
            logging.info("paypal not valid")

class AllCodesPage(Handler):
    def get(self):
        _format = int(self.request.get("format"))
        page = int(self.request.get("page"))
        user = users.get_current_user()
        codes = getAllCodesForFormat(_format)
        numpages = len(codes)/16 + (1 if len(codes)%16 > 0 else 0)
        codes = codes[(16*page-16):(16*page)]
        log_url = ""

        if user:
            log_url = users.create_logout_url('/')

        else:
            log_url = users.create_login_url('/')

        self.render("allcodes.html", 
                    codes=codes,
                    format=_format,
                    currpage=page,
                    numpages=numpages,
                    user=user, 
                    log_url=log_url)

    def post(self):
        query = self.request.get("query")
        self.redirect("/search?q=" + query + "&page=1")


class MessagePage(Handler):
    def get(self):
        recipientid = self.request.get("recipient")
        recipient = getUser(recipientid)
        currentuser = getUser(users.get_current_user().user_id())
        log_url = ""

        if currentuser:
            log_url = users.create_logout_url('/')

        else:
            log_url = users.create_login_url('/')

        self.render("sendmessage.html", currentuser=currentuser, recipient=recipient, log_url=log_url)

    def post(self):
        recipientid = self.request.get("recipientid")
        recipient = getUser(recipientid)
        subject = self.request.get("subject")
        message = self.request.get("message")
        currentuser = getUser(users.get_current_user().user_id())

        mail.send_mail(sender=currentuser.email,
                        to=recipient.email,
                        subject=subject,
                        body=message)

        self.redirect('/profile?id=' + recipient.userid)



class SettingsPage(Handler):
    def get(self):
        user = getUser(users.get_current_user().user_id())
        log_url = users.create_logout_url('/')

        self.render("settings.html", user=user, log_url=log_url)

    def post(self):
        user = getUser(users.get_current_user().user_id())
        log_url = users.create_logout_url('/')
        updatedusername = self.request.get("username")
        updatedemail = self.request.get("email")

        userWithEmail = getUserByEmail(updatedemail)
        userWithUsername = getUserByUsername(updatedusername)

        if ((userWithEmail is None or userWithEmail.userid == user.userid) 
            and (userWithUsername is None or userWithUsername.userid == user.userid)):
            user.username = updatedusername
            user.email = updatedemail
            user.put()
            self.redirect("/settings")

        elif getUserByUsername(updatedusername) is not None and userWithUsername.userid != user.userid:
            error = "(User with this username already exists.)"
            self.render("settings.html", user=user, log_url=log_url, usererror=error)

        else:
            error = "(User with this email already exists.)"
            self.render("settings.html", user=user, log_url=log_url, emailerror=error)



class ReviewsPage(Handler):
    def get(self):
        currentuser = users.get_current_user()
        user = getUser( self.request.get("id") )
        reviews = getReviewsForUser(user.userid)
        log_url = ""

        if currentuser:
            currentuser = getUser(currentuser.user_id())
            log_url = users.create_logout_url('/')

        else:
            log_url = users.create_login_url('/')

        self.render("reviews.html", reviewee=user, reviews=reviews, log_url=log_url, reviewer=currentuser)

    def post(self):
        role = self.request.get("role")
        rating = 1 if int(self.request.get("rating")) > 0 else -1
        comment = self.request.get("comment")
        reviewee = getUser( self.request.get("reviewee") )
        reviewer = users.get_current_user().user_id()

        if rating > 0:
            reviewee.reputation = reviewee.reputation + 1
        else:
            reviewee.reputation = reviewee.reputation - 1

        reviewee.put()

        if role == "buyer":
            addReview(reviewee.userid, reviewer, reviewer, comment, rating)
        else:
            addReview(reviewer, reviewee.userid, reviewer, comment, rating)

        self.redirect("/reviews?id=" + reviewee.userid)


class AJAXCodeSearchResults(Handler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'

        query = self.request.get("q")
        codes = getAllCodes()

        results = []
        for code in codes:
            if (
                ((code.title.lower().startswith( query.lower() )) or
                (code.title.lower().startswith("the ") and code.title[4:].lower().startswith( query.lower() )) or
                (code.title.lower().startswith("a ") and code.title[2:].lower().startswith( query.lower() ))) and
                (code.title not in results)
            ):
                results.append( code.title )

        jsonResponse = "{ \"results\": ["
        firstRecord = True
        for result in results:
            if not firstRecord:
                jsonResponse += " , ";
            else:
                firstRecord = False

            jsonResponse += " { \"title\" : "
            jsonResponse += "\"" + result + "\""
            jsonResponse += " } "

        jsonResponse += "]}"

        self.response.out.write(jsonResponse)




application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/myprofile', MyProfilePage),
    (r'/profile.*', OtherProfilePage),
    ('/entercode', PostCodePage),
    (r'/message.*', MessagePage),
    (r'/code.*', CodePage),
    (r'/notify_purchase.*', CodePurchasedPage),
    (r'/allcodes.*', AllCodesPage),
    (r'/settings', SettingsPage),
    (r'/reviews.*', ReviewsPage),
    (r'/search.*', SearchResultsPage),
    (r'/ajaxcodesearch.*', AJAXCodeSearchResults)
], debug=True)