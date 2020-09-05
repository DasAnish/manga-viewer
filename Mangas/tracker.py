import os
from pickle import load, dump
join = os.path.join


class MangaProgress:
    def __init__(self, name = None, url=None, indict=None):

        self.name = self.current_page = self.cur_dir = \
            self.path = self.chapters = self.max = self.url = None
        if name is not None and url is not None:
            self.setup(name, url)
        if indict is not None:
            self.load(indict)
        if (name is None or url is None) and indict is None:
            raise ValueError("No name or indict provided")

    def setup(self, name, url):
        self.name = name
        self.url = url
        self.current_page = 0
        self.cur_dir = os.path.join(os.getcwd(), 'Mangas')
        self.path = os.path.join(self.cur_dir,
                                 '_'.join(name.split(' ')) )
        self.chapters = self.get_chapters()
        self.max = len(self.chapters)

    def get_chapters(self):
        # print(self.path)

        def sort_key(x):
            chap, page = x.split('_')[-2:]
            chap = int(float(chap)*1000)
            page = int(page.split('.')[0])
            # print(chap+page, __name__)
            return chap+page


        for i in os.walk(self.path):
            # print(i[2])
            out = i[2]
            out = [i for i in out if i != self.name]
            out.sort(key=sort_key)
            return out

    def __getitem__(self, item):
        if not isinstance(item, int):
            raise ValueError("Integer expected")
        item %= self.max
        # self.current_page = item
        return self.chapters[item]

    def next(self):
        self.current_page += 1
        self.current_page %= self.max
        return self[self.current_page]

    def prev(self):
        self.current_page += 1
        self.current_page %= self.max
        return self[self.current_page]


    @property
    def current_page_name(self):
        return self[self.current_page]

    def dump(self):
        output = {
            'name': self.name,
            'url': self.url,
            'current_page':self.current_page,
            'cur_dir': self.cur_dir,
            'path': self.path,
            'chapters': self.chapters,
            'max': self.max
        }

        return output

    def load(self, indict):
        self.name = indict['name']
        self.url = indict['url']
        self.current_page = indict['current_page']
        self.cur_dir = indict['cur_dir']
        self.chapters = indict['chapters']
        self.max = indict['max']
        self.path = indict['path']


class OverallProgress:

    __path_to_tracker = None

    def __init__(self, cur_dir):
        # print(__name__, cur_dir) ## cur_dir = ./MangaReader/Mangas
        if self.__path_to_tracker is None:
            self.__path_to_tracker = join(cur_dir,
                                          'tracking',
                                          'OverallProgress.dat')

        if os.path.exists(self.__path_to_tracker):
            self.load()
        else:
            self.cur_dir = cur_dir
            self.current_manga = 0
            # self.max = 1
            self.path = cur_dir
            self.mangas = OverallProgress.get_mangas(self.path)
            self.max = len(self.mangas)

    @property
    def current_manga_object(self):
        return self[self.current_manga]

    @staticmethod
    def get_mangas(path):
        for obj in os.walk(path):
            break
        mangas = obj[1]
        # print(path, mangas)
        output = list()
        for manga in mangas:
            if manga in ['tracking', '__pycache__']: continue

            name = '_'.join(manga.split(' '))
            manga_object_path = join(path, 'tracking', f"{name}.dat")
            if os.path.exists(manga_object_path):
                with open(manga_object_path, 'rb') as f:
                    indict = load(f)
                    # print(indict)
                output.append(MangaProgress(indict=indict))
            else:
                output.append(MangaProgress(name=manga))

        return output

    def __getitem__(self, item):
        if not isinstance(item, int):
            raise ValueError("Expected an Integer")

        item %= self.max
        # self.current_manga = item
        return self.mangas[item]

    def next(self):
        self.current_manga += 1
        self.current_manga %= self.max
        return self.mangas[self.current_manga]

    def prev(self):
        self.current_manga -= 1
        self.current_manga %= self.max
        return self.mangas[self.current_manga]

    def dump(self):
        print ("****STARTING***DUMP******")
        for manga in self.mangas:
            output = manga.dump()
            with open(join(self.cur_dir, 'tracking', f"{manga.name}.dat"), 'wb') as f:
                dump(output, f)

        del self.mangas
        with open(self.__path_to_tracker, 'wb') as f:
            dump(self, f)

    def load(self):
        with open(self.__path_to_tracker, 'rb') as f:
            obj= load(f)

        self.mangas = OverallProgress.get_mangas(obj.path)
        self.path = obj.cur_dir
        self.current_manga = obj.current_manga
        self.max = len(self.mangas)
        self.cur_dir = obj.cur_dir


if __name__ == '__main__':
    progress = OverallProgress()
