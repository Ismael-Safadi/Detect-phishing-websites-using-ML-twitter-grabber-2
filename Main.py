import tweepy
from sklearn import tree
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from utils import generate_data_set

import numpy as np
import sys


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

consumer_key = 'OIZUckqxoE8QjlO2rp4YEXJDp'
consumer_secret = 'RMjVCxZE1GtQalBM0ZVOtHqllC3nYeJvsrhau3KBA1MhfmrCHH'
access_token = '937653227918675969-OwkD2puKOsQFkLOAtzjlmmpAWlcZ02z'
access_token_secret = 'hTtje1Ei2prVvhGH94J9Jx9uxuUidGkoCfEWQrxuHkHm0'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

def load_data():
    '''
    Load data from CSV file
    '''
    # Load the training data from the CSV file
    training_data = np.genfromtxt('dataset.csv', delimiter=',', dtype=np.int32)

    # Extract the inputs from the training data
    inputs = training_data[:,:-1]

    # Extract the outputs from the training data
    outputs = training_data[:, -1]

    # This model follow 80-20 rule on dataset
    # Split 80% for traning and 20% testing
    boundary = int(0.8*len(inputs))

    training_inputs, training_outputs, testing_inputs, testing_outputs = train_test_split(inputs, outputs, test_size=0.33)

    # Return the four arrays
    return training_inputs, training_outputs, testing_inputs, testing_outputs
def run(classifier, name):
    '''
    Run the classifier to calculate the accuracy score
    '''
    # Load the training data
    train_inputs, test_inputs,train_outputs, test_outputs = load_data()

    # Train the decision tree classifier
    classifier.fit(train_inputs, train_outputs)

    # Use the trained classifier to make predictions on the test data
    predictions = classifier.predict(test_inputs)

    # Print the accuracy (percentage of phishing websites correctly predicted)
    accuracy = 100.0 * accuracy_score(test_outputs, predictions)
    print ("Accuracy score using {} is: {}\n".format(name, accuracy))

number_of_all_tweets = 0
number_of_tweets_contains_url = 0
number_of_infected_urls = 0
Number_of_tweets = int(Number_of_tweets)
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
    '''
    Main function -
    Following are several models trained to detect phishing webstes.
    Only the best and worst classifier outputs are displayed.
    '''

    # Decision tree
    # classifier = tree.DecisionTreeClassifier()
    # run(classifier, "Decision tree")

    # Random forest classifier (low accuracy)
    # classifier = RandomForestClassifier()
    # run(classifier, "Random forest")

    # Custom random forest classifier 1
    # print ("Best classifier for detecting phishing websites.")
    # classifier = RandomForestClassifier(n_estimators=500, max_depth=15, max_leaf_nodes=10000)
    # run(classifier, "Random forest")

    # Linear SVC classifier
    # classifier = svm.SVC(kernel='linear')
    # run(classifier, "SVC with linear kernel")

    # RBF SVC classifier
    # classifier = svm.SVC(kernel='rbf')
    # run(classifier, "SVC with rbf kernel")

    # Custom SVC classifier 1
    # classifier = svm.SVC(decision_function_shape='ovo', kernel='linear')
    # run(classifier, "SVC with ovo shape")

    # Custom SVC classifier 2
    # classifier = svm.SVC(decision_function_shape='ovo', kernel='rbf')
    # run(classifier, "SVC with ovo shape")

    # NuSVC classifier
    # classifier = svm.NuSVC()
    # run(classifier, "NuSVC")

    # OneClassSVM classifier
    # print ("Worst classifier for detecting phishing websites.")
    # classifier = svm.OneClassSVM()
    # run(classifier, "One Class SVM")
    try:
        for url in tweet.entities['urls']:
            if len(url['expanded_url'])>5:
                number_of_tweets_contains_url+=1
                classifier = RandomForestClassifier(n_estimators=500, max_depth=15, max_leaf_nodes=10000)
                run(classifier, "Random forest")
                classifier = svm.OneClassSVM()
                run(classifier, "One Class SVM")
                print(url['expanded_url'])
                data_set = generate_data_set(url['expanded_url'])

                # Reshape the array
                data_set = np.array(data_set).reshape(1, -1)

                # Load the date
                train_inputs, test_inputs, train_outputs, test_outputs = load_data()

                # Create and train the classifier
                classifier = RandomForestClassifier(n_estimators=500, max_depth=15, max_leaf_nodes=10000)
                classifier.fit(train_inputs, train_outputs)
                check_phishing_result = classifier.predict(data_set)
                if "-1" in str(check_phishing_result):
                    number_of_infected_urls+=1

                print(">>>>>>>>>>>>>| ",classifier.predict(data_set))

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

