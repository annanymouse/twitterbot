from secret import C_KEY, C_SECRET, A_TOKEN, A_TOKEN_SECRET, WEATHER_KEY, CITY
import tweepy # for tweeting
import nltk # for sentence parsing
import requests
import json
import requests
import sys
import urllib

nltk.download('punkt')

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
    api.update_status(status=message)

def weather():
    try:
        u = "http://api.openweathermap.org/data/2.5/weather?id={0}&mode=json&units=imperial&APPID={1}"
        r = requests.get(u.format(CITY, WEATHER_KEY))
        j = json.loads(r.text)
    except:
        sys.stderr.write("Couldn't load current conditions\n")
    temperature = j['main']['temp']
    conditions = j['weather'][0]['description']
    humidity = j['main']['humidity']
    s = "Irvine Weather: {0} with a temperature of {1}" u"\u00B0" "F, humidity at {2}%."
    currentweather = s.format(conditions[0].upper() + conditions[1:].lower(),
    int(round(temperature)), int(round(humidity)))
    return currentweather

#tweet(get_next_chunk())
tweet(weather())
#print(weather())
