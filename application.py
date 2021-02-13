import os

from flask import Flask, session, render_template, request, flash, redirect, abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

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
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        exist = db.execute("SELECT * FROM users WHERE username=:username", {"username":username})
        userdata = exist.fetchone()
        # if there is no username in the database matching the entered username, show error page
        if userdata is None:
            return render_template("error_login.html", err = "No account associated with this username. Please try again.")
        # check the password
        if check_password_hash(userdata[2],password) is False:
            return render_template("error_login.html", err = "Incorrect password. Please try again.")
        # if password is correct, log the user in and remember session. If the password is incorrect, show error page
        session['username'] = username
        return render_template("site.html",username=username)


# reroute back to login, for use in error pages
@app.route('/gotologin', methods=['POST', 'GET'])
def gotologin():
        return render_template("login.html")

# log out of account
@app.route('/logout', methods=['POST', 'GET'])
def logout():
        # remove the username from the session
        session.pop('username', None)
        return render_template("error_login.html", err = "You have been logged out.")
