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
from tkinter import ttk
import PIL
from PIL import ImageTk, Image
import os

HEIGHT = 600
WIDTH = 700

LARGE_FONT= ("Verdana", 12)

class Application(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.init_menu(container)

        self.frames = {}
        for F in (HomePage, ImageViewer):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(HomePage)
    
    def init_menu(self, container):
        menu_bar = tk.Menu(container)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command()
        file_menu.add_separator()
        file_menu.add_command(label='Load Image', 
                                command=lambda: controller.show_frame(HomePage))
        file_menu.add_command(label='Exit',
                                command=self.exit_client)
        menu_bar.add_cascade(label='Actions', menu=file_menu)
        
        tk.Tk.config(self, menu=menu_bar)

    def show_frame(self, controller):
        frame = self.frames[controller]
        frame.tkraise()

    def exit_client(self):
        exit()


class HomePage(tk.Frame):
    
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        self.master = master
        label = tk.Label(self,  text="Start Page")
        label.pack(pady=10, padx=10)
        #self.init_menu()
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        self.picture_dir = os.path.join(self.root_dir, "pictures")

    def init_window(self):
        self.master.title("Active Contours")
        self.canvas = tk.Canvas(self.master, height=HEIGHT, width=WIDTH)
        self.canvas.pack()
        self.background_frame = tk.Frame(self.master, bg="#8fbaff")
        self.background_frame.place(relwidth=1, relheight=1)


class ImageViewer(tk.Frame):

    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        #load_image()

    def load_image(self):
        file_name = tk.filedialog.askopenfilename(initialdir=self.picture_dir, 
                                                    title="Select a Picture", 
                                                    filetypes=[("all images","*.pnm *.png *.jpg")])
        my_image = ImageTk.PhotoImage(Image.open(file_name))
        my_image_label = tk.Label(image=my_image).pack()

def main():

    

    MainApp = Application()

    MainApp.geometry(str(WIDTH) + "x" +str(HEIGHT))

    MainApp.mainloop()

if __name__ == '__main__':
    main()


