import json
import argparse

parser = argparse.ArgumentParser(prog="Search statuses", description="This program parses trough a statuses json list and creates a Pajek graph file")

parser.add_argument("-i", "--input", help ="Name for the input file", required=True)
parser.add_argument("-o", "--output", help ="Name for the output file", default="")

args = parser.parse_args()

input = args.input

if "." not in input:
    input = input + ".json"

f = open(input)

relationships = json.load(f)

vertices = {}

arcs = []

for relationship in relationships:
    if relationship["from"]["did"] not in vertices:
        vertices[relationship["from"]["did"]] = {"handle": relationship["from"]["handle"], "color": "green"}
    if relationship["to"]["did"] not in vertices:
        vertices[relationship["to"]["did"]] = {"handle": relationship["to"]["handle"], "color": "green"}
    vertices[relationship["statusAuthor"]["did"]] = {"handle": relationship["statusAuthor"]["handle"], "color": "red"}
    arcColor = ""
    if relationship["type"] == "repost":
        arcColor = "emerald"
    elif relationship["type"] == "mention":
        arcColor = "fuchsia"
    elif relationship["type"] == "reply":
        arcColor = "royalblue"
    elif relationship["type"] == "quote":
        arcColor = "indigo"
    else:
        arcColor = "blue"
    arcs.append({"from": relationship["from"]["did"], "to": relationship["to"]["did"] , "color": arcColor})

output = args.output

if "" == output:
    dotPos = input.rfind('.')
    if dotPos < 0:
        output = input + ".net"
    elif dotPos == 0:
        output = ".net"
    else:
        output = input[:dotPos] + ".net"

if "." not in output:
    output = output + ".net"

f = open(output, "w")

f.write("*vertices " + str(len(vertices)) + "\n")

i = 1

for vertice in vertices.values():
    f.write(str(i) + " \"" + vertice["handle"] + "\" ")
    f.write("ic " + vertice["color"] + " bc black\n")
    vertice["index"] = i
    i += 1

f.write("*arcs\n")

for arc in arcs:
    fr = str(vertices[arc["from"]]["index"])
    to = str(vertices[arc["to"]]["index"])
    f.write(fr + " " + to + " 1 c " + arc["color"] + "\n")