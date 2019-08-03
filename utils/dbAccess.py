import sqlite3
import datetime
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
                                "url_hash"	TEXT NOT NULL
                            );""".format(LIST_TABLE_NAME)

    def __init__(self):

        self.__dbName = 'list.db'
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
        return big_tag, title, timestamp, gallery_id, uploader, pages, url_hash


    def insertNewData(self, listDataFormat):
        dataPackage = self.__parseListDataFormat(listDataFormat)
        query = """INSERT INTO {} VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)""".format(self.LIST_TABLE_NAME)
        with self.__conn:
            cursor = self.__conn.cursor()
            cursor.execute(query, dataPackage)
        self.__commit()

    def updateDataByGalleryId(self, listDataFormat):
        _, _, timestamp, gallery_id, _, pages, url_hash = self.__parseListDataFormat(listDataFormat)
        query = """UPDATE {} SET timestamp = ?, pages = ?, url_hash = ? WHERE gallery_id = ?""".format(self.LIST_TABLE_NAME)
        with self.__conn:
            cursor = self.__conn.cursor()
            cursor.execute(query, (timestamp, pages, url_hash, gallery_id))
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
                allGalleryId = [ result[0] for result in results]
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

    def __init__(self):

        self.__dbName = 'list.db'
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

    def __parsePageDataFormat(self, pageDataFormat):
        gallery_id = pageDataFormat.get('gallery_id')
        tags = pageDataFormat.get('tags')
        favorited_time = pageDataFormat.get('favorited_time')
        rating_count = pageDataFormat.get('rating_count')
        average_score = pageDataFormat.get('average_score')
        last_update_time = datetime.datetime.utcnow()
        # ehentai timezone UTC-1
        last_update_time = last_update_time - datetime.timedelta(hours=1)
        last_update_time = datetime.datetime.strftime(last_update_time, '%Y-%m-%d %H:%M')
        all_downloaded_check = 0
        return gallery_id, tags, favorited_time, rating_count, average_score, last_update_time, all_downloaded_check


    def insertNewData(self, pageDataFormat):
        dataPackage = self.__parsePageDataFormat(pageDataFormat)
        query = """INSERT INTO {} VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)""".format(self.PAGE_TABLE_NAME)
        with self.__conn:
            cursor = self.__conn.cursor()
            cursor.execute(query, dataPackage)
        self.__commit()

    def updateDataByGalleryId(self, pageDataFormat):
        gallery_id, tags, favorited_time, rating_count, average_score, last_update_time, _ = self.__parsePageDataFormat(pageDataFormat)
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

