from secret import C_KEY, C_SECRET, A_TOKEN, A_TOKEN_SECRET, WEATHER_KEY, CITY
import tweepy # for tweeting
import nltk # for sentence parsing
import requests
import json
import requests
import sys
import urllib
import redis
from datetime import datetime

TWITTER_TIMEOUT_SECS = 10 * 60 # 10 minutes

# Connect to redis server
R = redis.Redis()

# Server already has downloaded the data
# nltk.download('punkt')

def too_soon():
    if R.get('tweetbot_timeout') is not None:
        return True
    else:
        R.setex('tweetbot_timeout','running', TWITTER_TIMEOUT_SECS)
        return False

def get_next_chunk():
    # open text file
    text_file = open('book.txt', 'r+')
    text_string = text_file.read()
    # separate the text into sentences
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = tokenizer.tokenize(text_string)
    # tweet the whole sentence if it's short enough
    if len(sentences[0]) <= 140:
        chunk = sentences[0]
    # otherwise just print the first 140 characters
    else:
        chunk = sentences[0][0:140]

    # delete what we just tweeted from the text file
    text_file.seek(0)
    text_file.write(text_string[len(chunk):len(text_string)])
    text_file.truncate()
    text_file.close()
    return chunk

def tweet(message):
    auth = tweepy.OAuthHandler(C_KEY, C_SECRET)  
    auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)  
    api = tweepy.API(auth)
    auth.secure = True
    print("Posting message {}".format(message))
    api.update_status(status=message[:140])

def dateformatter(ts):
    dt = datetime.fromtimestamp(ts)
    return dt.strftime("%I:%M%p")

def weather():
    try:
        u = "http://api.openweathermap.org/data/2.5/weather?id={0}&mode=json&units=imperial&APPID={1}"
        r = requests.get(u.format(CITY, WEATHER_KEY))
        j = json.loads(r.text)
    except:
        sys.stderr.write("Couldn't load current conditions\n")

    temperature = int(round(j['main']['temp']))
    conditions = j['weather'][0]['description'].title()
    humidity = int(round(j['main']['humidity']))
    sunrise = dateformatter(j['sys']['sunrise'])
    sunset = dateformatter(j['sys']['sunset'])

    s = u"Irvine Weather: {}, {}°F, {}% humidity."
    s += u" Sunrise at {}, sunset at {}."
    currentweather = s.format(conditions, temperature, humidity, sunrise, sunset)
    return currentweather

def do_tweet(tweet_type='weather'):
    if tweet_type == 'weather':
        data = weather()
    elif tweet_type == 'sonnet':
        data = get_next_chunk()
    tweet(data)

def main():
    if not too_soon():
        do_tweet()

if __name__ == '__main__':
    main()
    
