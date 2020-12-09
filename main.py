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
    1) pillow
    2) tkinter

 Design Choices:
    1) 

"""
import tkinter as tk
import tkinter.filedialog
import PIL # Python Image Library
from PIL import ImageTk, Image
from math import sqrt
import os
import time

HEIGHT = 600
WIDTH = 700

TITLE = "Active Contours"
MENU_1 = "Pages"
MENU_2 = "Actions"
MENU_3 = "Edit"
MENU_4 = "Debug"

LARGE_FONT= ("Verdana", 12)

# General Parameters
ITERATIONS = 150
UPDATE_SPEED = 0.02 # Time Time in seconds 
OVAL_RADIUS = 5
OUTLINE_COLOR = 'blue' # 'black'
WINDOW_SIZE = 7

# Balloon Model Parameters
CIRCLE_RADIUS = 10
CONTOUR_DELETION_BALLOON = 3 # keep every i'th point

# Rubber-band Model Parameters 
CONTOUR_DELETION = 5 # keep every i'th contour point 
REQUIRED_POINTS = 8 # The number of required points in a contour line

# Set this term to 0 if you wish to exclude an energy 
# Rubber-band Model Parameters
ALPHA = 1.0 # Internal energy factor -> stretch/elasticity factor
BETA = 1.0  # Internal energy factor -> curvature factor
GAMMA = 0.0 # External energy factor -> negative gradient magnitude
DELTA = 0.0 # External energy factor -> grayscale intensity
EPSILON = 1.0 # External energy factor -> gradient vector flow/field

# Balloon model parameters
ALPHA_BALLOON = -1.0 # Internal energy factor -> stretch/elasticity factor
BETA_BALLOON = -1.0  # Internal energy factor -> curvature factor
GAMMA_BALLOON = 0.0 # External energy factor -> negative gradient magnitude
DELTA_BALLOON = 0.0 # External energy factor -> grayscale intensity
EPSILON_BALLOON = 4.0 # External energy factor -> gradient vector flow/field

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
        self.image_status = None # Track which image is loaded

        # Convolution Properties
        self.GAUSSIAN_SIZE = 5
        self.GAUSSIAN_TEMPLATE = [1,  4,  6,  4,  1,
                                  4, 16, 24, 16,  4,
                                  6, 24, 36, 24,  6,
                                  4, 16, 24, 16,  4,
                                  1,  4,  6,  4,  1]
        self.GAUSSIAN_1D = [1,  4,  6,  4,  1]
        self.GAUSSIAN_BLUR = [i * (1/16) for i in self.GAUSSIAN_1D]
        self.GAUSSIAN_BLUR_2 = [i * (1/256) for i in self.GAUSSIAN_TEMPLATE]
        self.SOBEL_SIZE = 3
        self.SOBEL_X = [-1,  0, 1,
                        -2,  0, 2,
                        -1,  0, 1]
        self.SOBEL_Y = [-1, -2, -1,
                         0,  0,  0,
                         1,  2,  1]

        # Properties to store the contour points 
        self.oval_coords = {"x":0,"y":0,"x2":0,"y2":0}
        self.final_ovals_coords = []
        self.contour_lines = []
        self.ovals_references = []
        self.final_ovals_references = []
        self.contour_lines_references = []
        self.balloon_final_ovals_coords = []
        self.balloon_ovals_references = []
        self.balloon_final_ovals_references = []
        self.balloon_contour_lines = []
        self.balloon_contour_lines_references = []
        self.contour_start = 0 # used for contour point deletion
        self.balloon_contour_start = 0

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
        self.file_menu_edit.add_command(label='Original', 
                                command=lambda: self.image_to_original())
        self.file_menu_edit.add_command(label='Grayscale', 
                                command=lambda: self.image_to_grayscale(0))
        self.file_menu_edit.add_command(label='Gaussian Blur', 
                                command=lambda: self.gaussian_smoothing(0, "grayscale"))
        self.file_menu_edit.add_command(label='Red Channel', 
                                command=lambda: self.image_to_channels(self.red_channel))
        self.file_menu_edit.add_command(label='Blue Channel', 
                                command=lambda: self.image_to_channels(self.blue_channel))
        self.file_menu_edit.add_command(label='Green Channel', 
                                command=lambda: self.image_to_channels(self.green_channel))
        self.file_menu_edit.add_command(label='Gradient X', 
                                command=lambda: self.sobel_filter(0, "grayscale"))
        self.file_menu_edit.add_command(label='Gradient Y', 
                                command=lambda: self.sobel_filter(1, "grayscale"))
        self.file_menu_edit.add_command(label='Edges', 
                                command=lambda: self.sobel_filter(2, "grayscale"))
        self.file_menu_edit.add_command(label='Edges Inverted', 
                                command=lambda: self.sobel_filter(3, "grayscale"))
        self.file_menu_edit.add_command(label='Edges Blurred', 
                                command=lambda: self.gaussian_smoothing(1, "edges"))
        self.file_menu_edit.add_command(label='Gradient Vector Field (GVF)', 
                                command=lambda: self.sobel_filter(4, "blur"))
        self.file_menu_edit.add_command(label='GVF Inverted', 
                                command=lambda: self.sobel_filter(5, "blur"))
        self.file_menu_edit.add_command(label='Clear', 
                                command=lambda: self.clear_image())
        # Debug menu options
        self.file_menu_debug = tk.Menu(controller.menu_bar, tearoff=0)
        controller.menu_bar.add_cascade(label=MENU_4, menu=self.file_menu_debug)
        self.file_menu_debug.add_command(label='Contour Information', 
                                command=lambda: self.contour_stats_debug())
        self.file_menu_debug.add_command(label='Internal Engery Curvature', 
                                command=lambda: self.energy_calculations())
        self.file_menu_debug.add_command(label='Active Contours - Rubber Band', 
                                command=lambda: self.active_contours(model="rubber-band"))
        self.file_menu_debug.add_command(label='Active Contours - Balloon', 
                                command=lambda: self.active_contours(model="balloon"))

    def load_image(self):
        # Clear variables from previous image
        self.grayscale_pixels = []
        self.grayscale_pixels_norm_one = []
        #self.red_pixels = []
        #self.red_channel = []
        #self.green_pixels = []
        #self.green_channel = []
        #self.blue_pixels = []
        #self.blue_channel = []
        self.gaussian_blur_pixels = []
        self.sobel_x_pixels = []
        self.sobel_x_pixels_norm = []
        self.sobel_y_pixels = []
        self.sobel_y_pixels_norm = []
        self.sobel_mag_pixels = []
        self.sobel_mag_pixels_norm = []
        self.sobel_x_blur_pixels = []
        self.sobel_y_blur_pixels = []
        self.edges_blur_pixels = [] 
        self.edges_blur_pixels_norm = [] 
        self.edges_blur_pixels_norm_one = []
        self.gvf_pixels = [] 
        self.gvf_pixels_negative = []
        self.gvf_pixels_norm = [] 
        self.gvf_pixels_norm_one = [] 
        self.gvf_pixels_norm_inverted = [] 
        self.clear_image()

        self.image_status = "original"
        
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        PICTURE_DIR = os.path.join(ROOT_DIR, "pictures")
        self.file_name = tk.filedialog.askopenfilename(initialdir=PICTURE_DIR, 
                                                    title="Select a Picture", 
                                                    filetypes=[("all images","*.ppm *.pnm *.png *.jpg")])
        print(self.file_name)

        # Load image/pixel data and save as variables i'm used to
        self.original_image = Image.open(self.file_name)
        self.COLS, self.ROWS = self.original_image.size
        self.image_type = self.original_image.mode
        self.original_pixels = list(self.original_image.getdata())
        if self.image_type != 'L':
            self.red_channel = [(d[0],0,0) for d in self.original_pixels]
            self.red_pixels = [d[0] for d in self.original_pixels]
            min_val, max_val = min(self.red_pixels), max(self.red_pixels)
            self.red_pixels_norm_one = [(((i - min_val) * 1) / (max_val - min_val)) for i in self.red_pixels]
            self.green_channel = [(0, d[1], 0) for d in self.original_pixels]
            self.green_pixels = [d[1] for d in self.original_pixels]
            min_val, max_val = min(self.green_pixels), max(self.green_pixels)
            self.green_pixels_norm_one = [(((i - min_val) * 1) / (max_val - min_val)) for i in self.green_pixels]
            self.blue_channel = [(0, 0, d[2]) for d in self.original_pixels]
            self.blue_pixels = [d[2] for d in self.original_pixels]
            min_val, max_val = min(self.blue_pixels), max(self.blue_pixels)
            self.blue_pixels_norm_one = [(((i - min_val) * 1) / (max_val - min_val)) for i in self.blue_pixels]
            

        # Perform convolutions and image processing on image load
        self.image_to_grayscale(4)
        self.gaussian_smoothing(4, "grayscale")
        self.sobel_filter(6,"blur")
        if GAMMA > 0.0:
            self.sobel_filter(6,"grayscale")
            self.gaussian_smoothing(4, "edges")


        self.init_UI(self.original_image)


    def init_UI(self, image_loader):
        """
         Initialize the canvas and load the chosen image

         image_loader - a PIL.Image object to be loaded.
        """
        self.image = ImageTk.PhotoImage(image_loader)
        if self.canvas == None:
            self.canvas = tk.Canvas(self, width = self.image.width(), height = self.image.height(), bg='white', cursor="cross")
            self.canvas.pack()
            self.canvas.create_image(0, 0, image=self.image, anchor="nw")
            self.init_mouse_events()
        else:
            self.canvas.delete("all")
            self.canvas.config(width=self.image.width(), height=self.image.height())
            self.canvas.create_image(0, 0, image=self.image, anchor="nw")

        self.controller.enable_menu(MENU_3)
        self.controller.geometry(str(self.image.width()) + "x" + str(self.image.height()))
        #self.controller.resizable(False, False)


    def pixels_to_grayscale(self):
        """ Convert grayscale pixels and store in property """
        ROWS = self.ROWS
        COLS = self.COLS
        if self.image_type == 'L': # if original image is already grayscale
            for r in range(ROWS):
                for c in range(COLS):
                    self.grayscale_pixels.append(self.original_pixels[r*COLS+c])
            return

        self.grayscale_pixels = []
        for r in range(ROWS):
            for c in range(COLS):
                pixel = self.original_pixels[r*COLS+c]
                pixel_average = int(sum(pixel) / len(pixel) + 0.5)
                self.grayscale_pixels.append(pixel_average)


    def image_to_grayscale(self, mode):
        """ Calculate grayscale version of RGB image """
        if self.image_status == "grayscale":
            return
            
        if self.grayscale_pixels == []:
            self.pixels_to_grayscale()
            min_val, max_val = min(self.grayscale_pixels), max(self.grayscale_pixels)
            self.grayscale_pixels_norm_one = [(((i - min_val) * 1) / (max_val - min_val)) for i in self.grayscale_pixels]
        
        if mode == 0:
            self.image_status = "grayscale"
            new_image = Image.new(mode="L", size = (self.COLS, self.ROWS))
            new_image.putdata(self.grayscale_pixels)
            #new_image.save("grayscale.pnm")
            self.grayscale_image = new_image
            self.init_UI(self.grayscale_image)
            print("Grayscale Loaded")
        else:
            return


    def image_to_channels(self, channel):
        """Load the R, G, or B channel of the image"""
        self.image_status = "channel"
        new_image = Image.new(mode="RGBA", size = (self.COLS, self.ROWS))
        new_image.putdata(channel)
        self.channel_image = new_image
        self.init_UI(self.channel_image)
        print("Channel Loaded")


    def convolution_seperable(self, kernel, kernel_size, image):
        """ 
         Convolve the loaded image with separable filters 
        
         image - a string denoting which pixels to blur
                 "grayscale" to blur grayscale image
                 "edges" to blur the sobel magnitude
        """
        ROWS = self.ROWS
        COLS = self.COLS
        self.temp_pixels = [] # store the intermediate steps of convolution
        self.convolution_pixels = []

        # Compute grayscale pixels if not already done
        if self.grayscale_pixels == []:
            self.pixels_to_grayscale()

        pixels_to_convolve = []
        if image == "grayscale":
            pixels_to_convolve = self.grayscale_pixels
        elif image == "edges":
            pixels_to_convolve = self.sobel_mag_pixels

        r2 = 0
        for r in range(ROWS):
            for c in range(COLS): 
                pixel_sum = 0
                kernel_index = 0
                for c2 in range(-1*(kernel_size//2), (kernel_size//2)+1):
                    if((c + c2 < 0) or (c + c2 >= COLS)):
                        pixel_sum += 0
                    else:
                        pixel_sum += pixels_to_convolve[((r+r2)*COLS)+(c+c2)] * kernel[kernel_index]
                    kernel_index = kernel_index + 1
                self.temp_pixels.append(pixel_sum)

        c2 = 0
        for r in range(ROWS):
            for c in range(COLS): 
                
                kernel_index = 0
                pixel_sum = 0
                for r2 in range(-1*(kernel_size//2), (kernel_size//2)+1):
                    if((r + r2 < 0) or (r + r2 >= ROWS)):
                        pixel_sum += 0
                    else:
                        pixel_sum += self.temp_pixels[((r+r2)*COLS)+(c+c2)] * kernel[kernel_index]
                    kernel_index = kernel_index + 1
                self.convolution_pixels.append(int(pixel_sum + 0.5))

    def convolution_2d(self, kernel, kernel_size, image):
        """ 
         Convolve the loaded image with 2d convolution filters
        
         image - a string denoting which pixels to blur
                 "grayscale" to blur grayscale image
                 "edges" to blur the sobel magnitude and create the gradient vector flow 
        """
        ROWS = self.ROWS
        COLS = self.COLS
        self.temp_pixels = [] # store the intermediate steps of convolution
        self.convolution_pixels = []

        # Compute grayscale pixels if not already done
        if self.grayscale_pixels == []:
            self.pixels_to_grayscale()

        pixels_to_convolve = []
        if image == "grayscale":
            pixels_to_convolve = self.grayscale_pixels
        elif image == "blur":
            pixels_to_convolve = self.gaussian_blur_pixels

        for r in range(ROWS):
            for c in range(COLS): 
                
                kernel_index = 0
                pixel_sum = 0
                for r2 in range(-1*(kernel_size//2), (kernel_size//2)+1):
                    for c2 in range(-1*(kernel_size//2), (kernel_size//2)+1):
                        if (c + c2 < 0) or (c + c2 >= COLS) or (r + r2 < 0) or (r + r2 >= ROWS):
                            pixel_sum += 0
                        else:
                            pixel_sum += pixels_to_convolve[((r+r2)*COLS)+(c+c2)] * kernel[kernel_index]
                        kernel_index = kernel_index + 1
                self.convolution_pixels.append(pixel_sum)


    def gaussian_smoothing(self, mode, image):
        """
         Calculate gaussian blur and gvf if not already done, then dispaly either image
        
         mode - 0 -> grayscale blur, 1 -> edges blur 
        """
        if self.image_status == "gaussian":
            return

        if self.gaussian_blur_pixels == []:
            if image == "grayscale":
                self.convolution_seperable(self.GAUSSIAN_BLUR, self.GAUSSIAN_SIZE, image)
                self.gaussian_blur_pixels = self.convolution_pixels
                new_image = Image.new(mode="L", size = (self.COLS, self.ROWS))
                new_image.putdata(self.gaussian_blur_pixels)
                self.gaussian_image = new_image
        if self.edges_blur_pixels == []:
            if image == "edges":
                self.convolution_seperable(self.GAUSSIAN_BLUR, self.GAUSSIAN_SIZE, image)
                self.edges_blur_pixels = self.convolution_pixels
                min_val, max_val = min(self.edges_blur_pixels), max(self.edges_blur_pixels)
                self.edges_blur_pixels_norm = [(((i - min_val) * 255) / (max_val - min_val)) for i in self.edges_blur_pixels]
                self.edges_blur_pixels_norm_one = [(((i - min_val) * 1) / (max_val - min_val)) for i in self.edges_blur_pixels]
                new_image = Image.new(mode="L", size = (self.COLS, self.ROWS))
                new_image.putdata(self.edges_blur_pixels_norm)
                self.edges_blur_image = new_image
            
        if mode == 0:
            self.image_status = "gaussian"
            self.init_UI(self.gaussian_image)
            print("Gaussian Smoothing Loaded")
        if mode == 1:
            self.image_status = "edges blur"
            self.init_UI(self.edges_blur_image)
            print("Blurred edge loaded")
        else:
            return


    def sobel_filter(self, mode, image):
        """
         compute x and y gradients of the sobel filter along with the magnitude image

         mode - which sobel image to display
                    0 -> x gradient
                    1 -> y gradient
                    2 -> magnitude gradient
        """
        if self.sobel_x_pixels == []:
            if image == "grayscale":
                self.convolution_2d(self.SOBEL_X, self.SOBEL_SIZE, image)
                self.sobel_x_pixels = self.convolution_pixels
                min_val, max_val = min(self.sobel_x_pixels), max(self.sobel_x_pixels)
                self.sobel_x_pixels_norm = [(((i - min_val) * 255) / (max_val - min_val)) for i in self.sobel_x_pixels]
        if self.sobel_x_blur_pixels == []:
            if image == "blur":
                self.convolution_2d(self.SOBEL_X, self.SOBEL_SIZE, "blur")
                self.sobel_x_blur_pixels = self.convolution_pixels
        if self.sobel_y_pixels == []:
            if image == "grayscale":
                self.convolution_2d(self.SOBEL_Y, self.SOBEL_SIZE, image)
                self.sobel_y_pixels = self.convolution_pixels
                min_val, max_val = min(self.sobel_y_pixels), max(self.sobel_y_pixels)
                self.sobel_y_pixels_norm = [(((i - min_val) * 255) / (max_val - min_val)) for i in self.sobel_y_pixels]
        if self.sobel_y_blur_pixels == []:
            if image == "blur":
                self.convolution_2d(self.SOBEL_Y, self.SOBEL_SIZE, image)
                self.sobel_y_blur_pixels = self.convolution_pixels
        if self.sobel_mag_pixels == []:
            if image == "grayscale":
                self.sobel_mag_pixels = [sqrt((self.sobel_x_pixels[index]*self.sobel_x_pixels[index]) + (self.sobel_y_pixels[index]*self.sobel_y_pixels[index]) )  for index in range(self.ROWS*self.COLS)]
                self.sobel_mag_pixels_negative = [-1 * value for value in self.sobel_mag_pixels]
                min_val, max_val = min(self.sobel_mag_pixels), max(self.sobel_mag_pixels)
                self.sobel_mag_pixels_norm = [(((i - min_val) * 255) / (max_val - min_val)) for i in self.sobel_mag_pixels]
                min_val, max_val = min(self.sobel_mag_pixels_negative), max(self.sobel_mag_pixels_negative)
                self.sobel_mag_pixels_norm_inverted = [(((i - min_val) * 255) / (max_val - min_val)) for i in self.sobel_mag_pixels_negative]
                self.sobel_mag_pixels_norm_one = [(((i - min_val) * 1) / (max_val - min_val)) for i in self.sobel_mag_pixels_negative]
                print("Sobel done")
        if self.gvf_pixels == []:
            if image == "blur":
                self.gvf_pixels = [sqrt((self.sobel_x_blur_pixels[index]*self.sobel_x_blur_pixels[index]) + (self.sobel_y_blur_pixels[index]*self.sobel_y_blur_pixels[index]))  for index in range(self.ROWS*self.COLS)]
                self.gvf_pixels_negative = [-1 * value for value in self.gvf_pixels]
                min_val, max_val = min(self.gvf_pixels), max(self.gvf_pixels)
                self.gvf_pixels_norm = [(((i - min_val) * 255) / (max_val - min_val)) for i in self.gvf_pixels]
                min_val, max_val = min(self.gvf_pixels_negative), max(self.gvf_pixels_negative)
                self.gvf_pixels_norm_inverted = [(((i - min_val) * 255) / (max_val - min_val)) for i in self.gvf_pixels_negative]
                self.gvf_pixels_norm_one = [(((i - min_val) * 1) / (max_val - min_val)) for i in self.gvf_pixels_negative]
                print("GVF done")

        if mode == 0:
            if self.image_status == "sobel_x":
                return
            else:
                self.image_status = "sobel_x"
                new_image = Image.new(mode="L", size = (self.COLS, self.ROWS))
                new_image.putdata(self.sobel_x_pixels_norm)
                self.sobel_x_image = new_image
                self.init_UI(self.sobel_x_image)
                print("Sobel X loaded")
        elif mode == 1:
            if self.image_status == "sobel_y":
                return
            else:
                self.image_status = "sobel_y"
                new_image = Image.new(mode="L", size = (self.COLS, self.ROWS))
                new_image.putdata(self.sobel_y_pixels_norm)
                self.sobel_y_image = new_image
                self.init_UI(self.sobel_y_image)
                print("Sobel Y loaded")
        elif mode == 2:
            if self.image_status == "sobel_norm":
                return
            else:
                self.image_status = "sobel_norm"
                new_image = Image.new(mode="L", size = (self.COLS, self.ROWS))
                new_image.putdata(self.sobel_mag_pixels_norm)
                self.sobel_mag_image = new_image
                self.init_UI(self.sobel_mag_image)
                print("Sobel Edges loaded")
        elif mode == 3:
            if self.image_status == "sobel_norm_inverted":
                return
            else:
                self.image_status = "sobel_norm_inverted"
                new_image = Image.new(mode="L", size = (self.COLS, self.ROWS))
                new_image.putdata(self.sobel_mag_pixels_norm_inverted)
                self.sobel_mag_inverted_image = new_image
                self.init_UI(self.sobel_mag_inverted_image)
                print("Sobel Edges Inverted loaded")
        elif mode == 4:
            if self.image_status == "gvf":
                return
            else:
                self.image_status = "gvf"
                new_image = Image.new(mode="L", size = (self.COLS, self.ROWS))
                new_image.putdata(self.gvf_pixels_norm)
                self.gvf_image = new_image
                self.init_UI(self.gvf_image)
                print("gvf loaded")
        elif mode == 5:
            if self.image_status == "gvf_inverted":
                return
            else:
                self.image_status = "gvf_inverted"
                new_image = Image.new(mode="L", size = (self.COLS, self.ROWS))
                new_image.putdata(self.gvf_pixels_norm_inverted)
                self.gvf_inverted_image = new_image
                self.init_UI(self.gvf_inverted_image)
                print("gvf inverted loaded")
        else:
            return
                

    def image_to_original(self):
        """ Reload orginal image """
        if self.image_status == "original":
            return
        self.image_status = "original"
        self.init_UI(self.original_image)


    def resize_image(self):
        self.clear_image()
        max_size = (self.image.width() / 2, self.image.height() / 2)
        self.raw_image.thumbnail(max_size, Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(self.raw_image)
        self.init_UI()
    
    ## Calculate energies for contour model

    def energy_calculations(self, contour_lines_parameter, model="rubber-band"):
        """ 
        Calculate the internal and external energy.

        parameters:
            model - "rubber-band" => use the rubber band model, "balloon" => use the balloon model 

        Internal energies:
        formula_curvature = |V(i+1)-2Vi+V(i-1)|^2 -> (X(i+1)-2Xi+X(i-1))^2 + (Y(i+1)-2Yi+Y(i-1))^2 

        formula_stretch/elasticity = (average_distance_x - sqrt((X(i+1)-X(i))^2 + (Y(i+1)-Y(i))^2)))^2

        Graveyard (Failed energies):
            1) Calculating the distance between each color channel from the sliding pixel
               in the window, and the center of the window pixel
               - external energy
               - this worked a little bit but was not successful in complex images
             

        """ 

        if self.sobel_mag_pixels == [] and GAMMA > 0.0:
            self.sobel_filter(4, "Grayscale")

        self.internal_energy_curvature = []
        self.internal_energy_stretch = []
        self.internal_energy_inflation = []

        # Loop through all contour lines
        for contour_line in contour_lines_parameter:
            int_energy_curve = []
            int_energy_stretch = []
            int_energy_inflation = []
            
            # Calcuate average distance between all contour points 
            distance = 0
            for index in range(len(contour_line) - 1):
                x_distance = contour_line[index+1][2] - (contour_line[index][2])
                y_distance = contour_line[index+1][3] - (contour_line[index][3])
                distance += sqrt((x_distance*x_distance) + (y_distance*y_distance))
            x_distance = contour_line[0][2] - (contour_line[-1][2])
            y_distance = contour_line[0][3] - (contour_line[-1][3])
            distance += sqrt((x_distance*x_distance) + (y_distance*y_distance))
            average_distance = distance / len(contour_line) 

            for index in range(len(contour_line) - 1):
                i = 0
                point_energy_curve = []
                point_energy_stretch = []
                point_energy_inflation = []
                for r in range(-1*(WINDOW_SIZE//2), (WINDOW_SIZE//2)+1):
                    for c in range(-1*(WINDOW_SIZE//2), (WINDOW_SIZE//2)+1):
                        if model == "rubber-band":
                            x_term_curve = contour_line[index+1][2] - 2*(contour_line[index][2]+c) + contour_line[index-1][2] # internal energy curve (attempt 1)
                            y_term_curve = contour_line[index+1][3] - 2*(contour_line[index][3]+r) + contour_line[index-1][3]
                            #x_term_curve = contour_line[index+1][2] - (contour_line[index][2]+c) # internal energy curve (attempt 2)
                            #y_term_curve = contour_line[index+1][3] - (contour_line[index][3]+r)
                            x_term_stretch = contour_line[index+1][2] - (contour_line[index][2]+c) # internal energy stretch
                            y_term_stretch = contour_line[index+1][3] - (contour_line[index][3]+r)  
                        if model =="balloon":
                            x_term_curve = contour_line[index+1][2] - 2*(contour_line[index][2]+c) + contour_line[index-1][2] # internal energy curve (attempt 1)
                            y_term_curve = contour_line[index+1][3] - 2*(contour_line[index][3]+r) + contour_line[index-1][3]
                            #x_term_curve = contour_line[index+1][2] - (contour_line[index][2]+c) # internal energy curve (attempt 2)
                            #y_term_curve = contour_line[index+1][3] - (contour_line[index][3]+r)
                            x_term_stretch = contour_line[index+1][2] - (contour_line[index][2]+c) # internal energy stretch
                            y_term_stretch = contour_line[index+1][3] - (contour_line[index][3]+r)
                            
                        point_energy_curve.append((x_term_curve*x_term_curve)  + (y_term_curve*y_term_curve))
                        point_energy_stretch.append((x_term_stretch*x_term_stretch)  + (y_term_stretch*y_term_stretch))
                
                if model == "rubber-band":
                    point_energy_stretch = [(average_distance-sqrt(value))*(average_distance-sqrt(value)) for value in point_energy_stretch]
                if model == "balloon":
                    point_energy_stretch = [(average_distance+sqrt(value))*(average_distance+sqrt(value)) for value in point_energy_stretch]
                
                int_energy_curve.append(point_energy_curve)
                int_energy_stretch.append(point_energy_stretch)
                if model == "balloon":
                    point_energy_inflation = [1 / ((average_distance-sqrt(value))*(average_distance-sqrt(value))) if average_distance-sqrt(value) != 0 else 0 for value in point_energy_stretch]
                    int_energy_inflation.append(point_energy_inflation)

            point_energy_curve = []
            point_energy_stretch = []
            point_energy_inflation = []
            for r in range(-1*(WINDOW_SIZE//2), (WINDOW_SIZE//2)+1):
                for c in range(-1*(WINDOW_SIZE//2), (WINDOW_SIZE//2)+1):
                    if model == "rubber-band":
                        x_term_curve = contour_line[0][2] - 2*(contour_line[-1][2]+c) + contour_line[-2][2]  
                        y_term_curve = contour_line[0][3] - 2*(contour_line[-1][3]+r) + contour_line[-2][3]
                        #x_term_curve = contour_line[0][2] - (contour_line[-1][2]+c) # internal energy curve (attempt 2)
                        #y_term_curve = contour_line[0][3] - (contour_line[-1][3]+r)
                        x_term_stretch = contour_line[0][2] - (contour_line[-1][2]+c)   
                        y_term_stretch = contour_line[0][3] - (contour_line[-1][3]+r)   
                        point_energy_curve.append((x_term_curve*x_term_curve) + (y_term_curve*y_term_curve))
                        point_energy_stretch.append((x_term_stretch*x_term_stretch) + (y_term_stretch*y_term_stretch))
                    if model == "balloon":
                        x_term_curve = contour_line[0][2] - 2*(contour_line[-1][2]+c) + contour_line[-2][2]  
                        y_term_curve = contour_line[0][3] - 2*(contour_line[-1][3]+r) + contour_line[-2][3]
                        x_term_stretch = contour_line[0][2] - (contour_line[-1][2]+c)   
                        y_term_stretch = contour_line[0][3] - (contour_line[-1][3]+r)   
                        point_energy_curve.append((x_term_curve*x_term_curve) + (y_term_curve*y_term_curve))
                        point_energy_stretch.append((x_term_stretch*x_term_stretch) + (y_term_stretch*y_term_stretch))
            if model == "rubber-band":
                point_energy_stretch = [(average_distance-sqrt(value))*(average_distance-sqrt(value)) for value in point_energy_stretch]
            if model == "balloon":
                point_energy_stretch = [(average_distance+sqrt(value))*(average_distance+sqrt(value)) for value in point_energy_stretch]
            
            if model == "balloon":
                point_energy_inflation = [1 / ((average_distance-sqrt(value))*(average_distance-sqrt(value))) if average_distance-sqrt(value) != 0 else 0 for value in point_energy_stretch]
                int_energy_inflation.append(point_energy_inflation)

            int_energy_curve.append(point_energy_curve)
            int_energy_stretch.append(point_energy_stretch)
            
            self.internal_energy_curvature.append(int_energy_curve)
            self.internal_energy_stretch.append(int_energy_stretch)
            if model == "balloon":
                self.internal_energy_inflation.append(int_energy_inflation)

        # Normalize all energies between 0-1
        self.all_energies_sum = []
        for contour in range(len(contour_lines_parameter)):
            contour_energy_sum = []
            for point in range(len(contour_lines_parameter[contour])):
                point_energy_sum = []
                val_min_curve, val_max_curve = min(self.internal_energy_curvature[contour][point]), max(self.internal_energy_curvature[contour][point])
                val_min_stretch, val_max_stretch = min(self.internal_energy_stretch[contour][point]), max(self.internal_energy_stretch[contour][point])
                if model == "balloon":
                    val_min_inflation, val_max_inflation = min(self.internal_energy_inflation[contour][point]), max(self.internal_energy_inflation[contour][point])
                energy_sum = 0
                point_stretch_norm = []
                index = 0
                for r in range(-1*(WINDOW_SIZE//2), (WINDOW_SIZE//2)+1):
                    for c in range(-1*(WINDOW_SIZE//2), (WINDOW_SIZE//2)+1):
                        energy_sum = 0
                        curve = self.internal_energy_curvature[contour][point][index]
                        stretch = self.internal_energy_stretch[contour][point][index]
                        if model == "balloon":
                            inflation = self.internal_energy_inflation[contour][point][index]
                        col_coord = contour_lines_parameter[contour][point][2] + c
                        row_coord = contour_lines_parameter[contour][point][3] + r 
                        if model == "rubber-band":
                            energy_sum += ALPHA * ((stretch - val_min_stretch) / (val_max_stretch - val_min_stretch))
                            energy_sum += BETA * ((curve - val_min_curve) / (val_max_curve - val_min_curve))
                        elif model == "balloon":
                            energy_sum += ALPHA_BALLOON * ((stretch - val_min_stretch) / (val_max_stretch - val_min_stretch))
                            energy_sum += BETA_BALLOON * ((curve - val_min_curve) / (val_max_curve - val_min_curve))
                        index = index + 1
                        if row_coord >= 0 and row_coord <= self.ROWS and col_coord >= 0 and col_coord <= self.COLS:
                            if GAMMA > 0.0:
                                energy_sum += GAMMA * (self.sobel_mag_pixels_norm_one[row_coord * self.COLS + col_coord])
                            if model == "rubber-band":
                                energy_sum += EPSILON * (self.gvf_pixels_norm_one[row_coord * self.COLS + col_coord])
                            elif model == "balloon":
                                energy_sum += EPSILON_BALLOON * (self.gvf_pixels_norm_one[row_coord * self.COLS + col_coord])
                            if self.image_type == 'L':
                                energy_sum += DELTA * (self.grayscale_pixels_norm_one[row_coord * self.COLS + col_coord])
                            else:
                                center_pixel = contour_lines_parameter[contour][point][3] + r * self.COLS + contour_lines_parameter[contour][point][2]
                                sliding_pixel = row_coord * self.COLS + col_coord
                                if DELTA > 0.0:
                                    red_difference = self.red_pixels_norm_one[sliding_pixel] - self.red_pixels_norm_one[center_pixel]
                                    green_difference = self.green_pixels_norm_one[sliding_pixel] - self.green_pixels_norm_one[center_pixel]
                                    blue_difference = self.blue_pixels_norm_one[sliding_pixel] - self.blue_pixels_norm_one[center_pixel]
                                    energy_sum += DELTA * (red_difference*red_difference + green_difference*green_difference + blue_difference*blue_difference)
                        else:
                            energy_sum += 0.0
                        point_energy_sum.append(energy_sum)
                contour_energy_sum.append(point_energy_sum)
            self.all_energies_sum.append(contour_energy_sum)
        """
        uncomment to print energy sums for each contour point
        for contour in self.all_energies_sum:
            for point in contour:
                for i in range(1,WINDOW_SIZE*WINDOW_SIZE+1):
                    print("%f  " % (point[i-1]), end='')
                    if i % WINDOW_SIZE == 0:
                        print("")
                print("")
                print("")
        """
    def greedy_minimization(self, contour_lines_parameter, contour_lines_references_parameter):
        for contour in range(len(self.all_energies_sum)):
            for point in range(len(self.all_energies_sum[contour])):
                point_ref = self.all_energies_sum[contour][point]
                oval_ref = contour_lines_references_parameter[contour][point]
                offset_c = 0
                offset_r = 0
                min_value = point_ref[0]
                for r in range(WINDOW_SIZE):
                    for c in range(WINDOW_SIZE):
                        if point_ref[r*WINDOW_SIZE+c] < min_value:
                            min_value = point_ref[r*WINDOW_SIZE+c]
                            offset_c = c
                            offset_r = r
                self.canvas.move(oval_ref, (-1*(WINDOW_SIZE//2)) + offset_c, (-1*(WINDOW_SIZE//2)) + offset_r)
                contour_lines_parameter[contour][point][0] = contour_lines_parameter[contour][point][0] - (WINDOW_SIZE//2) + offset_c  
                contour_lines_parameter[contour][point][1] = contour_lines_parameter[contour][point][1] - (WINDOW_SIZE//2) + offset_r 
                contour_lines_parameter[contour][point][2] = contour_lines_parameter[contour][point][2] - (WINDOW_SIZE//2) + offset_c
                contour_lines_parameter[contour][point][3] = contour_lines_parameter[contour][point][3] - (WINDOW_SIZE//2) + offset_r

    def active_contours(self, model="rubber-band"):
        """Driver function for the active contours algorithm"""
        for i in range(ITERATIONS):
            if model == "rubber-band":
                self.energy_calculations(self.contour_lines,model=model)
                self.greedy_minimization(self.contour_lines, self.contour_lines_references)
            if model == "balloon":
                self.energy_calculations(self.balloon_contour_lines, model=model)
                self.greedy_minimization(self.balloon_contour_lines, self.balloon_contour_lines_references)
            #print("Iteration %d finished" % (i))
            self.canvas.update() # update canvas during the loop
            time.sleep(UPDATE_SPEED) # argument in seconds


    def init_mouse_events(self):
        """Bind mouse events"""
        # Events:
        #   ButtonPress-1 -> left mouse click
        #   ButtonPress-2 -> middle (scroll) mouse click
        #   ButtonPress-3 -> right mouse click
        #   B1-Motion     -> mouse is moved when B1 is pressed
        self.canvas.bind("<ButtonPress-1>", self.on_left_click) 
        self.canvas.bind("<B1-Motion>", self.on_left_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_release)
        self.canvas.bind("<ButtonPress-3>", self.on_right_click) 
        self.canvas.bind("<B3-Motion>", self.on_right_drag)
        self.canvas.bind("<ButtonRelease-3>", self.on_right_release)


    def on_left_click(self, event):
        # Coords and dimensions of oval 
        self.final_ovals_coords = []
        self.oval_coords["x"] = event.x
        self.oval_coords["y"] = event.y
        self.oval_coords["x2"] = event.x + OVAL_RADIUS
        self.oval_coords["y2"] = event.y + OVAL_RADIUS
        self.ovals_references.append(self.canvas.create_oval(self.oval_coords["x"], 
                                        self.oval_coords["y"], 
                                        self.oval_coords["x2"], 
                                        self.oval_coords["y2"],
                                        outline=OUTLINE_COLOR))
        self.final_ovals_coords.append([self.oval_coords["x"], self.oval_coords["y"], self.oval_coords["x2"], self.oval_coords["y2"]])


    def on_left_release(self, event):
        """ Keep every fifth oval on mouse release """
        ovals_new = []
        ovals_new_references = []
        for i in range(len(self.final_ovals_coords)):
            if i % CONTOUR_DELETION == 0:
                ovals_new.append(self.final_ovals_coords[i])
                ovals_new_references.append(self.ovals_references[i + self.contour_start])

            else:
                self.canvas.delete(self.ovals_references[i + self.contour_start])
        self.contour_start = self.contour_start + len(self.final_ovals_coords)
        self.final_ovals_coords = ovals_new
        self.final_ovals_references = ovals_new_references
        
        if len(ovals_new) >= REQUIRED_POINTS:
            self.contour_lines.append(ovals_new) 
            self.contour_lines_references.append(ovals_new_references)
        else:
            for oval in ovals_new_references:
                 self.canvas.delete(oval)
        # self.contour_lines contains every contour line and their pixel points
        # contour_lines_references contains the references created by tkiner - used to move and delete points


    def on_left_drag(self, event):
        # Start coords of line
        self.oval_coords["x"] = event.x
        self.oval_coords["y"] = event.y
        self.oval_coords["x2"] = event.x + OVAL_RADIUS
        self.oval_coords["y2"] = event.y + OVAL_RADIUS
        self.ovals_references.append(self.canvas.create_oval(self.oval_coords["x"], 
                                        self.oval_coords["y"], 
                                        self.oval_coords["x2"], 
                                        self.oval_coords["y2"],
                                        outline=OUTLINE_COLOR))
        self.final_ovals_coords.append([self.oval_coords["x"], self.oval_coords["y"], self.oval_coords["x2"], self.oval_coords["y2"]])
        # Dynamically update
        #self.canvas.coords(self.final_ovals_coords[-1],self.oval_coords["x"], 
        #                    self.oval_coords["y"], 
        #                    self.oval_coords["x2"], 
        #                    self.oval_coords["y2"])

    def on_right_click(self, event):
        # Coords and dimensions of oval 
        start_x = event.x
        start_y = event.y
        self.balloon_final_ovals_coords = []

        for r in range(-1 * (CIRCLE_RADIUS+OVAL_RADIUS),(CIRCLE_RADIUS+OVAL_RADIUS)+1):
            for c in range(-1 * (CIRCLE_RADIUS+OVAL_RADIUS),(CIRCLE_RADIUS+OVAL_RADIUS)+1):
                if (r*r+c*c <= CIRCLE_RADIUS*CIRCLE_RADIUS + CIRCLE_RADIUS + 1 and r*r+c*c >= CIRCLE_RADIUS*CIRCLE_RADIUS - CIRCLE_RADIUS + 1):
                    self.oval_coords["x"] = event.x + c
                    self.oval_coords["y"] = event.y + r
                    self.oval_coords["x2"] = event.x + c + OVAL_RADIUS
                    self.oval_coords["y2"] = event.y + r + OVAL_RADIUS
                    self.balloon_ovals_references.append(self.canvas.create_oval(self.oval_coords["x"], 
                                            self.oval_coords["y"], 
                                            self.oval_coords["x2"], 
                                            self.oval_coords["y2"],
                                            outline=OUTLINE_COLOR))
                    self.balloon_final_ovals_coords.append([self.oval_coords["x"], 
                                            self.oval_coords["y"], 
                                            self.oval_coords["x2"], 
                                            self.oval_coords["y2"]])
                    
    def on_right_release(self, event):
        """ Keep every third oval on mouse release """
        balloon_ovals_new = []
        balloon_ovals_new_references = []
        for i in range(len(self.balloon_final_ovals_coords)):
            if i % CONTOUR_DELETION_BALLOON == 0:
                balloon_ovals_new.append(self.balloon_final_ovals_coords[i])
                balloon_ovals_new_references.append(self.balloon_ovals_references[i + self.balloon_contour_start])

            else:
                self.canvas.delete(self.balloon_ovals_references[i + self.balloon_contour_start])
        self.balloon_contour_start = self.balloon_contour_start + len(self.balloon_final_ovals_coords)
        self.balloon_final_ovals_coords = balloon_ovals_new
        self.balloon_final_ovals_references = balloon_ovals_new_references
        
        self.balloon_contour_lines.append(balloon_ovals_new) 
        self.balloon_contour_lines_references.append(balloon_ovals_new_references)

    def on_right_drag(self, event):
        """ Do nothing on right click drag """
        pass


    def clear_image(self):
        for contour in self.contour_lines_references:
            for point in contour:
                self.canvas.delete(point)
        self.oval_coords = {"x":0,"y":0,"x2":0,"y2":0}
        self.final_ovals_coords = []
        self.contour_lines = []
        self.ovals_references = []
        self.final_ovals_references = []
        self.contour_lines_references = []
        self.contour_start = 0
        #self.canvas.config(width=self.image.width(), height=self.image.height())
        #self.controller.geometry(str(WIDTH) + "x" +str(HEIGHT))


    def contour_stats_debug(self):
        """Function used for debugging. Prints number of elastic and balloon contour lines w/ # of points"""
        print("There is %d elastic contour line(s)" % (len(self.contour_lines)))
        for i in range(len(self.contour_lines)):
            print("Contour line %d has %d points" % (i, len(self.contour_lines[i])))
        print("There is %d balloon contour line(s)" % (len(self.balloon_contour_lines)))
        for i in range(len(self.balloon_contour_lines)):
            print("Contour line %d has %d points" % (i, len(self.balloon_contour_lines[i])))

def main():

    MainApp = Application()
    MainApp.geometry(str(WIDTH) + "x" + str(HEIGHT))
    MainApp.mainloop()

if __name__ == '__main__':
    main()


