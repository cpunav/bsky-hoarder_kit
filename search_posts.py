# from mastodon import Mastodon
import json
import argparse
from atproto import *
from tqdm import tqdm

def check_positive(value):
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue


parser = argparse.ArgumentParser(prog="Search posts", description="This program searches posts given a text prompt")

parser.add_argument('query', help="The search query that will get posts")
parser.add_argument("-o", "--output", help ="Name for the output file (default is posts.json)", default="")
parser.add_argument("-q", "--quantity", help ="The amount of posts that will be saved", type=check_positive, default="100")

args = parser.parse_args()

with open('tokens/bsky-hoarder_kit_session_string', 'r') as file:
    session_string = file.read()

client = Client()
client.login(session_string=session_string)

all_posts = {}

cursor = None

until = None

lastDate = None

pbar = tqdm(total=args.quantity)
try:
    while len(all_posts) < args.quantity:
        result = client.app.bsky.feed.search_posts(params={"q":args.query, "cursor":cursor, "until":until, "limit": 100})

        cursor = result.cursor

        pbar.update(len(result.posts))

        for post in result.posts:
            if args.since is None or args.since <= post.indexed_at:
                all_posts[str(post.cid)] = post.model_dump()
                lastDate = post.indexed_at
            else:
                until = lastDate

        if len(result.posts) == 0 or cursor is None:
            if until == lastDate:
                break
            else:
                until = lastDate
except:
    pass

all_posts = list(all_posts.values())

if len(all_posts) > args.quantity:
    all_posts = all_posts[:args.quantity]

print("")
print("Found " + str(len(all_posts)) + " posts")

# print(list(map(lambda status: status.id, posts)))

output = args.output
if output == "":
    output = args.query.replace(" ", "_") + ".json"

if "." not in output:
    output = output + ".json"

with open(output, "w") as outfile: 
    json.dump(all_posts, outfile, default=str)

