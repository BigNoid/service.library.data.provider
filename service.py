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
import xbmcvfs
import random
import urllib
import datetime
from traceback import print_exc
from time import gmtime, strftime

if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

__addon__        = xbmcaddon.Addon()
__addonversion__ = __addon__.getAddonInfo('version')
__addonid__      = __addon__.getAddonInfo('id')
__addonname__    = __addon__.getAddonInfo('name')
__localize__     = __addon__.getLocalizedString
__datapath__     = os.path.join( xbmc.translatePath( "special://profile/addon_data/" ).decode('utf-8'), __addonid__ )

def log(txt):
    message = '%s: %s' % (__addonname__, txt.encode('ascii', 'ignore'))
    xbmc.log(msg=message, level=xbmc.LOGDEBUG)

class Main:
    def __init__(self):
        self._parse_argv()
        self.WINDOW = xbmcgui.Window(10000)
        
        # Create datapath if not exists
        if not xbmcvfs.exists(__datapath__):
            xbmcvfs.mkdir(__datapath__)
        
        if self.TYPE == "randommovies":
            self.parse_movies( 'randommovies', __localize__(32004) )
        elif self.TYPE == "recentmovies":
            self.parse_movies( 'recentmovies', __localize__(32005) )
        elif self.TYPE == "recommendedmovies":
            self.parse_movies( 'recommendedmovies', __localize__(32006) )
        elif self.TYPE == "recommendedepisodes":
            self.parse_tvshows_recommended( 'recommendedepisodes', __localize__(32010) )
        elif self.TYPE == "recentepisodes":
            self.parse_tvshows( 'recentepisodes', __localize__(32008) )
        elif self.TYPE == "randomepisodes":
            self.parse_tvshows( 'randomepisodes', __localize__(32007) )
        elif self.TYPE == "randomalbums":
            self.parse_albums( 'randomalbums', __localize__(32016) )
        elif self.TYPE == "recentalbums":
            self.parse_albums( 'recentalbums', __localize__(32017) )
        elif self.TYPE == "recommendedalbums":
            self.parse_albums( 'recommendedalbums', __localize__(32018) )
        elif self.TYPE == "randomsongs":
            self.parse_song( 'randomsongs', __localize__(32015) )
            
        # Play an albums
        elif self.TYPE == "play_album":
            self.play_album( self.ALBUM )
            
        if not self.TYPE:
            # clear our property, if another instance is already running it should stop now
            self._init_vars()
            self.WINDOW.clearProperty('LibraryDataProvider_Running')
            a_total = datetime.datetime.now()
            self._fetch_random()
            self._fetch_recent()
            self._fetch_recommended()
            b_total = datetime.datetime.now()
            c_total = b_total - a_total
            log('Total time needed for all queries: %s' % c_total)
            # give a possible other instance some time to notice the empty property
            self.WINDOW.setProperty('LibraryDataProvider_Running', 'true')
            self._daemon()
            
            
    def _init_vars(self):
        self.WINDOW = xbmcgui.Window(10000)
        self.Player = Widgets_Player(action = self._update)
        self.Monitor = Widgets_Monitor(update_listitems = self._update)

            
    def _fetch_random( self ):
        self._fetch_random_movies()
        self._fetch_random_episodes()
        self._fetch_random_songs()
        self._fetch_random_albums()
        
    def _fetch_random_movies( self ):
        file = self.open_file( 'randommovies' )
        json_string = '{"jsonrpc": "2.0",  "id": 1, "method": "VideoLibrary.GetMovies", "params": {"properties": ["title", "originaltitle", "votes", "playcount", "year", "genre", "studio", "country", "tagline", "plot", "runtime", "file", "plotoutline", "lastplayed", "trailer", "rating", "resume", "art", "streamdetails", "mpaa", "director"], "limits": {"end": %d},' % self.LIMIT
        if self.RANDOMITEMS_UNPLAYED:
            json_query = xbmc.executeJSONRPC('%s "sort": {"method": "random" }, "filter": {"field": "playcount", "operator": "lessthan", "value": "1"}}}' %json_string)
        else:
            json_query = xbmc.executeJSONRPC('%s "sort": {"method": "random" } }}' %json_string)
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        self.save_data( file, json_query )
        xbmcgui.Window( 10000 ).setProperty( "randommovies",strftime( "%Y%m%d%H%M%S",gmtime() ) )
        
    def _fetch_random_episodes( self ):
        file = self.open_file( 'randomepisodes' )
        json_string = '{"jsonrpc": "2.0", "id": 1, "method": "VideoLibrary.GetEpisodes", "params": { "properties": ["title", "playcount", "season", "episode", "showtitle", "plot", "file", "rating", "resume", "tvshowid", "art", "streamdetails", "firstaired", "runtime"], "limits": {"end": %d},' %self.LIMIT
        if self.RANDOMITEMS_UNPLAYED:
            json_query = xbmc.executeJSONRPC('%s "sort": {"method": "random" }, "filter": {"field": "playcount", "operator": "lessthan", "value": "1"}}}' %json_string)
        else:
            json_query = xbmc.executeJSONRPC('%s "sort": {"method": "random" }}}' %json_string)
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        self.save_data( file, json_query )
        xbmcgui.Window( 10000 ).setProperty( "randomepisodes",strftime( "%Y%m%d%H%M%S",gmtime() ) )

    def _fetch_random_songs( self ):
        file = self.open_file( 'randomsongs' )
        json_string = '{"jsonrpc": "2.0", "id": 1, "method": "AudioLibrary.GetSongs", "params": {"properties": ["title", "playcount", "genre", "artist", "album", "year", "file", "thumbnail", "fanart", "rating"], "filter": {"field": "playcount", "operator": "lessthan", "value": "1"}, "limits": {"end": %d},' %self.LIMIT
        if self.RANDOMITEMS_UNPLAYED == "True":
            json_query = xbmc.executeJSONRPC('%s "sort": {"method": "random"}, "filter": {"field": "playcount", "operator": "lessthan", "value": "1"}}}'  %json_string)
        else:
            json_query = xbmc.executeJSONRPC('%s  "sort": {"method": "random"}}}'  %json_string)
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        self.save_data( file, json_query )
        xbmcgui.Window( 10000 ).setProperty( "randomsongs",strftime( "%Y%m%d%H%M%S",gmtime() ) )
        
    def _fetch_random_albums( self ):
        file = self.open_file( 'randomalbums' )
        json_string = '{"jsonrpc": "2.0", "id": 1, "method": "AudioLibrary.GetAlbums", "params": {"properties": ["title", "description", "albumlabel", "theme", "mood", "style", "type", "artist", "genre", "year", "thumbnail", "fanart", "rating", "playcount"], "limits": {"end": %d},' %self.LIMIT
        json_query = xbmc.executeJSONRPC('%s "sort": {"method": "random"}}}' %json_string)
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        self.save_data( file, json_query )
        xbmcgui.Window( 10000 ).setProperty( "randomalbums",strftime( "%Y%m%d%H%M%S",gmtime() ) )

        
    def _fetch_recent( self ):
        self._fetch_recent_movies()
        self._fetch_recent_episodes()
        self._fetch_recent_albums()
        
    def _fetch_recent_movies( self ):
        file = self.open_file( 'recentmovies' )
        json_string = '{"jsonrpc": "2.0",  "id": 1, "method": "VideoLibrary.GetMovies", "params": {"properties": ["title", "originaltitle", "votes", "playcount", "year", "genre", "studio", "country", "tagline", "plot", "runtime", "file", "plotoutline", "lastplayed", "trailer", "rating", "resume", "art", "streamdetails", "mpaa", "director"], "limits": {"end": %d},' % self.LIMIT
        if self.RECENTITEMS_UNPLAYED:
            json_query = xbmc.executeJSONRPC('%s "sort": {"order": "descending", "method": "dateadded"}, "filter": {"field": "playcount", "operator": "is", "value": "0"}}}' %json_string)
        else:
            json_query = xbmc.executeJSONRPC('%s "sort": {"order": "descending", "method": "dateadded"}}}' %json_string)
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        self.save_data( file, json_query )
        xbmcgui.Window( 10000 ).setProperty( "recentmovies",strftime( "%Y%m%d%H%M%S",gmtime() ) )

    def _fetch_recent_episodes( self ):
        file = self.open_file( 'recentepisodes' )
        json_string = '{"jsonrpc": "2.0", "id": 1, "method": "VideoLibrary.GetEpisodes", "params": { "properties": ["title", "playcount", "season", "episode", "showtitle", "plot", "file", "rating", "resume", "tvshowid", "art", "streamdetails", "firstaired", "runtime"], "limits": {"end": %d},' %self.LIMIT
        if self.RECENTITEMS_UNPLAYED:
            json_query = xbmc.executeJSONRPC('%s "sort": {"order": "descending", "method": "dateadded"}, "filter": {"field": "playcount", "operator": "lessthan", "value": "1"}}}' %json_string)
        else:
            json_query = xbmc.executeJSONRPC('%s "sort": {"order": "descending", "method": "dateadded"}}}' %json_string)
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        self.save_data( file, json_query )
        xbmcgui.Window( 10000 ).setProperty( "recentepisodes",strftime( "%Y%m%d%H%M%S",gmtime() ) )
        
    def _fetch_recent_albums( self ):
        file = self.open_file( 'recentalbums' )
        json_string = '{"jsonrpc": "2.0", "id": 1, "method": "AudioLibrary.GetAlbums", "params": {"properties": ["title", "description", "albumlabel", "theme", "mood", "style", "type", "artist", "genre", "year", "thumbnail", "fanart", "rating", "playcount"], "limits": {"end": %d},' %self.LIMIT
        json_query = xbmc.executeJSONRPC('%s "sort": {"order": "descending", "method": "dateadded" }}}' %json_string)
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        self.save_data( file, json_query )
        xbmcgui.Window( 10000 ).setProperty( "recentalbums",strftime( "%Y%m%d%H%M%S",gmtime() ) )
    
    
    def _fetch_recommended( self ):
        self._fetch_recommended_movies()
        self._fetch_recommended_episodes()
        self._fetch_recommended_albums()

    def _fetch_recommended_movies( self ):
        file = self.open_file( 'recommendedmovies' )
        json_string = '{"jsonrpc": "2.0",  "id": 1, "method": "VideoLibrary.GetMovies", "params": {"properties": ["title", "originaltitle", "votes", "playcount", "year", "genre", "studio", "country", "tagline", "plot", "runtime", "file", "plotoutline", "lastplayed", "trailer", "rating", "resume", "art", "streamdetails", "mpaa", "director"], "limits": {"end": %d},' % self.LIMIT
        json_query = xbmc.executeJSONRPC('%s "sort": {"order": "descending", "method": "lastplayed"}, "filter": {"field": "inprogress", "operator": "true", "value": ""}}}' %json_string)
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        self.save_data( file, json_query )
        xbmcgui.Window( 10000 ).setProperty( "recommendedmovies",strftime( "%Y%m%d%H%M%S",gmtime() ) )
    
    def _fetch_recommended_episodes( self ):
        file = self.open_file( 'recommendedepisodes' )
        json_string = '{"jsonrpc": "2.0", "id": 1, "method": "VideoLibrary.GetEpisodes", "params": { "properties": ["title", "playcount", "season", "episode", "showtitle", "plot", "file", "rating", "resume", "tvshowid", "art", "streamdetails", "firstaired", "runtime"], "limits": {"end": %d},' %self.LIMIT
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": {"properties": ["title", "studio", "mpaa", "file", "art"], "sort": {"order": "descending", "method": "lastplayed"}, "filter": {"field": "inprogress", "operator": "true", "value": ""}, "limits": {"end": %d}}, "id": 1}' %self.LIMIT)
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_query1 = simplejson.loads(json_query)
        if json_query1.has_key('result') and json_query1['result'].has_key('tvshows'):
            for item in json_query1['result']['tvshows']:
                file2 = self.open_file( str( item['tvshowid'] ) )
                if xbmc.abortRequested:
                    break
                json_query2 = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": {"tvshowid": %d, "properties": ["title", "playcount", "plot", "season", "episode", "showtitle", "file", "lastplayed", "rating", "resume", "art", "streamdetails", "firstaired", "runtime"], "sort": {"method": "episode"}, "filter": {"field": "playcount", "operator": "is", "value": "0"}, "limits": {"end": 1}}, "id": 1}' %item['tvshowid'])
                json_query2 = unicode(json_query2, 'utf-8', errors='ignore')
                self.save_data( file2, json_query2 )
                self.WINDOW.setProperty(str(item['tvshowid']), json_query2)
        
        self.save_data( file, json_query )
        xbmcgui.Window( 10000 ).setProperty( "recommendedepisodes",strftime( "%Y%m%d%H%M%S",gmtime() ) )
        
    def _fetch_recommended_albums( self ):
        file = self.open_file( 'recommendedalbums' )
        json_string = '{"jsonrpc": "2.0", "id": 1, "method": "AudioLibrary.GetAlbums", "params": {"properties": ["title", "description", "albumlabel", "theme", "mood", "style", "type", "artist", "genre", "year", "thumbnail", "fanart", "rating", "playcount"], "limits": {"end": %d},' %self.LIMIT
        json_query = xbmc.executeJSONRPC('%s "sort": {"order": "descending", "method": "playcount" }}}' %json_string)
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        self.save_data( file, json_query)
        xbmcgui.Window( 10000 ).setProperty( "recommendedalbums",strftime( "%Y%m%d%H%M%S",gmtime() ) )

        
    def parse_movies(self, request, list_type):
        json_query = self.load_file( request )
        if json_query:
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
                    for key, value in item['streamdetails'].iteritems():
                        for stream in value:
                            liz.addStreamInfo( key, stream ) 

                    for key, value in art.items():
                        try:
                            liz.setProperty( key, value )
                        except: print_exc()
                    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=item['file'],listitem=liz,isFolder=False)
        del json_query
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))
        
    def parse_tvshows_recommended(self, request, list_type):
        json_query = self.load_file( request )
        if json_query:
            # First unplayed episode of recent played tvshows
            json_query = simplejson.loads(json_query)
            list_type = __localize__(32010)
            if json_query.has_key('result') and json_query['result'].has_key('tvshows'):
                count = 0
                for item in json_query['result']['tvshows']:
                    if xbmc.abortRequested:
                        break
                    count += 1
                    json_query2 = self.load_file( str( item['tvshowid'] ) )
                    if json_query:
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
                        liz = xbmcgui.ListItem(item2['title'])
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
                        for key, value in item2['streamdetails'].iteritems():
                            for stream in value:
                                liz.addStreamInfo( key, stream ) 
                        for key, value in art.items():
                            try:
                                liz.setProperty( key, value )
                            except: print_exc()
                        
                        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=item2['file'],listitem=liz,isFolder=False)
        del json_query
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))

    def parse_tvshows(self, request, list_type):
        #json_query = unicode(self.WINDOW.getProperty( request + '-data' ) , 'utf-8', errors='ignore')
        json_query = self.load_file( request )
        if json_query:
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
                    for key, value in item['streamdetails'].iteritems():
                        for stream in value:
                            liz.addStreamInfo( key, stream ) 
                    for key, value in art.items():
                        try:
                            liz.setProperty( key, value )
                        except: print_exc()

                    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=item['file'],listitem=liz,isFolder=False)
        del json_query
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))
        
    def parse_song(self, request, list_type):
        json_query = self.load_file( request )
        if json_query:
            json_string = '{"jsonrpc": "2.0", "id": 1, "method": "AudioLibrary.GetSongs", "params": {"properties": ["title", "playcount", "genre", "artist", "album", "year", "file", "thumbnail", "fanart", "rating"], "filter": {"field": "playcount", "operator": "lessthan", "value": "1"}, "limits": {"end": %d},' %self.LIMIT
            json_query = simplejson.loads(json_query)
            list_type = __localize__(32015)
            if json_query.has_key('result') and json_query['result'].has_key('songs'):
                count = 0
                for item in json_query['result']['songs']:
                    count += 1
                    liz = xbmcgui.ListItem(item['title'])
                    liz.setInfo( type="Music", infoLabels={ "Title": item['title'] })
                    liz.setInfo( type="Music", infoLabels={ "Artist": item['artist'][0] })
                    liz.setInfo( type="Music", infoLabels={ "Genre": " / ".join(item['genre']) })
                    liz.setInfo( type="Music", infoLabels={ "Year": item['year'] })
                    liz.setInfo( type="Music", infoLabels={ "Rating": str(float(item['rating'])) })
                    liz.setInfo( type="Music", infoLabels={ "Album": item['album'] })
                    liz.setProperty("type", list_type)

                    liz.setThumbnailImage(item['thumbnail'])
                    liz.setIconImage('DefaultMusicSongs.png')
                    liz.setProperty("fanart_image", item['fanart'])

                    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=item['file'],listitem=liz,isFolder=False)
        del json_query
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))
        
    def parse_albums (self, request, list_type):
        json_query = self.load_file( request )
        if json_query:
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
                    
                    # Path will call plugin again, with the album id
                    path = sys.argv[0] + "?type=play_album&album=" + str(item['albumid'])
                    
                    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=path,listitem=liz,isFolder=False)
        del json_query
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))
        
    def play_album( self, album ):
        xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "Player.Open", "params": { "item": { "albumid": %d } }, "id": 1 }' % int(album) )
        # Return ResolvedUrl as failed, as we've taken care of what to play
        xbmcplugin.setResolvedUrl( handle=int( sys.argv[1]), succeeded=False, listitem=xbmcgui.ListItem() )
        
    def load_file(self, request):
        path = os.path.join( __datapath__, request + ".json" )
        if not xbmcvfs.exists( path ):
            return None
        
        # If we can't load the file, it's currently being updated
        try:
            file = xbmcvfs.File( path, 'r' )
            fileOpened = True
            content = file.read().decode("utf-8")
            file.close()
            return( content )
        except:
            return None
        
    def open_file(self, request):
        path = os.path.join( __datapath__, request + ".json" )
        log( "Opening file - " + path )
        
        # Keep trying to open file until succeeded (avoids race condition)
        fileOpened = False
        tries = 0
        
        while fileOpened == False:
            try:
                file = xbmcvfs.File( path, 'w' )
                fileOpened = True
            except:
                print_exc()
                tries = tries + 1
                wait = 1
                
        return( file )
        
    def save_data(self, file, data):
        log( "Saving file" )
        file.write( data.encode("utf-8") )
        file.close()
        
        
    def _daemon(self):
        # deamon is meant to keep script running at all time
        count = 0
        home_update = False
        while (not xbmc.abortRequested) and self.WINDOW.getProperty('LibraryDataProvider_Running') == 'true':
            xbmc.sleep(500)
            if not xbmc.Player().isPlayingVideo():
                # Update random items
                count += 1
                if count == 1200: # 10 minutes
                    self._fetch_random()
                    count = 0    # reset counter
                    
    def _update(self, type):
        xbmc.sleep(1000)
        if type == 'movie':
            self._fetch_recommended_movies()
            self._fetch_recent_movies()
        elif type == 'episode':
            self._fetch_recommended_episodes()
            self._fetch_recent_episodes()
        elif type == 'video':
            #only on db update
            self._fetch_recommended_movies()
            self._fetch_recommended_episodes()
            self._fetch_recent_movies()
            self._fetch_recent_episodes()
        elif type == 'music':
            self._fetch_recommended_albums()
            self._fetch_recent_albums()
            
    def _parse_argv( self ):
        try:
            params = dict( arg.split( "=" ) for arg in sys.argv[ 2 ].split( "&" ) )
        except:
            params = {}
        print params
        self.LIMIT = int(__addon__.getSetting("limit"))
        self.TYPE = params.get( "?type", "" )
        self.ALBUM = params.get( "album", "" )
        self.RECENTITEMS_UNPLAYED = __addon__.getSetting("recentitems_unplayed")  == 'true'
        self.PLOT_ENABLE = __addon__.getSetting("plot_enable")  == 'true'
        self.RANDOMITEMS_UNPLAYED = __addon__.getSetting("randomitems_unplayed")  == 'true'
    
