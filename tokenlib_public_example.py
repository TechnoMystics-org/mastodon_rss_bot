#!/usr/bin/python3

def whattokenswehave():
	tokenlist=["example.com"]
	return tokenlist

def getmytokenfor(Mastodon_server):
    if Mastodon_server == "example.com":
        tokendict={
        "host_instance": 'https://example.com',
        "pa_token": "access_token",  ## create tokens yourselfin your mastodon profile
        "botname": "botname"}
    return tokendict

