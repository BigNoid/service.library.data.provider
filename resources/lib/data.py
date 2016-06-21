#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2012 Team-XBMC
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#    This script is based on service.skin.widgets
#    Thanks to the original authors

import sys
import xbmc
import xbmcgui
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson


def get_playlist_stats(path):
    WINDOW = xbmcgui.Window(10000)
    if ("activatewindow" in path) and ("://" in path) and ("," in path):
        if ("\"" in path):
            # remove &quot; from path (gets added by favorites)
            path = path.translate(None, '\"')
        playlistpath = path.split(",")[1]
        json_query = xbmc.executeJSONRPC('''{"jsonrpc": "2.0", "method": "Files.GetDirectory",
                                             "params": {"directory": "%s", "media": "video",
                                             "properties": ["playcount",
                                                            "resume",
                                                            "episode",
                                                            "watchedepisodes",
                                                            "tvshowid"]},
                                             "id": 1}''' % (playlistpath))
        json_response = simplejson.loads(json_query)
        if "result" not in json_response:
            return None
        if "files" not in json_response["result"]:
            return None
        played = 0
        numitems = 0
        inprogress = 0
        episodes = 0
        watchedepisodes = 0
        tvshows = []
        tvshowscount = 0
        if "files" in json_response["result"]:
            for item in json_response["result"]["files"]:
                if "type" not in item:
                    continue
                if item["type"] == "episode":
                    episodes += 1
                    if item["playcount"] > 0:
                        watchedepisodes += 1
                    if item["tvshowid"] not in tvshows:
                        tvshows.append(item["tvshowid"])
                        tvshowscount += 1
                elif item["type"] == "tvshow":
                    episodes += item["episode"]
                    watchedepisodes += item["watchedepisodes"]
                    tvshowscount += 1
                else:
                    numitems += 1
                    if "playcount" in item.keys():
                        if item["playcount"] > 0:
                            played += 1
                        if item["resume"]["position"] > 0:
                            inprogress += 1
        WINDOW.setProperty('PlaylistWatched', str(played))
        WINDOW.setProperty('PlaylistCount', str(numitems))
        WINDOW.setProperty('PlaylistTVShowCount', str(tvshowscount))
        WINDOW.setProperty('PlaylistInProgress', str(inprogress))
        WINDOW.setProperty('PlaylistUnWatched', str(numitems - played))
        WINDOW.setProperty('PlaylistEpisodes', str(episodes))
        WINDOW.setProperty('PlaylistEpisodesUnWatched', str(episodes - watchedepisodes))
