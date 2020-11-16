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

 Design Choices:
    1) 

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
MENU_1 = "Pages"
MENU_2 = "Actions"
MENU_3 = "Edit"

LARGE_FONT= ("Verdana", 12)


class Application(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Create menu bar - was in a function but ran into too many errors
        self.menu_bar = tk.Menu(self.container)
        # Pages option
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=MENU_1, menu=self.file_menu)
        #self.file_menu.add_separator()
        self.file_menu.add_command(label='Home Page', 
                                command=lambda: self.frame_enable("HomePage", MENU_2, 0))
        self.file_menu.add_command(label='Image Viewer', 
                                command=lambda: self.frame_enable("ImageViewer", MENU_2, 1))
        self.file_menu.add_command(label='Exit',
                                command=self.exit_client)
        

        tk.Tk.config(self, menu=self.menu_bar)

        # Initalize and stack frames
        self.frames = {}

        for F in (HomePage, ImageViewer):
            page_name = F.__name__
            frame = F(master=self.container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("HomePage")
        self.disable_menu(MENU_2)
        self.disable_menu(MENU_3)

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    def enable_menu(self, option):
        self.menu_bar.entryconfig(option, state="normal")

    def disable_menu(self, option):
        self.menu_bar.entryconfig(option, state="disabled")

    def frame_enable(self, page_name, option, enabler=1):
        """
         Shows the desired frame and enables/disables a menu option of the 
         users choice. Function was created to call 2 functions in 1 menu call

         page_name - the name of the frame to display (string)

         option - the name of the menu option to toggle (string)

         enabler - 1 => enable menu option, 0 => disable menu option 
        """
        if enabler == 1:
            self.show_frame(page_name)
            self.enable_menu(option)
        else:
            self.show_frame(page_name)
            self.disable_menu(option)
        
    def exit_client(self):
        exit()


class HomePage(tk.Frame):
    
    # controller allows functions from the Application
    # class to be accessed in different classes
    # I don't fully understand how this works
    def __init__(self, master, controller):
        tk.Frame.__init__(self, master, bg='#aec8f5')
        self.controller = controller
        self.controller.title('Active Contours')

        #self.controller.state('zoomed') # fills entire screen on load
    

class ImageViewer(tk.Frame):

    def __init__(self, master, controller):
        tk.Frame.__init__(self, master, bg='#FFFFFF')
        self.controller = controller
        self.master = master
        self.controller.title('Active Contours')
        self.canvas = None

        # Add additional menu options
        # Easier to add them to access image editing functions  
        # Actions menu options
        self.file_menu_actions = tk.Menu(controller.menu_bar, tearoff=0)
        controller.menu_bar.add_cascade(label=MENU_2, menu=self.file_menu_actions)
        self.file_menu_actions.add_command(label='Load Image', 
                                command=lambda: self.load_image())
        # Edit image options
        self.file_menu_edit = tk.Menu(controller.menu_bar, tearoff=0)
        controller.menu_bar.add_cascade(label=MENU_3, menu=self.file_menu_edit)
        self.file_menu_edit.add_command(label='Shrink x2', 
                                command=lambda: self.resize_image())
        self.file_menu_edit.add_command(label='Clear', 
                                command=lambda: self.clear_image())


    def load_image(self):
        
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        PICTURE_DIR = os.path.join(ROOT_DIR, "pictures")


        self.file_name = tk.filedialog.askopenfilename(initialdir=PICTURE_DIR, 
                                                    title="Select a Picture", 
                                                    filetypes=[("all images","*.pnm *.png *.jpg")])
        print(self.file_name)

        self.raw_image = Image.open(self.file_name)
        self.image = ImageTk.PhotoImage(self.raw_image)
        self.init_UI()

    def init_UI(self):
        print("width and height of image should be ", self.image.width(), self.image.height())
        self.image_on_canvas = None
        if self.canvas == None:
            self.canvas = tk.Canvas(self, width = self.image.width(), height = self.image.height(), bg='white')
            self.canvas.pack()
            self.canvas.create_image(0, 0, image=self.image, anchor="nw")
        else:
            self.canvas.delete("all")
            self.canvas.config(width=self.image.width(), height=self.image.height())
            self.canvas.create_image(0, 0, image=self.image, anchor="nw")

        #self.canvas.grid(row=0, column=0)
        self.controller.enable_menu(MENU_3)
        self.controller.geometry(str(self.image.width()) + "x" + str(self.image.height()))
        #self.controller.resizable(False, False)

    def resize_image(self):
        self.clear_image()
        max_size = (self.image.width() / 2, self.image.height() / 2)
        self.raw_image.thumbnail(max_size, Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(self.raw_image)
        self.init_UI()
        
    def clear_image(self):
        self.canvas.delete(self.image)
        self.controller.geometry(str(WIDTH) + "x" +str(HEIGHT))


def main():

    MainApp = Application()
    MainApp.geometry(str(WIDTH) + "x" + str(HEIGHT))
    MainApp.mainloop()

if __name__ == '__main__':
    main()


