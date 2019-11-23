import tweepy
from utils import generate_data_set
from Spark_Process import spark_activity_to_detect
print("""
###############################################################################################################
#                                                                                                             #
#  _____  _     _     _     _               _    _ _____  _                _      _            _              #
# |  __ \| |   (_)   | |   (_)             | |  | |  __ \| |              | |    | |          | |             #
# | |__) | |__  _ ___| |__  _ _ __   __ _  | |  | | |__) | |     ___    __| | ___| |_ ___  ___| |_ ___  _ __  #
# |  ___/| '_ \| / __| '_ \| | '_ \ / _` | | |  | |  _  /| |    / __|  / _` |/ _ \ __/ _ \/ __| __/ _ \| '__| #
# | |    | | | | \__ \ | | | | | | | (_| | | |__| | | \ \| |____\__ \ | (_| |  __/ ||  __/ (__| || (_) | |    #
# |_|    |_| |_|_|___/_| |_|_|_| |_|\__, |  \____/|_|  \_\______|___/  \__,_|\___|\__\___|\___|\__\___/|_|    #
#                                    __/ |                                                                    #
#                                   |___/                                                                     #
#                                                                                                             #
###############################################################################################################

""")
Hashtag = input("Enter hashtag on twitter : ")
Number_of_tweets = input("Enter Number of tweets : ")
Date = input("Enter date that you want to start collecting tweets from should be YYYY-MM-DD : ")
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)
number_of_all_tweets = 0
number_of_tweets_contains_url = 0
number_of_infected_urls = 0
Number_of_tweets = int(Number_of_tweets)
list_of_trusted_sites = ["twitter","google","youtube","facebook","github","instagram"]
for tweet in tweepy.Cursor(api.search, q=Hashtag, count=int(Number_of_tweets),
                           lang="en",
                           since=Date).items():
    Number_of_tweets-=1
    print(tweet.created_at, tweet.text)
    print("*********")
    print(tweet.retweet_count)
    print("*********")
    print(tweet.favorite_count)
    print("*******")
    print(tweet.user.location)
    print("*******")
    print(tweet.source)
    print("###################")
    number_of_all_tweets+=1

    try:
        for url in tweet.entities['urls']:
            if len(url['expanded_url'])>5:
                number_of_tweets_contains_url+=1
                if str(url) not in list_of_trusted_sites:
                    list_of_ones = generate_data_set(url)
                    check_phishing_result = spark_activity_to_detect(list_of_ones)
                    if "-1" in str(check_phishing_result):
                        number_of_infected_urls+=1

                    print("Phishing site : ",url)

    except Exception as e:
        print(e)
    print("##############")
    if Number_of_tweets <0:
        break
print("***********************************")
print("statistics : ")
print("number_of_all_tweets : ",number_of_all_tweets)
print("number_of_tweets_contains_url : ",number_of_tweets_contains_url)
print("number_of_infected_urls : ",number_of_infected_urls)

