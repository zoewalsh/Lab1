CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR NOT NULL UNIQUE,
  password VARCHAR NOT NULL,
  email VARCHAR NOT NULL UNIQUE
);

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username UNIQUE NOT NULL,
  password VARCHAR NOT NULL
);

INSERT INTO users (id,username,password)VALUES('','','')
