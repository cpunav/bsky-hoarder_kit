# from mastodon import Mastodon
import json
import argparse
import time
from atproto import *

import atexit


def check_positive(value):
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue


parser = argparse.ArgumentParser(prog="Search posts", description="This program searches posts given a text prompt in real time. Exit the program (Ctrl + C) to end the fetch and save to a json file")

parser.add_argument('query', help="The search query that will get posts")
parser.add_argument("-o", "--output", help ="Name for the output file (default is posts.json)", default="")
parser.add_argument("-t", "--time", help ="The amount of time (in seconds) between refreshes of the query", type=check_positive, default=60)

args = parser.parse_args()

with open('tokens/bsky-hoarder_kit_session_string', 'r') as file:
    session_string = file.read()

client = Client()
client.login(session_string=session_string)

posts = {}

def exit_handler():
    statusList = list(posts.values())

    print("Found " + str(len(statusList)) + " total posts")

    output = args.output
    if output == "":
        output = args.query.replace(" ", "_") + ".json"

    if "." not in output:
        output = output + ".json"

    with open(output, "w") as outfile: 
        json.dump(statusList, outfile, default=str)

atexit.register(exit_handler)

result = client.app.bsky.feed.search_posts(params={"q":args.query}).posts

if len(result) > 0:
    lastStamp = result[0].record.created_at
else:
    lastStamp = "0"

while True:
    time.sleep(args.time)
    print("fetching posts...")
    result = client.app.bsky.feed.search_posts({"q":args.query, "since":lastStamp}).posts
    count = 0
    for post in result:
        if post.record.created_at > lastStamp:
            posts[post.cid] = post
            count += 1
    print("Found " + str(count) + " posts")
    if len(result) > 0:
        lastStamp = result[0].record.created_at
