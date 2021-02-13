import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    # open the books csv file
    with open("books.csv",'r') as f:
        next(f) #skip header line
        # use csv reader
        read = csv.reader(f)
        # for the rows in the csv file, add them to the rows in the database
        for isbn, title, author, year in read:
            db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",{"isbn": isbn, "title": title, "author": author, "year": year})
        # commit to the database
        db.commit()

if __name__ == "__main__":
    main()
