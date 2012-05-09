#!/usr/bin/env python
"""Bookmark migrator between Readability and GetPocket (formerly ReadItLater)
"""

import readability
import marshal
import os

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


print conn.get_me()

bookmarks = conn.get_bookmarks()

print bookmarks
bookmark = bookmarks[0]
print bookmark
print dir(bookmark)
