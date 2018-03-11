from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
import sqlite3
from textblob import TextBlob
from unidecode import unidecode
import time
import pandas as pd

conn = sqlite3.connect('twitter.db')
c = conn.cursor()

def create_table():
    c.execute("CREATE TABLE IF NOT EXISTS sentiment(unix REAL, user TEXT, tweet TEXT, sentiment REAL)")
    c.execute("CREATE INDEX IF NOT EXISTS fast_unix ON sentiment(unix)")
    c.execute("CREATE INDEX IF NOT EXISTS fast_user ON sentiment(user)")
    c.execute("CREATE INDEX IF NOT EXISTS fast_tweet ON sentiment(tweet)")
    c.execute("CREATE INDEX IF NOT EXISTS fast_sentiment ON sentiment(sentiment)")
    conn.commit()


create_table()

# Twitter API Credentials
CKEY = ""
CSECRET = ""
ATOKEN = ""
ASECRET = ""


class listener(StreamListener):

    def on_data(self, raw_data):
        try:
            data = json.loads(raw_data)
            user = data['user']['screen_name']
            tweet = unidecode(data['text'])
            time_ms = data['timestamp_ms']

            analysis = TextBlob(tweet)
            sentiment = analysis.sentiment.polarity

            print(time_ms, user, tweet, sentiment)
            c.execute("INSERT INTO sentiment (unix, user, tweet, sentiment) VALUES (?, ?, ?, ?)", (time_ms, user, tweet, sentiment))

            conn.commit()

        except KeyError as e:
            print('Error:', e)
        return True

    def on_error(self, status_code):
        print(status_code)



extract = False

if extract:
    # Extract tweets to database
    while True:
        try:
            auth = OAuthHandler(CKEY, CSECRET)
            auth.set_access_token(ATOKEN, ASECRET)

            twitterStream = Stream(auth, listener())
            twitterStream.filter(languages=["en"], track=['a', 'e', 'i', 'o', 'u'])
        except Exception as e:
            print(e)
            time.sleep(5)
else:
    # Read tweets from database
    df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE '%usa%' ORDER BY unix DESC LIMIT 1000", conn)
    df.sort_values('unix', inplace=True)

    df['smoothed_sentiment'] = df['sentiment'].rolling(int(len(df)/5)).mean()
    df.dropna(inplace=True)
    print(df.tail())

