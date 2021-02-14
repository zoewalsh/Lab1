CREATE TABLE users (
  username VARCHAR PRIMARY KEY,
  password VARCHAR NOT NULL,
  email VARCHAR NOT NULL UNIQUE
);

CREATE TABLE books (
  isbn VARCHAR PRIMARY KEY,
  title TEXT,
  author TEXT,
  year INTEGER
);

CREATE TABLE reviews (
  isbn VARCHAR NOT NULL,
  rating INTEGER NOT NULL,
  comment TEXT,
  username VARCHAR NOT NULL
);
