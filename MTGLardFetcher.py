#!/usr/bin/env python

import praw
import re
import sys
import time
import random
import sqlite3
import os
from tendo import singleton
import sys
import pprint
import importlib


importlib.reload(sys)
#sys.setdefaultencoding('utf-8')

conn = sqlite3.connect('state.sqlite')
cursor = conn.cursor()
persistence = True


def check_condition(c, r):
    pp = pprint.PrettyPrinter(indent=4)
    text = c.body
    matches = get_matches(text)
    comment_id =  c.id
    comment_author = str(c.author)
    cursor.execute('SELECT comment_id FROM replied WHERE comment_id=?', (c.id, ))
    already_replied = cursor.fetchone()
    holytopic = 'Weekly /unjerk Thread' 

    #print "checking comment in thread " + pp.pformat(vars(c)) + " -- " + comment_id + " matches " + str(matches) + " replied " + str(already_replied)
    #print "checking comment in thread -" + c.link_title + "-:" + holytopic +  ": -- " + comment_id + " matches " + str(matches) + " replied " + str(already_replied)

    print(f"{comment_id} {comment_author} {already_replied} {matches}")

    # don't reply twice and never reply to own comment to prevent possible loops
    if (matches and 
        already_replied is None and 
        c.author != 'MTGLardFetcher' and 
        c.link_title != holytopic):

        print("replying to unanswered comment " + comment_id)
        return matches
    else:
        print("ignoring answered/uneligible comment " + comment_id)
        return False

def get_matches(text):
    matches = re.findall(r'\[\[([^\[\]]*?)\]\]', text)
    #matches = re.findall(r'\[\[(.*?)\]\]', text)
    return matches

def get_links(r):
    #subreddit = r.get_subreddit('MTGLardFetcher')
    subreddit = r.subreddit('MTGLardFetcher')
    candidates = ['http://i.imgur.com/66Knlyo.png'] # pot of greed is always an option
    #candidates = ['https://i.redd.it/4f1qxxl3dqc21.png'] # bleep bleep
    for post in subreddit.hot(limit=50):
        if not "/r/MTGLardFetcher" in post.url:
            # allow only serious domains 
            if re.search('(i.redd.it|i.imgur.com)', post.url):
                candidates.append(post.url)
                print("cool domain approved by MARO", post.url)
            else:
                print("shitty domain excluded by speculators", post.url)

    print("refreshed candidate list:")
    for c in candidates:
        print(c)

    return candidates        
        

def bot_action(c, matches, links, respond=False):

    text = "^(Probably totally what you linked)\n\n"

    for m in matches:
        #print m
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
    #print text

    if respond:
        try:
            c.reply(text)
        except praw.errors.APIException:
            print("TOO_OLD or some other crap, going on")
        finally: 
            cursor.execute('insert into replied (comment_id) values (?)', (c.id, ))
            conn.commit()


if __name__ == '__main__':

    me = singleton.SingleInstance()

    cursor.execute('''CREATE TABLE IF NOT EXISTS replied (comment_id text)''')
    conn.commit()

    UA = 'MTGLardFetcher, a MTGCardFetcher Parody bot for /r/magicthecirclejerking. Kindly direct complaints to /u/0x2a'
    #r = praw.Reddit(UA)

    r = praw.Reddit( user_agent=UA, 
            client_id=os.getenv('CLIENT_ID'),
            client_secret=os.getenv('CLIENT_SECRET'),
            refresh_token=os.getenv('REFRESH_TOKEN')
            )
    

    last_refresh = int(time.time())
    links = get_links(r)

    #target = '0x2a_personal' 
    target = 'magicthecirclejerking' 

    for c in r.subreddit(target).stream.comments():
        matches = check_condition(c, r)
        if matches:    
            now = int(time.time()) 
            if (now - last_refresh > 60): 
                links = get_links(r)
                last_refresh = now

            bot_action(c, matches, links, True)

    conn.close()
