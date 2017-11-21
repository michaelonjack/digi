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

SORT_BY_PRICE = 0
SORT_BY_TITLE = 1
SORT_BY_CREATED = 2



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

    @classmethod
    def add_user(cls, user):
        newUser = User(userid=user.user_id(), username=user.nickname(), email=user.email(), reputation=0)
        newUser.put()
        return newUser

    @classmethod
    def get_user(cls, id):
        matchedUser = User.query(User.userid == id).fetch(1)

        # No user found
        if len(matchedUser) == 0:
            return None

        return matchedUser[0]

    @classmethod
    def get_username(cls, id):
        matchedUser = User.query(User.userid == id).fetch(1)

        # No user found
        if len(matchedUser) == 0:
            return ""

        return matchedUser[0].username

    @classmethod
    def get_user_by_username(cls, username):
        query = User.query(User.username == username)
        result = query.fetch()

        if(len(result) > 0):
            return result[0]
        else:
            return None

    @classmethod
    def get_user_by_email(cls, email):
        query = User.query(User.email == email)
        result = query.fetch()

        if(len(result) > 0):
            return result[0]
        else:
            return None








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

    @classmethod
    def add_code(cls, seller_id, movie_id, price, code_format, code_type, quality, title, poster_url, backdrop_url, season, code):
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

    @classmethod
    def get_code(cls, id):
        return Code.get_by_id(id)

    @classmethod
    def get_all_codes(cls, sortoption):
        if sortoption == SORT_BY_PRICE:
            return Code.query().order(+Code.price).fetch()
        elif sortoption == SORT_BY_TITLE:
            return Code.query().order(+Code.title).fetch()
        else:
            return Code.query().order(-Code.created).fetch()



    @classmethod
    def get_all_codes_for_format(cls, _format, sortoption):
        if sortoption == SORT_BY_PRICE:
            return Code.query(Code.codeformat == _format).order(+Code.price).fetch()
        elif sortoption == SORT_BY_TITLE:
            return Code.query(Code.codeformat == _format).order(+Code.title).fetch()
        else:
            return Code.query(Code.codeformat == _format).order(-Code.created).fetch()

    @classmethod
    def get_codes_for_seller(cls, sellerid):
        query = Code.query(Code.sellerid == sellerid).order(-Code.created)
        return query.fetch()

    @classmethod
    def get_codes_by_name(cls, name):
        query = Code.query(Code.title == name).order(+Code.price)
        results = query.fetch()
        return results

    @classmethod
    def get_recent_codes_for_format(cls, _format):
        query = Code.query(Code.codeformat == _format).order(-Code.created)
        result = query.fetch(10)
        return result








class Review(ndb.Model):
    buyerid = ndb.StringProperty()
    sellerid = ndb.StringProperty()
    createdby = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    comment = ndb.StringProperty()
    rating = ndb.IntegerProperty()

    @classmethod
    def add_review(cls, sellerid, buyerid, createdby, comment, rating):
        newReview = Review(sellerid=sellerid, buyerid=buyerid, createdby=createdby, comment=comment, rating=rating)
        newReview.put()
        return newReview

    @classmethod
    def get_reviews_for_user(cls, userid):
        query = Review.query( ndb.AND(ndb.OR(Review.sellerid == userid, Review.buyerid == userid), Review.createdby != userid)).order(+Review.createdby).order(-Review.created)
        results = query.fetch()
        return results









