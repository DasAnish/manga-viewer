import urllib.request as request
import bs4 as bs
import os, time, pickle
import re
import pickle
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from PIL import Image

url_list = ["https://mangapark.net/manga/one-piece",
            "https://mangapark.net/manga/bokutachi-wa-benkyou-ga-dekinai"
            ]
mangapark = 'https://mangapark.net'
DEBUG = True

curDir = os.getcwd()


def print_debug(*args, **kwargs):
    if DEBUG: print(*args, **kwargs)


print_debug(f'Cur Dir: {curDir}')



def get_soup(url):
    with request.urlopen(url) as page:
        _soup = bs.BeautifulSoup(page.read(), 'lxml')
    return _soup

# TODO: change the soup data thing to be a list of strings containing the relavent information
# so that we can keep editing the timer regularly


class MangaParser:

    __instance = None

    @staticmethod
    def get_instance():
        if MangaParser.__instance is None:
            MangaParser.__instance = MangaParser()
        return MangaParser.__instance

    def __init__(self):
        if MangaParser.__instance is not None:
            raise Exception("There should be only on instance")
        else:
            MangaParser.__instance = self
            self.urls = None
            self.manga_viewer = None
            self.parsers = []

            self.executor = ThreadPoolExecutor(max_workers=5)
            self.futures = None

    def set_manga_viewer(self, mangaviewer):
        self.manga_viewer = mangaviewer

    def set_urls(self, urls):
        urls.sort()
        self.urls = urls
        self.parsers = [Parser(url, self.manga_viewer) for url in urls]

    def submit(self):
        self.futures = []
        self.manga_viewer.soup_data = ""
        for parser in self.parsers:
            self.futures.append(self.executor.submit(parser.update_page_url))

    def completed(self):
        ret = []
        for future in as_completed(self.futures):
            # print_debug("***OUTPUT: ", future.result())
            ret.append(future.result())
        return '\n'.join(ret)

class Parser:
    """
    Initialize a parser for all the mangas
    run a main loop with all the parsers in it
    """

    regex = re.compile(r'.*/c(?P<ch>[0-9]+)$')

    def __init__(self, url, mangaViewer):
        self.url = url
        self.page_url = None
        self.mangaViewer = mangaViewer
        # self.chapters = {}
        self.latest_chapter = None
        self.tag_to_latest = None
        self.version = ''
        self.soup = None
        self.soup = get_soup(url)

        self.version, \
        self.latest_chapter,\
        self.tag_to_latest = self.get_latest_info(self.soup)

        # self.thread = None

    @property
    def name(self):
        return " ".join(map(lambda x: x.capitalize(),
                            self.url.split("/")[-1].split("-")))

    @staticmethod
    def get_latest_info(soup):
        print_debug("____GETTING CHAPTERS_____")
        max_chap = 'ch.'
        max_version = None
        max_tag = None
        for div in soup.findAll('div'):
            id = div.get('id')
            # print(id)
            if id is None: continue
            if not id.startswith('stream'): continue

            for span in div.findAll('span'):
                break
            version = span.string.split(' ')[1]

            for ul in div.findAll('ul', attrs={'class': 'chapter'}):
                break
            for li in ul.findAll('li'):
                break

            for a in li.findAll('a'):
                if a.string is not None and a.string.startswith('ch.') and a.get('href') is not None:
                    break
            chap = a.string
            # print(version, chap, div)
            if max_chap < chap:
                max_chap = chap
                max_version = version
                max_tag = a
        print(max_version, max_chap)

        # for a in max_div.findAll('a'):
        #     if a.string is None: continue
        #     strings = a.string.split(' ')
        #     if  strings[-1].startswith('ch.'):
        #         chap = (a.string[3:])
        #         chapters[chap] = a

        return max_version, max_chap, max_tag

    def update_page_url(self):

        def get_latest_chapter():
            _m = max(self.chapters.keys())
            _tag = self.chapters[_m]
            _days = _tag.parent.next_sibling.next_sibling.string.strip()

            return _tag, _days

            # soup = get_soup(self.url)
        tag, days = get_latest_chapter()

        chap = tag.get('href').split('/')[-1][1:]
        ret = f"{self.name}:: {chap}--{days}\n"
        self.mangaViewer.soup_data += ret

        # Downloader.download_chapter(tag)
        return ret


