# from mastodon import Mastodon
import json
import argparse
import typing as t
from atproto import *
from tqdm import tqdm

def get_reposts(uri):
    reposts: t.List['models.AppBskyActorDefs.ProfileView'] = []
    cursor = None
    while True:
        result = client.app.bsky.feed.get_reposted_by(params={"uri":uri, "limit":100, "cursor": cursor})

        reposts.extend(result.reposted_by)
        
        cursor = result.cursor

        if cursor is None:
            return reposts

def get_quotes(uri):
    quotes: t.List['models.AppBskyFeedDefs.PostView'] = []
    cursor = None
    while True:
        result = client.app.bsky.feed.get_quotes(params={"uri":uri, "limit":100, "cursor": cursor})

        quotes.extend(result.posts)
        
        cursor = result.cursor

        if cursor is None:
            return quotes

def process_thread(thread: 'models.AppBskyFeedDefs.ThreadViewPost'):
    if isinstance(thread.parent, models.AppBskyFeedDefs.ThreadViewPost):
        status_relationships[thread.post.cid + thread.parent.post.cid] = {"statusAuthor": post["author"], "from": thread.post.author.model_dump(), "to": thread.parent.post.author.model_dump(), "type": "reply"}
        process_thread(thread.parent)
    if thread.replies is not None:
        for reply in thread.replies:
            if isinstance(reply, models.AppBskyFeedDefs.ThreadViewPost):
                status_relationships[reply.post.cid + thread.post.cid] = {"statusAuthor": post["author"], "from": reply.post.author.model_dump(), "to": thread.post.author.model_dump(), "type": "reply"}
                process_thread(reply)

parser = argparse.ArgumentParser(prog="Get relationships from posts", description="This program parses trough a posts json list and gets all relationships")

parser.add_argument("-i", "--input", help ="Name for the input file", required=True)
parser.add_argument("-o", "--output", help ="Name for the output file", default="")
parser.add_argument("-t", "--type", help ="The type of relationships to be sought for (default is all)", default="all", choices=["reposts", "mentions", "replies", "quotes", "all"])

args = parser.parse_args()

input = args.input

if "." not in input:
    input = input + ".json"

with open('tokens/bsky-hoarder_kit_session_string', 'r') as file:
    session_string = file.read()

client = Client()
client.login(session_string=session_string)

f = open(input)

posts = json.load(f)

relationship_type = args.type

all_relationships = []

status_relationships = {}



try:
    for post in tqdm(posts):
        if (relationship_type in ["reposts" ,"all"]) & post["repost_count"] > 0:
            try:
                reposts = get_reposts(post["uri"])
                for repost in reposts:
                    all_relationships.append({"statusAuthor": post["author"], "from": repost.model_dump(), "to": post["author"], "type": "repost"})
            except:
                pass

        if relationship_type in ["mentions" ,"all"] and post["record"]["facets"] is not None:
            for facet in post["record"]["facets"]:
                for feature in facet["features"]:
                    if "did" in feature:
                        profile = client.app.bsky.actor.get_profile(params={"actor":feature["did"]})
                        all_relationships.append({"statusAuthor": post["author"], "from": post["author"], "to": profile.model_dump(), "type": "mention"})

        if relationship_type in ["replies" ,"all"]:
            if "reply" in post["record"] and post["record"]["reply"] is not None:
                root_uri = post["record"]["reply"]["root"]["uri"]
            elif post["reply_count"] > 0:
                root_uri = post["uri"]
            try:
                result = client.app.bsky.feed.get_post_thread(params={"uri":root_uri, "depth": 1000, "parent_height": 1000})
            except:
                pass
            else:
                process_thread(result.thread)

        if relationship_type in ["quotes" ,"all"]:
            try:
                if post["record"]["embed"] is not None:
                    embed = post["record"]["embed"]
                    if embed["py_type"] == "app.bsky.embed.recordWithMedia" and "record" in embed:
                        embed = embed["record"]
                    if embed["py_type"] == "app.bsky.embed.record" and "record" in embed and "uri" in embed["record"]:
                        result = client.app.bsky.feed.get_posts(params={"uris":[embed["record"]["uri"]]})
                        if len(result.posts) > 0:
                            quoted_post = result.posts[0]
                            status_relationships[post["cid"] + quoted_post.cid] = {"statusAuthor": post["author"], "from": post["author"], "to": quoted_post.author.model_dump(), "type": "quote"}
                if post["quote_count"] > 0:
                    quotes = get_quotes(post["uri"])
                    for quote in quotes:
                        status_relationships[quote.cid + post["cid"]] = {"statusAuthor": post["author"], "from": quote.author.model_dump(), "to": quoted_post.author.model_dump(), "type": "quote"}
            except:
                pass
except:
    pass
for relationship in status_relationships.values():
    all_relationships.append(relationship)

output = args.output

if "" == output:
    dotPos = input.rfind('.')
    if dotPos < 0:
        input + "_relationships.json"
    elif dotPos == 0:
        "relationships" + input
    else:
        output = input[:dotPos] + "_relationships" + input[dotPos:]

if "." not in output:
    output = output + ".json"

with open(output, "w") as outfile: 
    json.dump(all_relationships, outfile, default=str)
