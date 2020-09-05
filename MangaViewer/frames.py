from tkinter import Frame
import abc

DOWNLOAD, LATEST, MENU, READ = (i for i in range(4))


class DefaultFrame(Frame):

    def __init__(self, parent, main, **kwargs):
        Frame.__init__(self, parent, **kwargs)
        self.master = parent
        self.main = main
        self.configure(bg='black')
        self.grid(column=0, row=0)

    @abc.abstractmethod
    def hide_items(self):
        pass

    @abc.abstractmethod
    def show_items(self):
        pass