# Written by Rudy Pikulik 07/17

import praw
import pickle
import time
from Structures.Queue import Queue
import garlicbot
from datetime import datetime

print("Starting up the bots!")

with open('id.txt','r') as f:
    reddit = praw.Reddit(client_id=f.readline()[:-1],
                      client_secret=f.readline()[:-1],
                      user_agent='garlicbot v0.1',
                      username='garlicbot',
                      password=f.readline()[:-1])

# This defines the domain from which to collect comments. "all" for all comments.
sub = reddit.subreddit("all")

def start_stream():
    comments = sub.stream.comments()
    for comment in comments:
        if garlicbot.validate_comment(comment):
            queue = pickle.load(open(garlicbot.file, 'rb'))
            if queue:
                queue.enqueue(comment.id)
            else:
                queue = Queue()
                queue.enqueue(comment.id)
            pickle.dump(queue, open(garlicbot.file, 'wb'))
            timestr = str(time.localtime()[3]) + ":" + str(time.localtime()[4])
            print("> %s - Added comment to queue! Queue length: %s" % (timestr, len(queue)))


while True:
    try:
        print('Starting comment stream at %s' % (datetime.now()))
        start_stream()
    except Exception as e:
        print("> %s - Connection lost. Restarting in 3 seconds... %s" % (datetime.now(), e))
        time.sleep(3)
        continue
