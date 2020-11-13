"""
 main.py
 Bradley Selee
 ECE 6310 Fall 2020
 Graduate Project

 Purpose:

 Assumptions:
    1) 

 Bugs:
    1) Running this project in a git bash with "python main.py"
        - fix: Run in git bash using "py main.py"

 Dependencies:
    Run these commands on a windows command line
    1) pip install pillow

 Defintions:
    Canvas - main screen to work with
    Frame - organize widgets

"""
import tkinter as tk
import tkinter.filedialog
import PIL
from PIL import ImageTk, Image
import os

HEIGHT = 600
WIDTH = 700
TITLE = "Active Contours"

LARGE_FONT= ("Verdana", 12)

def load_image():

    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    PICTURE_DIR = os.path.join(ROOT_DIR, "pictures")

    file_name = tk.filedialog.askopenfilename(initialdir=PICTURE_DIR, 
                                                title="Select a Picture", 
                                                filetypes=[("all images","*.pnm *.png *.jpg")])
    load = Image.open(file_name)
    render = ImageTk.PhotoImage(load)
    img = tk.Label(image=render)
    img.image = render
    img.place(x=0, y=0)


class Application(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        for F in (HomePage, ImageViewer):
            page_name = F.__name__
            frame = F(master=container, controller=self)
            self.frames[page_name] = frame
            
            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("HomePage")
        self.init_menu(container)

    
    def init_menu(self, container):
        menu_bar = tk.Menu(container)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command()
        file_menu.add_separator()
        file_menu.add_command(label='Load Image', 
                                command=lambda: load_image())
        file_menu.add_command(label='Exit',
                                command=self.exit_client)
        menu_bar.add_cascade(label='Actions', menu=file_menu)
        
        tk.Tk.config(self, menu=menu_bar)

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    def exit_client(self):
        exit()


class HomePage(tk.Frame):
    
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master, bg='red')
        self.controller = controller
        self.controller.title('Active Contours')
        #self.controller.state('zoomed') # fills entire screen on load
        

    def init_window(self):
        self.master.title("Active Contours")
        self.canvas.pack()
        self.background_frame = tk.Frame(self.master, bg="#8fbaff")
        self.background_frame.place(relwidth=1, relheight=1)


class ImageViewer(tk.Frame):

    def __init__(self, master, controller):
        tk.Frame.__init__(self, master, bg="green")
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        self.picture_dir = os.path.join(self.root_dir, "pictures")
        label = tk.Label(self,  text="ImageViewer Page")
        label.pack(pady=10, padx=10)


def main():

    MainApp = Application()
    MainApp.geometry(str(WIDTH) + "x" +str(HEIGHT))


    MainApp.mainloop()

if __name__ == '__main__':
    main()


