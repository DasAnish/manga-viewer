from MangaViewer.frames import *
from MangaViewer.imageLabel import ImageLabel
from tkinter.ttk import Label, Button
from tkinter import font


class Menu(DefaultFrame):

    def __init__(self, master, main, progress_tracker, cur_dir):

        DefaultFrame.__init__(self, master, main)
        self.image_label = ImageLabel(self, cur_dir, anchor='center')
        self.info_label = Label(self, text='to be implmented',
                                font=font.Font(size=20))
        self.info_label.configure(background='#000000', foreground='#FFFFFF')
        self.update_button = Button(self, text='UPDATE',
                                    command=lambda:print("Not Implmented"),
                                    width=40)
        self.add_button = Button(self, text="Add Manga",
                                 command=lambda: print("Not Implemented"),
                                 width=40)

        self.cur_dir = cur_dir
        self.progress_tracker = progress_tracker

    def show_items(self):
        # self.grid(column=0, row=0)
        self.main.bind('<KeyPress>', self.key_pressed)
        self.image_label.grid(column=0, row=2, columnspan=3)
        self.info_label.config(text=self.manga_info)
        self.info_label.grid(column=0, row=0, columnspan=3)
        self.update_button.grid(column=0, row=1, sticky='N')
        self.add_button.grid(column=1, row=1, sticky='N')
        print(self.manga_info)
        # self.info_label.config(text=self.manga_info)
        self.image_label.show_image(front_page=True)
        print(self.progress_tracker.current_manga_object[0])

    def hide_items(self):
        # self.grid_forget()
        self.image_label.grid_forget()
        self.info_label.grid_forget()
        self.add_button.grid_forget()
        self.update_button.grid_forget()

    def key_pressed(self, e):
        if e.keysym == 'Left':
            self.progress_tracker.next()
        elif e.keysym == 'Right':
            self.progress_tracker.prev()
        elif e.keysym == 'Return':
            self.main.show_frame(READ)
            return

        self.info_label.config(text=self.manga_info)
        print(self.manga_info)
        self.image_label.show_image(front_page=True)

    @property
    def manga_info(self):
        st = ''
        manga_obj = self.progress_tracker.current_manga_object
        st = f'{manga_obj.name}  ' \
             f'{manga_obj.current_page}  ' \
             f'{manga_obj.max}'
        return st

    def update_manga(self):
        '''The function that is called when you click the UPDATE button and it will
        check for the latest additions to the manga.'''

        manga_obj = self.progress_tracker.current_manga_object
