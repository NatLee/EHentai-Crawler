import sqlite3
import datetime
from tqdm import tqdm
from utils.config import galleryUrl



class listDatabase():

    LIST_TABLE_NAME = 'hentai_list'
    HENTAI_LIST_TABLE_SQL = """CREATE TABLE IF NOT EXISTS "{}" (
	                            "id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	                            "big_tag"	TEXT NOT NULL,
	                            "title"	TEXT NOT NULL,
	                            "timestamp"	INTEGER NOT NULL,
	                            "gallery_id"	INTEGER NOT NULL UNIQUE,
	                            "uploader"	TEXT NOT NULL,
	                            "pages"	INTEGER NOT NULL,
                                "url_hash"	TEXT NOT NULL,
                                "removed"	INTEGER NOT NULL
                            );""".format(LIST_TABLE_NAME)

    def __init__(self, dbName:str='list.db'):

        self.__dbName = dbName
        self.__conn = self.__buildDatabase()
        

    def __loadDatabase(self):
        conn = sqlite3.connect(self.__dbName)
        return conn

    def __buildDatabase(self):
        conn = self.__loadDatabase()
        with conn:
            cursor = conn.cursor()
            cursor.execute(self.HENTAI_LIST_TABLE_SQL)
        return conn

    def __commit(self):
        self.__conn.commit()

    def __parseListDataFormat(self, listDataFormat):
        big_tag = listDataFormat.get('big_tag')
        title = listDataFormat.get('title')
        timestamp = listDataFormat.get('timestamp')
        gallery_id = listDataFormat.get('gallery_id')
        uploader = listDataFormat.get('uploader')
        pages = listDataFormat.get('pages')
        url_hash = listDataFormat.get('url_hash')
        if listDataFormat.get('removed') is None:
            removed = 0
        else:
            removed = listDataFormat.get('removed')
        return big_tag, title, timestamp, gallery_id, uploader, pages, url_hash, removed


    def insertNewData(self, listDataFormat):
        dataPackage = self.__parseListDataFormat(listDataFormat)
        query = """INSERT INTO {} VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)""".format(self.LIST_TABLE_NAME)
        with self.__conn:
            cursor = self.__conn.cursor()
            cursor.execute(query, dataPackage)
        self.__commit()

    def updateDataByGalleryId(self, listDataFormat):
        _, _, timestamp, gallery_id, _, pages, url_hash, removed = self.__parseListDataFormat(listDataFormat)
        query = """UPDATE {} SET timestamp = ?, pages = ?, url_hash = ?, removed = ? WHERE gallery_id = ?""".format(self.LIST_TABLE_NAME)
        with self.__conn:
            cursor = self.__conn.cursor()
            cursor.execute(query, (timestamp, pages, url_hash, removed, gallery_id))
        self.__commit()

    def updateRemovedByGalleryId(self, galleryId, removedStatus):
        query = """UPDATE {} SET removed = ? WHERE gallery_id = ?""".format(self.LIST_TABLE_NAME)
        with self.__conn:
            cursor = self.__conn.cursor()
            cursor.execute(query, (removedStatus, galleryId))
        self.__commit()


    def getAllGalleryId(self) -> list:
        query = """SELECT gallery_id FROM {}""".format(self.LIST_TABLE_NAME)
        with self.__conn:
            cursor = self.__conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()            
            if results is None:
                allGalleryId = list()
            else:
                allGalleryId = [result[0] for result in results]
        return allGalleryId


    def getAllGalleryPublishTimeWithGalleryId(self) -> list:
        query = """SELECT gallery_id, timestamp FROM {}""".format(self.LIST_TABLE_NAME)
        with self.__conn:
            cursor = self.__conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()            
            if results is None:
                allGalleryPublishTimeWithGalleryId = list()
            else:
                allGalleryPublishTimeWithGalleryId = {result[0]:result[1] for result in results}
        return allGalleryPublishTimeWithGalleryId


    def getAllGalleryUrlWithGalleryId(self) -> dict:
        query = """SELECT gallery_id, url_hash FROM {}""".format(self.LIST_TABLE_NAME)
        with self.__conn:
            cursor = self.__conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()            
            if results is None:
                allGalleryUrlWithGalleryId = list()
            else:
                allGalleryUrlWithGalleryId = {result[0]: galleryUrl + str(result[0]) + '/' + str(result[1]) + '/' for result in results}
        return allGalleryUrlWithGalleryId

    def getAllGalleryPagesWithGalleryId(self) -> dict:
        query = """SELECT gallery_id, pages FROM {}""".format(self.LIST_TABLE_NAME)
        with self.__conn:
            cursor = self.__conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()            
            if results is None:
                allGalleryPagesWithGalleryId = list()
            else:
                allGalleryPagesWithGalleryId = {result[0]:result[1] for result in results}
        return allGalleryPagesWithGalleryId


    def getGalleryUrlByGalleryId(self, gallery_id:int) -> str:
        query = """SELECT url_hash FROM {} WHERE gallery_id = ?""".format(self.LIST_TABLE_NAME)
        with self.__conn:
            cursor = self.__conn.cursor()
            cursor.execute(query, (gallery_id,))
            result = cursor.fetchone()
            if result is None:
                url = ''
            else:
                url = galleryUrl + str(gallery_id) + '/' + str(result[0]) + '/'
        return url

    def getLastPublishTime(self) -> datetime.datetime:
        query = """SELECT timestamp FROM {} ORDER BY timestamp DESC LIMIT 1""".format(self.LIST_TABLE_NAME)
        with self.__conn:
            cursor = self.__conn.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            if result is None:
                lastPublishTime = datetime.datetime(2000, 1, 1, 0, 0, 0)
            else:
                lastPublishTime = datetime.datetime.strptime(result[0], '%Y-%m-%d %H:%M')
        return lastPublishTime

    def getNotRemovedGalleryId(self) -> list:
        query = """SELECT gallery_id FROM {} WHERE removed = 0""".format(self.LIST_TABLE_NAME)
        with self.__conn:
            cursor = self.__conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            if results is None:
                notBeenRemovedGallery = list()
            else:
                notBeenRemovedGallery = [result[0] for result in results]
        return notBeenRemovedGallery

    def getAllListData(self) -> dict:
        query = """SELECT * FROM {}""".format(self.LIST_TABLE_NAME)
        with self.__conn:
            cursor = self.__conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            allData = dict()
            if results is not None:
                for result in results:
                    gallery_id = result[4]
                    big_tag = result[1]
                    title = result[2]
                    timestamp = result[3]
                    uploader = result[5]
                    pages = result[6]
                    url_hash = result[7]
                    removed = result[8]
                    listDataFormat = {'big_tag': big_tag, 'timestamp': timestamp, 'title': title, 'gallery_id': gallery_id, 'uploader': uploader, 'pages': pages, 'url_hash': url_hash, 'removed': removed}
                    allData[gallery_id] = listDataFormat
        return allData

    def syncList(self, addDb):
        addDbAllData = addDb.getAllListData()
        mainDbAllData = self.getAllListData()
        for galleryId, dataFormat in tqdm(addDbAllData.items(), desc='List Data Sync...', ascii=True):
            addTimestamp = datetime.datetime.strptime(dataFormat.get('timestamp'), '%Y-%m-%d %H:%M')
            addRemoved = dataFormat.get('removed')
            mainDbDataFormat = mainDbAllData.get(galleryId)
            if mainDbDataFormat is not None:
                mainTimestamp = datetime.datetime.strptime(mainDbDataFormat.get('timestamp'), '%Y-%m-%d %H:%M')
                mainRemoved = mainDbDataFormat.get('removed')
                if int(mainRemoved) < int(addRemoved):
                    dataFormat['removed'] = addRemoved
                if mainTimestamp < addTimestamp:
                    self.updateDataByGalleryId(dataFormat)
            else:
                self.insertNewData(dataFormat)



