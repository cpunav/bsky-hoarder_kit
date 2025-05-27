# from mastodon import Mastodon
import json
import argparse
from atproto import *
from tqdm import tqdm
from collections import OrderedDict

parser = argparse.ArgumentParser(prog="Get user relationships", description="This program parses trough a user json file and gets all relationships")

parser.add_argument("-i", "--input", help ="Name for the input file", required=True)
parser.add_argument("-o", "--output", help ="Name for the output file", default="")

args = parser.parse_args()

input = args.input

if "." not in input:
    input = input + ".json"

with open('tokens/bsky-hoarder_kit_session_string', 'r') as file:
    session_string = file.read()

client = Client()
client.login(session_string=session_string)

f = open(input)

document = json.load(f)

all_relationships = []

checked_users = { document["profile"]["did"]: document["profile"] }

iterable_users = OrderedDict()

for followed in document["following"]:
    iterable_users[followed["did"]] = followed

for follower in document["followers"]:
    iterable_users[follower["did"]] = follower

try:
    for user in tqdm(iterable_users.values()):
        user_relationships = []

        did_list = list(checked_users.keys())
        
        for i in range(0, len(did_list), 30):
            reduced_list = did_list[i: min(i + 30, len(did_list))]

            result = client.app.bsky.graph.get_relationships(params={"actor":user["did"], "others":reduced_list})

            for relationship in result.relationships:

                if relationship.following is not None:
                    user_relationships.append({"statusAuthor": document["profile"], "from": user, "to": checked_users[relationship.did], "type": "follow"})

                if relationship.followed_by is not None:
                    user_relationships.append({"statusAuthor": document["profile"], "from": checked_users[relationship.did], "to": user, "type": "follow"})

        all_relationships.extend(user_relationships)

        checked_users[user["did"]] = user
except:
    pass

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
