from tkinter.ttk import Label, Button
from datetime import datetime
from MangaViewer.frames import *
from MangaViewer.imageLabel import ImageLabel
from tkinter import font


url_list = ["https://mangapark.net/manga/one-piece"
            ]
# url_list = []


class Reader(DefaultFrame):

    def __init__(self, master, main, progress_tracker, cur_dir):
        self.count = 0
        self.soup_data = None

        DefaultFrame.__init__(self, master, main)
        self.main.bind('<KeyPress>', self.key_pressed)

        self.curDir = cur_dir
        self.progress_tracker = progress_tracker

        ## House keeping information
        self.manga_progress = progress_tracker.current_manga_object

        ## Items
        self.progress_label = Label(self, text="None atm",
                             font=font.Font(size=20))
        self.image_label = ImageLabel(self, self.curDir, anchor='center')

        ## More vars for navigation

    def key_pressed(self, e):
        print(e.keysym)
        if e.keysym == 'Right':
            self.manga_progress.next()
        elif e.keysym == 'Left':
            self.manga_progress.prev()
        elif e.keysym == 'Escape':
            self.main.show_frame(MENU)
        self.image_label.show_image()

    def show_items(self):
        self.main.bind('<KeyPress>', self.key_pressed)
        # self.grid(column=0, row=0)
        self.progress_label.grid(column=0, row=0)
        self.progress_label.config(text=str(self.now))
        self.image_label.grid(column=0, row=1, sticky='wens')
        self.image_label.show_image()

    def hide_items(self):
        self.progress_label.grid_forget()
        # self.grid_forget()
        self.image_label.grid_forget()


    @property
    def now(self):
        return datetime.now().strftime("%H:%M:%S")

    @property
    def soup(self):
        return self.soup_data

    def update_soup(self):
        self.parser.submit()
        return self.parser.completed()

        # self.after(5*60, self.update_soup)

    def after(self, secs, func, *args):
        super(Reader, self).after(secs*1000, func)



# if __name__ == "__main__":
#     root = tk.Tk()
#     tkt = TkThread(root)
#     app = Viewer(root, url_list)
#     tkt(root.mainloop)
#     print_debug("I AM HERE")
#     app.head.config(text=f"{app.count}")





