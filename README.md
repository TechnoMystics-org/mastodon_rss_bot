# rssbot.py
A mastodon rss bot

## AUTHOR 
 RSSBOT by @mpoletiek
 https://enlightened.army/@mpoletiek

## CREDITS 
 - https://github.com/hanscees/mastodon-bot

## RSSBOT
 RSS Bot for Mastodon communities
 - Official Site: https://github.com/mpoletiek/mastodon_rss_bot
 - Official RSS List: 
 - https://enlightened.army/@rssbot

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
### See example `tokenlib_public_example.py`
Modify and cp to `tokenlib_public.py`
