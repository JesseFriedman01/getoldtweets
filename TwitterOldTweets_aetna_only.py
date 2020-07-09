import GetOldTweets3 as got
import csv
from datetime import datetime as dt
import html
import ftfy
import time
import sys, getopt

def read_from_text_file(file_name):
    lst = []
    with open(file_name, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            lst.append(row[0])
    return lst

def get_tweets(market, keyword, start_date, end_date):
    # .setMaxTweets was removed
    tweetCriteria = got.manager.TweetCriteria().setQuerySearch(keyword)\
                                               .setSince(start_date)\
                                               .setUntil(end_date)\
                                               .setMaxTweets(9500) 
                                               # .setNear(market)

    tweets = got.manager.TweetManager.getTweets(tweetCriteria)
    return tweets

def write_csv_headers(file_name):
    with open(file_name, mode ='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["date","username","to","replies",
                         "retweets","favorites","text","geo","hashtags","id","permalink", "market", "keyword"])

def write_to_csv(file_name, tweets):
    # replaces improper characters from tweet
    def cleanse_tweet(tweet):
        tweet = html.unescape(tweet)
        return ftfy.fix_text(tweet)
    with open(file_name, mode ='a', encoding = "utf_8_sig", newline='') as f:
        writer = csv.writer(f)
        for i in range(len(tweets)):
            cleansed_tweet = cleanse_tweet(tweets[i].text)
            # a field for market was added as the geo tag didn't seem to populate any data
            # market is simply the market from market.txt that's currently being iterated through
            write_row=[tweets[i].date, tweets[i].username,tweets[i].to, tweets[i].replies, tweets[i].retweets, tweets[i].favorites,
                       cleansed_tweet, tweets[i].geo, tweets[i].hashtags, tweets[i].id, tweets[i].permalink, market, keyword] # all needed fields
            writer.writerow(write_row)

def date_to_ordinal(d):
    if isinstance(d, str):
        d =  dt.strptime(d, '%Y-%m-%d').date()
    return d.toordinal()

def date_from_ordinal(ord):
    return dt.fromordinal(ord).strftime("%Y-%m-%d")

def sleep():
    for remaining in range(sleep_duration * 60, 0, -1):
        min, sec = divmod(remaining, 60)
        sys.stdout.write("\r")
        sys.stdout.write("%02d:%02d" % (min, sec))
        sys.stdout.flush()
        time.sleep(1)

def parseDateInput(argv):
    start_date = ''
    end_date = ''
    try:
        opts, args = getopt.getopt(argv, "s:e:")
    except getopt.GetoptError:
        print('TwitterOldTweets.py -s <start_date> -e <end_date>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-s':
            start_date = arg
        elif opt == '-e':
            end_date = arg
    return start_date, end_date

if __name__ == "__main__":
    start_date, end_date = parseDateInput(sys.argv[1:])
    markets = read_from_text_file('markets.txt')
    keywords = read_from_text_file('keywords.txt')

    # ordinal of start_date
    start_date_ord = date_to_ordinal(start_date)
    # ordinal of end_date
    end_date_ord = date_to_ordinal(end_date)

    # file name is saved with a date and time stamp as to not overwrite existing files
    csv_file_name = dt.now().strftime("%Y-%m-%d_%H.%M.%S") + '_output.csv'
    write_csv_headers(csv_file_name)

    # num days in chunk (chunk is time-span)
    chunk_size = 1
    # do not change
    request_count = 0
    # in minutes
    sleep_duration = 16

    # print('getting tweets')
    # tweets = get_tweets(None, 'cvs', date_from_ordinal(start_date_ord),
    #                     date_from_ordinal(start_date_ord + chunk_size))
    #
    # write_to_csv(csv_file_name, tweets)



    # while end_date_ord > start_date_ord:
    #     print('Current start period:', date_from_ordinal(start_date_ord), 'Current end period:', date_from_ordinal(start_date_ord + chunk_size))
    #     # for market in markets:
    #     #     print('\tCurrent market:', market)
    #     for keyword in ['aetna']:
    #         print('\t\tCurrent keyword:', keyword)
    #         request_count += 1
    #         tweets = get_tweets(None, keyword, date_from_ordinal(start_date_ord), date_from_ordinal(start_date_ord + chunk_size))
    #         write_to_csv(csv_file_name, tweets)
    #         if request_count == 15:
    #             print ('\t\t\tSleeping')
    #             request_count = 0
    #             sleep()

    #             if request_count == 100:
    #                 print ('\t\t\tSleeping')
    #                 request_count = 0
    #                 sleep()

    market = None
    keyword = 'aetna'

    while end_date_ord > start_date_ord:
        print('Current start period:', date_from_ordinal(start_date_ord), 'Current end period:', date_from_ordinal(start_date_ord + chunk_size))
        request_count += 1
        tweets = get_tweets(market, keyword, date_from_ordinal(start_date_ord), date_from_ordinal(start_date_ord + chunk_size))
        write_to_csv(csv_file_name, tweets)
        if request_count == 15:
            print ('\t\t\tSleeping')
            request_count = 0
            sleep()

        start_date_ord += chunk_size

    # print(date_from_ordinal(start_date_ord), date_from_ordinal(end_date_ord))
