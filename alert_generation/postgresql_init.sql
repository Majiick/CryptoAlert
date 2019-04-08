CREATE EXTENSION IF NOT EXISTS pgcrypto;

DROP TABLE IF EXISTS EMAIL_NOTIFICATION;
DROP TABLE IF EXISTS NOTIFICATION;
DROP TABLE IF EXISTS PRICE_POINT_ALERT;
DROP TABLE IF EXISTS VOLUME_POINT_ALERT;
DROP TABLE IF EXISTS PRICE_PERCENTAGE_ALERT;
DROP TABLE IF EXISTS ALERT;
DROP TABLE IF EXISTS REGISTERED_USER;
DROP TABLE IF EXISTS TRADE;
DROP TABLE IF EXISTS ORDER_BOOK;
DROP TABLE IF EXISTS INTERRUPTION;
DROP TABLE IF EXISTS OHLC;
-- DROP TABLE IF EXISTS INTERESTING_EVENT;

CREATE TABLE IF NOT EXISTS REGISTERED_USER(
  user_pk SERIAL PRIMARY KEY,
  user_name VARCHAR(100) NOT NULL UNIQUE,
  password VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS ALERT(
  alert_pk SERIAL PRIMARY KEY,
  created_by_user INTEGER REFERENCES REGISTERED_USER(user_pk),
  fulfilled BOOL NOT NULL,
  repeat BOOL NOT NULL,
  alert_type VARCHAR(100) NOT NULL CHECK (alert_type IN ('pricepoint', 'volumepoint', 'pricepercentage')),
  broadcast_interesting_event_on_trigger BOOL NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS NOTIFICATION(
  notification_pk SERIAL PRIMARY KEY,
  notify_on_which_alert INTEGER REFERENCES ALERT(alert_pk)
);

CREATE TABLE IF NOT EXISTS EMAIL_NOTIFICATION(
  user_to_notify INTEGER REFERENCES REGISTERED_USER(user_pk)
) INHERITS(NOTIFICATION);

CREATE TABLE IF NOT EXISTS PRICE_POINT_ALERT(
  exchange VARCHAR(100) NOT NULL,
  pair VARCHAR(20) NOT NULL,
  point REAL NOT NULL,
  direction VARCHAR(20) NOT NULL CHECK (direction IN ('up', 'down'))
) INHERITS(ALERT);

CREATE TABLE IF NOT EXISTS VOLUME_POINT_ALERT(
  exchange VARCHAR(100) NOT NULL,
  pair VARCHAR(20) NOT NULL,
  point REAL NOT NULL
) INHERITS(ALERT);

CREATE TABLE IF NOT EXISTS PRICE_PERCENTAGE_ALERT(
  exchange VARCHAR(100) NOT NULL,
  pair VARCHAR(20) NOT NULL,
  point REAL NOT NULL,
  direction VARCHAR(20) NOT NULL CHECK (direction IN ('up', 'down')),
  time_frame REAL NOT NULL
) INHERITS(ALERT);

CREATE TABLE IF NOT EXISTS TRADE(
  trade_time BIGINT NOT NULL,
  exchange TEXT NOT NULL,
  market TEXT NOT NULL,
  buy BOOL NOT NULL,
  price float(53) NOT NULL,
  size float(53) NOT NULL,

  PRIMARY KEY(trade_time, exchange, market, buy)
);

CREATE TABLE IF NOT EXISTS INTERESTING_EVENT(
  id SERIAL PRIMARY KEY,
  event_time BIGINT NOT NULL,
  exchange TEXT NOT NULL,
  market TEXT NOT NULL,
  message TEXT NOT NULL,
  event_type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS INTERRUPTION(
  id SERIAL PRIMARY KEY,
  start_time BIGINT NOT NULL,
  end_time BIGINT NOT NULL,
  exchange TEXT NOT NULL,
  fulfilled BOOLEAN NOT NULL,
  times_tried INTEGER
);

CREATE TABLE IF NOT EXISTS OHLC(
  id SERIAL PRIMARY KEY,
  close_time BIGINT NOT NULL, /* In Seconds */
  open_price float(53) NOT NULL,
  high_price float(53) NOT NULL,
  low_price float(53) NOT NULL,
  close_price float(53) NOT NULL,
  volume float(53) NOT NULL,
  exchange TEXT NOT NULL,
  market TEXT NOT NULL,
  time_interval INTEGER NOT NULL /* In Seconds */
);
CREATE INDEX idx_ohlc_close_time ON OHLC(close_time);

CREATE UNLOGGED TABLE IF NOT EXISTS ORDER_BOOK(
  snapshot_time BIGINT NOT NULL,
  exchange TEXT NOT NULL,
  market TEXT NOT NULL,
  book JSON NOT NULL,
  keep BOOL NOT NULL,

  PRIMARY KEY(snapshot_time, exchange, market)
);