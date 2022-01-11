-- create tables
CREATE TABLE users(
  id VARCHAR NOT NULL,
  id_str VARCHAR NOT NULL,
  screen_name VARCHAR (20),
  name TEXT,
  created_at_timestamp VARCHAR (25),
  created_at VARCHAR (15),
  created_at_year INTEGER,
  created_at_month INTEGER,
  created_at_day INTEGER,
  created_at_weekday INTEGER,
  created_at_month_name VARCHAR(10),
  created_at_day_name VARCHAR(10),
  created_at_time_hour VARCHAR (10),
  created_at_hour INTEGER,
  created_at_minute INTEGER,
  created_at_second INTEGER,
  created_at_quarter INTEGER,
  created_at_dayofyear INTEGER,
  created_at_weekofyear INTEGER,
  description TEXT,
  statuses_count BIGINT,
  protected INTEGER,
  verified INTEGER,
  followers_count INTEGER,
  favourites_count INTEGER,
  friends_count INTEGER,
  listed_count INTEGER,
  location TEXT,
  profile_image_url_https TEXT,
  url TEXT,
  PRIMARY KEY (id, screen_name)
);

CREATE TABLE ids(
    id_str VARCHAR NOT NULL,
    FOREIGN KEY (id_str) REFERENCES users (id_str),
    PRIMARY KEY (id_str)
);