class Transaction(ndb.Expando):
    # Attributes defined here are referenced in other parts of the application.
    # Using the ndb.Expando type allows us to add additional Attributes later on.
    dateSent = ndb.DateTimeProperty(auto_now_add=True)
    transaction_id = ndb.StringProperty()
    payment_status = ndb.StringProperty()
    custom = ndb.StringProperty()
    verified = ndb.BooleanProperty()

    @classmethod
    def transaction_exists(cls, id):
        match = Transaction.query(ndb.AND(Transaction.transaction_id == id, Transaction.verified == True)).fetch()
        if match:
            return True
        else:
            return False

    @classmethod
    def get_transaction(cls, id):
        match = Transaction.query(ndb.AND(Transaction.transaction_id == id, Transaction.verified == True)).fetch()
        if len(match) > 0:
            return match[0]
        else:
            return None
 



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

        ultraviolet = Code.get_recent_codes_for_format(ULTRAVIOLET)
        itunes = Code.get_recent_codes_for_format(ITUNES)
        googleplay = Code.get_recent_codes_for_format(GOOGLEPLAY)
        disney = Code.get_recent_codes_for_format(DMA)
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
        all_codes = Code.get_all_codes(SORT_BY_PRICE)
        codes = []
        for code in all_codes:
            if query.lower() in code.title.lower():
                codes.append(code) 

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
        user = User.get_user(users.get_current_user().user_id())
        if user is None:
            user = User.add_user(users.get_current_user())
        
        log_url = users.create_logout_url('/')

        selling = Code.get_codes_for_seller(user.userid)
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
        otheruser = User.get_user(otheruserid)
        currentuser = users.get_current_user()

        if otheruser is None:
            self.render("error.html")
            return
        
        if currentuser:
            currentuser = User.get_user(currentuser.user_id())
            log_url = users.create_logout_url('/')

        else:
            log_url = users.create_login_url('/')

        selling = Code.get_codes_for_seller(otheruser.userid)
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

        Code.add_code(seller_id, movie_id, 
                price, code_format, 
                code_type, quality, 
                title, poster_url, 
                backdrop_url, season, code)

        # return to account page
        selling = Code.get_codes_for_seller(user.user_id())
        self.redirect("/myprofile")


class CodePage(Handler):
    def get(self):
        codeid = int(self.request.get("id"))
        code = Code.get_code(codeid)

        if code is None:
            self.render("error.html")
            return

        user = users.get_current_user()
        seller = User.get_user(code.sellerid)
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
        buyer = User.get_user( users.get_current_user().user_id() )
        codeid = int(self.request.get("codeid"))
        code = Code.get_code(codeid)
        seller = User.get_user(code.sellerid)

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
        buyer = User.get_user( self.request.get("buyerid") )
        codeid = int(self.request.get("codeid"))
        code = Code.get_code(codeid)
        
        seller = None
        if code:
            seller = User.get_user(code.sellerid)

        # Create a new Transaction instance for this deal
        logging.debug(post_data)
        payment = None
        if 'payment_type' in post_data and 'txn_type' in post_data:
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
                                code_id = codeid,
                                verified = False)

        else:
            logging.debug('POST request does not have a payment_type. Could be a filed claim from past purchase.')


        # Check if the transaction has already been recorded in the DB
        if Transaction.transaction_exists(post_data['txn_id']) or ('parent_txn_id' in post_data and Transaction.transaction_exists(post_data['parent_txn_id'])):
            # This transaction has already been verified and processed.
            logging.debug('Transaction already exists')

            # Check if we're dealing with a filed claim from a past purchase
            existingTrans = Transaction.get_transaction(post_data['txn_id'])
            if not existingTrans:
                existingTrans = Transaction.get_transaction(post_data['parent_txn_id'])
            if existingTrans and 'case_type' in post_data:
                existingTrans.case_type = post_data['case_type']
                existingTrans.case_creation_date = post_data['case_creation_date']
                existingTrans.case_info = post_data['buyer_additional_information']
                existingTrans.put()
            # Check if we're dealing with a refunded past purchase
            elif existingTrans and 'payment_status' in post_data:
                existingTrans.payment_status = post_data['payment_status']
                existingTrans.put()


        # Check if the transaction is verified by PayPal
        elif buyer is not None and verify_ipn(post_data):

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


            # Delete the code from the database now that it has been purchased
            code.key.delete()


        else:
            logging.info("paypal not valid or buyer was null")

class AllCodesPage(Handler):
    def get(self):
        _format = int(self.request.get("format"))
        page = int(self.request.get("page"))
        sort = self.request.get("sort")
        if sort.isdigit():
            sort = int(sort)%3
        else:
            sort = SORT_BY_PRICE

        user = users.get_current_user()
        codes = Code.get_all_codes_for_format(_format, sort)
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
                    sort=sort,
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
        recipient = User.get_user(recipientid)
        currentuser = User.get_user(users.get_current_user().user_id())
        log_url = ""

        if currentuser:
            log_url = users.create_logout_url('/')

        else:
            log_url = users.create_login_url('/')

        self.render("sendmessage.html", currentuser=currentuser, recipient=recipient, log_url=log_url)

    def post(self):
        recipientid = self.request.get("recipientid")
        recipient = User.get_user(recipientid)
        subject = self.request.get("subject")
        message = self.request.get("message")
        currentuser = User.get_user(users.get_current_user().user_id())

        mail.send_mail(sender=currentuser.email,
                        to=recipient.email,
                        subject=subject,
                        body=message)

        self.redirect('/profile?id=' + recipient.userid)



