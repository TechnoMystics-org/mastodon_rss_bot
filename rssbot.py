#!/usr/bin/python3
##################
## DEPENDENCIES ##
##################
import time, os, re, json, csv

from mastodon import Mastodon
from datetime import datetime
from dateutil import parser

import feedparser
import tokenlib_public
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
# Official Site: https://github.com/mpoletiek/mastodon_rss_bot
# Official RSS List: https://github.com/mpoletiek/mastodon_rss_bot/blob/main/rss_list.csv
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

#####################
## SETUP VARIABLES ##
#####################
# botname is set in tokenlib_public.py
LOCAL_TIMEZONE="CST"
last_run_path="./rssbot_last_run.txt"
rss_feed_path="./rss_list.csv"
time_format_code = '%a, %d %b %Y %X'
now_str = datetime.now().strftime(time_format_code)
# Add local timezone to now_str
now_str += " %s" % (LOCAL_TIMEZONE)
hashtagcontent = "#biznews"

##################
## GET LAST RUN ##
##################
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
with open(rss_feed_path, mode ='r')as file:
  csvFile = csv.reader(file)
  for lines in csvFile:
        #print(lines)
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
        # check multiple values for published date
        try:
            e_dt = parser.parse(entry['published'])
        except:
            try:
                e_dt = parser.parse(entry['date'])
            except:
                e_dt = parser.parse(entry['pubDate'])
        # print("Entry Date: %s" % (e_dt))
        # entry is newer than last run
        # First make sure entry isn't in the future
        if e_dt.timestamp() < parser.parse(now_str).timestamp():
            if e_dt.timestamp() > lr_dt.timestamp():
                lrgr_entry_count += 1
                print("New Entry: %s" % (entry['title']))
                # Check multiple values for entry link
                if entry['link']:
                    new_entries.append([entry['title'], entry['link']])
                elif entry['guid']:
                    new_entries.append([entry['title'], entry['guid']])
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
    print("POSTING AS %s" %(botname))

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
        
        # prepend botname to hashtags
        hashtag1 = "#" + botname

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
# Add local timezone to now_str
now_str += " %s" % (LOCAL_TIMEZONE)
print("Now string: %s" % (now_str))

#save value if we found new entries
if lrgr_entry_count > 0:
    print("%s New Entries Found" % (lrgr_entry_count))
    with open(last_run_path, "w") as myfile:
        myfile.write("%s" % (now_str))
else:
    print("No New Entries")
######################
