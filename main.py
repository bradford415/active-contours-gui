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

 Design Choices:
    1) 

"""
import tkinter as tk
import tkinter.filedialog
import PIL # Python Image Library
from PIL import ImageTk, Image
from math import sqrt
import os

HEIGHT = 600
WIDTH = 700

TITLE = "Active Contours"
MENU_1 = "Pages"
MENU_2 = "Actions"
MENU_3 = "Edit"
MENU_4 = "Debug"

LARGE_FONT= ("Verdana", 12)

OVAL_RADIUS = 5
WINDOW_SIZE = 7

ALPHA = 1.0 # Internal energy stretch factor
BETA = 1.0  # Internal energy curvature factor
GAMMA = 1.0 # External energy factor
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
        self.final_ovals = []
        self.contour_lines = []
        self.ovals_references = []
        self.contour_start = 0

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
                                command=lambda: self.gaussian_smoothing(0))
        self.file_menu_edit.add_command(label='Gradient X', 
                                command=lambda: self.sobel_filter(0))
        self.file_menu_edit.add_command(label='Gradient Y', 
                                command=lambda: self.sobel_filter(1))
        self.file_menu_edit.add_command(label='Edges', 
                                command=lambda: self.sobel_filter(2))
        self.file_menu_edit.add_command(label='Clear', 
                                command=lambda: self.clear_image())
        # Debug menu options
        self.file_menu_debug = tk.Menu(controller.menu_bar, tearoff=0)
        controller.menu_bar.add_cascade(label=MENU_4, menu=self.file_menu_debug)
        self.file_menu_debug.add_command(label='Print Variable', 
                                command=lambda: self.print_values())
        self.file_menu_debug.add_command(label='Internal Engery Curvature', 
                                command=lambda: self.energy_calculations())


    def load_image(self):
        # Clear variables from previous image
        self.grayscale_pixels = []
        self.gaussian_blur_pixels = []
        self.sobel_x_pixels = []
        self.sobel_x_pixels_norm = []
        self.sobel_y_pixels = []
        self.sobel_y_pixels_norm = []
        self.sobel_mag_pixels = []
        self.sobel_mag_pixels_norm = []

        self.image_status = "original"

        
        
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        PICTURE_DIR = os.path.join(ROOT_DIR, "pictures")
        self.file_name = tk.filedialog.askopenfilename(initialdir=PICTURE_DIR, 
                                                    title="Select a Picture", 
                                                    filetypes=[("all images","*.pnm *.png *.jpg")])
        print(self.file_name)

        # Load image/pixel data and save as variables i'm used to
        self.original_image = Image.open(self.file_name)
        self.COLS, self.ROWS = self.original_image.size
        self.original_pixels = list(self.original_image.getdata())

        # Perform convolutions and image processing on image load
        self.sobel_filter(3)
        self.gaussian_smoothing(3)
        self.image_to_grayscale(3)

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

        #self.canvas.grid(row=0, column=0)
        self.controller.enable_menu(MENU_3)
        self.controller.geometry(str(self.image.width()) + "x" + str(self.image.height()))
        #self.controller.resizable(False, False)


    ## Functions to modify the image

    def pixels_to_grayscale(self):
        """ Convert grayscale pixels and store in property """
        ROWS = self.ROWS
        COLS = self.COLS
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


    def convolution_seperable(self, kernel, kernel_size):
        """ Convolve the loaded image with separable filters """
        ROWS = self.ROWS
        COLS = self.COLS
        self.temp_pixels = [] # store the intermediate steps of convolution
        self.convolution_pixels = []

        # Compute grayscale pixels if not already done
        if self.grayscale_pixels == []:
            self.pixels_to_grayscale()

        r2 = 0
        for r in range(ROWS):
            for c in range(COLS): 
                pixel_sum = 0
                kernel_index = 0
                for c2 in range(-1*(kernel_size//2), (kernel_size//2)+1):
                    if((c + c2 < 0) or (c + c2 >= COLS)):
                        pixel_sum += 0
                    else:
                        pixel_sum += self.grayscale_pixels[((r+r2)*COLS)+(c+c2)] * kernel[kernel_index]
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

    def convolution_2d(self, kernel, kernel_size):
        """ Convolve the loaded image with 2d convolution filters """
        ROWS = self.ROWS
        COLS = self.COLS
        self.temp_pixels = [] # store the intermediate steps of convolution
        self.convolution_pixels = []

        # Compute grayscale pixels if not already done
        if self.grayscale_pixels == []:
            self.pixels_to_grayscale()

        for r in range(ROWS):
            for c in range(COLS): 
                
                kernel_index = 0
                pixel_sum = 0
                for r2 in range(-1*(kernel_size//2), (kernel_size//2)+1):
                    for c2 in range(-1*(kernel_size//2), (kernel_size//2)+1):
                        if (c + c2 < 0) or (c + c2 >= COLS) or (r + r2 < 0) or (r + r2 >= ROWS):
                            pixel_sum += 0
                        else:
                            pixel_sum += self.grayscale_pixels[((r+r2)*COLS)+(c+c2)] * kernel[kernel_index]
                        kernel_index = kernel_index + 1
                self.convolution_pixels.append(pixel_sum)


    def gaussian_smoothing(self, mode):
        if self.image_status == "gaussian":
            return


        if self.gaussian_blur_pixels == []:
            self.convolution_seperable(self.GAUSSIAN_BLUR, self.GAUSSIAN_SIZE)
            self.gaussian_blur_pixels = self.convolution_pixels
            new_image = Image.new(mode="L", size = (self.COLS, self.ROWS))
            new_image.putdata(self.gaussian_blur_pixels)
            #new_image.save("gaussian.pnm")
            self.gaussian_image = new_image
        if mode == 0:
            self.image_status = "gaussian"
            self.init_UI(self.gaussian_image)
            print("Gaussian Smoothing Loaded")
        else:
            return


    def sobel_filter(self, mode):
        """
         compute x and y gradients of the sobel filter along with the magnitude image

         mode - which sobel image to display
                    0 -> x gradient
                    1 -> y gradient
                    2 -> magnitude gradient
        """
        if self.sobel_x_pixels == []:
            self.convolution_2d(self.SOBEL_X, self.SOBEL_SIZE)
            self.sobel_x_pixels = self.convolution_pixels
            min_val, max_val = min(self.sobel_x_pixels), max(self.sobel_x_pixels)
            self.sobel_x_pixels_norm = [(((i - min_val) * 255) / (max_val - min_val)) for i in self.sobel_x_pixels]
        if self.sobel_y_pixels == []:
            self.convolution_2d(self.SOBEL_Y, self.SOBEL_SIZE)
            self.sobel_y_pixels = self.convolution_pixels
            min_val, max_val = min(self.sobel_y_pixels), max(self.sobel_y_pixels)
            self.sobel_y_pixels_norm = [(((i - min_val) * 255) / (max_val - min_val)) for i in self.sobel_y_pixels]
        if self.sobel_mag_pixels == []:
            self.sobel_mag_pixels = [sqrt((self.sobel_x_pixels[index]*self.sobel_x_pixels[index]) + (self.sobel_y_pixels[index]*self.sobel_y_pixels[index]) )  for index in range(self.ROWS*self.COLS)]
            min_val, max_val = min(self.sobel_mag_pixels), max(self.sobel_mag_pixels)
            self.sobel_mag_pixels_norm = [(((i - min_val) * 255) / (max_val - min_val)) for i in self.sobel_mag_pixels]
            self.sobel_mag_pixels_norm_one = [(((i - min_val) * 1) / (max_val - min_val)) for i in self.sobel_mag_pixels]
            print("Sobel done")

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

    def energy_calculations(self):
        """ 
        Calculate the curvature energy. 
        Stored as: [[[x1, y1], [x2, y2]], <--- energy for contour line 1
                    [[x1, y1], [x2, y2]]] <--- energy for contour line 2

        formula_curvature = |V(i+1)-2Vi+V(i-1)|^2 -> (X(i+1)-2Xi+X(i-1))^2 + (Y(i+1)-2Yi+Y(i-1))^2 
        """ 

        if self.sobel_mag_pixels == []:
            self.sobel_filter(3)

        self.internal_energy_curvature = []
        self.internal_energy_stretch = []
        
        print(self.contour_lines)
        print("There are %d contour lines" % (len(self.contour_lines)))
        # Loop through all contour lines but only testing with one right now
        for contour_line in self.contour_lines:
            int_energy_curve = []
            int_energy_stretch = []
            distance = 0
            for index in range(len(contour_line) - 1):
                i = 0
                point_energy_curve = []
                point_energy_stretch = []
                distance = 0
                for r in range(-1*(WINDOW_SIZE//2), (WINDOW_SIZE//2)+1):
                    for c in range(-1*(WINDOW_SIZE//2), (WINDOW_SIZE//2)+1):
                        x_term_curve = contour_line[index+1][2] - 2*(contour_line[index][2]+c) + contour_line[index-1][2]  
                        y_term_curve = contour_line[index+1][3] - 2*(contour_line[index][3]+r) + contour_line[index-1][3]
                        x_term_stretch = contour_line[index+1][2] - (contour_line[index][2]+c)  
                        y_term_stretch = contour_line[index+1][3] - (contour_line[index][3]+r)  
                        point_energy_curve.append((x_term_curve*x_term_curve)  + (y_term_curve*y_term_curve))
                        point_energy_stretch.append((x_term_stretch*x_term_stretch)  + (x_term_stretch*x_term_stretch))
                        
                        if r == 0 and c == 0:
                            distance += sqrt((x_term_stretch*x_term_stretch) + (y_term_stretch*y_term_stretch))

                int_energy_curve.append(point_energy_curve)
                int_energy_stretch.append(point_energy_stretch)

            point_energy_curve = []
            point_energy_stretch = []
            for r in range(-1*(WINDOW_SIZE//2), (WINDOW_SIZE//2)+1):
                for c in range(-1*(WINDOW_SIZE//2), (WINDOW_SIZE//2)+1):
                    x_term_curve = contour_line[0][2] - 2*(contour_line[-1][2]+c) + contour_line[-2][2]  
                    y_term_curve = contour_line[0][3] - 2*(contour_line[-1][3]+r) + contour_line[-2][3]
                    x_term_stretch = contour_line[0][2] - (contour_line[-1][2]+c)  
                    y_term_stretch = contour_line[0][3] - (contour_line[-1][3]+r)   
                    point_energy_curve.append((x_term_curve*x_term_curve) + (y_term_curve*y_term_curve))
                    point_energy_stretch.append((x_term_stretch*x_term_stretch) + (x_term_stretch*x_term_stretch))
                    
                    if r == 0 and c == 0:
                        distance += sqrt((x_term_stretch*x_term_stretch) + (y_term_stretch*y_term_stretch))
            
            average_distance = distance / len(contour_line) 
            point_energy_stretch = [value - average_distance for value in point_energy_stretch]

            int_energy_curve.append(point_energy_curve)
            int_energy_stretch.append(point_energy_stretch)
            
        self.internal_energy_curvature.append(int_energy_curve)
        self.internal_energy_stretch.append(int_energy_stretch)

        # Normalize all energies between 0-1
        self.all_energies_sum = []
        for contour in range(len(self.contour_lines)):
            contour_energy_sum = []
            for point in range(len(self.contour_lines[contour])):
                point_energy_sum = []
                val_min_curve, val_max_curve = min(self.internal_energy_curvature[contour][point]), max(self.internal_energy_curvature[contour][point])
                val_min_stretch, val_max_stretch = min(self.internal_energy_stretch[contour][point]), max(self.internal_energy_stretch[contour][point])
                energy_sum = 0
                point_stretch_norm = []
                index = 0
                for r in range(-1*(WINDOW_SIZE//2), (WINDOW_SIZE//2)+1):
                    for c in range(-1*(WINDOW_SIZE//2), (WINDOW_SIZE//2)+1):
                        energy_sum = 0
                        curve = self.internal_energy_curvature[contour][point][index]
                        stretch = self.internal_energy_stretch[contour][point][index]
                        col_coord = self.contour_lines[contour][point][2] + c
                        row_coord = self.contour_lines[contour][point][3] + r 
                        energy_sum += (curve - val_min_curve) / (val_max_curve - val_min_curve)
                        energy_sum += (stretch - val_min_stretch) / (val_max_stretch - val_min_stretch)
                        index = index + 1
                        if (row_coord) >= 0 and (row_coord) <= self.ROWS and (col_coord) >= 0 and (col_coord) <= self.COLS:
                            energy_sum += self.sobel_mag_pixels_norm_one[r * self.COLS + c]
                        else:
                            energy_sum += 0.0
                        point_energy_sum.append(energy_sum)
                contour_energy_sum.append(point_energy_sum)
            self.all_energies_sum.append(contour_energy_sum)
            print(self.all_energies_sum)
        """
        if self.gaussian_blur_pixels == []:
            self.convolution_seperable(self.GAUSSIAN_BLUR, self.GAUSSIAN_SIZE)
            self.gaussian_blur_pixels = self.convolution_pixels
            self.external_energy = self.gaussian_blur_pixels
        else:
            self.gaussian_blur_pixels = self.convolution_pixels
            self.external_energy = self.gaussian_blur_pixels
        """
    #def active_contours(self):



    def init_mouse_events(self):
        """Bind mouse events"""
        # Events:
        #   ButtonPress-1 -> left mouse click
        #   ButtonPress-2 -> middle (scroll) mouse click
        #   ButtonPress-3 -> right mouse click
        #   B1-Motion     -> mouse is moved when B1 is pressed
        self.canvas.bind("<ButtonPress-1>", self.on_left_click) 
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_release)


    def on_left_click(self, event):
        # Coords and dimensions of oval 
        self.final_ovals = []
        self.oval_coords["x"] = event.x
        self.oval_coords["y"] = event.y
        self.oval_coords["x2"] = event.x + OVAL_RADIUS
        self.oval_coords["y2"] = event.y + OVAL_RADIUS
        self.ovals_references.append(self.canvas.create_oval(self.oval_coords["x"], 
                                        self.oval_coords["y"], 
                                        self.oval_coords["x2"], 
                                        self.oval_coords["y2"]))
        self.final_ovals.append([self.oval_coords["x"], self.oval_coords["y"], self.oval_coords["x2"], self.oval_coords["y2"]])


    def on_left_release(self, event):
        """ Keep every fifth oval on mouse release """
        ovals_new = []
        for i in range(len(self.final_ovals)):
            if i % 5 == 0:
                ovals_new.append(self.final_ovals[i])
            else:
                self.canvas.delete(self.ovals_references[i + self.contour_start])
        self.contour_start = self.contour_start + len(self.final_ovals)
        self.final_ovals = ovals_new
        self.contour_lines.append(ovals_new)


    def on_drag(self, event):
        # Start coords of line
        self.oval_coords["x"] = event.x
        self.oval_coords["y"] = event.y
        self.oval_coords["x2"] = event.x + OVAL_RADIUS
        self.oval_coords["y2"] = event.y + OVAL_RADIUS
        self.ovals_references.append(self.canvas.create_oval(self.oval_coords["x"], 
                                        self.oval_coords["y"], 
                                        self.oval_coords["x2"], 
                                        self.oval_coords["y2"]))
        self.final_ovals.append([self.oval_coords["x"], self.oval_coords["y"], self.oval_coords["x2"], self.oval_coords["y2"]])
        # Dynamically update
        #self.canvas.coords(self.final_ovals[-1],self.oval_coords["x"], 
        #                    self.oval_coords["y"], 
        #                    self.oval_coords["x2"], 
        #                    self.oval_coords["y2"])

    def clear_image(self):
        for i in range(len(self.ovals_references)):
            self.canvas.delete(self.ovals_references[i])
        #self.canvas.config(width=self.image.width(), height=self.image.height())
        #self.controller.geometry(str(WIDTH) + "x" +str(HEIGHT))


    def print_values(self):
        print("There are %d ovals before downszing, their coordinates are below (x, y) top left and (x2, y2) bottom right" % (len(self.final_ovals)))
        for contour in self.contour_lines:
            print(len(contour))

def main():

    MainApp = Application()
    MainApp.geometry(str(WIDTH) + "x" + str(HEIGHT))
    MainApp.mainloop()

if __name__ == '__main__':
    main()


