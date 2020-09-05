from tkinter.ttk import Label
import PIL.Image
import PIL.ImageTk
import os
join = os.path.join


class DeleteBuffer:
    def __init__(self, maxLen=10):
        self.buffer = []
        self.len = 0
        self.max_len = maxLen

    def add(self, item):
        self.buffer.append(item)
        self.len += 1
        if self.len >= self.max_len:
            del self.buffer
            self.buffer = list()


class ImageLabel(Label):

    def __init__(self, master, cur_dir, **kwargs):
        Label.__init__(self, master, **kwargs)
        self.master = master
        self.cur_dir = cur_dir
        self.image = None
        self.buffer = DeleteBuffer()

    def show_image(self, front_page=False):
        manga_object = self.master.progress_tracker.current_manga_object
        if front_page:
            path_to_image = join(self.cur_dir,
                                 'Mangas',
                                 manga_object.name,
                                 manga_object[0])
        else:
            path_to_image = join(self.cur_dir,
                                 'Mangas',
                                 manga_object.name,
                                 manga_object.current_page_name)

        load = PIL.Image.open(path_to_image)
        load = load.resize(self.hw(load), PIL.Image.ANTIALIAS)
        render = PIL.ImageTk.PhotoImage(load)
        self.config(image=render)
        self.image = render

        self.delete(render, load)

    def hw(self, img):
        '''Checks the height according to the aspect ration to adjust it'''
        n=900
        w, h = img.size
        f = n/float(h)
        w=int(f*w)
        h=n
        return w, h

    def delete(self, *items):
        for item in items:
            self.buffer.add(item)
