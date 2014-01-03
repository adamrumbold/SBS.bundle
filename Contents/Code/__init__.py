# PMS plugin framework
import re
from sbs_class import *
####################################################################################################

VIDEO_PREFIX = "/video/sbs"
NAME = L('Title')
DEFAULT_CACHE_INTERVAL = 1800
OTHER_CACHE_INTERVAL = 300
ART = 'art-default.png'
ICON = 'icon-default.png'
BASE_URL = "http://www.sbs.com.au/ondemand/video/"
ROUTE_PREFIX = "/video/sbs"

sbs = SBS_channel()

####################################################################################################

def Start():
    Plugin.AddPrefixHandler(VIDEO_PREFIX, viewCategory, L('VideoTitle'), ICON, ART)
    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)
    #HTTP.SetCacheTime(DEFAULT_CACHE_INTERVAL)
    #referrer
    HTTP.CookiesForURL('http://www.sbs.com.au/ondemand')
    #http://www.sbs.com.au/ondemand/video/22739523672/The-Tales-Of-Nights

@route(ROUTE_PREFIX + '/category')
def viewCategory(category=None):

    if category is None:
        cats = sbs.getCategories()
        title = 'SBS On Demand'
    else:
        category = sbs.findCategory(category)
        children = category['children']
        cats = sbs.getCategories(children)
        title = category['name']

    dir = ObjectContainer(title2=title)

    catPrefix = ''

    for child in cats:
        if child['clickable'] == '0':
            catPrefix = child['name'] + ' - '
            continue

        id = child['id']
        if 'children' in child:
            call = Callback(viewCategory, category=id)
        else:
            call = Callback(viewShows, category=id)

        link = DirectoryObject(
            key=call,
            title=catPrefix + child['name']
        )
        dir.add(link)

    dir.add(InputDirectoryObject(key = Callback(ParseSearchResults), title = 'Search...', prompt = 'Search for Videos'))
    return dir


@route(ROUTE_PREFIX + '/shows/{category}')
def viewShows(category):
    category = sbs.findCategory(category)
    dir = ObjectContainer(title2=category['name'])
    shows = sbs.getShows(category)

    for show in shows:
        url = unicode(show['url'])
        dir.add(videoLink(url=url, title=show['title']))

    return dir

def videoLink(url, title):
    vco = VideoClipObject(
        url=url,
        title=title,
    )
    return vco

@route(ROUTE_PREFIX + '/search')
def ParseSearchResults(query = ''):
    dir = ObjectContainer(title2='Search Results')
    shows = sbs.search(query)

    for show in shows:
        url = unicode(show['url'])
        dir.add(videoLink(url=url, title=show['title']))

    return dir

