#!/usr/bin/python3

# Mastodon Bot
# RSS Reader Poster

# RSSBOT by @mpoletiek
# https://enlightened.army/@mpoletiek
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
# As you can probably guess tokens are stored in tokenlib_public.
# We use Mastodon.py to interact with a Mastodon instance.
#
# This script depends on 2 files
# 1. Source of RSS feeds. This comes from Github for now.
# 2. rssbot_last_run.txt: Do Not Touch. Modify at your own risk. A simple text file for keeping track of time.
###########

##################
## DEPENDENCIES ##
##################
import time, os, re, json, csv, requests

from mastodon import Mastodon
from datetime import datetime
from dateutil import parser

import feedparser
import tokenlib_public
##################

#####################
## SETUP VARIABLES ##
#####################
# botname is set in tokenlib_public.py
csv_url="https://raw.githubusercontent.com/TechnoMystics-org/ea_rss_bot_feeds/main/technews_rss.csv"
temp_csv_path="./temp.csv"
last_run_path="./rssbot_lastrun.txt"
time_format_code = '%Y-%m-%d:%H:%M'
now_dt = datetime.now()
now_str = now_dt.strftime(time_format_code)
print("Now: "+now_str)

# Hashtags for toots, seperate by spaces
hashtagcontent = "#technews"

## Testing URL Hosted CSV
r = requests.get(csv_url, stream = True)
# write the returned chunks to file
with open(temp_csv_path,"wb") as tempcsv:
    for chunk in r.iter_content(chunk_size=1024):
         if chunk:
             tempcsv.write(chunk)

## GET LAST RUN ##
# Get the last time we ran this script
try:
    with open(last_run_path, "r") as myfile:
        data = myfile.read()
except:
    ## SET LAST RUN DATE ##
    #save value if we found new entries
    with open(last_run_path, "w") as myfile:
        myfile.write("%s" % (now_str))
    print("Wrote %s" % (last_run_path))
    # re-open file
    with open(last_run_path, "r") as myfile:
        data = myfile.read()

# Normalize date
lr_dt = datetime.strptime(data,time_format_code)
lr_str = lr_dt.strftime(time_format_code)
print("Last Run: %s" % (lr_str))

lrgr_entry_count=0
################

## GET RSS FEED LIST ##
# reading the CSV file
target_feed = temp_csv_path
feed_list = []
with open(target_feed, mode ='r')as file:
  csvFile = csv.reader(file)
  for lines in csvFile:
        #print(lines)
        feed_list.append(lines)
#######################

# Helper function for discovering a feed's published date field
def getPubDate(entry):
    known_values = ['published', 'date','PubDate','updated','pubDate']
    this_pubdate = None
    for field in known_values:
        try: 
            this_pubdate = entry[field]
        except:
            pass

    if this_pubdate == None:
        print("Couldn't find entry date")    

    return this_pubdate

## GET RSS FEED & NEW ENTRIES ##
# Get feed, count entries
new_entries = []
for feed in feed_list:

    print("Feed: %s" % (feed))
    try:
        d = feedparser.parse(feed[0])
    except:
        print("Failed to parse RSS feed: %s" %(feed))

    print ("Found %s entries in RSS Feed." % (len(d['entries'])))

    # foreach entry, see if it's newer than last run
    for entry in d['entries']:
        # check multiple values for published date
        entry_dt_str = getPubDate(entry)
        entry_dt = None
        # Did we find an entry date?
        if entry_dt_str != None:
            entry_dt = parser.parse(entry_dt_str)
            entry_dt_str = entry_dt.strftime(time_format_code)
        # Normalize date
        new_dt = datetime.strptime(entry_dt_str,time_format_code)

        # Check if entry is new!
        # First make sure entry isn't in the future
        # Entry time is smaller than now time.
        # This means it was posted in the past.
        # We don't accept posts from the "future".
        if new_dt < now_dt: 
            if new_dt > lr_dt: # Entry time is larger than last run time.
                lrgr_entry_count += 1
                print("New Entry: %s" % (entry['title']))
                # Check multiple values for entry link
                if entry['link']:
                    new_entries.append([entry['title'], entry['link'], entry_dt_str])
                elif entry['guid']:
                    new_entries.append([entry['title'], entry['guid'], entry_dt_str])
###############################

## NEW ENTRIES FOUND ##
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

    ## POST NEW ENTRIES ##
    toots_attempted_count=0
    # collect array of pubDates
    new_pubdates = []
    for toot in new_entries:
        toots_attempted_count += 1
        print("Posting New Toot %s/%s in 20 seconds" % (toots_attempted_count, len(new_entries)))
        time.sleep(20)
        
        # the text to toot
        feed_title = toot[0]
        feed_link = toot[1]
        new_pubdates.append(toot[2])
        toottxt = "%s \n%s" % (feed_title, feed_link)
        
        # prepend botname to hashtags
        hashtag1 = "#" + botname

        #hashtags and toottext together
        post_text = str(toottxt) + "\n" + "posted by " + hashtag1 + " " + hashtagcontent + "\n" # creating post text
        post_text = post_text[0:499]
        print("%s\n" % (post_text))

        ## POST TOOT ##
        try: 
            mastodon.status_post(post_text)
        except:
            print("Failed to post to Mastodon")

    # sort the pubdates
    new_pubdates.sort(reverse=True)
    print("Latest post date: %s" % (new_pubdates[0]))

    with open(last_run_path, "w") as myfile:
        myfile.write("%s" % (new_pubdates[0]))

else:
    print("No New Entries")
######################
