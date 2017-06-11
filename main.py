import configparser
import sys
import os
from json.decoder import JSONDecodeError

import spotipy
import spotipy.util as util

# Check username parameter
if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print("Usage: %s username" % (sys.argv[0],))
    sys.exit(1)

# Check config file existence
if not os.path.isfile("config.ini"):
    print("Did you forget to create config.ini file?")
    sys.exit(1)


config = configparser.ConfigParser()
config.read("config.ini")

# Check config content
try:
    client_id = config["credentials"]["client_id"]
    client_secret = config["credentials"]["client_secret"]
    redirect_uri = config["credentials"]["redirect_uri"]
except KeyError:
    print("config.ini file has corrupted. Please create new one from config.ini.example.")
    sys.exit(1)

# Get token
scope = "user-library-modify"
try:
    token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)
except (AttributeError, JSONDecodeError):
    # Why are we deleting cache? What is wrong?
    # https://github.com/plamere/spotipy/issues/176
    os.remove(f".cache-{username}")
    token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)

if not token:
    print(f"Can't get token for {username}, username or credentials might be wrong.")
    sys.exit(1)

sp = spotipy.Spotify(auth=token)
sp.trace = False
username = sp.me()["id"]

playlists, counter, done = [], 0, False
while not done:
    response = sp.current_user_playlists(offset=counter * 50, limit=50)
    playlists.extend(response["items"])
    done = not response["next"]
    counter += 1

playlists = [pl for pl in playlists if pl["owner"]["id"] == username]

# TODO: Choose playlist via simple interface

for pl in playlists:
    uri = pl["uri"]
    playlist_id = uri.split(':')[4]

    # TODO: Get all tracks (pagination)
    tracks = sp.user_playlist(username, playlist_id)

    # TODO: Find duplicates
    # TODO: Show duplicates to user and request approval
    # TODO: Delete duplicates
