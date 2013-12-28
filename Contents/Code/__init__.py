# PMS plugin framework
import re
####################################################################################################

VIDEO_PREFIX = "/video/sbs"
NAME = L('Title')
DEFAULT_CACHE_INTERVAL = 1800
OTHER_CACHE_INTERVAL = 300
ART           = 'art-default.png'
ICON          = 'icon-default.png'
BASE_URL = "http://www.sbs.com.au/ondemand/video/"
ROUTE_PREFIX ="/video/sbs"

####################################################################################################

def Start():
    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, L('VideoTitle'), ICON, ART)
    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)
    #HTTP.SetCacheTime(DEFAULT_CACHE_INTERVAL)
    #referrer
    HTTP.CookiesForURL('http://www.sbs.com.au/ondemand')
    #http://www.sbs.com.au/ondemand/video/22739523672/The-Tales-Of-Nights

@route(ROUTE_PREFIX + '/list')
def VideoMainMenu():
    dir = ObjectContainer(title2='Shows')
    content = GetContent()
    #Log("Content>>" + content)
    for show in content:
        temp = re.sub(' ','-',show['programName'])
        url=BASE_URL+show['ID']+'/'+re.sub('-+','-',temp)
        url=unicode(url)
        Log('Adding Show: ' + show['name'] + ', url: ' + url)
        dir.add(Play_sbsvod(url, title=show['name']))
    Log('Returning DIR')
    return dir

@route(ROUTE_PREFIX + '/view')
def Lvl2(content):
    key = content
    content = GetContent()
    dir = ObjectContainer(view_group="InfoList", title2=key)
    for show in content:
        for genre in show['genres']:
            if genre == key:
                temp = re.sub(' ','-',show['programName'])
                url=BASE_URL+show['ID']+'/'+re.sub('-+','-',temp)
                Log('For show '+ show['name'] + ' adding URL>>' + url + "<<")
                try:
                    dir.add(Play_sbsvod(url, title=show['name'], subtitle='runtime: '+ str(int(show['duration']/60)) +' mins.', thumb=show['thumbnailURL'], summary=show['description']))
                except:
                    Log('failure to add web video for : ' + str(show))
    for channel in show['channels']:
            if channel == key:
                temp = re.sub(' ','-',show['programName'])
                url=BASE_URL+show['ID']+'/'+re.sub('-+','-',temp)
                Log('For show '+ show['name'] + ' adding URL: ' + url)
                try:
                    dir.add(Play_sbsvod(url, title=show['name'], subtitle='runtime: '+ str(int(show['duration']/60)) +' mins.', thumb=show['thumbnailURL'], summary=show['description']))
                except:
                    Log('failure to add web video for : ' + str(show))            
    
    return dir

def Play_sbsvod(url, title):

    # url='http://sbsauvod-f.akamaihd.net/SBS_Production/managed/2013/12/2013-12-23_484359_,128,512,1000,1500,K.mp4.csmil_0_3@2?v=3.0.3&fp=LNX%2011,9,900,152&r=VJRXF&g=FQKLKKTYIJTG&seek=423'

    vco = VideoClipObject(
        url=url,
        title=title,
    )

    return vco

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
    
def ParseContent(contentJSON):
    content = []
    
    for entry in contentJSON['entries'] :
        show = {}
        Log("Found show" + entry['title'])
        try:
            show['thumbnailURL']=entry['media$thumbnails'][0]['plfile$downloadUrl']
        except:
            Log("Failed to get thumbnail URL for " + entry['title'])
            
        show['ID'] = re.search('.*/([0-9]+$)',entry['id']).group(1)
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
                Log("skipping category")
        show['genres'] = genres
        show['channels'] = channels
        show['duration'] = entry['media$content'][0]['plfile$duration']
        try:
            show['rating'] = entry['media$ratings'][0]['rating']
        except:
            Log("Couldn't get rating")
        try:
            show['programName'] = entry['pl1$programName']
        except:
            show['programName'] = entry['title']
        show['name'] = entry['title']
        show['description'] = entry['description']
        content.append(show)
    return content    

def GetContent():
    showsJSON = JSON.ObjectFromURL("http://www.sbs.com.au/api/video_feed/f/dYtmxB/section-programs?form=json")
    filmsJSON = JSON.ObjectFromURL("http://www.sbs.com.au/api/video_feed/f/Bgtm9B/sbs-section-sbstv?form=json&byCategories=Film%7CShort+Film%2CSection%2FClips%7CSection%2FPrograms")
    
    shows = ParseContent(showsJSON)
    films = ParseContent(filmsJSON)
    #get unique content
    SBSContent = shows +  [x for x in films if x not in shows]
    return SBSContent