class Widgets_Monitor(xbmc.Monitor):
    def __init__(self, *args, **kwargs):
        xbmc.Monitor.__init__(self)
        self.update_listitems = kwargs['update_listitems']

    def onDatabaseUpdated(self, database):
        self.update_listitems(database)
        

class Widgets_Player(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self)
        self.type = ""
        self.action = kwargs[ "action" ]
        self.substrings = [ '-trailer', 'http://' ]

    def onPlayBackStarted(self):
        xbmc.sleep(1000)
        # Set values based on the file content
        if (self.isPlayingAudio()):
            self.mediatype = "music"  
        else:
            if xbmc.getCondVisibility('VideoPlayer.Content(movies)'):
                filename = ''
                isMovie = True
                try:
                    filename = self.getPlayingFile()
                except:
                    pass
                if filename != '':
                    for string in self.substrings:
                        if string in filename:
                            isMovie = False
                            break
                if isMovie:
                    self.mediatype = "movie"
            elif xbmc.getCondVisibility('VideoPlayer.Content(episodes)'):
                # Check for tv show title and season to make sure it's really an episode
                if xbmc.getInfoLabel('VideoPlayer.Season') != "" and xbmc.getInfoLabel('VideoPlayer.TVShowTitle') != "":
                    self.mediatype = "episode"

    def onPlayBackEnded(self):
        self.onPlayBackStopped()

    def onPlayBackStopped(self):
        if self.mediatype == 'movie':
            self.action('movie')
        elif self.mediatype == 'episode':
            self.action('episode')
        elif self.mediatype == 'music':
            self.action('music')
        self.mediatype = ""

    
log('script version %s started' % __addonversion__)
Main()
log('script version %s stopped' % __addonversion__)
