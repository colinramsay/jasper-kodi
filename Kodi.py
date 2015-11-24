# -*- coding: utf-8-*-
import random
import re
import os
import logging
from client import jasperpath
from xbmcjson import XBMC, PLAYER_VIDEO

WORDS = ["SWITCH", "ON", "OFF", "TV", "PLAY"]
LOGGER = logging.getLogger(__name__)
xbmc = XBMC("http://pi.local:8080/jsonrpc")

def play(item):
    print item
    players = xbmc.Player.GetActivePlayers()
    xbmc.Playlist.Clear({ "playlistid": 0 })
    xbmc.Playlist.Add({ "playlistid": 0, "item": item})
    xbmc.Player.Open({ "item": { "playlistid": 0, "position": 0 }})

def play_latest_episode(showid):
    raw = xbmc.VideoLibrary.GetEpisodes({ "tvshowid": showid, "properties": ["lastplayed"], "sort": {"method": "episode"} })

    episodes = raw['result']['episodes']

    for ep in episodes:
        if not ep['lastplayed']:
            latest = ep
            break

    if ep:
        play({ "episodeid": ep['episodeid'] })
    else:
        print 'No episodes'

def search_latest_tv(term):
    raw = xbmc.VideoLibrary.GetTVShows({ "filter": {"field": "title", "operator": "contains", "value": term}})

    print raw
    albums = raw['result']['tvshows']

    print 'Got shows'

    for album in albums:
        if term.lower() in album['label'].lower():
            showid = album['tvshowid']
            break

    if showid:
        print 'Found show'
        play_latest_episode(showid)

    return None


def play_album(term):
    albums = xbmc.AudioLibrary.GetAlbums()['result']['albums']

    for album in albums:
        if term.lower() in album['label'].lower():
            play({ "albumid": album['albumid'] })

    return None

def switch_on():
    os.system("""ssh pi 'echo "on 0" | cec-client -s'; ssh pi 'echo "as" | cec-client -s'""")

def switch_off():
    os.system("""ssh pi 'echo "standby 0" | cec-client -s'""")

def handle(text, mic, profile):
    text = text.upper()
    if "TV OFF" in text:
        LOGGER.info("Switching TV off")
        switch_off()
    elif "TV ON" in text:
        LOGGER.info("Switching TV on")
        switch_on()
    elif "PLAY ALBUM" in text:
        print "playing album..."
        play_album(text.replace("PLAY ALBUM ", ""))
    elif "PLAY LATEST" in text:
        print "playing latest..."
        search_latest_tv(text.replace("PLAY LATEST ", ""))

def isValid(text):
    tv = bool(re.search(r'\btv off|on\b', text, re.IGNORECASE))
    album = bool(re.search(r'\bplay album\b', text, re.IGNORECASE))
    epi = bool(re.search(r'\bplay latest\b', text, re.IGNORECASE))

    return tv or album or epi
