#!/home/mpoletiek/Devspace/mastodon_rss_bot/venv/bin/python3

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
import time, os, re, json, csv, requests, redis, pickle, argparse

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
csv_url="https://raw.githubusercontent.com/TechnoMystics-org/ea_rss_bot_feeds/main/enews_rss.csv"
temp_csv_path="./temp.csv"
time_format_code = '%Y-%m-%d:%H:%M'
now_dt = datetime.now()
now_str = now_dt.strftime(time_format_code)
print("Now: "+now_str)
# Mastodon Variables
tokendict=tokenlib_public.getmytokenfor("enlightened.army")
pa_token = tokendict["pa_token"]
host_instance = tokendict["host_instance"]
botname = tokendict["botname"]
# Redis Variables
redis_password = tokenlib_public.getRedisPassword()
r_target = 'mastodon_rstore_%s' % botname
r_store_template = {
    "entries":[],
    "last_run": now_str
}
stor = {}

# Extra hashtags for toots, seperate by spaces
#hashtagcontent = "#rss #bot"

# Parse for initialize flag
args_parser = argparse.ArgumentParser(description="Mastodon RSS Bot")
args_parser.add_argument('-i', '--initialize', action='store_true', help='Initialize Redis Store and scan RSS feeds for initial news set.')
args = args_parser.parse_args()

def initialize(r):
    if args.initialize == True:
        print("Initializing Redis Store.")
        r.delete(r_target)

def is_new_entry(stor,entry_link):
    is_new = True
    if len(stor['entries']) > 0:
        for stor_entry in stor['entries']:
            #print(stor_entry[1])
            if stor_entry[1] == entry_link:
                #print("old entry")
                is_new = False
    
    return is_new

## Testing URL Hosted CSV
r = requests.get(csv_url, stream = True)
# write the returned chunks to file
with open(temp_csv_path,"wb") as tempcsv:
    for chunk in r.iter_content(chunk_size=1024):
         if chunk:
             tempcsv.write(chunk)


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

## CONNECT TO REDIS ##
######################
r = redis.Redis(host='localhost',
                port=6379, 
                password=redis_password)
initialize(r)
p_stor = r.get(r_target)
if p_stor:
    print("Got current Redis store.")
    #print(p_stor)
    stor = pickle.loads(p_stor)
    #print(json.dumps(stor))
else:
    print("Creating new store.")
    p_template = pickle.dumps(r_store_template)
    r.set(r_target,p_template)
    stor = pickle.loads(r.get(r_target))
######################

## GET RSS FEED & NEW ENTRIES ##
# Get feed, count entries
new_entries = []
new_entry_count = 0
for feed in feed_list:

    print("Feed: %s" % (feed))
    try:
        d = feedparser.parse(feed[0])
    except:
        print("Failed to parse RSS feed: %s" %(feed))

    #print ("Found %s entries in RSS Feed." % (len(d['entries'])))

    # foreach entry, see if it's newer than last run
    for entry in d['entries']:
        #print("New Entry: %s" % (entry['title']))
        # Check multiple values for entry link
        if entry['link']:
            if is_new_entry(stor,entry['link']):
                new_entries.append([entry['title'], entry['link'], now_str])
                stor['entries'].append([entry['title'], entry['link'], now_str])
                new_entry_count += 1
        elif entry['guid']:
            if is_new_entry(stor,entry['guid']):
                new_entries.append([entry['title'], entry['guid'], now_str])
                stor['entries'].append([entry['title'], entry['guid'], now_str])
                new_entry_count += 1
        else:
            print("Can't interpret entry")
###############################

print("%s New Entries" % new_entry_count)
print("Updating Redis store.")
p_stor = pickle.dumps(stor)
r.set(r_target,p_stor)

## NEW ENTRIES FOUND ##
# If we find new entries, we'll attempt to post them
if len(new_entries) > 0 and args.initialize == False:
    ####################################
    ## SETTING UP MASTODON CONNECTION ##
    ## modify tokenlib_pub.py for Auth #
    ####################################
    ## now lets get the tokens for our bot
    ## we choose pixey for now
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

else:
    print("Nothing to post.")
######################