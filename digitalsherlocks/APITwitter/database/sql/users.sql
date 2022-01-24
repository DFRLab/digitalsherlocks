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

CREATE TABLE place(
  id VARCHAR NOT NULL PRIMARY KEY,
  name VARCHAR,
  full_name VARCHAR,
  country VARCHAR (100),
  country_code VARCHAR (10),
  place_type VARCHAR (100),
  type VARCHAR (10),
  coordinates TEXT
);

CREATE TABLE tweet(
  id VARCHAR NOT NULL,
  id_str VARCHAR NOT NULL,
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
  text TEXT,
  full_text TEXT,
  tokenized_sentence TEXT,
  retweet_count INTEGER,
  favorite_count INTEGER,
  screen_name VARCHAR (20),
  user_id VARCHAR REFERENCES users (id),
  user_id_str VARCHAR,
  source VARCHAR (100),
  in_reply_to_status_id VARCHAR,
  in_reply_to_status_id_str VARCHAR,
  in_reply_to_user_id VARCHAR,
  in_reply_to_user_id_str VARCHAR,
  in_reply_to_screen_name VARCHAR (20),
  is_quote_status INTEGER,
  quoted_user_screen_name VARCHAR (20),
  quoted_status_id_str VARCHAR,
  is_retweet_status INTEGER,
  rt_user_screen_name VARCHAR (20),
  rt_user_id_str VARCHAR,
  rt_status_id_str VARCHAR,
  rt_original_date_timestamp VARCHAR (25),
  rt_original_date VARCHAR (15),
  rt_original_date_year INTEGER,
  rt_original_date_month INTEGER,
  rt_original_date_day INTEGER,
  rt_original_date_weekday INTEGER,
  rt_original_date_month_name VARCHAR(10),
  rt_original_date_day_name VARCHAR(10),
  rt_original_date_time_hour VARCHAR (10),
  rt_original_date_hour INTEGER,
  rt_original_date_minute INTEGER,
  rt_original_date_second INTEGER,
  rt_original_date_quarter INTEGER,
  rt_original_date_dayofyear INTEGER,
  rt_original_date_weekofyear INTEGER,
  lang_code VARCHAR (5),
  place_id VARCHAR REFERENCES place (id),
  counter INTEGER,
  search_request VARCHAR NOT NULL,
  endpoint_type VARCHAR NOT NULL,
  timezone TEXT,
  PRIMARY KEY (id)
);

CREATE TABLE mentions(
  id VARCHAR NOT NULL,
  id_str VARCHAR NOT NULL,
  id_from_user VARCHAR,
  id_str_from_user VARCHAR,
  screen_name_from_user VARCHAR (20),
  id_user VARCHAR,
  id_str_user VARCHAR,
  screen_name_user VARCHAR (20),
  counter INTEGER,
  FOREIGN KEY (id) REFERENCES tweet (id),
  PRIMARY KEY (id, id_str_user, screen_name_user)
);

CREATE TABLE hashtags(
  id VARCHAR NOT NULL,
  id_str VARCHAR NOT NULL,
  id_from_user VARCHAR,
  id_str_from_user VARCHAR,
  screen_name_from_user VARCHAR (20),
  hashtag TEXT NOT NULL,
  counter INTEGER,
  FOREIGN KEY (id) REFERENCES tweet (id),
  PRIMARY KEY (id, id_str_from_user, hashtag)
);

CREATE TABLE urls(
  id VARCHAR NOT NULL,
  id_str VARCHAR NOT NULL,
  url TEXT,
  expanded_url TEXT,
  counter INTEGER,
  FOREIGN KEY (id) REFERENCES tweet (id),
  PRIMARY KEY (id, url)
);

CREATE TABLE media_tweet(
  id VARCHAR NOT NULL,
  id_str VARCHAR NOT NULL,
  id_media VARCHAR,
  id_str_media VARCHAR,
  FOREIGN KEY (id) REFERENCES tweet (id),
  PRIMARY KEY (id, id_media)
);

CREATE TABLE media(
  id VARCHAR NOT NULL,
  id_str VARCHAR NOT NULL,
  url TEXT NOT NULL,
  expanded_url TEXT,
  media_url_https TEXT,
  type VARCHAR (25),
  counter INTEGER,
  FOREIGN KEY (id) REFERENCES media_tweet (id_media),
  PRIMARY KEY (id, url)
);

CREATE TABLE media_video(
  id VARCHAR NOT NULL,
  id_str VARCHAR NOT NULL,
  duration_millis INTEGER,
  duration_secs NUMERIC,
  duration_mins NUMERIC,
  url TEXT NOT NULL,
  content_type VARCHAR (25),
  bitrate INTEGER,
  monetizable INTEGER,
  counter INTEGER,
  FOREIGN KEY (id) REFERENCES media_tweet (id_media),
  PRIMARY KEY (id, url)
);
