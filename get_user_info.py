# from mastodon import Mastodon
import json
import argparse
from atproto import *

def get_followers(handle):
    followers = []
    cursor = None
    while True:
        result = client.app.bsky.graph.get_followers(params={"actor":handle, "limit":100, "cursor": cursor})

        followers.extend(result.followers)
        
        cursor = result.cursor

        if cursor is None:
            return followers

def get_follows(handle):
    follows = []
    cursor = None
    while True:
        result = client.app.bsky.graph.get_follows(params={"actor":handle, "limit":100, "cursor": cursor})

        follows.extend(result.follows)
        
        cursor = result.cursor

        if cursor is None:
            return follows

parser = argparse.ArgumentParser(prog="Get user info", description="This program gets information for a user")

parser.add_argument('query', help="The search query that will get the account")
parser.add_argument("-o", "--output", help ="Name for the output file (default is account.json)", default="")

args = parser.parse_args()

with open('tokens/bsky-hoarder_kit_session_string', 'r') as file:
    session_string = file.read()

client = Client()
client.login(session_string=session_string)

# result = mastodon.account_search(args.query)
result = client.app.bsky.actor.search_actors(params={"q": args.query})

if len(result.actors) > 1:
    print("Accounts found:")
    for x in range(0, len(result.actors) - 1):
        print("[" + str(x) + "] " + result.actors[x].handle)
    try:
        option = int(input('--> Enter desired account: '))
    except:
        pass
else:
    option = 0
    

profile = result.actors[option]


# print("Is followed by:")
followers = get_followers(profile.handle)

# for account in followers:
#     print(account.handle)

# print("Is following:")
following = get_follows(profile.handle)

# for account in following:
#     print(account.handle)

# print("Toots/Statuses:")
# statuses = mastodon.account_statuses(result[option].id)

# for status in statuses:
#     print(status.content)

outputDict = {
    "profile": profile.model_dump(),
    "followers": list(map(lambda user: user.model_dump(), followers)),
    "following": list(map(lambda user: user.model_dump(), following))
}

output = args.output
if output == "":
    output = args.query.replace(" ", "_") + ".json"

if "." not in output:
    output = output + ".json"

with open(output, "w") as outfile: 
    json.dump(outputDict, outfile, default=str)