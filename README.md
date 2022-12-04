# rssbot.py
A mastodon rss bot

## AUTHOR 
 by @mpoletiek
 https://enlightened.army/@mpoletiek
 https://github.com/mpoletiek

## CREDITS 
 - https://github.com/hanscees/mastodon-bot

## RSSBOT
 RSS Bot for Enlightened.Army a Mastodon community
 - Official Site: https://github.com/mpoletiek/mastodon_rss_bot
 - Official RSS List: https://github.com/mpoletiek/mastodon_rss_bot/blob/main/rss_list.csv
 - Official Feed: https://enlightened.army/@rssbot

## DEPENDENCIES
```
import requests, datetime, time
import os, re, json, csv
import feedparser
from mastodon import Mastodon
from datetime import datetime
import hcmastodonlib
import tokenlib_public
```

## RUNNING
`./run.sh`
Edit run.sh to adjust sleep to increase or decrease interval.

## MASTODON AUTH
as you can probably guess:
tokens are storen in `tokenlib_public.py`

## NOTES 
 This script depends on 2 files
 1. `rss_list.csv` is a list of rss feeds, one on each line
 2. `rssbot_last_run.txt` is a file the bot uses to keep track of RSS updates. The bot will create the file if it doesn't exist.

## Live Examples
Here are some bots you can follow today.
 1. [@technewsbot](https://enlightened.army/@technewsbot)
 2. [@enewsbot](https://enlightened.army/@enewsbot)
 3. [@biznewsbot](https://enlightened.army/@biznewsbot)
