#!/usr/bin/env python
"""Bookmark migrator between Readability and GetPocket (formerly ReadItLater)
"""

import readability
import marshal
import os
import readitlater

# Import config file
from config import *

oauth_tokens = {}
conn = None

if os.path.exists('secretdb.dat'):
    if DEBUG:
        print "Secret DB exists.. reading token from there"

    ot_file = open('secretdb.dat', 'rb')
    oauth_tokens = marshal.load(ot_file)
    if DEBUG_SECRETS:
        print "Read OAuth Tokens from DB", oauth_tokens
    ot_file.close()

    xauth_token = oauth_tokens[USERNAME]

    print "Connecting to Readability..."
    conn = readability.oauth(CONSUMER_KEY, CONSUMER_SECRET, token=xauth_token)
    if DEBUG:
        if conn is None:
            print "Unable to connect to readability with local tokens"
        else:
            print "Connection to Readability created...", conn


if conn is None:
    if DEBUG:
        print "Requesting new tokens form Readability"

    xauth_token = readability.xauth(CONSUMER_KEY, CONSUMER_SECRET, USERNAME,
        PASSWORD)
    if DEBUG_SECRETS:
        print "Got XAuth Token", xauth_token

    print "Connecting to Readiability..."
    conn = readability.oauth(CONSUMER_KEY, CONSUMER_SECRET, token=xauth_token)
    if DEBUG:
        print "Connection to Readability created...", conn

    if conn.token_tuple:
        if DEBUG:
            print "Storing OAuth tokens to secret DB"
        oauth_tokens[USERNAME] = conn.token_tuple
        ot_file = open('secretdb.dat', 'wb')
        marshal.dump(oauth_tokens, ot_file)


if conn is None:
    print "We are unable to authenticate to readability"
    import sys
    sys.exit()


print "The loggedin username"
print conn.get_me()

# Get readability bookmarks
print "Getting bookmarks from readability..."
bookmarks = conn.get_bookmarks()

# Connect to GetPocket
gp_conn = readitlater.API(GETPOCKET_API_KEY, GETPOCKET_USERNAME,
        GETPOCKET_PASSWORD)

print "Getting GetPocket Status..."
print gp_conn.status()

# List to hold the bookmarks in single batch
readitlater_batch = []

print "Adding bookmarks to GetPockets..."
for mark in bookmarks:
    item = {}
    item['url'] = mark.article.url
    item['title'] = mark.article.title
    readitlater_batch.append(item)
    if len(readitlater_batch) >= 10:
        print "Adding batch of 10 urls to GetPocket"
        gp_conn.send(new=readitlater_batch)
        readitlater_batch = []

if readitlater_batch:
    print "Add batch of %d urls to GetPocket" % len(readitlater_batch)
    gp_conn.send(new=readitlater_batch)

print "Completed the copying of bookmarks from Readability to GetPocket"
