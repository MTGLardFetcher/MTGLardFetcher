#!/usr/bin/python

import praw
import re
import sys
import time
import random
import sqlite3
import os
from tendo import singleton

conn = sqlite3.connect('state.sqlite')
cursor = conn.cursor()
persistence = True

def check_condition(c):
    text = c.body
    matches = get_matches(text)
    comment_id =  c.id
    comment_author = str(c.author)
    cursor.execute('SELECT comment_id FROM replied WHERE comment_id=?', (c.id, ))
    already_replied = cursor.fetchone()

    print "checking comment " + comment_id + " matches " + str(matches) + " replied " + str(already_replied)

    # don't reply twice and never reply to own comment to prevent possible loops
    if matches and already_replied is None and c.author is not 'MTGLardFetcher':
        return matches
    else:
        return False

def get_matches(text):
    matches = re.findall(r'\[\[([^\[\]]*?)\]\]', text)
    #matches = re.findall(r'\[\[(.*?)\]\]', text)
    return matches

def get_links(r):
    subreddit = r.get_subreddit('MTGLardFetcher')
    candidates = []
    for post in subreddit.get_hot(limit=15):
        if not "/r/MTGLardFetcher" in post.url:
            candidates.append(post.url)

    print "refreshed candidate list:"
    for c in candidates:
        print c

    return candidates        
        

def bot_action(c, matches, links, respond=False):

    text = "^(Probably totally what you linked)\n\n"

    for m in matches:
        print m
        link = random.choice(links)
        text += " * [" +m+ "]("+ link + ")\n"


    text += " "
    text += "\n"
    text += "\n"
    text += "*********\n\n"
    text += """^^^If ^^^WotC ^^^didn't ^^^do ^^^anything ^^^wrong ^^^this ^^^week, 
            ^^^you ^^^can ^^^rage ^^^at ^^^this ^^^bot ^^^instead ^^^at
            ^^^/r/MTGLardFetcher ^^^or ^^^even ^^^submit ^^^some ^^^of 
            ^^^the ^^^sweet ^^^Siege ^^^Rhino ^^^alters ^^^your ^^^GF ^^^made\n"""
    print text

    if respond:
        c.reply(text)
        cursor.execute('insert into replied (comment_id) values (?)', (c.id, ))
        conn.commit()


if __name__ == '__main__':

    me = singleton.SingleInstance()

    cursor.execute('''CREATE TABLE IF NOT EXISTS replied (comment_id text)''')
    conn.commit()

    UA = 'MTGLardFetcher, a MTGCardFetcher Parody bot for /r/magicthecirclejerking. Kindly direct complaints to /u/0x2a'
    r = praw.Reddit(UA)

    r.set_oauth_app_info(client_id=os.getenv('CLIENT_ID'), 
            client_secret=os.getenv('CLIENT_SECRET'), 
            redirect_uri='http://127.0.0.1:666/authorize_callback') 
    r.refresh_access_information(os.getenv('REFRESH_TOKEN'))

    # get initial auth and refresh token, then paste the refresh token into refresh_access_information() 
    #url = r.get_authorize_url('xxx1238', ['submit', 'read'] , True)
    #print url
    #access_information = r.get_access_information('access token from redirect above')
    #print access_information
    #add refresh token to ENV

    last_refresh = int(time.time())
    links = get_links(r)


    for c in praw.helpers.comment_stream(r, 'magicthecirclejerking'):
        matches = check_condition(c)
        if matches:    
            now = int(time.time()) 
            if (now - last_refresh > 60): 
                links = get_links(r)
                last_refresh = now
            bot_action(c, matches, links, True)

    conn.close()