class SettingsPage(Handler):
    def get(self):
        user = User.get_user(users.get_current_user().user_id())
        log_url = users.create_logout_url('/')

        self.render("settings.html", user=user, log_url=log_url)

    def post(self):
        user = User.get_user(users.get_current_user().user_id())
        log_url = users.create_logout_url('/')
        updatedusername = self.request.get("username")
        updatedemail = self.request.get("email")

        userWithEmail = User.get_user_by_email(updatedemail)
        userWithUsername = User.get_user_by_username(updatedusername)

        if ((userWithEmail is None or userWithEmail.userid == user.userid) 
            and (userWithUsername is None or userWithUsername.userid == user.userid)):
            user.username = updatedusername
            user.email = updatedemail
            user.put()
            self.redirect("/settings")

        elif User.get_user_by_username(updatedusername) is not None and userWithUsername.userid != user.userid:
            error = "(User with this username already exists.)"
            self.render("settings.html", user=user, log_url=log_url, usererror=error)

        else:
            error = "(User with this email already exists.)"
            self.render("settings.html", user=user, log_url=log_url, emailerror=error)



class ReviewsPage(Handler):
    def get(self):
        currentuser = users.get_current_user()
        user = User.get_user( self.request.get("id") )
        
        reviews = Review.get_reviews_for_user(user.userid)
        log_url = ""

        if currentuser:
            currentuser = User.get_user(currentuser.user_id())
            log_url = users.create_logout_url('/')

        else:
            log_url = users.create_login_url('/')

        self.render("reviews.html", reviewee=user, reviews=reviews, log_url=log_url, reviewer=currentuser, User = User)

    def post(self):
        role = self.request.get("role")
        rating = 1 if int(self.request.get("rating")) > 0 else -1
        comment = self.request.get("comment")
        reviewee = User.get_user( self.request.get("reviewee") )
        reviewer = users.get_current_user().user_id()

        if rating > 0:
            reviewee.reputation = reviewee.reputation + 1
        else:
            reviewee.reputation = reviewee.reputation - 1

        reviewee.put()

        if role == "buyer":
            Review.add_review(reviewee.userid, reviewer, reviewer, comment, rating)
        else:
            Review.add_review(reviewer, reviewee.userid, reviewer, comment, rating)

        self.redirect("/reviews?id=" + reviewee.userid)


class AJAXCodeSearchResults(Handler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'

        query = self.request.get("q")
        codes = Code.get_all_codes(SORT_BY_PRICE)

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



class AJAXNextPageResults(Handler):
    def get(self):

        self.response.headers['Content-Type'] = 'application/json'

        page = int(self.request.get("page"))
        codeFormat = int(self.request.get("format"))
        sort = self.request.get("sort")
        if sort.isdigit():
            sort = int(sort)%3
        else:
            sort = SORT_BY_PRICE

        codes = Code.get_all_codes_for_format(codeFormat, sort)
        numpages = len(codes)/16 + (1 if len(codes)%16 > 0 else 0)
        codes = codes[(16*page-16):(16*page)]

        jsonResponse = "{ \"results\": ["
        firstRecord = True
        for code in codes:
            if not firstRecord:
                jsonResponse += " , ";
            else:
                firstRecord = False

            jsonResponse += " { \"title\" : "
            jsonResponse += "\"" + code.title + "\", "
            jsonResponse += "\"price\" : \"" + str(code.price) + "\", "
            jsonResponse += "\"id\" : \"" + str(code.key.id()) + "\", "
            jsonResponse += "\"posterurl\" : \"" + code.posterurl + "\" "
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
    (r'/ajaxcodesearch.*', AJAXCodeSearchResults),
    (r'/ajaxgetnextpage.*', AJAXNextPageResults)
], debug=True)