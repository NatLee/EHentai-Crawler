
# EHentai Crawler

Crawl tags and images from EHentai or ExHentai.

## Description

This crawler can help user to fetch information and images from EHentai by mocking browsers behavior with selenium.

There are many **hard coding** used to avoid some errors in these codes because this project is developed in few days.

I only run this program at Windows 10 build 1903. You can help me to test at other OS.

At last, if you find a critical error or want to make this project better, just pull requests! Thank you!

## Usage 

You may need to install some packages by using the command as following.

`pip install -r requirements.txt`

Then, you can read the help by executing `python main.py` and the result is shown in below.

```
usage: main.py [-h] [--crawl_list [CRAWL_LIST]]
               [--update_crawl_list [UPDATE_CRAWL_LIST]]
               [--crawl_each_page [CRAWL_EACH_PAGE]]
               [--crawl_tag_only [CRAWL_TAG_ONLY]]

EHentai Crawler: You need crawl list to get list information from ehentai at
first. Second, you can only crawl tags or both tags and images.

optional arguments:
  -h, --help            show this help message and exit
  --crawl_list [CRAWL_LIST]
                        Crawl EHentai page list.
  --update_crawl_list [UPDATE_CRAWL_LIST]
                        Crawl EHentai page list and update with time check.
  --crawl_each_page [CRAWL_EACH_PAGE]
                        Crawl EHentai tags and save images for each page.
  --crawl_tag_only [CRAWL_TAG_ONLY]
                        Crawl EHentai tags for each page.
```

And we use Chrome as our browser with selenium, so you need to install [Chrome](https://www.google.com/chrome/).

Selenium operate the browser with [Chromedriver](https://chromedriver.chromium.org/) and ours version in `.\chromedriver` is **75.0.3770.140**.

## Start

First, you must set some settings in the file,`setting.ini`.

**!!!THE NUMBER OF THREAD YOU SET MORE, THE PROBILITY OF IP BAN IS GETTING MORE!!!**

### Step: Indexing

Indexing is very important, so we need to crawl the index list.

`python .\main.py --crawl_list`

This may take about 25 hours to crawl the list from the EHentai index. I'll make it parallelly work in the future.

### Step: Crawl information

Then, we start to crawl images and information which likes tags, rating, the number of favorite for each gallery by using the command below. A lot of image files will take up a lot of space, so you may need to prepare a larger storage disk.

`python .\main.py --crawl_each_page`

Or, you just want information, we can use this.

`python .\main.py crawl_tag_only`

This step can take a very long time, and each IP has a limit on the number of image downloads. 

Even if you only grab the general information, it will take a lot of time. 

But, I have no idea to solve this problem now.


### Data

All data you can find in the file `list.db` created in the first run and images are in the folder you assign in the `settings.ini`.

The file `list.db` belongs to `SQLite` format.

I suggest that you can use this tool [DB Browser for SQLite](https://sqlitebrowser.org/) to easily veiw the details.


