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
#    ######################

# This script depends on 2 files
# 1. Source of RSS feeds. This comes from Github for now.
# 2. rssbot_last_run.txt: Do Not Touch. Modify at your own risk. A simple text file for keeping track of time.
###########

##################
## DEPENDENCIES ##
##################
import time, os, re, json, csv, requests, redis, pickle, argparse

from mastodon import Mastodon
from datetime import datetime, timedelta
from dateutil import parser

import feedparser
import tokenlib_public
##################

# Initialize Redis Stor Object
def initialize(r,args):
    if args.initialize == True:
        print("Initializing Redis Store.")
        r.delete(r_target)

# Check if RSS Entry is new
def is_new_entry(stor,entry_link):
    is_new = True
    if len(stor['entries']) > 0:
        for stor_entry in stor['entries']:
            #print(stor_entry[1])
            if stor_entry[1] == entry_link:
                #print("old entry")
                is_new = False
    
    return is_new

# Get RSS Feeds from URL
def get_rss_feeds(csv_url):
    r = requests.get(csv_url, stream = True)
    feed_list = []
    csvFile = csv.reader(r.content.decode('utf-8').splitlines(),delimiter=',')
    for lines in csvFile:
        feed_list.append(lines)
    
    return feed_list

# Get RSS Feed Entries
def get_feed_entries(feed_list,stor,now_str):
    new_entries = []
    new_entry_count = 0
    for feed in feed_list:

        print("Feed: %s" % (feed))
        try:
            d = feedparser.parse(feed[0])
        except:
            print("Failed to parse RSS feed: %s" %(feed))

        for entry in d['entries']:
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

    return {'new_entries':new_entries,'new_entry_count':new_entry_count}

# Store new RSS entries in Redis Obj
def store_new_entries(r,stor,new_entry_count,r_target):
    print("%s New Entries" % new_entry_count)
    print("Updating Redis store.")
    p_stor = pickle.dumps(stor)
    r.set(r_target,p_stor)

# Connect to Mastodon Instance
def connect_mastodon(host_instance,pa_token,botname):
    mastodon = Mastodon(
        access_token = pa_token,
        api_base_url = host_instance
    )

    return mastodon

# Post new RSS entries to Mastodon
def post_new_entries(mastodon,botname,new_entries,hashtagcontent):
    if len(new_entries):
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

# Connect to Redis DB and return Stor
def redis_connect(r_target, now_str, args):
    redis_variables = tokenlib_public.getRedisVariables()
    # Redis Obj Template
    r_store_template = {
        "entries":[],
        "last_run": now_str
    }
    stor = {}

    r = redis.Redis(host=redis_variables['host'],
                    port=redis_variables['port'], 
                    password=redis_variables['password'])
    initialize(r, args)
    p_stor = r.get(r_target)
    if p_stor:
        print("Got current Redis store.")
        stor = pickle.loads(p_stor)
    else:
        print("Creating new store.")
        p_template = pickle.dumps(r_store_template)
        r.set(r_target,p_template)
        stor = pickle.loads(r.get(r_target))

    return {'r':r,'stor':stor}

# Delete old RSS Entries
def delete_old_posts(r,cleanup_dt,time_format_code):
    saved_entries = []
    for entry in r['stor']['entries']:
        entry_dt = datetime.strptime(entry[2],time_format_code)
        if entry_dt >= cleanup_dt:
            saved_entries.append(entry)

    r['stor']['entries'] = saved_entries

def main():
    #####################
    ## SETUP VARIABLES ##
    #####################
    csv_url = tokenlib_public.getCSVUrl()

    time_format_code = '%Y-%m-%d:%H:%M'
    now_dt = datetime.now()
    now_str = now_dt.strftime(time_format_code)
    cleanup_dt = now_dt - timedelta(days=15)

    # Mastodon Variables
    tokendict=tokenlib_public.getmytokenfor("enlightened.army")
    pa_token = tokendict["pa_token"]
    host_instance = tokendict["host_instance"]
    botname = tokendict["botname"]
    # Redis Target Obj
    r_target = 'mastodon_rstore_%s' % botname

    # Extra hashtags for toots, seperate by spaces
    hashtagcontent = "#rss #bot"

    # Parse CLI Arguments
    args_parser = argparse.ArgumentParser(description="Mastodon RSS Bot")
    args_parser.add_argument('-i', '--initialize', action='store_true', help='Initialize Redis Store and scan RSS feeds for initial news set.')
    args_parser.add_argument('-c','--cleanup', action='store_true', help='Cleanup Redis store, purging posts older than 15 days')
    args = args_parser.parse_args()

    
    # Connect to Redis
    r = redis_connect(r_target, now_str, args)
    
    # Delete older posts
    if args.cleanup == True:
        delete_old_posts(r,cleanup_dt,time_format_code)
        

    # Get RSS feed list
    feed_list = get_rss_feeds(csv_url)
    
    # Find new RSS entries
    new_entries = get_feed_entries(feed_list,r['stor'], now_str)
    
    # Store new RSS entries
    store_new_entries(r['r'],
                      r['stor'],
                      new_entries['new_entry_count'],
                      r_target)
    
    # Post new RSS entries if not intializing
    if args.initialize == False and len(new_entries['new_entries']) > 0:
        mastodon = connect_mastodon(host_instance,pa_token,botname)
        post_new_entries(mastodon,botname,new_entries['new_entries'],hashtagcontent)


if __name__ == "__main__":
    main()