DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS artpiece;
DROP TABLE IF EXISTS wallet;
DROP TABLE IF EXISTS contract;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE wallet (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  owner_id INTEGER NOT NULL,
  balance DECIMAL(11, 2) NOT NULL,
  FOREIGN KEY (owner_id) REFERENCES user (id)
);

CREATE TABLE contract(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  artpiece_about INTEGER NOT NULL,
  enddate TIMESTAMP NOT NULL,
  price DECIMAL(10, 2) NOT NULL,
  lender_id INTEGER NOT NULL,
  borrower_id INTEGER,
  FOREIGN KEY (artpiece_about) REFERENCES artpiece (id),
  FOREIGN KEY (lender_id) REFERENCES user (id),
  FOREIGN KEY (borrower_id) REFERENCES user (id)
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  artpiece_id INTEGER,
  contract_id INTEGER,
  FOREIGN KEY (author_id) REFERENCES user (id),
  FOREIGN KEY (artpiece_id) REFERENCES artpiece (id),
  FOREIGN KEY (contract_id) REFERENCES contract (id)
);

CREATE TABLE artpiece (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  owner_id INTEGER NOT NULL,
  renter_id INTEGER,
  uploadtime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  artpiecename TEXT NOT NULL,
  image BLOB NOT NULL,
  imagetype TEXT NOT NULL,
  value DECIMAL(10, 2) NOT NULL,
  FOREIGN KEY (owner_id) REFERENCES user (id)
  FOREIGN KEY (renter_id) REFERENCES user (id)
);
