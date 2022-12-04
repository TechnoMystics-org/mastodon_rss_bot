# rssbot.py
A mastodon rss bot

## AUTHOR 
 RSSBOT by @mpoletiek
 https://enlightened.army/@mpoletiek
## CREDITS 
 - https://github.com/hanscees/mastodon-bot

## RSSBOT
 RSS Bot for Enlightened.Army a Mastodon community
 - Official Site: 
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
