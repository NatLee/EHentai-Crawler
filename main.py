import logging
import time
import sys
import random
import datetime
import argparse
import threading
import urllib.request
from pathlib import Path
from tqdm import tqdm
from bs4 import BeautifulSoup

from utils.selectDriver import selectDriver
from utils.dbAccess import listDatabase, pageDatabase
from utils.crawler import crawlTagAndImage, ThreadEndCounter, ThreadWithReturnValue, batch
from utils.config import indexUrl, listUrl, numberOfThread, imgDataFolder, exMode

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s : %(message)s')

parser = argparse.ArgumentParser(description='EHentai Crawler: You need crawl list to get list information from ehentai at first. Second, you can only crawl tags or both tags and images.')
parser.add_argument('--crawl_list', action='store', nargs='?', const=True, default=False, type=bool, help='Crawl EHentai page list.')
parser.add_argument('--update_crawl_list', action='store', nargs='?', const=True, default=False, type=bool, help='Crawl EHentai page list and update with time check.')
parser.add_argument('--crawl_each_page', action='store', nargs='?', const=True, default=False, type=bool, help='Crawl EHentai tags and save images for each page.')
parser.add_argument('--crawl_tag_only', action='store', nargs='?', const=True, default=False, type=bool, help='Crawl EHentai tags for each page.')
parser.print_help()
config = parser.parse_args()

listDb = listDatabase()

