# Imports

from tkinter import messagebox     # Error display
import tkinter as tk               # Tkinter
from tkinter import TclError       # Detect when window destroyed
from requests import get           # Get images from online API
from PIL import Image              # Image object
from io import BytesIO             # Image to bytes conversion
import math                        # Math library


# Base window for program and canvas with fill page and parameters

class Gui:
    def __init__(self):                     
        self.root = tk.Tk()
        self.root.title('Satellite Imager')
        self.can = tk.Canvas(self.root, width=600, height=600)
        self.can.pack(fill=tk.BOTH, expand=1)
        self.imgs = []
        
# Ignore

    def __repr__(self):
        return f'__SatelliteImager.Graphics'
    
# Adds image "temp.pmg", appends to array and anchors the image at NW

    def addImg(self, x, y):
        self.img = tk.PhotoImage(file='temp.png')
        self.imgs.append(self.img)
        self.can.create_image(x, y, anchor=tk.NW, image=self.img)

# Instead of raising normal python error, gives an error box 

    def error(self, message):
        messagebox.showerror('Fatal error', message)
        del self
        
# Allows for the window to be closed properly

    def clr(self):
        for w in self.root.winfo_children():
            w.destroy() 

# Updates the GUI and any pending GUI updates

    def upd(self):
        self.root.update()

# This converts a latitude and longitude Into a tile number

def convert(lat, lon, z, extent = 1):
    z2 = 1 << z
    lon = ((lon + 180.0) % 360.0)
    lat = max(min(lat, 89.9), -89.9)
    lat_rad = math.radians(lat)
    zl_x = int(round(lon / (360.0 / (extent * z2))))
    zl_y = int(round(((extent * z2) / 2) * (1.0 - (math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi))))
    return [zl_x, zl_y]

# Authorizes access to Mapbox API which allows requests from satellite image.
# The function also sends https request and wraps the response in BytesIO object which lets PIL read it as an image.
# Finally it resizes the image and saves the image

def getImg(xt, yt, z, rf):
    token = 'pk.eyJ1IjoicGJhcm4xMCIsImEiOiJja29neWRpa3kwdHNyMzBsYTMyZzY3Mjh2In0.4qncuUkuvlkh_AwRpz5pog'
    r = get(
        f'https://api.mapbox.com/v4/mapbox.satellite/{z}/{xt}/{yt}@2x.pngraw?access_token={token}',
        )
    img = Image.open(BytesIO(r.content))
    img = img.resize((512//(2**rf),512//(2**rf)))
    img.save('temp.png')

# Globalizes variables to allow them to be accessed and modified within the function.
# Checks for update to exit by comparing width,height,latitude and longitude with the main window
# Calculates the tile coords 'xta', 'yta'
# Calls the getImg() function with coords as arguements. This will add the retrieved image to the GUI canvas at specified positions
# Calls g.upd() to update the GUI and process and process pending events.
# xt and xy variables are multiplied by 2 to update coords for next iteration of loops

def update():
    global zoom, lat, lon, g, od

    xt, yt = convert(lat, lon, zoom)
    for zc in range(3):
        z = zoom + zc
        
        for x in range(math.ceil(g.root.winfo_width()/(512//(2**zc)))):
            for y in range(math.ceil(g.root.winfo_height()/(512//(2**zc)))):
                cd = [g.root.winfo_width(), g.root.winfo_height(), lat, lon]
                if od != cd:
                    od = cd
                    return

                xta = xt + x
                yta = yt + y
                getImg(xta, yta, z, zc)
                g.addImg(x*(512//(2**zc)), y*(512//(2**zc)))
                g.upd()
        xt *= 2
        yt *= 2

# Globalizes variables to allow them to be accessed and modified within the function.
# initializes Gui window
# Allows user to input their zoom level and custom coords
# While loop basically compares od variable with cd variable and updats gui accordingly

def main():
    global zoom, lat, lon, g, od

    g = Gui()

    zoom, lat, lon = 17, 37.937290, 21.271713
    od = [600, 600, lat, lon] # OLD DATA width, height, x, y

    while 1:
        cd = [g.root.winfo_width(), g.root.winfo_height(), lat, lon]
        if od != cd:
            od = cd
            update()
        else:
            g.upd()

# This is standard code for handling and displaying errors in the GUI applicatiom without causing the program to terminate abruptly. 

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        if type(e) != TclError:
            g.error(e)
        raise
