# Project 1
ENGO 551

The purpose of this web application is to provide users a place to look up information about books contained in our database as well as leave reviews for the books. Users are able to make an account, log in and out, browse books by searching, leave reviews on books, and read other users' book reviews.


application.py - The main python application, containing all of the code for site paths, interacting with the database, and handling "post" and "get" methods. This python file is to be run using Flask.

templates:

index.html - The html page for the first page of the site, which users are first directed to when visiting the site. The user has the option to register for an account or click "Already have an account?" if they wish to log in with existing credentials. As long as the username and email are not already taken, their information is committed to the database (note: the passwords are hashed)

login.html - The html page where users can log in with their username and password. They can also choose to go back to the register page (index.html) if they do not have an account. If the user enters a matching username and password, they are logged in (note: the passwords are hashed).

site.html - Once logged in, this is the page of the site where users can search for a book. The top of the page displays the username they are logged in with, in case they are using a shared computer and another user forgot to log out. They also have the option of logging out from this page. The user can search by ISBN, title, or author, and partial searches will still provide results.

results.html - The page that displays search results to the user. If their search returned results, it will display "You have results:" followed by the matching results. If the search returned no results, the user is instead taken to "noresults.html". The top of the page gives users the option to log out or go back to the search page to try another search. The book titles and authors matching the search criteria are displayed as links that the user can click on.

book.html - If the user clicks on a book from results.html, they are taken to this page which will display the information about the book (title, author, year, and isbn). The google books API review count and average review are also shown here (if they exist). If there are no reviews on google books, the fields display "None". The user has the option to submit a review for the book on this page. A rating is required (from a list of 1-5), but a comment is not. Below the submit button, there will be a message if the user has already submitted a review for that book. Once submitted, the page will refresh to show their review and show a message "Review Submitted.". Below is a table of all the reviews for the book that have been submitted to the site. If there are no reviews yet, there will be a message saying "There are no reviews for this book." The top of the book page also gives the user the option to log out or go back to the search page.

error_login.html - The error page if the user's attempt to login failed with a specific message (incorrect username (no account associated with the username), incorrect password). This page is also used to display "You have been logged out." when the user logs out. This page is also used for the 404 error if accessing API data for the ISBN is not successful. The user is given the option to go back to the login page.

error.html - A basic error page which displays a specific error message and gives the user the option to go back to the index page.

noresults.html - The error page if a user performed a search that returned no results. It gives the option of going back to the search page.

layout.html - Contains the layout structure for all the html pages as well as styling.


import.py - The python file used for importing the book csv data to the database.

requirements.txt - Contains list of python packages that need to be installed to run the application.

create.sql - SQL commands used to create database tables.
