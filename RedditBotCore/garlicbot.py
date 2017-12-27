# Created by Rudy Pikulik 04/17
# Last Updated 12/17
import praw
import pickle
import time
from Structures.Queue import Queue

with open('id.txt','r') as f:
    rsr = praw.Reddit(client_id=f.readline()[:-1],
                      client_secret=f.readline()[:-1],
                      user_agent='garlicbot v0.1',
                      username='garlicbot',
                      password=f.readline()[:-1])
file = 'RSRQueue.p'
command = '!redditgarlic'
banned_subs = ["slayone"]

def validate_comment(comment):
    # Decides whether or not to reply to a given comment.
    #    - Must contain command
    #    - Must not have already replied
    #    - Must not reply to self
    if command in comment.body.lower():
        queue = pickle.load(open(file, "rb"))
        if not queue:
            queue = Queue()
        data = pickle.load(open('RSRData.p', 'rb'))
        # Already in the queue, don't add.
        if queue.contains(comment.id) or comment.id in [x[0] for x in data]:
            return False
        # We wrote the comment, don't loop.
        if comment.author.name is "garlicbot":
            _register_comment(comment, "Cannot respond to self.")
            return False
        # Parent comment was deleted, don't respond.
        if get_receiver(comment) == '[deleted]':
            _register_comment(comment, "Parent comment was deleted!")
            return False
        # We've blacklisted this sub, don't respond.
        if comment.subreddit.display_name.lower() in banned_subs:
            _register_comment(comment, "Subreddit is blacklisted!")
            return False

        comment.refresh()
        for child_comment in comment.replies:
            if child_comment.author.name == "garlicbot":
                _register_comment(comment, "Already replied to this comment. Will not do it again.")
                return False
        return True
    return False


def reply(comment):
    # Makes a message and replies to the given comment.
    message = _make_message(comment)
    timestr = str(time.localtime()[3]) + ":" + str(time.localtime()[4])
    try:
        comment.reply(message)
        print("> %s - Posted: %s -> " % (timestr, comment.author.name) + get_receiver(comment))
        _register_comment(comment, "Posted!")
    except Exception as comment_exception:
        print(comment_exception)
        print("> %s - Unable to post comment: %s -> " % (timestr, comment.author.name) + get_receiver(comment))
        _register_comment(comment, "Unable to post. Reason: %s" % comment_exception)


def _register_comment(comment, result):
    # Stores data in a list of tuples
    # (ID, (User, Receiver, Time, Result))
    tup = (comment.id, (comment.author.name, get_receiver(comment), time.localtime(), result))
    data = pickle.load(open("RSRData.p", 'rb'))
    if data:
        data.append(tup)
    else:
        data = [tup]
    pickle.dump(data, open("RSRData.p", 'wb'))


def get_receiver(comment):
    #print(comment1.fullname)
    text = comment.body.lower().split()
    #text = ''
    try:
        # Kind of gross looking code below. Splits the comment exactly once at '!Redditgarlic',
        # then figures out if the very next character is a new line. If it is, respond to parent.
        # If it is not a new line, either respond to the designated person or the parent.
        split = comment.body.lower().split(command, 1)[1].replace(' ', '')
        if split[0] is "\n":
            try:
                receiver = comment.parent().author.name
            except AttributeError:
                receiver = '[deleted]'
        else:
            receiver = text[text.index(command) + 1]
    # An IndexError is thrown if the user did not specify a recipient.
    except IndexError:
        try:
            receiver = comment.parent().author.name
        except AttributeError:
            receiver = '[deleted]'
    # A ValueError is thrown if '!Redditgarlic' is not found. Example: !RedditgarlicTest would throw this.
    except ValueError:
        return None
    if '/u/' in receiver:
        receiver = receiver.replace('/u/', '')
    if 'u/' in receiver:
        receiver = receiver.replace('u/', '')
    if '/' in receiver:
        receiver = receiver.replace('/', '')
    # This line is to change the name from all lowercase.
        receiver = rsr.redditor(receiver).name
    return receiver

def _garlic_counter(comment):
    data_entries = pickle.load(open('RSRData.p', 'rb'))
    count = 0
    if data_entries:
        receiver = get_receiver(comment)
        for entry in [x[1][1] for x in data_entries]:
            if entry == receiver:
                count += 1
        return count+1
    else:
        return 1


def _make_message(comment):
    garlic_count = _garlic_counter(comment)
    if garlic_count == 1:
        s = ""
    else:
        s = "s"
    message = "[**Here's your Reddit Garlic, " + get_receiver(comment)
    message += "!**](http://i.imgur.com/dYGNvmR.jpg \"Reddit Garlic\") \n\n"
    message += "/u/" + get_receiver(comment) + " has received garlic " + str(garlic_count)
    message += " time%s. (given by /u/" % s
    message += comment.author.name + ") "
   # message += "__[info](http://reddit.com/r/RedditgarlicRobot)__" + comment.subreddit.display_name
    return message

if __name__ == '__main__':

    try:
        queue = pickle.load(open(file, "rb"))
    except EOFError and FileNotFoundError as e:
        print("queue startup: %s" % e)
        queue = Queue()
        pickle.dump(queue, open(file, 'wb'))

    try:
        __data = pickle.load(open("RSRData.p", "rb"))
    except EOFError and FileNotFoundError:
        __data = []
        pickle.dump(__data, open("RSRData.p", 'wb'))
    if __data:
        print("There are %s entries in data." % len(__data))
    else:
        print("Data is empty.")
    if queue:
        print("There are %s entries in the deque." % len(queue))
    else:
        print("Queue is empty.")
    while True:
        try:
            queue = pickle.load(open(file, 'rb'))
        except EOFError:
            queue = Queue()
        if queue and len(queue) > 0:
            comment_id = queue.dequeue()
            pickle.dump(queue, open(file, 'wb'))
            print(comment_id)
            comment = praw.models.Comment(rsr, comment_id)
            reply(comment)
