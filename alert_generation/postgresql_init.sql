CREATE TABLE IF NOT EXISTS REGISTERED_USER(
  user_pk SERIAL PRIMARY KEY,
  user_name VARCHAR(100) UNIQUE,
  password VARCHAR(100),
  email VARCHAR(100) UNIQUE
);

CREATE TABLE IF NOT EXISTS ALERT(
  alert_pk SERIAL PRIMARY KEY,
  created_by_user INTEGER REFERENCES REGISTERED_USER(user_pk),
  fulfilled BOOL,
  repeat BOOL
);

CREATE TABLE IF NOT EXISTS EMAIL_NOTIFICATION(
  registered_user INTEGER REFERENCES REGISTERED_USER(user_pk),
  alert INTEGER REFERENCES ALERT(alert_pk),
  PRIMARY KEY(registered_user, alert)
);

CREATE TABLE IF NOT EXISTS PRICE_POINT_ALERT(
  exchange VARCHAR(100),
  pair VARCHAR(20),
  point REAL
) INHERITS(ALERT);