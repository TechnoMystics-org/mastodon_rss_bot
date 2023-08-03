#!/usr/bin/python3

def whattokenswehave():
	tokenlist=["enlightened.army"]
	return tokenlist

def getmytokenfor(Mastodon_server):
    if Mastodon_server == "enlightened.army":
        tokendict={
        "host_instance": 'https://enlightened.army',
        "pa_token": "---",  ## create tokens yourselfin your mastodon profile
        "botname": "enewsbot"}
    return tokendict

def getRedisVariables():
     redis_variables = {'password':'---',
                        'host':'localhost',
                        'port':6379}
     return redis_variables

def getCSVUrl():
    csv_url="https://raw.githubusercontent.com/TechnoMystics-org/ea_rss_bot_feeds/main/enews_rss.csv"
    return csv_url