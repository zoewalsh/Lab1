import os
import sys

from flask import Flask, session, render_template, request, flash, redirect, abort, json, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
import requests

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# fix windows terminal issue on my computer
if sys.platform.lower() == "win64":
    os.system('color')

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/", methods=['POST', 'GET'])
def index():
    if 'username' in session:
        username = session['username']
        return render_template('site.html', username=username)
    return render_template('index.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    session.clear()
    if request.method == 'POST':
        username = request.form.get("username")
        # hash the password for privacy
        password = generate_password_hash(request.form.get("password"));
        email = request.form.get("email")

        # check if username is already taken, or if the email is already registered
        taken = db.execute("SELECT username FROM users where username=:username", {"username":username}).fetchone()
        registered = db.execute("SELECT email FROM users where email=:email", {"email":email}).fetchone()

        # if username is not taken, check if email is registered already
        if taken is None:
            if registered is None:
                # if the username and password are not in use, add the registration info to the database
                db.execute("INSERT into users (username, password, email) VALUES (:username, :password, :email)",
                {"username": username, "password":password, "email":email})
                db.commit()
                # go to login page
                return render_template("login.html")
            elif registered is not None:
                # if the email is already registered, show error page
                return render_template("error_login.html", err = "This email is already registered to an account.")
        # if username is already taken, show error page
        elif taken is not None:
            return render_template("error.html", err = "This username is taken.")

@app.route('/login', methods=['POST', 'GET'])
def login():
    session.clear()
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        exist = db.execute("SELECT * FROM users WHERE username=:username", {"username":username})
        userdata = exist.fetchone()
        # if there is no username in the database matching the entered username, show error page
        if userdata is None:
            return render_template("error_login.html", err = "No account associated with this username. Please try again.")
        # check the password
        if check_password_hash(userdata['password'],password) is False:
            return render_template("error_login.html", err = "Incorrect password. Please try again.")
        # if password is correct, log the user in and remember session. If the password is incorrect, show error page
        session['username'] = username
        return render_template("site.html",username=username)

@app.route('/search', methods=['POST'])
def search():
    searched = "%" + request.form.get("searched") + "%"
    # book titles and author titles are capitalized
    searched = searched.title()
    # search based on isbn, title, or author (can be partial)
    books = db.execute("SELECT isbn, title, author FROM books WHERE (isbn LIKE :searched OR title LIKE :searched OR author LIKE :searched)", {"searched":searched})
    if books.rowcount == 0:
        return render_template("noresults.html", err="Your search returned no results, please try again.")

    results = books.fetchall()
    return render_template("results.html", results=results)

@app.route("/<isbn>", methods=['POST', 'GET'])
def bookinfo(isbn):
    # Google books API key
    key = "AIzaSyA0RrFKJyniz8S_4aZhIj9tXBRpWH6yPv8"
    # use isbn to request reviews and convert to json object
    revs = requests.get("https://www.googleapis.com/books/v1/volumes", params={"key":key,"q":isbn})
    googlerev = revs.json()
    item = googlerev['items'][0]['volumeInfo']
    # create google object with averageRating and ratingsCount attributes
    google=[]
    averageRating = item.get('averageRating')
    ratingsCount = item.get('ratingsCount')
    google.append(averageRating)
    google.append(ratingsCount)

    if request.method == 'GET':
        # query
        book = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn":isbn}).fetchone()
        reviews = db.execute("SELECT * FROM reviews WHERE isbn=:isbn", {"isbn":isbn})
        results = reviews.fetchall()

        # if there are no reviews for the book
        if reviews.rowcount == 0:
            return render_template("book.html", book=book, reviews=[], google=google, err="")

        # if the user has already left a review, show a message
        exist = db.execute("SELECT * FROM reviews WHERE (isbn=:isbn AND username=:username)", {"isbn":isbn, "username":session['username']})
        if exist.rowcount != 0:
            return render_template("book.html", book=book, reviews=results, google=google, err="Note: You have already left a review for this book.")

        return render_template("book.html", book=book, reviews= results, google=google, err="")

    if request.method == 'POST':

        # if the user has already left a review
        exist = db.execute("SELECT * FROM reviews WHERE (isbn=:isbn AND username=:username)", {"isbn":isbn, "username":session['username']})
        if exist.rowcount != 0:
            return render_template("noresults.html", err="You have already reviewed this book.")

        #add review
        db.execute("INSERT into reviews (isbn, rating, comment, username) VALUES (:isbn, :rating, :comment, :username)",
            {"isbn": isbn, "rating":request.form.get("rating"), "comment":request.form.get("comment"), "username":session['username']})
        db.commit()

        # query again
        book = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn":isbn}).fetchone()
        reviews = db.execute("SELECT * FROM reviews WHERE isbn=:isbn", {"isbn":isbn}).fetchall()

        return render_template("book.html", book=book, reviews=reviews, google=google, err= "Review submitted.")

@app.route("/api/<isbn>", methods=['GET'])
def api(isbn):
    # return a 404 error if the isbn does not exist in our database
    exist = db.execute("SELECT * FROM books WHERE isbn=:isbn",{"isbn":isbn})
    if exist.rowcount==0:
        return render_template("error_login.html", err="404 Error: ISBN not found. Please check spelling or log in to search for a book.")
    # Google books API key
    key = "AIzaSyA0RrFKJyniz8S_4aZhIj9tXBRpWH6yPv8"
    # use isbn to request data from google api and convert to json object
    revs = requests.get("https://www.googleapis.com/books/v1/volumes", params={"key":key,"q":isbn})
    googlerev = revs.json()
    item = googlerev['items'][0]['volumeInfo']
    ISBN_13 = googlerev['items'][0]['volumeInfo']['industryIdentifiers'][1]['identifier']
    # use google books API to get info
    book = {
        "title": item.get('title'),
        "author": googlerev['items'][0]['volumeInfo']['authors'][0],
        "publishedDate": item.get('publishedDate'),
        "ISBN_10": isbn,
        "ISBN_13": ISBN_13,
        "averageRating": item.get('averageRating'),
        "ratingsCount": item.get('ratingsCount')
    }
    return(jsonify(book))


# reroute back to login, for use in error pages
@app.route('/gotologin', methods=['POST', 'GET'])
def gotologin():
        return render_template("login.html")

# log out of account
@app.route('/logout', methods=['POST', 'GET'])
def logout():
        # remove the username from the session
        session.pop('username', None)
        session.clear()
        return render_template("error_login.html", err = "You have been logged out.")

# reroute back to search
@app.route('/gotosearch', methods=['POST', 'GET'])
def gotosearch():
        username = session['username']
        return render_template("site.html", username=username)
