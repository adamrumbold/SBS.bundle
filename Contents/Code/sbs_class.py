MENU_URL = 'http://www.sbs.com.au/ondemand/js/video-menu?v=1.1'
API_BASE = 'http://www.sbs.com.au'
VIDEO_URL = 'http://www.sbs.com.au/ondemand/video'

class SBS_channel:
    def loadMenu(self):
        request = HTTP.Request(MENU_URL)
        request.load()
        content = request.content
        content = content.replace('VideoMenu =', '')
        menu = JSON.ObjectFromString(content)
        return menu

    def getMenu(self):
        try:
            menu = self.menu
        except:
            menu = self.loadMenu()
            self.menu = menu
        return menu

    def getCategories(self, menu=None):
        if menu is None:
            menu = self.getMenu()
        data = []

        try:
            menu = menu.values()
        except:
            menu = menu

        for category in menu:
            if category['clickable'] == '0':
                continue
            data.append(category)
        return data

    def getShows(self, category):
        url = category['url']
        fullURL = API_BASE + url
        apiData = JSON.ObjectFromURL(fullURL)
        returnData = []
        for data in apiData['entries']:
            if self.is_int(data):
                data = apiData['entries'][data]
            data['url'] = self.extractShowURL(data)
            returnData.append(data)
        return returnData;

    def extractShowURL(self, show):
        showID = show['id']
        id = showID.split("/")[-1]
        return VIDEO_URL + '/' + id


    def findCategory(self, id):
        menu = self.getMenu()
        menu = menu.items()
        for key, category in menu:
            child = self.checkCategory(id, category)
            if child is not None:
                return child
        return None

    def checkCategory(self, id, category):
        if category['id'] == id:
            return category
        elif 'children' in category:
            for childCat in category['children']:
                if self.is_int(childCat):
                    childCat = category['children'][childCat]
                child = self.checkCategory(id, childCat)
                if child is not None:
                    return child
        return None

    def is_int(self, s):
        try:
            int(s)
            return True
        except:
            return False


