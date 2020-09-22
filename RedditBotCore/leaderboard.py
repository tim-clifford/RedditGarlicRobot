# Created by Rudy Pikulik 04/17
# Forked by Tim Clifford 12/17
# Last updated 12/17
import praw
import pickle
from time import sleep
from collections import Counter

with open('id.txt','r') as f:
    rsr = praw.Reddit(client_id=f.readline()[:-1],
                      client_secret=f.readline()[:-1],
                      user_agent='garlicbot v0.1',
                      username='garlicbot',
                      password=f.readline()[:-1])

LEADERBOARD = rsr.submission("ixn388")

def edit(data,extradata):
    # Edits the leaderboard with counted data

    counted_dict = Counter(sum((y*[x] for x,y in extradata[1]),[]) + [x[1][1] for x in data])
    counted = sorted([(y,x) for (x,y) in counted_dict.items() if x != None and y != None], reverse=True)
    leaderboard = f"\
Here is the !redditgarlic leaderboard, updated every 15 minutes. \
Total garlic given: {extradata[0] + sum(counted_dict.values())}\n\n"
    leaderboard += "\n\n".join(
            f"{i+1}: {y} - {x} garlic" for i,(x,y) in enumerate(counted[:100])
    )
    try:
        LEADERBOARD.edit(leaderboard)
    except Exception as edit_exception:
            print(edit_exception)

if __name__ == '__main__':
    while True:
        data = pickle.load(open("RSRData.p", "rb"))
        extradata = pickle.load(open("ExtraData.p","rb"))
        edit(data,extradata)
        sleep(15*60)
