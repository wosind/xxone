
from tkinter import *

def main():
    root = Tk()
    ScreenWidth = root.winfo_width()
    ScreeHeingt = root.winfo_height()

    root.title("ChessPlay")
    width = 800
    Height = 600
    x = (ScreenWidth-width)/4
    y =(ScreeHeingt-Height)/2
    root.geometry("%dx%d+%d+%d"%(width,Height,x,y))
    root.mainloop()

main()