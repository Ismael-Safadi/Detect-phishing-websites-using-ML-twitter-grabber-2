import re

import tweepy
import csv
from urllib.request import urlopen
import pandas as pd
####input your credentials here

def Collect_tweets(Hashtag , Number_of_tweets,Date):
    consumer_key = 'OIZUckqxoE8QjlO2rp4YEXJDp'
    consumer_secret = 'RMjVCxZE1GtQalBM0ZVOtHqllC3nYeJvsrhau3KBA1MhfmrCHH'
    access_token = '937653227918675969-OwkD2puKOsQFkLOAtzjlmmpAWlcZ02z'
    access_token_secret = 'hTtje1Ei2prVvhGH94J9Jx9uxuUidGkoCfEWQrxuHkHm0'

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth,wait_on_rate_limit=True)

    for tweet in tweepy.Cursor(api.search,q=Hashtag,count=Number_of_tweets,
                               lang="en",
                               since=Date).items():
        print (tweet.created_at, tweet.text)
        print("*********")
        print(tweet.retweet_count)
        print("*********")
        print(tweet.favorite_count)
        print("*******")
        print(tweet.user.location)
        print("*******")
        print(tweet.source)
        print("###################")
        for url in tweet.entities['urls']:
            print(url['expanded_url'])
        print("##############")
        #csvWriter.writerow([tweet.created_at, tweet.text.encode('utf-8')])