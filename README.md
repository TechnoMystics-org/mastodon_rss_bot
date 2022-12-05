# rssbot.py
A mastodon rss bot.

## AUTHOR 
 by @mpoletiek
 https://enlightened.army/@mpoletiek
 https://github.com/mpoletiek

## CREDITS 
 Major inspiration to be found below.
 - https://github.com/hanscees/mastodon-bot

## RSSBOT
 RSS Bot for Mastodon.
 - Official Site: https://github.com/mpoletiek/mastodon_rss_bot
 - Official RSS List: https://github.com/mpoletiek/mastodon_rss_bot/blob/main/rss_list.csv
 - Official Feed: https://enlightened.army/@rssbot

## DEPENDENCIES
```
import time, os, re, json, csv

from mastodon import Mastodon
from datetime import datetime
from dateutil import parser

import feedparser
import tokenlib_public
```

## MASTODON AUTH
as you can probably guess:
tokens are storen in `tokenlib_public.py`
You will need to create	this file first. Example can be	found in `tokenlib_public_example.py`
This is	where you set your bot name.

## RUNNING
`./run.sh`

Default is set to run every minute.
New posts are collected and tooted out every 20 seconds.

Edit `run.sh` to adjust sleep to increase or decrease interval.

## NOTES 
 This script depends on 2 files
 1. `rss_list.csv` is a list of rss feeds, one on each line
 2. `rssbot_last_run.txt` is a file the bot uses to keep track of RSS updates. The bot will create the file if it doesn't exist.

## Live Examples
Here are some bots you can follow today.
 1. [@technewsbot](https://enlightened.army/@technewsbot)
 2. [@enewsbot](https://enlightened.army/@enewsbot)
 3. [@biznewsbot](https://enlightened.army/@biznewsbot)
