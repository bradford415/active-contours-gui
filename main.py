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

 Defintions:
    Canvas - main screen to work with
    Frame - organize widgets

"""
import tkinter as tk

HEIGHT = 600
WIDTH = 700


class Application:
    
    def __init__(self, master):
        self.master = master
        self.init_window()
        self.init_menu()
    
    def init_window(self):
        self.master.title("Active Contours")
        self.canvas = tk.Canvas(self.master, height=HEIGHT, width=WIDTH)
        self.canvas.pack()
        self.background_frame = tk.Frame(self.master, bg="#6200EE")
        self.background_frame.place(relwidth=1, relheight=1)

        
    def init_menu(self):
        menu = tk.Menu(self.master)
        self.master.config(menu=menu)

        actions = tk.Menu(menu)
        menu.add_cascade(label='Actions', menu=actions)

        actions.add_command(label='Load Image', command=self.test_func)
        actions.add_command(label='Exit', command=self.exit_client)

    def test_func(self):
        print("Test")
    
    def exit_client(self):
        exit()


def main():

    
    root = tk.Tk()

    MainApp = Application(root)

    root.mainloop()

if __name__ == '__main__':
    main()


