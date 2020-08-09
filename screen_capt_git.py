from PIL import ImageGrab
import numpy as np
from pynput.mouse import Button, Controller
import time, datetime, cv2, webbrowser
import tkinter as tk
import tkinter.font as font
from tkinter import colorchooser


# this part solves the problem with the windows 10's scaling feature
# by reducing the scaling to 100% to its normal value
import ctypes
awareness = ctypes.c_int()
ctypes.windll.shcore.SetProcessDpiAwareness(2)

timeStarted = None
goOn = None
clickCount = None
drawCentroid = None
printCoordinates = None
drawContours = None



# coordinates to the portion of the scrren to be captured
x1 = 1566
y1 = 960

x2 = 1700
y2 = 1033


upper_clr = np.array([200,100,100])
lower_clr = np.array([140,60,32])

def colourPicker(state):
    colorRGB = colorchooser.askcolor()[0]
    colorRGB = RGBtoHSV(colorRGB)
    print(colorRGB)
    
    if state == True:
        upper_clr = np.array([round(colorRGB[0]), round(colorRGB[1]), round(colorRGB[2])])
        entry1.delete(0, tk.END)
        entry1.insert(0, str(upper_clr[0])+" "+str(upper_clr[1])+" "+str(upper_clr[2]))
    
    elif state == False:
        lower_clr = np.array([round(colorRGB[0]), round(colorRGB[1]), round(colorRGB[2])])
        entry2.delete(0, tk.END)
        entry2.insert(0, str(lower_clr[0])+" "+str(lower_clr[1])+" "+str(lower_clr[2]))

def HSVtoOpencvHSV(hsv):
    return np.array([int(hsv[0]/2), int(255*hsv[1]/100), int(255*hsv[2]/100)])

def OpencvHSVtoHSV(ocv_hsv):
    return np.array([int(ocv_hsv[0]*2), int(ocv_hsv[1]*100/255), int(ocv_hsv[2]*100/255)])


def RGBtoHSV(rgb):
    H = S = V = None
    R = rgb[0]/255
    G = rgb[1]/255
    B = rgb[2]/255
    cMax = max(R, G, B)
    cMin = min(R, G, B)
    delta = cMax - cMin

    if delta == 0:
        H = 0
    elif cMax == R:
        H = 60*((G-B)/delta % 6)
    elif cMax == G:
        H = 60*((B-R)/delta+2)
    elif cMax == B:
        H = 60*((R-G)/delta+4)

    if cMax == 0:
        S = 0
    else:
        S = delta/cMax*100

    V = cMax*100
    
    return [H, S, V]

def parseHSV(hsv_txt):
    x = hsv_txt.split()
    if len(x) != 3:
        print("too much or too less values mf")
        return
    try:
        for i in range(len(x)):
            x[i] = int(x[i])
            if i == 0 and (x[i] > 360 or x[i] < 0):
                print("H is not in range mf")
                return
            if i > 0:
                if x[i] < 0 or x[i] > 100:
                    print("too big or too small values mf")
                    return
    except ValueError:
        print("enter integers mf")
        return
    

    return x

def saveAll():
    global x1, y1, x2, y2, upper_clr, lower_clr

    upper_clr = np.array(parseHSV(entry1.get()))
    lower_clr = np.array(parseHSV(entry2.get()))
    x1 = int(cordx1.get())
    y1 = int(cordy1.get())
    x2 = int(cordx2.get())
    y2 = int(cordy2.get())



def optionsWindow():
    global entry1, entry2, cordx1, cordx2, cordy1, cordy2

    options = tk.Toplevel()


    
    options.title("Options")

    framehsv = tk.LabelFrame(options, text="HSV Colour Range", padx=5, pady=5)
    framehsv.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N+tk.W)

    text1 = tk.Label(framehsv, text="Upper: ", anchor=tk.W)
    text1.grid(row=0, column=0, sticky=tk.E+tk.W)
    
    entry1 = tk.Entry(framehsv, borderwidth=5)
    entry1.grid(row=1, column=0)
    entry1.insert(0, str(upper_clr[0])+" "+str(upper_clr[1])+" "+str(upper_clr[2]))

    buttonUpper = tk.Button(framehsv, text="Choose Upper", command=lambda : colourPicker(True))
    buttonUpper.grid(row=2, column=0)

    text2 = tk.Label(framehsv, text="Lower: ", anchor=tk.W)
    text2.grid(row=3, column=0, sticky=tk.E+tk.W)
    
    entry2 = tk.Entry(framehsv, borderwidth=5)
    entry2.grid(row=4, column=0)
    entry2.insert(0, str(lower_clr[0])+" "+str(lower_clr[1])+" "+str(lower_clr[2]))

    buttonLower = tk.Button(framehsv, text="Choose Lower", command=lambda : colourPicker(False))
    buttonLower.grid(row=5, column=0)


    frameCoordinate = tk.LabelFrame(options, text="Coordinates", padx=5, pady=5)
    frameCoordinate.grid(row=0, column=1, sticky=tk.E+tk.N, padx=5, pady=5, rowspan=2)

    frameUpper = tk.LabelFrame(frameCoordinate, text="Upper Left", padx=5, pady=5)
    frameUpper.grid(row=0, column=0, padx=5, pady=5)

    cordx1 = tk.Label(frameUpper, text="X: ", anchor=tk.W)
    cordx1.grid(row=0, column=0, sticky=tk.E+tk.W)

    cordx1 = tk.Entry(frameUpper, borderwidth=5)
    cordx1.grid(row=1, column=0)
    cordx1.insert(0, str(x1))

    cordy1 = tk.Label(frameUpper, text="Y: ", anchor=tk.W)
    cordy1.grid(row=2, column=0, sticky=tk.E+tk.W)
    
    cordy1 = tk.Entry(frameUpper, borderwidth=5)
    cordy1.grid(row=3, column=0)
    cordy1.insert(0, str(y1))


    frameLower = tk.LabelFrame(frameCoordinate, text="Lower Right", padx=5, pady=5)
    frameLower.grid(row=1, column=0, padx=5, pady=5)

    cordx2 = tk.Label(frameLower, text="X: ", anchor=tk.W)
    cordx2.grid(row=0, column=0, sticky=tk.E+tk.W)
    
    cordx2 = tk.Entry(frameLower, borderwidth=5)
    cordx2.grid(row=1, column=0)
    cordx2.insert(0, str(x2))


    cordy2 = tk.Label(frameLower, text="Y: ", anchor=tk.W)
    cordy2.grid(row=2, column=0, sticky=tk.E+tk.W)
    
    cordy2 = tk.Entry(frameLower, borderwidth=5)
    cordy2.grid(row=3, column=0)
    cordy2.insert(0, str(y2))

    frameDeveloper = tk.LabelFrame(options, text="Developer", padx=47, pady=30)
    frameDeveloper.grid(row=1, column=0, padx=5, pady=5)

    devButton = tk.Button(frameDeveloper, text="GGKUS", font=tk.font.Font(size=12),
     command=lambda: webbrowser.open('https://github.com/ggkus', new=2))
    devButton.grid(row=1, column=1)


    saveButton = tk.Button(options, text="Save Changes", command=saveAll, padx=135, pady=3, borderwidth=5, font=tk.font.Font(size=11))
    saveButton.grid(row=4, column=0, padx=5, pady=5, columnspan=2)



