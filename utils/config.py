
import configparser
from pathlib import Path

CONFIG = configparser.ConfigParser()
CONFIG.read('setting.ini')

exMode = CONFIG.getboolean('Mode', 'EX_MODE')
headless = CONFIG.getboolean('Mode', 'HEADLESS')

if not exMode:
    indexUrl = CONFIG.get('HentaiUrl', 'EHENTAI_INDEX')
    listUrl = CONFIG.get('HentaiUrl', 'EHENTAI_LIST')
    galleryUrl = CONFIG.get('HentaiUrl', 'EHENTAI_GALLERY')
else:
    indexUrl = CONFIG.get('HentaiUrl', 'EXHENTAI_INDEX')
    listUrl = CONFIG.get('HentaiUrl', 'EXHENTAI_LIST')
    galleryUrl = CONFIG.get('HentaiUrl', 'EXHENTAI_GALLERY')  

ipbPassId = CONFIG.get('ExHentaiAccess', 'IPB_MEMBER_ID')  
ipbHash = CONFIG.get('ExHentaiAccess', 'IPB_PASS_HASH')  


numberOfThread = CONFIG.getint('Parallel', 'NUMBER_OF_THREAD')


imgDataFolder = Path(CONFIG.get('ImageFolder', 'IMAGE_FOLDER_PATH'))
if not imgDataFolder.exists():
    imgDataFolder.mkdir()