class pageDatabase():

    PAGE_TABLE_NAME = 'page_information'
    PAGE_INFORMATION_TABLE_SQL = """CREATE TABLE IF NOT EXISTS "{}" (
	                            "id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	                            "gallery_id"	INTEGER NOT NULL UNIQUE,
                                "tags"	TEXT,
                                "favorited_time"	INTEGER NOT NULL,
                                "rating_count"	INTEGER NOT NULL,
                                "average_score"	REAL NOT NULL,
                                "last_update_time"	TEXT NOT NULL,
                                "all_downloaded_check" INTEGER NOT NULL
                            );""".format(PAGE_TABLE_NAME)

    def __init__(self, dbName:str='list.db'):

        self.__dbName = dbName
        self.__timezone = datetime.timezone(datetime.timedelta(hours=8))
        self.__conn = self.__buildDatabase()
        

    def __loadDatabase(self):
        conn = sqlite3.connect(self.__dbName)
        return conn

    def __buildDatabase(self):
        conn = self.__loadDatabase()
        with conn:
            cursor = conn.cursor()
            cursor.execute(self.PAGE_INFORMATION_TABLE_SQL)
        return conn

    def __commit(self):
        self.__conn.commit()

    def __parsePageDataFormat(self, pageDataFormat, last_update_time=None, all_downloaded_check=0):
        gallery_id = pageDataFormat.get('gallery_id')
        tags = pageDataFormat.get('tags')
        favorited_time = pageDataFormat.get('favorited_time')
        rating_count = pageDataFormat.get('rating_count')
        average_score = pageDataFormat.get('average_score')
        if last_update_time is None:
            last_update_time = datetime.datetime.utcnow()
            # ehentai timezone UTC-1
            last_update_time = last_update_time - datetime.timedelta(hours=1)
            last_update_time = datetime.datetime.strftime(last_update_time, '%Y-%m-%d %H:%M')
        return gallery_id, tags, favorited_time, rating_count, average_score, last_update_time, all_downloaded_check


    def insertNewData(self, pageDataFormat, last_update_time=None, all_downloaded_check=0):
        dataPackage = self.__parsePageDataFormat(pageDataFormat, last_update_time, all_downloaded_check)
        query = """INSERT INTO {} VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)""".format(self.PAGE_TABLE_NAME)
        with self.__conn:
            cursor = self.__conn.cursor()
            cursor.execute(query, dataPackage)
        self.__commit()

    def updateDataByGalleryId(self, pageDataFormat, last_update_time=None, all_downloaded_check=0):
        gallery_id, tags, favorited_time, rating_count, average_score, last_update_time, _ = self.__parsePageDataFormat(pageDataFormat, last_update_time, all_downloaded_check)
        query = """UPDATE {} SET tags = ?, favorited_time = ?, rating_count = ?, average_score = ?, last_update_time = ? WHERE gallery_id = ?""".format(self.PAGE_TABLE_NAME)
        with self.__conn:
            cursor = self.__conn.cursor()
            cursor.execute(query, (tags, favorited_time, rating_count, average_score, last_update_time, gallery_id))
        self.__commit()


    def getNotDownloadYetGalleryId(self) -> list:
        query = """SELECT gallery_id FROM {} where all_downloaded_check = 0""".format(self.PAGE_TABLE_NAME)
        with self.__conn:
            cursor = self.__conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()            
            if results is None:
                notDownloadYetGalleryId = list()
            else:
                notDownloadYetGalleryId = [result[0] for result in results]
        return notDownloadYetGalleryId

    def updateDownloadedCheck(self, gallery_id:int, all_downloaded_check:int):
        query = """UPDATE {} SET all_downloaded_check = ? where gallery_id = ?""".format(self.PAGE_TABLE_NAME)
        with self.__conn:
            cursor = self.__conn.cursor()
            cursor.execute(query, (all_downloaded_check, gallery_id))
        self.__commit()
    

    def getLastUpdateTime(self) -> datetime.datetime:
        query = """SELECT last_update_time FROM {} ORDER BY last_update_time DESC LIMIT 1""".format(self.PAGE_TABLE_NAME)
        with self.__conn:
            cursor = self.__conn.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            if result is None:
                lastUpdateTime = datetime.datetime(2000, 1, 1, 0, 0, 0)
            else:
                lastUpdateTime = datetime.datetime.strptime(result[0], '%Y-%m-%d %H:%M')
        return lastUpdateTime


    def getAllLastUpdateTimeWithGalleryId(self) -> dict:
        query = """SELECT gallery_id, last_update_time FROM {}""".format(self.PAGE_TABLE_NAME)
        with self.__conn:
            cursor = self.__conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            if results is None:
                allLasteUpdateTimeWithGalleryId = list()
            else:
                allLasteUpdateTimeWithGalleryId = {result[0]:result[1] for result in results}
        return allLasteUpdateTimeWithGalleryId


    def getAllPageData(self) -> dict:
        query = """SELECT * FROM {}""".format(self.PAGE_TABLE_NAME)
        with self.__conn:
            cursor = self.__conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            allData = dict()
            if results is not None:
                for result in results:
                    gallery_id = result[1]
                    tagClass = result[2]
                    favorited_time = result[3]
                    rating_count = result[4]
                    average_score = result[5]
                    last_update_time = result[6]
                    pageDataFormat = {'favorited_time': favorited_time, 'rating_count': rating_count, 'average_score': average_score, 'gallery_id': gallery_id, 'tags': tagClass, 'last_update_time': last_update_time}
                    allData[gallery_id] = pageDataFormat
        return allData


    def syncPage(self, addDb):
        addDbAllData = addDb.getAllPageData()
        mainDbAllData = self.getAllPageData()
        for galleryId, dataFormat in tqdm(addDbAllData.items(), desc='Page Data Sync...', ascii=True):
            addTime = dataFormat.get('last_update_time')
            if len(addTime) > 16:
                addTime = addTime[:16]
            try:
                addLastUpdateTime = datetime.datetime.strptime(addTime, '%Y-%m-%d %H:%M')
            
                mainDbDataFormat = mainDbAllData.get(galleryId)
                if mainDbDataFormat is not None:
                    mainTime = mainDbDataFormat.get('last_update_time')
                    if len(mainTime) > 16:
                        mainTime = mainTime[:16]
                    mainLastUpdateTime = datetime.datetime.strptime(mainTime, '%Y-%m-%d %H:%M')
                    if mainLastUpdateTime < addLastUpdateTime:
                        self.updateDataByGalleryId(dataFormat, addLastUpdateTime)
                else:
                    self.insertNewData(dataFormat, addLastUpdateTime)
            except Exception:
                import pdb; pdb.set_trace()


