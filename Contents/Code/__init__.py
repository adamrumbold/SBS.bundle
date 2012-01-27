# PMS plugin framework
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *
import re
####################################################################################################

VIDEO_PREFIX = "/video/sbs"
NAME = L('Title')
DEFAULT_CACHE_INTERVAL = 1800
OTHER_CACHE_INTERVAL = 300
ART           = 'art-default.png'
ICON          = 'icon-default.png'
BASE_URL = "http://sbs.com.au/ondemand/video/"

####################################################################################################

def Start():
    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, L('VideoTitle'), ICON, ART)
    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)
    HTTP.SetCacheTime(DEFAULT_CACHE_INTERVAL)

def VideoMainMenu():
    dir = MediaContainer(viewGroup="InfoList")
    content = GetContent()
    for channel in GetChannels(content):
        dir.Append(Function(DirectoryItem(Lvl2, title=channel), key=channel, content=content))
    for genre in GetGenres(content):
        dir.Append(Function(DirectoryItem(Lvl2, title=genre), key=genre, content=content))   
    return dir

def Lvl2(sender, key, content):
    dir = MediaContainer(viewGroup="InfoList", title2=key)
    for show in content:
        for genre in show['genres']:
            if genre == key:
                temp = re.sub(' ','-',show['name'])
                url=BASE_URL+show['ID']+'/'+re.sub('-+','-',temp)
                Log('For show '+ show['name'] + ' adding URL: ' + url)
                dir.Append(WebVideoItem(url, title=show['name'], subtitle='runtime: '+ str(show['duration']/60) +' mins.', thumb=show['thumbnailURL'], summary=show['description']))
        for channel in show['channels']:
            if channel == key:
                temp = re.sub(' ','-',show['name'])
                url=BASE_URL+show['ID']+'/'+re.sub('-+','-',temp)
                try:
                    dir.Append(WebVideoItem(url, title=show['name'], subtitle='runtime: '+ str(show['duration']/60) +' mins.', thumb=show['thumbnailURL'], summary=show['description']))
                except:
                    Log('failure to add web video for : ' + str(show))            
    return dir

def GetGenres(content):
    distinct = []
    for show in content:
        for genre in show['genres']:
            if genre not in distinct:
                distinct += [ genre ]
    return distinct
    
def GetChannels(content):
    distinct = []
    for show in content:
        for channel in show['channels']:
            if channel not in distinct:
                distinct += [ channel ]
    return distinct
    
def GetContent():
    x = JSON.ObjectFromURL("http://www.sbs.com.au/api/video_feed/f/dYtmxB/section-programs?form=json")
    content = []
    for entry in x['entries'] :
        show = {}
        show['thumbnailURL']=entry['media$thumbnails'][0]['plfile$downloadUrl']
        show['ID'] = entry['id'][-10:]
        genres = []
        channels = []            
        for j in entry['media$categories']:
            try:
                if j['media$scheme'] == 'Genre':
                    genres.append(str(j['media$name']))
                if j['media$scheme'] == 'Channel':
                    if j['media$name'] != 'Channel':
                        channels.append(str(j['media$name']))
            except:
                Log('error with >>' + str(j))
        show['genres'] = genres
        show['channels'] = channels
        show['duration'] = entry['media$content'][0]['plfile$duration']
        try:
            show['rating'] = entry['media$ratings'][0]['rating']
        except:
            Log("Couldn't get rating")
        show['name'] = entry['title']
        show['description'] = entry['description']
        content.append(show)
    return content    