if __name__== '__main__':

    if config.update_crawl_list or config.crawl_list:

        sd = selectDriver()
        sd.driver.get(indexUrl)
        if exMode:
            sd.driver.delete_all_cookies()
        sd.setCookie()
        if exMode:
            sd.driver.get(indexUrl)

        # flag which detect whether arrive last update
        ARRIVED_LAST_UPDATE = False

        page = 0
        maxPage = 999999

        crawledList = set()
        dataInDb = set(listDb.getAllGalleryId())
        crawledList = crawledList.union(dataInDb)
        works = list()

        lastPublishTime = listDb.getLastPublishTime()

        # crawl list

        while page < maxPage:

            listUrlWithPage = listUrl + str(page)

            htmlText = sd.getPageSource(listUrlWithPage)

            listPageHtml = BeautifulSoup(htmlText, 'html.parser')
            listPageTable = listPageHtml.find_all('table', attrs={'class': 'gltc'})

            # ban detection
            if len(listPageTable) == 0:
                logging.info(listPageHtml)
                # relax 1 hour :)
                sleepBar = tqdm(range(60*60), desc='You got banned or encountered some trouble. We are sleeping...', ascii=True)
                for i in sleepBar:
                    time.sleep(1)
                continue
            else:
                listPageTable = listPageTable[0]
                
            maxPage = int(listPageHtml.find_all('table', attrs={'class': 'ptt'})[0].find_all('a')[-2].text)
            listPageTableTrs = listPageTable.find_all('tr')

            # pop the column name
            listPageTableTrs.pop(0)

            
            listBar = tqdm(listPageTableTrs, desc='Crawling the list ...', ascii=True)

            for listPageTableTr in listBar:

                listDataFormat = {'big_tag': None, 'timestamp': None, 'title': None, 'gallery_id': None, 'uploader': None, 'pages': None, 'url_hash': None}

                try:
                    listDataFormat['big_tag'] = listPageTableTr.td.text
                    listDataFormat['title'] = listPageTableTr.img.get('alt')
                    listDataFormat['timestamp'] = listPageTableTr.find_all('div')[7].text

                    if not config.update_crawl_list:
                        if lastPublishTime > datetime.datetime.strptime(listDataFormat['timestamp'], '%Y-%m-%d %H:%M'):
                            logging.info('We arrived last update point with timestamp {}'.format(lastPublishTime))
                            ARRIVED_LAST_UPDATE = True
                            break

                    listDataFormat['gallery_id'] = int(listPageTableTr.find_all('div')[11].div.attrs.get('id').split('_')[1])
                    listDataFormat['uploader'] = listPageTableTr.find_all('div')[-2].text
                    listDataFormat['pages'] = listPageTableTr.find_all('div')[-1].text.split(' ')[0]
                    
                    galleryUrl = listPageTableTr.find_all('td', attrs={'class':'gl3c glname'})[0].a.get('href')
                    listDataFormat['url_hash'] = galleryUrl.split('/')[-2] if galleryUrl[-1] == '/' else galleryUrl.split('/')[-1]

                except Exception as e:
                    logging.warning(e)
                    pass

                if listDataFormat['gallery_id'] is not None and listDataFormat['url_hash'] is not None:
                    if listDataFormat['gallery_id'] not in crawledList:
                        crawledList.add(listDataFormat['gallery_id'])
                        works.append(listDataFormat)
                        listDb.insertNewData(listDataFormat)
                    else:
                        listDb.updateDataByGalleryId(listDataFormat)
                
            if ARRIVED_LAST_UPDATE:
                break

            page = page + 1
            sleepBar = tqdm(range(random.randint(1, 3)), desc='After crawling page {}. We are sleeping...'.format(page), ascii=True)
            for i in sleepBar:
                time.sleep(1)
        
        sd.close()

    if config.crawl_each_page or config.crawl_tag_only:


        crawlTagOnly = config.crawl_tag_only

        # crawl every page and images
        allGalleryUrlWithGalleryId = listDb.getAllGalleryUrlWithGalleryId()
        allGalleryPublishTimeWithGalleryId = listDb.getAllGalleryPublishTimeWithGalleryId()
        allGalleryPagesWithGalleryId = listDb.getAllGalleryPagesWithGalleryId()

        pd = pageDatabase()
        allLastUpdateTimeWithGalleryId = pd.getAllLastUpdateTimeWithGalleryId()
        notDownloadYetGalleryId = pd.getNotDownloadYetGalleryId()

        # determinate which one need to be crawled
        if not crawlTagOnly:
            needToBeCrawledGallery = set(notDownloadYetGalleryId)
        else:
            needToBeCrawledGallery = set()
        for galleryId, publishTime in tqdm(allGalleryPublishTimeWithGalleryId.items(), desc='Preparing which gallery need to be crawled ...', ascii=True):
            lastUpdateTime = allLastUpdateTimeWithGalleryId.get(galleryId)
            if lastUpdateTime is None or publishTime > lastUpdateTime:
                needToBeCrawledGallery.add(galleryId)

        needToBeCrawledGalleryUrlWithGalleryId = dict()
        for galleryId in tqdm(list(needToBeCrawledGallery), desc='Getting gallery url ...', ascii=True):
            url = allGalleryUrlWithGalleryId.get(galleryId)
            if url is not None:
                needToBeCrawledGalleryUrlWithGalleryId[galleryId] = url
         
        needToBeCrawledItems = list(needToBeCrawledGalleryUrlWithGalleryId.items())
        
        # you change the order when we crawl each page
        random.shuffle(needToBeCrawledItems)

   
        # split two or more threads for paralleling
        batchList = tqdm(list(batch(needToBeCrawledItems, numberOfThread)), desc='Split to {} threads for each batch ...'.format(numberOfThread), ascii=True)
        for needToBeCrawledSlice in batchList:
            threads = list()
            pageDataFormats = list()
            counter = ThreadEndCounter(len(needToBeCrawledSlice))
            for i, element in enumerate(needToBeCrawledSlice):
                threads.append(ThreadWithReturnValue(target=crawlTagAndImage, args=(element, crawlTagOnly, imgDataFolder), counter=counter))

            for thread in threads:    
                thread.start()
            time.sleep(random.randint(1,3))

            for thread in threads:
                pageDataFormats.append(thread.join())

            for pageDataFormat in pageDataFormats:
                if pageDataFormat == -1 or pageDataFormat is None:
                    continue
                gallery_id = pageDataFormat.get('gallery_id')
                if allLastUpdateTimeWithGalleryId.get(gallery_id) is None:
                        pd.insertNewData(pageDataFormat)
                else:
                    pd.updateDataByGalleryId(pageDataFormat)
                
                if pageDataFormat.get('get_all_images') is not None:
                    pd.updateDownloadedCheck(gallery_id, pageDataFormat.get('get_all_images'))

                if pageDataFormat.get('crawl_tag_only') is not None:
                    crawlTagOnly = pageDataFormat['crawl_tag_only']

            

