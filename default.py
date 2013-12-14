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

import os
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import random
import urllib
from traceback import print_exc

if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

__addon__        = xbmcaddon.Addon()
__addonversion__ = __addon__.getAddonInfo('version')
__addonid__      = __addon__.getAddonInfo('id')
__addonname__    = __addon__.getAddonInfo('name')
__localize__    = __addon__.getLocalizedString

def log(txt):
    message = '%s: %s' % (__addonname__, txt.encode('ascii', 'ignore'))
    xbmc.log(msg=message, level=xbmc.LOGDEBUG)

class Main:
    def __init__(self):
        try:
            params = dict( arg.split( "=" ) for arg in sys.argv[ 2 ].split( "&" ) )
            self.TYPE = params.get( "?type", "" )
        except:
            params = {}
        self.LIMITOVERRIDE = params.get( "limit", "false" )
        if not self.LIMITOVERRIDE:
            self.LIMIT = int(self.LIMITOVERRIDE)
        else:
            self.LIMIT = int(__addon__.getSetting("limit"))

        self.init_property()
        if self.TYPE == "randommovies":
            self.fetch_movies( 'randommovies' )
        elif self.TYPE == "recentmovies":
            self.fetch_movies( 'recentmovies' )
        elif self.TYPE == "recommendedmovies":
            self.fetch_movies( 'recommendedmovies' )
        elif self.TYPE == "recommendedepisodes":
            self.fetch_tvshows_recommended( 'recommendedepisodes' )
        elif self.TYPE == "recentepisodes":
            self.fetch_tvshows( 'recentepisodes' )
        elif self.TYPE == "randomepisodes":
            self.fetch_tvshows( 'randomepisodes' )
        # TODO Need to find out how to play an album    
        #elif self.TYPE == "recentalbums":
        #    self.fetch_albums( 'recentalbums' )
        #elif self.TYPE == "randomalbums":
        #    self.fetch_albums( 'randomalbums' )
        elif self.TYPE == "randomsongs":
            self.fetch_song( 'randomsongs' )

    def fetch_movies(self, request):
        if not xbmc.abortRequested:
            json_string = '{"jsonrpc": "2.0",  "id": 1, "method": "VideoLibrary.GetMovies", "params": {"properties": ["title", "originaltitle", "votes", "playcount", "year", "genre", "studio", "country", "tagline", "plot", "runtime", "file", "plotoutline", "lastplayed", "trailer", "rating", "resume", "art", "streamdetails", "mpaa", "director"], "limits": {"end": %d},' % self.LIMIT
            if request == "randommovies" and self.RANDOMITEMS_UNPLAYED:
                json_query = xbmc.executeJSONRPC('%s "sort": {"method": "random" }, "filter": {"field": "playcount", "operator": "lessthan", "value": "1"}}}' %json_string)
                list_type = __localize__(32004)
            elif request == "randommovies":
                json_query = xbmc.executeJSONRPC('%s "sort": {"method": "random" } }}' %json_string)
                list_type = __localize__(32004)
            elif request == 'recentmovies' and self.RECENTITEMS_UNPLAYED:
                json_query = xbmc.executeJSONRPC('%s "sort": {"order": "descending", "method": "dateadded"}, "filter": {"field": "playcount", "operator": "is", "value": "0"}}}' %json_string)
                list_type = __localize__(32005)
            elif request == "recentmovies":
                json_query = xbmc.executeJSONRPC('%s "sort": {"order": "descending", "method": "dateadded"}, "filter": {"field": "playcount", "operator": "is", "value": "0"}}}' %json_string)
                list_type = __localize__(32005)
            elif request == "recommendedmovies":
                json_query = xbmc.executeJSONRPC('%s "sort": {"order": "descending", "method": "lastplayed"}, "filter": {"field": "inprogress", "operator": "true", "value": ""}}}' %json_string)
                list_type = __localize__(32006)
            json_query = unicode(json_query, 'utf-8', errors='ignore')
 
            json_query = simplejson.loads(json_query)
            if json_query.has_key('result') and json_query['result'].has_key('movies'):
                for item in json_query['result']['movies']:
                    if (item['resume']['position'] and item['resume']['total'])> 0:
                        resume = "true"
                        played = '%s%%'%int((float(item['resume']['position']) / float(item['resume']['total'])) * 100)
                    else:
                        resume = "false"
                        played = '0%'
                    if item['playcount'] >= 1:
                        watched = "true"
                    else:
                        watched = "false"
                    if not self.PLOT_ENABLE and watched == "false":
                        plot = __localize__(32014)
                    else:
                        plot = item['plot']
                    art = item['art']
                    #streaminfo = item['streamdetails']
                    #f = open(os.devnull, 'w')
                    #sys.stdout = f
                    votes = '(' + item['votes'] + ' ' + xbmc.getLocalizedString(20350) + ')'

                    # create a list item
                    liz = xbmcgui.ListItem(item['title'])
                    liz.setInfo( type="Video", infoLabels={ "Title": item['title'] })
                    liz.setInfo( type="Video", infoLabels={ "OriginalTitle": item['originaltitle'] })
                    liz.setInfo( type="Video", infoLabels={ "Year": item['year'] })
                    liz.setInfo( type="Video", infoLabels={ "Genre": " / ".join(item['genre']) })
                    liz.setInfo( type="Video", infoLabels={ "Studio": item['studio'][0] })
                    liz.setInfo( type="Video", infoLabels={ "Country": item['country'][0] })
                    liz.setInfo( type="Video", infoLabels={ "Plot": plot })
                    liz.setInfo( type="Video", infoLabels={ "PlotOutline": item['plotoutline'] })
                    liz.setInfo( type="Video", infoLabels={ "Tagline": item['tagline'] })
                    liz.setInfo( type="Video", infoLabels={ "Duration": item['runtime']/60 })
                    liz.setInfo( type="Video", infoLabels={ "Rating": str(float(item['rating'])) })
                    liz.setInfo( type="Video", infoLabels={ "Votes": votes })
                    liz.setInfo( type="Video", infoLabels={ "MPAA": item['mpaa'] })
                    liz.setInfo( type="Video", infoLabels={ "Director": " / ".join(item['director']) })
                    liz.setInfo( type="Video", infoLabels={ "Trailer": item['trailer'] })
                    liz.setInfo( type="Video", infoLabels={ "Playcount": item['playcount'] })
                    liz.setProperty("resumetime", str(item['resume']['position']))
                    liz.setProperty("totaltime", str(item['resume']['total']))
                    liz.setProperty("type", list_type)

                    liz.setThumbnailImage(art.get('poster', ''))
                    liz.setIconImage('DefaultVideoCover.png')
                    liz.setProperty("fanart_image", art.get('fanart', ''))
                    #for key, value in streaminfo.items():
                    #   try:
                    #        liz.addStreamInfo( key, value[0] )
                    #    except: f

                    for key, value in art.items():
                        try:
                            liz.setProperty( key, value )
                        except: print_exc()
                    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=item['file'],listitem=liz,isFolder=False)
            del json_query
            xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))
            
    def fetch_tvshows_recommended(self, request):
        if not xbmc.abortRequested:
            # First unplayed episode of recent played tvshows
            json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": {"properties": ["title", "studio", "mpaa", "file", "art"], "sort": {"order": "descending", "method": "lastplayed"}, "filter": {"field": "inprogress", "operator": "true", "value": ""}, "limits": {"end": %d}}, "id": 1}' %self.LIMIT)
            json_query = unicode(json_query, 'utf-8', errors='ignore')
            json_query = simplejson.loads(json_query)
            list_type = __localize__(32010)
            if json_query.has_key('result') and json_query['result'].has_key('tvshows'):
                count = 0
                for item in json_query['result']['tvshows']:
                    if xbmc.abortRequested:
                        break
                    count += 1
                    json_query2 = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": {"tvshowid": %d, "properties": ["title", "playcount", "plot", "season", "episode", "showtitle", "file", "lastplayed", "rating", "resume", "art", "streamdetails", "firstaired", "runtime"], "sort": {"method": "episode"}, "filter": {"field": "playcount", "operator": "is", "value": "0"}, "limits": {"end": 1}}, "id": 1}' %item['tvshowid'])
                    json_query2 = unicode(json_query2, 'utf-8', errors='ignore')
                    json_query2 = simplejson.loads(json_query2)
                    if json_query2.has_key('result') and json_query2['result'] != None and json_query2['result'].has_key('episodes'):
                        for item2 in json_query2['result']['episodes']:
                            episode = ("%.2d" % float(item2['episode']))
                            season = "%.2d" % float(item2['season'])
                            rating = str(round(float(item2['rating']),1))
                            art2 = item2['art']
                    if (item2['resume']['position'] and item2['resume']['total']) > 0:
                        resume = "true"
                        played = '%s%%'%int((float(item2['resume']['position']) / float(item2['resume']['total'])) * 100)
                    else:
                        resume = "false"
                        played = '0%'
                    if item2['playcount'] >= 1:
                        watched = "true"
                    else:
                        watched = "false"
                    if not self.PLOT_ENABLE and watched == "false":
                        plot = __localize__(32014)
                    else:
                        plot = item2['plot']
                    art = item['art']
                    liz = xbmcgui.ListItem(item['title'])
                    liz.setInfo( type="Video", infoLabels={ "Title": item2['title'] })
                    liz.setInfo( type="Video", infoLabels={ "Episode": item2['episode'] })
                    liz.setInfo( type="Video", infoLabels={ "Season": item2['season'] })
                    liz.setInfo( type="Video", infoLabels={ "Studio": item['studio'][0] })
                    liz.setInfo( type="Video", infoLabels={ "Premiered": item2['firstaired'][0] })
                    liz.setInfo( type="Video", infoLabels={ "Plot": plot })
                    liz.setInfo( type="Video", infoLabels={ "TVshowTitle": item2['showtitle'] })
                    liz.setInfo( type="Video", infoLabels={ "Duration": item2['runtime']/60 })
                    liz.setInfo( type="Video", infoLabels={ "Rating": str(float(item2['rating'])) })
                    liz.setInfo( type="Video", infoLabels={ "MPAA": item['mpaa'] })
                    liz.setInfo( type="Video", infoLabels={ "Playcount": item2['playcount'] })
                    liz.setProperty("resumetime", str(item2['resume']['position']))
                    liz.setProperty("totaltime", str(item2['resume']['total']))
                    liz.setProperty("type", list_type)

                    liz.setThumbnailImage(art2.get('thumb',''))
                    liz.setIconImage('DefaultTVShows.png')
                    liz.setProperty("fanart_image", art2.get('tvshow.fanart',''))
                    for key, value in art.items():
                        try:
                            liz.setProperty( key, value )
                        except: print_exc()
                    
                    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=item2['file'],listitem=liz,isFolder=False)
            del json_query
            xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))
            
    def fetch_tvshows(self, request):
        if not xbmc.abortRequested:
            json_string = '{"jsonrpc": "2.0", "id": 1, "method": "VideoLibrary.GetEpisodes", "params": { "properties": ["title", "playcount", "season", "episode", "showtitle", "plot", "file", "rating", "resume", "tvshowid", "art", "streamdetails", "firstaired", "runtime"], "limits": {"end": %d},' %self.LIMIT
            if request == 'recentepisodes' and self.RECENTITEMS_UNPLAYED:
                json_query = xbmc.executeJSONRPC('%s "sort": {"order": "descending", "method": "dateadded"}, "filter": {"field": "playcount", "operator": "lessthan", "value": "1"}}}' %json_string)
                list_type = __localize__(32008)
            elif request == 'recentepisodes':
                json_query = xbmc.executeJSONRPC('%s "sort": {"order": "descending", "method": "dateadded"}}}' %json_string)
                list_type = __localize__(32008)
            elif request == 'randomepisodes' and self.RANDOMITEMS_UNPLAYED:
                json_query = xbmc.executeJSONRPC('%s "sort": {"method": "random" }, "filter": {"field": "playcount", "operator": "lessthan", "value": "1"}}}' %json_string)
                list_type = __localize__(32007)
            else:
                json_query = xbmc.executeJSONRPC('%s "sort": {"method": "random" }}}' %json_string)
                list_type = __localize__(32007)
            json_query = unicode(json_query, 'utf-8', errors='ignore')
            json_query = simplejson.loads(json_query)
            if json_query.has_key('result') and json_query['result'].has_key('episodes'):
                count = 0
                for item in json_query['result']['episodes']:
                    count += 1
                    episode = ("%.2d" % float(item['episode']))
                    season = "%.2d" % float(item['season'])
                    rating = str(round(float(item['rating']),1))
                    if (item['resume']['position'] and item['resume']['total']) > 0:
                        resume = "true"
                        played = '%s%%'%int((float(item['resume']['position']) / float(item['resume']['total'])) * 100)
                    else:
                        resume = "false"
                        played = '0%'
                    if item['playcount'] >= 1:
                        watched = "true"
                    else:
                        watched = "false"
                    if not self.PLOT_ENABLE and watched == "false":
                        plot = __localize__(32014)
                    else:
                        plot = item['plot']
                    art = item['art']
                    #streaminfo = media_streamdetails(item['file'].encode('utf-8').lower(), item['streamdetails'])
                    liz = xbmcgui.ListItem(item['title'])
                    liz.setInfo( type="Video", infoLabels={ "Title": item['title'] })
                    liz.setInfo( type="Video", infoLabels={ "Episode": item['episode'] })
                    liz.setInfo( type="Video", infoLabels={ "Season": item['season'] })
                    #liz.setInfo( type="Video", infoLabels={ "Studio": item['studio'][0] })
                    liz.setInfo( type="Video", infoLabels={ "Premiered": item['firstaired'] })
                    liz.setInfo( type="Video", infoLabels={ "Plot": plot })
                    liz.setInfo( type="Video", infoLabels={ "TVshowTitle": item['showtitle'] })
                    liz.setInfo( type="Video", infoLabels={ "Duration": item['runtime']/60 })
                    liz.setInfo( type="Video", infoLabels={ "Rating": str(float(item['rating'])) })
                    #liz.setInfo( type="Video", infoLabels={ "MPAA": item['mpaa'] })
                    liz.setInfo( type="Video", infoLabels={ "Playcount": item['playcount'] })
                    liz.setProperty("resumetime", str(item['resume']['position']))
                    liz.setProperty("totaltime", str(item['resume']['total']))
                    liz.setProperty("type", list_type)

                    liz.setThumbnailImage(art.get('thumb',''))
                    liz.setIconImage('DefaultTVShows.png')
                    liz.setProperty("fanart_image", art.get('tvshow.fanart',''))
                    for key, value in art.items():
                        try:
                            liz.setProperty( key, value )
                        except: print_exc()

                    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=item['file'],listitem=liz,isFolder=False)
            del json_query
            xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))
            
    def fetch_albums(self, request):
        if not xbmc.abortRequested:
            json_string = '{"jsonrpc": "2.0", "id": 1, "method": "AudioLibrary.GetAlbums", "params": {"properties": ["title", "description", "albumlabel", "theme", "mood", "style", "type", "artist", "genre", "year", "thumbnail", "fanart", "rating", "playcount"], "limits": {"end": %d},' %self.LIMIT
            if request == 'recommendedalbums':
                json_query = xbmc.executeJSONRPC('%s "sort": {"order": "descending", "method": "playcount" }}}' %json_string)
            elif request == 'recentalbums':
                json_query = xbmc.executeJSONRPC('%s "sort": {"order": "descending", "method": "dateadded" }}}' %json_string)
            else:
                json_query = xbmc.executeJSONRPC('%s "sort": {"method": "random"}}}' %json_string)
            json_query = unicode(json_query, 'utf-8', errors='ignore')
            json_query = simplejson.loads(json_query)
            if json_query.has_key('result') and json_query['result'].has_key('albums'):
                count = 0
                for item in json_query['result']['albums']:
                    count += 1
                    rating = str(item['rating'])
                    if rating == '48':
                        rating = ''
                    liz = xbmcgui.ListItem(item['title'])
                    liz.setInfo( type="Music", infoLabels={ "Title": item['title'] })
                    liz.setInfo( type="Music", infoLabels={ "Artist": item['artist'] })
                    liz.setInfo( type="Music", infoLabels={ "Genre": " / ".join(item['genre']) })
                    liz.setInfo( type="Music", infoLabels={ "Year": item['year'] })
                    liz.setInfo( type="Music", infoLabels={ "Rating": rating })
                    liz.setProperty("Album_Mood", " / ".join(item['mood']) )
                    liz.setProperty("Album_Style", " / ".join(item['style']) )
                    liz.setProperty("Album_Theme", " / ".join(item['theme']) )
                    liz.setProperty("Album_Type", " / ".join(item['type']) )
                    liz.setProperty("Album_Label", item['albumlabel'])
                    liz.setProperty("Album_Description", item['description'])

                    liz.setThumbnailImage(item['thumbnail'])
                    liz.setIconImage('DefaultAlbumCover.png')
                    liz.setProperty("fanart_image", item['fanart'])
                    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=play,listitem=liz,isFolder=False)
            del json_query
            xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))
            
    def fetch_song(self, request):
        if not xbmc.abortRequested:
            json_string = '{"jsonrpc": "2.0", "id": 1, "method": "AudioLibrary.GetSongs", "params": {"properties": ["title", "playcount", "genre", "artist", "album", "year", "file", "thumbnail", "fanart", "rating"], "filter": {"field": "playcount", "operator": "lessthan", "value": "1"}, "limits": {"end": %d},' %self.LIMIT
            if request == 'randomsongs' and self.RANDOMITEMS_UNPLAYED == "True":
                json_query = xbmc.executeJSONRPC('%s "sort": {"method": "random"}, "filter": {"field": "playcount", "operator": "lessthan", "value": "1"}}}'  %json_string)
            else:
                json_query = xbmc.executeJSONRPC('%s  "sort": {"method": "random"}}}'  %json_string)
            json_query = unicode(json_query, 'utf-8', errors='ignore')
            json_query = simplejson.loads(json_query)
            list_type = __localize__(32015)
            if json_query.has_key('result') and json_query['result'].has_key('songs'):
                count = 0
                for item in json_query['result']['songs']:
                    count += 1
                    liz = xbmcgui.ListItem(item['title'])
                    liz.setInfo( type="Music", infoLabels={ "Title": item['title'] })
                    liz.setInfo( type="Music", infoLabels={ "Artist": item['artist'] })
                    liz.setInfo( type="Music", infoLabels={ "Genre": " / ".join(item['genre']) })
                    liz.setInfo( type="Music", infoLabels={ "Year": item['year'] })
                    liz.setInfo( type="Music", infoLabels={ "Rating": str(float(item['rating'])) })
                    liz.setProperty("type", list_type)

                    liz.setThumbnailImage(item['thumbnail'])
                    liz.setIconImage('DefaultMusicSongs.png')
                    liz.setProperty("fanart_image", item['fanart'])

                    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=item['file'],listitem=liz,isFolder=False)
            del json_query
            xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))

    def init_property(self):
        self.PLOT_ENABLE = __addon__.getSetting("plot_enable")  == 'true'
        self.RECENTITEMS_UNPLAYED = __addon__.getSetting("recentitems_unplayed")  == 'true' 
        self.RANDOMITEMS_UNPLAYED = __addon__.getSetting("randomitems_unplayed")  == 'true' 
    
    
log('script version %s started' % __addonversion__)
Main()
log('script version %s stopped' % __addonversion__)
