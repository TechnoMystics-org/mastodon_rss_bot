#!/usr/bin/python3
##################
## DEPENDENCIES ##
##################
import requests, datetime, time
import os, re, json, csv
import feedparser
from mastodon import Mastodon
from datetime import datetime
import tokenlib_public
from dateutil import parser
##################

############
## AUTHOR ##
############
# RSSBOT by @mpoletiek
# https://enlightened.army/@mpoletiek
############

#############
## CREDITS ##
#############
# 1: https://github.com/hanscees/mastodon-bot
#############

############
## RSSBOT ##
############
# RSS Bot for Enlightened.Army a Mastodon community
# Official Site: 
# Official RSS List: 
# Official Feed: https://enlightened.army/@rssbot
############

###########
## NOTES ##
###########
## as you can probably guess:
# tokens are storen in tokenlib_public
# functions to post to mastodon are in hcmastodonlib
#
# This script depends on 2 files
# 1. rss_list.csv is a list of rss feeds, one on each line
# 2. rssbot_last_run.txt is a file the bot uses to keep track of RSS updates
###########

##################
## GET LAST RUN ##
##################
LOCAL_TIMEZONE="CST"
last_run_path="./rssbot_last_run.txt"
try:
    with open(last_run_path, "r") as myfile:
        data = myfile.read()
except:
    #######################
    ## SET LAST RUN DATE ##
    #######################
    time_format_code = '%a, %d %b %Y %X'
    # datetime to str
    now = datetime.now()
    now_str = now.strftime(time_format_code)
    print(now_str)

    #save value if we found new entries
    with open(last_run_path, "w") as myfile:
        myfile.write("%s %s" % (now_str, LOCAL_TIMEZONE))
    print("Wrote %s" % (last_run_path))
    # re-open file
    with open(last_run_path, "r") as myfile:
        data = myfile.read()

lr_dt = parser.parse(data)
print("LAST RUN: %s" % (lr_dt))
lrgr_entry_count=0
################

#######################
## GET RSS FEED LIST ##
#######################
# reading the CSV file
feed_list = []
with open('./rss_list.csv', mode ='r')as file:
  csvFile = csv.reader(file)
  for lines in csvFile:
        print(lines)
        feed_list.append(lines)
#######################


################################
## GET RSS FEED & NEW ENTRIES ##
################################
# Get feed, count entries
new_entries = []
for feed in feed_list:
    print("Feed: %s" % (feed))
    d = feedparser.parse(feed[0])
    print ("Found %s entries in RSS Feed: " % (len(d['entries'])))

    # foreach entry, see if it's newer than last run
    for entry in d['entries']:
        e_dt = parser.parse(entry['published'])
        # entry is newer than last run
        if e_dt > lr_dt:
            lrgr_entry_count += 1
            print("New Entry: %s" % (entry['title']))
            new_entries.append([entry['title'], entry['link']])
###############################

#######################
## NEW ENTRIES FOUND ##
#######################
# If we find new entries, we'll attempt to post them
if len(new_entries) > 0:

    ####################################
    ## SETTING UP MASTODON CONNECTION ##
    ## modify tokenlib_pub.py for Auth #
    ####################################
    ## now lets get the tokens for our bot
    ## we choose pixey for now
    tokendict=tokenlib_public.getmytokenfor("enlightened.army")
    pa_token = tokendict["pa_token"]
    host_instance = tokendict["host_instance"]
    botname = tokendict["botname"]
    print("host instance is", host_instance)

    # we need this to use pythons Mastodon.py package
    mastodon = Mastodon(
        access_token = pa_token,
        api_base_url = host_instance
    )

    ######################
    ## POST NEW ENTRIES ##
    ######################
    toots_attempted_count=0
    for toot in new_entries:
        toots_attempted_count += 1
        print("Posting New Toot %s/%s in 20 seconds" % (toots_attempted_count, len(new_entries)))
        time.sleep(20)
        
        # the text to toot
        feed_title = toot[0]
        feed_link = toot[1]
        toottxt = "%s \n%s" % (feed_title, feed_link)
        
        # some hashtags that stay constant
        botname="rssbot"
        hashtag1 = "#" + botname
        hashtagcontent = "#test"

        #hashtags and tweettext together
        post_text = str(toottxt) + "\n" + "posted by " + hashtag1 + " " + hashtagcontent + "\n" # creating post text
        post_text = post_text[0:499]
        print("%s\n" % (post_text))

        ###############
        ## POST TOOT ##
        ###############
        mastodon.status_post(post_text)
        ###############
########################

#######################
## SET LAST RUN DATE ##
#######################
time_format_code = '%a, %d %b %Y %X'
# datetime to str
now = datetime.now()
now_str = now.strftime(time_format_code)
print(now_str)

#save value if we found new entries
if lrgr_entry_count > 0:
    print("%s New Entries Found" % (lrgr_entry_count))
    with open(last_run_path, "w") as myfile:
        myfile.write("%s %s" % (now_str,LOCAL_TIMEZONE))
else:
    print("No New Entries")
######################