def watchScreen():

    global goOn, clickCount

    drawContours = tk.IntVar()
    drawCentroid = tk.IntVar()
    printCoordinates = tk.IntVar()


    image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    image = np.array(image)
    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    image_hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(image_hsv, HSVtoOpencvHSV(lower_clr), HSVtoOpencvHSV(upper_clr))

    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    mouse = Controller()

    for contour in contours:

        # only run if the area of the block of colour is bigger than the value
        area = cv2.contourArea(contour)
        if area > 1790:

            # to find the centroid of the contour
            # centroid is where we are going to click so the below coordinates are needed
            # https://docs.opencv.org/3.1.0/dd/d49/tutorial_py_contour_features.html for further info
            M = cv2.moments(contour)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

            # to draw the centroid above to 'capture' image
            cv2.circle(image_bgr, (cX, cY), 5, (0, 0, 255), -1)
            print(f"x coordinate {cX} y coordinate {cY}")
            cv2.drawContours(image_bgr, contour, -1, (0, 0, 255), 2)

            # sets the mouse position to the centroid and clicks
            mouse.position = (x1+cX, y1+cY)
            mouse.click(Button.left, 1)
            clickCount += 1
            clicks['text'] = "Times clicked: " + str(clickCount)

    cv2.imshow("capture", image_bgr)
    cv2.imshow("mask", mask)

    # print(contours)
    # for contour in contours:
    #     area = cv2.contourArea(contour)
    #
    #     if (area > 230):
    #         print(contour)
    #         x,y,w,h = cv2.boundingRect(contour)
    #         frame = cv2.rectangle(mask, (x, y), (x+w, y+h), (0, 0, 255), 10)


    #use this to add 'esc' stop key and add key == 27 to the if below
    #key = cv2.waitKey(1)
    
    if goOn != 0:
        # event handler of tkinter (so that we can run a loop alongside with the windows loop)
        root.after(1000, watchScreen)
    else:
        cv2.destroyAllWindows()
        goOn = 1
        return

def startCapture():
    global goOn, starting, stopping, timeStarted, clickCount

    timeStarted = datetime.datetime.now()

    clickCount = 0
    goOn = 1

    clicks['text'] = "Times clicked: " + str(clickCount)
    starting['state'] = tk.DISABLED
    stopping['state'] = tk.NORMAL
    options['state'] = tk.DISABLED
    
    watchScreen()
    return

def stopCapture():
    global goOn, starting, stopping, duration

    duration['text'] = "Last session duration: " + str(datetime.datetime.now()-timeStarted)
    
    goOn = 0

    stopping['state'] = tk.DISABLED
    starting['state'] = tk.NORMAL
    options['state'] = tk.NORMAL
    return




root = tk.Tk() 



root.title("Color detect v0.0.0.0.0.0")


textt = tk.Label(root, text="Color detect", font=tk.font.Font(size=11))
textt.grid(row=0, column=0, columnspan=2)

duration = tk.Label(root, text="Last session duration: ", anchor=tk.W)
duration.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E)

clicks = tk.Label(root, text="Times clicked: " + str(clickCount), anchor=tk.W)
clicks.grid(row=2, column=0, columnspan=2, sticky=tk.W+tk.E)

starting = tk.Button(root, text="Start", command=startCapture, state=tk.NORMAL,
 fg="green", padx=40, pady=20, font=tk.font.Font(size=15), borderwidth=5)
starting.grid(row=3, column=0, padx=5, pady=5)

stopping = tk.Button(root, text="Stop", command=stopCapture, state=tk.DISABLED,
 fg="red", padx=40, pady=20, font=tk.font.Font(size=15), borderwidth=5)
stopping.grid(row=3, column=1, padx=5, pady=5)

options = tk.Button(root, text="Options", command=optionsWindow, padx=123, pady=3, font=tk.font.Font(size=11), borderwidth=5)
options.grid(row=4, column=0, columnspan=2, padx=5, pady=5)



root.mainloop()

