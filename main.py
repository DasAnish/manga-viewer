from tkinter import Tk, Frame, font
from tkinter.ttk import Button, Style
from MangaViewer.reader import Reader
from MangaViewer.menu import Menu
from MangaViewer.frames import *
from Mangas.tracker import *
from tkthread import tk, TkThread
from threading import Thread


class Main(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.tkt = TkThread(self)
        # self.pack()

        self.geometry("1600x990")

        container = Frame(self)
        container.grid(column=0, row=0, columnspan=4)
        cur_dir = os.getcwd()

        self.style = Style()
        self.style.configure('TButton', background='black', relief='flat')
        self.style.configure('TLabel', background='black', foreground='white')
        # self.style.configure('TButton', foreground='white')
        self.style.theme_use('vista')
        self.configure(bg='black')
        container.configure(bg='black')

        self.current_frame = None

        self.download_button = Button(self, text="Download",
                                      command=(lambda: self.show_frame(DOWNLOAD)),
                                      width=65)
        self.latest_button = Button(self, text="Latest",
                                    command=(lambda: self.show_fame(LATEST)),
                                    width=65)
        self.source_button = Button(self, text="Menu",
                                    command=(lambda: self.show_frame(MENU)),
                                    width=65)
        self.read_button = Button(self, text="Read",
                                  command=(lambda: self.show_frame(READ)),
                                  width=65)

        self.download_button.grid(column=0 , row=1)
        self.latest_button.grid(column= 1, row=1)
        self.source_button.grid(column= 2, row=1)
        self.read_button.grid(column= 3, row=1)

        self.progress_tracker = OverallProgress(os.path.join(cur_dir, 'Mangas'))

        self.frames = {READ: Reader(container, self, self.progress_tracker, cur_dir),
                       MENU:   Menu(container, self, self.progress_tracker, cur_dir)
                       }

        self.show_frame(MENU)
        # print("showing frame")

    def show_frame(self, new):
        if self.current_frame is not None:
            self.current_frame.hide_items()

        self.current_frame = self.frames[new]
        self.current_frame.show_items()
        self.current_frame.tkraise()

    def mainloop(self, n=0):
        # tkt = tkthread.TkThread(self)
        self.tkt(lambda:Tk.mainloop(self, n))
        # self.progress_tracker.dump()
        return self

if __name__ == "__main__":
    Main().mainloop().progress_tracker.dump()