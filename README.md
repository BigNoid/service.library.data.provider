plugin.library.data.provider
============================

Python script for use with XBMC

============================

INFORMATION FOR SKINNERS
============================

Load a list with this content tag to override the user set limit (useful for backgrounds):
<content target="video">plugin://plugin.library.data.provider?type=randommovies&amp;limit=100</content>


Load a list with this content tag to let the user choose the limit:
<content target="video">plugin://plugin.library.data.provider?type=randommovies</content>

Available tags:
-   randommovies
-   recentmovies
-   recommendedmovies
-   recommendedepisodes
-   recentepisodes
-   randomepisodes
-   randomsongs

Available infolabels:
Most of the usual video library infolabels. 
For artwork other then ListItem.Art(thumb) and ListItem.Art(fanart) use ListItem.Property(<art-type>).
Streamdetails not yet implemented.


TODO:
Artist/Album/Musicvideo/Addons support.
Streamdetails support.

