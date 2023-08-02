#!/usr/bin/python3

def whattokenswehave():
	tokenlist=["enlightened.army"]
	return tokenlist

def getmytokenfor(Mastodon_server):
    if Mastodon_server == "enlightened.army":
        tokendict={
        "host_instance": 'https://enlightened.army',
        "pa_token": "-----------",  ## create tokens yourselfin your mastodon profile
        "botname": "botname"}
    return tokendict

def getRedisPassword():
     redisPassword = 'password'
     return redisPassword

