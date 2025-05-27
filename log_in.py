import os
from atproto import Client

client = Client()

if not os.path.isdir('tokens'):
    os.mkdir('tokens')

login = ''
password = ''
while login == '':
    print("What's your login?: ")
    login = input('--> ').strip()

while password == '':
    print("And your password?: ")
    password = input('--> ').strip()

client.login(login, password)

with open('tokens/bsky-hoarder_kit_session_string', "w") as outfile: 
    outfile.write(client.export_session_string())