class Downloader:
    '''
    This class will provide some helper function to download stuff
    Think most of this will be staticmethods
    '''

    __instance = None
    __driver = None

    @staticmethod
    def get_instance():
        if Downloader.__instance is None:
            Downloader()
        return Downloader.__instance

    def __init__(self):
        if Downloader.__instance is not None:
            raise Exception("you can't make multiple instances of this")
        else:
            Downloader.__instance = self

        self.__setup()
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.futures = {}
        self.mangaParser = MangaParser.get_instance()

    @staticmethod
    def __setup():
        if Downloader.__driver is not None: return
        options = webdriver.ChromeOptions()
        options.headless = False
        Downloader.__driver = webdriver.Chrome(options=options)

    @staticmethod
    def get(link):
        Downloader.__setup()

        Downloader.__driver.get(link)
        return Downloader.__driver.page_source

    @staticmethod
    def download_chapter_duck(page_source, name, chap, new_path, skip = []):
        print_debug('\n++++++++++starting', name, chap)
        if chap>'717': return None

        soup = bs.BeautifulSoup(page_source, 'lxml')
        for img in soup.findAll('img', attrs={'class': 'img'}):
            file_name = f"{name}_{chap}_{img.get('i')}"
            file_jpg = f'{file_name}.jpg'
            if file_jpg in skip:
                print_debug(f'{file_name}d', end=', ')
                continue
            # print_debug(file_name, end=", ") ##
            src = img.get('src')
            request.urlretrieve(src, f"{file_name}.webp")
            with Image.open(f'{file_name}.webp') as im:
                im.convert("RGB")
                file_path = os.path.join(new_path, file_name)
                im.save(file_jpg, 'jpeg')
            os.remove(f'{file_name}.webp')
        # print_debug('\n----------------finished', name, chap)

    def download_duck(self, parser, all, ch):
        link = parser.url
        # chapters = parser.chapters
        # reg = re.compile(r'^(?P<name>.*)_(?P<chap>[0-9]+)_(?P<page>[0-9]+).jpg$')

        name_chap_re = re.compile(rf'^{mangapark}/manga/(?P<name>.*)/i.*/c(?P<chap>[0-9]+)$')

        dir_name = re.match(rf'^{mangapark}/manga/(?P<name>.*)$', link).group('name').split('-')
        dir_name = '_'.join(i.capitalize() for i in dir_name)
        directory = next(os.walk(curDir))
        new_path = os.path.join(curDir, dir_name)
        # print_debug(curDir, dir_name, new_path)

        if dir_name in directory[1]:
            print_debug("Existed")
        else:
            os.mkdir(new_path)

        # os.chdir(new_path)

        files = next(os.walk(new_path))[2]
        # downloaded_chap = {}
        # for file in files:
        #     match = reg.match(file)
        #     c = int(match.group('chap'))
        #     n = int(match.group('page'))
        #     if c in downloaded_chap: downloaded_chap[c].append(n)
        #     else: downloaded_chap[c] = [n]

        # print_debug('---', len(downloaded_chap))
        # print_debug({chap:len(downloaded_chap[chap]) for chap in downloaded_chap})

        if all:
            tag = parser.tag_to_latest
            l = 'https://mangapark.net/manga/one-piece/i1867490/v63/c617'
            match = name_chap_re.match(l)
            if match is None: print(l)
            name = '_'.join(i.capitalize() for i in match.group('name').split('-'))
            chap = l.split('/')[1:]

            # for one piece
            self.__driver.get(l)
            elem = self.__driver.find_element_by_link_text('◀Prev')

            while elem is not None:
                data = self.__driver.page_source
                url = self.__driver.current_url
                chap = url.split('/')[-1][1:]

                print_debug('\n*********submitting', name, chap, end=" ")
                # print(files, os.path.join(new_path, 'One_Piece_979_1.jpg'))
                # break
                if (name, chap) not in self.futures:
                    future = self.executor.submit(lambda: self.download_chapter_duck(data, name, chap, new_path, files))
                    self.futures[(name, chap)] = future
                # time.sleep(0.1)
                # print_debug('\noooooooo clicking'+url, end="")
                elem.click()

                while True:
                    try:
                        elem = self.__driver.find_element_by_link_text('◀Prev')
                    except NoSuchElementException as e:
                        print(e)
                        elem = None
                    else:
                        break
                    finally:
                        if url == 'https://mangapark.net/manga/one-piece/i1976125/v1/c1':
                            elem = None
                            break


            # chapters_sorted = list(chapters.keys())
            # chapters_sorted.sort(reverse=True)
            # for chapter in chapters_sorted:
            #     tag = chapters[chapter]
            #     link = mangapark + tag.get('href')[:-2]
            #     match = name_chap_re.match(link)
            #     # print(link)
            #     if match is None: print(link)
            #     name = '_'.join([i.capitalize() for i in match.group('name').split('-')])
            #
            #     chap = int(match.group('chap'))
            #     print('here', chap)
            #     if chap >889: continue
            #
            #     data = self.get(link)
            #     print_debug('submitting', name, chap,
            #                 len(downloaded_chap[chap]) if chap in downloaded_chap else 0,
            #                 link)
            #     self.executor.submit(lambda: self.download_chapter_duck(data, name, chap,
            #                                                        skip=downloaded_chap[chap]))
        else:
            for c in ch:
                pass

from threading import Thread

def completed(downloader):
    for future in as_completed(downloader.futures):
        print('--------finished', future)

if __name__ == '__main__':
    link = 'https://mangapark.net/manga/one-piece'
    p = Parser(link, None)
    # os.chdir('One_Piece')
    # Downloader.download_chapter(Downloader.get(link), 'One_Piece', 870)
    # Parser(link, None)
    downloader = Downloader.get_instance()
    downloader.download_duck(p, True, [])