import cv2
import os
import numpy as np
from PIL import Image
from flask import Flask, render_template, request, redirect, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'lkjhasdlfjkh'

# mydir = os.getcwd()

app.config["IMAGE_UPLOADS"] = 'HOME/tmp'
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["PNG", "JPG", "JPEG"]

def allowed_image(filename):
    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        if request.files:
            image = request.files["image"]
            if image.filename == "":
                return redirect(request.url)
            if not allowed_image(image.filename):
                print('invalid image extension')
                return redirect(request.url)
            else:
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))
                
                crop_img(filename)
                barray = read_board("CROPPED.PNG")
                orbstring = ''
                for line in barray:
                    for char in line:
                        orbstring += char.upper()
                print(orbstring)
                os.remove("HALF.PNG")
                os.remove("CROPPED.PNG")
                os.remove(filename)

                session['my_var'] = orbstring
            return redirect("/results")
    return render_template("index.html")


@app.route("/results")
def res():
    my_var = session.get('my_var', None)
    return render_template("results.html", content=my_var)


def crop_img(filename):
    im = Image.open(filename)
    imw, imh = im.size
    left = 1
    top = imh / 2
    right = imw
    bottom = imh 
    im1 = im.crop((left, top, right, bottom))
    im1.save("HALF.PNG")
    
    img_to_crop = cv2.imread("HALF.PNG", 0)
    template = cv2.imread("HP1.PNG", 0)
    res = cv2.matchTemplate(img_to_crop, template, cv2.TM_CCOEFF_NORMED)
    w = template.shape[1]
    h = template.shape[0]

    threshold = 0.6

    yloc, xloc = np.where( res >= threshold)
    rectangles = []

    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])


    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    print(rectangles)

    for (x, y, w, h) in rectangles:
            cv2.rectangle(img_to_crop, (x, y), (x + w, y + h), (0,255,255), 2)
    print(rectangles[0])
    crop = rectangles[0][1] + rectangles[0][3]

    im = Image.open("HALF.PNG")
    imw, imh = im.size
    left = 1
    top = crop
    right = imw
    bottom = imh
    im1 = im.crop((left, top, right, bottom))
    im1.save("CROPPED.PNG")


def read_board(filename):
    toSend = []
    board = [['u', 'u', 'u', 'u', 'u', 'u'], # row 5, columns a-f (chess notation)
    ['u', 'u', 'u', 'u', 'u', 'u'], 
    ['u', 'u', 'u', 'u', 'u', 'u'], 
    ['u', 'u', 'u', 'u', 'u', 'u'], 
    ['u', 'u', 'u', 'u', 'u', 'u']]  # row 1
    
    orb_list = ["red.PNG", "blue.PNG", "green.PNG", "light.PNG", "dark.PNG", "heart.PNG"]
    
    for file in orb_list:
        img_rgb = cv2.imread(filename, 0)
        template = cv2.imread(file, 0)

        res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        w = template.shape[1]
        h = template.shape[0]

        threshold = 0.6

        yloc, xloc = np.where( res >= threshold)
        rectangles = []

        for (x, y) in zip(xloc, yloc):
            rectangles.append([int(x), int(y), int(w), int(h)])
            rectangles.append([int(x), int(y), int(w), int(h)])


        rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)

        for (x, y, w, h) in rectangles:
            cv2.rectangle(img_rgb, (x, y), (x + w, y + h), (0,255,255), 2)

        orb = file[0]

        for coordinate in rectangles:                                       # [ 30  84  72  66] LIGHT, SHOULD GO IN 'A5'
            x, y = coordinate[0], coordinate[1]                             # x = 30, y = 84
            xborders = [0, 127, 251, 373, 497, 620, 744]
            yborders = [0, 126, 249, 372, 497, 618]
            for xbi in range(len(xborders) - 1):                                  # 1st iteration:  xbi = 0
                for ybi in range(len(yborders) - 1):                              # ybi = 0 
                    if x > xborders[xbi] and x < xborders[xbi + 1]:           # if 30 > xborders[0] %0 and 30 < xborders[127] then orb will be in A column for sure
                        if y > yborders[ybi] and y < yborders[ybi + 1]:
                            board[ybi][xbi] = orb

    print("rectangles: ", toSend)
    return board

if __name__ == "__main__":
    app.run()



