#!/usr/local/bin/python3.7
"""
Mousikegram -- A Telegram bot that translates links between music streaming services.
Copyright (C) 2019 Luciano E. Laratelli

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

# python libraries
import logging
import re
import urllib.request
from bs4 import BeautifulSoup

# /python libraries

# telegram bot library
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

# /telegram bot library

# spotipy
import spotipy
import spotipy.util as util

# /spotipy

# API secrets and other garbage
from config import SP_CLIENT_ID, SP_CLIENT_SECRET, TELEGRAM_SECRET

# /API secrets and other garbage

url_regex = re.compile(
    r"^(?:http|ftp)s?://"  # http:// or https://
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
    r"localhost|"  # localhost...
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
    r"(?::\d+)?"  # optional port
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)

token = util.oauth2.SpotifyClientCredentials(
    client_id=SP_CLIENT_ID, client_secret=SP_CLIENT_SECRET
)

cache_token = token.get_access_token()
spotify = spotipy.Spotify(cache_token)


def read(bot, update):
    potential_link = update.message.text
    is_link = re.match(url_regex, potential_link)
    if is_link is not None:
        track_info = spotify.track(potential_link)
        track_name = track_info["name"]
        track_artist = track_info["artists"][0]["name"]
        track_album = track_info["album"]["name"]
        output_string = f"Your link is the song {track_name} from the album {track_album} by the artist {track_artist}\n"
        textToSearch = f"{track_name} {track_artist}"
        if(track_name == track_artist):
            textToSearch += "SINGLE"
        query = urllib.parse.quote(textToSearch)
        url = "https://www.youtube.com/results?search_query=" + query
        response = urllib.request.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html, "html.parser")
        for vid in soup.findAll(attrs={"class": "yt-uix-tile-link"}):
            output_string += f"Youtube Link: https://www.youtube.com{vid['href']}\n"
            break
        bot.send_message(chat_id=update.message.chat_id, text=output_string)


updater = Updater(token=TELEGRAM_SECRET)
dispatcher = updater.dispatcher
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

read_handler = MessageHandler(Filters.text, read)
dispatcher.add_handler(read_handler)

updater.start_polling()
