import logging
import urllib.request
import random
import time
import threading
from bs4 import BeautifulSoup
from tqdm import tqdm
from pathlib import Path
from utils.selectDriver import selectDriver
from utils.config import exMode

class ThreadEndCounter():
    def __init__(self, totalThread:int):
        self.value = 0
        #self.pbar = tqdm(range(totalThread))
    def increament(self):
        with threading.Lock():
            self.value += 1
            #self.pbar.update()


class ThreadWithReturnValue(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args:tuple=(), kwargs:dict={}, Verbose=None, counter:ThreadEndCounter=None):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self.__return = None
        if counter is not None:
            self.__counter = counter
    def run(self):
        #print(type(self._target))
        if self._target is not None:
            self.__return = self._target(*self._args, **self._kwargs)
        if self.__counter is not None:
            self.__counter.increament()
    def join(self, *args):
        threading.Thread.join(self, *args)
        return self.__return


def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


def crawlTagAndImage(needToBeCrawledItems, crawlTagOnly, imgDataFolder):

    cannotDownloadUrlWithGalleryId = list()

    ### crawl tags
    gallery_id = needToBeCrawledItems[0]
    galleryUrl = needToBeCrawledItems[1]

    logging.debug('Starting to crawl gallery::{}:: tags and images for each page ...'.format(gallery_id))

    sd = selectDriver()
    
    LOAD_SUCCESS_FLAG = False
    
    while not LOAD_SUCCESS_FLAG:
        try:
            htmlText = sd.getPageSource(galleryUrl)
            if exMode:
                sd.driver.delete_all_cookies()
            # skip ehentai warning
            sd.setCookie()
            if exMode:
                htmlText = sd.getPageSource(galleryUrl)
            galleryPageHtml = BeautifulSoup(htmlText, 'html.parser')

            if galleryPageHtml.text.find('Content Warning') > 0:
                # reload to skip content warning
                htmlText = sd.getPageSource(galleryUrl)
                galleryPageHtml = BeautifulSoup(htmlText, 'html.parser')


            galleryPageTagTable = galleryPageHtml.find_all('div', attrs={'id': 'taglist'})
            if len(galleryPageTagTable) != 0:
                rows = galleryPageTagTable[0].find_all('tr')
                tagClass = dict()
                for row in rows:
                    className = row.td.text.replace(':', '')
                    tagClass[className] = list()
                    columns = row.find_all('a')
                    for column in columns:
                        tagClass[className].append(column.text)
            
            ### crawl count and score
            favorited_time = galleryPageHtml.find_all('td', attrs={'id': 'favcount'})[0].text
            if favorited_time == 'Never':
                favorited_time = 0
            elif favorited_time == 'Once':
                favorited_time = 1
            else:
                favorited_time = int(favorited_time.split(' ')[0])
            
            rating_count = int(galleryPageHtml.find_all('span', attrs={'id': 'rating_count'})[0].text)
            average_score = float(galleryPageHtml.find_all('td', attrs={'id': 'rating_label'})[0].text.split(' ')[1])
            pageDataFormat = {'favorited_time': favorited_time, 'rating_count': rating_count, 'average_score': average_score, 'gallery_id': gallery_id, 'tags': str(tagClass)}
            LOAD_SUCCESS_FLAG = True

        except Exception as e:
            logging.warning('"{}" with gallery ::{}::'.format(e, gallery_id))
            if galleryPageHtml.text.find('This gallery has been removed or is unavailable or in EXHentai.') > 0:
                logging.warning('This gallery ::{}:: has been removed or is unavailable.'.format(gallery_id))
                return -1
            if galleryPageHtml.text.find('Error 503 Service Unavailable') > 0:
                logging.warning('You got 503 Error with gallery ::{}::. We sleep 30 sec(s).'.format(gallery_id))
                time.sleep(30)
            time.sleep(3)


    ### crawl all image

    ## step 1: determinate page
    ## step 2: find all image url
    ## step 3: goto page for each image
    ## step 4: download the image to specific folder


    if not crawlTagOnly:
        page = 0
        imgPageUrls = list()

        # check page information
        showingImageInformation = galleryPageHtml.find_all('p', attrs={'class': 'gpc'})[0].text
        maxImageNumberInOnePage = int(showingImageInformation.replace(',', '').split(' ')[3])
        maxImageNumberAllPage = int(showingImageInformation.replace(',', '').split(' ')[5])

        
        # get all image page url in this gallery
        while maxImageNumberInOnePage <= maxImageNumberAllPage:
            galleryUrlWithPage = galleryUrl + '?p={}'.format(str(page))
            htmlText = sd.getPageSource(galleryUrlWithPage)
            galleryPageHtml = BeautifulSoup(htmlText, 'html.parser')
            # double check page information
            showingImageInformation = galleryPageHtml.find_all('p', attrs={'class': 'gpc'})[0].text
            maxImageNumberInOnePage = int(showingImageInformation.replace(',', '').split(' ')[3])
            maxImageNumberAllPage = int(showingImageInformation.replace(',', '').split(' ')[5])
            # find all image page url
            galleryPageImageTable = galleryPageHtml.find_all('div', attrs={'class': 'gdtm'})
            for imgPageText in galleryPageImageTable:
                imgPageUrls.append(imgPageText.a.get('href'))
            # goto next page
            if maxImageNumberInOnePage == maxImageNumberAllPage:
                break
            else:
                page = page + 1
    
        # TODO check stored image avoid to repeatly download

        pageDataFormat['get_all_images'] = False
        downloadedPage = 0
        for imgPageUrl in imgPageUrls:
            while True:
                htmlText = sd.getPageSource(imgPageUrl)
                imgPageHtml = BeautifulSoup(htmlText, 'html.parser')
                # avoid 503 error
                if imgPageHtml.text.find('Error 503 Service Unavailable') > 0:
                    logging.warning('You got 503 Error with gallery ::{}:: when crawl images. We sleep 60 sec(s).'.format(gallery_id))
                    time.sleep(60)
                else:
                    break
            try:
                imgUrl = imgPageHtml.find_all('img', attrs={'id':'img'})[0].get('src')
                maxPageNumber = int(imgPageHtml.find_all('span')[-1].text)

                # exceed the download limit
                if imgUrl.find('/ehgt.org/g/509.gif') > 0 or imgUrl.find('.org/img/509.gif') > 0 :
                    logging.warning('We got limit to download ...')
                    # give up and crawl tag only
                    crawlTagOnly = True
                    break
                imgName = imgPageHtml.find_all('div')[4].text.split('::')[0].replace(' ', '')
                galleryStorePath = imgDataFolder / Path(str(gallery_id))
                if not galleryStorePath.exists():
                    galleryStorePath.mkdir()
                imgStorePath = galleryStorePath / imgName
                urllib.request.urlretrieve(imgUrl, imgStorePath.absolute().as_posix())
                sd.driver.implicitly_wait(random.randint(1,3))
                downloadedPage = downloadedPage + 1
            except Exception as e:
                cannotDownloadUrlWithGalleryId.append((gallery_id, imgPageUrl))
                logging.warning('"{}" with gallery ::{}::'.format(e, gallery_id))
                time.sleep(3)

        if maxPageNumber == downloadedPage:    
            pageDataFormat['get_all_images'] = 1
        
        if crawlTagOnly:
            pageDataFormat['crawl_tag_only'] = crawlTagOnly


    sd.close()
    return pageDataFormat

