import os, io
from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw
import copy

# Uses Google Vision API to detect Longhorns logos
# path: the path to the image to analyze
# returns: a 3d array frames[frame][vertex][coord val] that details the coordinates of the different Longhorn logos
def detect_logos(path):
    """Detects logos in the file."""
    from google.cloud import vision
    import io
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)
    response = client.logo_detection(image=image)

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    logos = response.logo_annotations
    frames = []
    for i, logo in enumerate(logos):
        # print(logo.description)
        valid_labels = ["Texas Longhorns football", "University of Texas at Austin"]
        if logo.description not in valid_labels:
            continue
        # else
        thisFrame = []
        for j, v in enumerate(logo.bounding_poly.vertices):
            thisFrame.append([v.x, v.y])

        frames.append(thisFrame)


    return frames   # returns frames[frame][vertex][coord val]


# Used for debugging purposes
def printFrameCoords(frames):
    for frame in frames:
        for coord in frame:
            print("(" + str(coord[0]) + ", " + str(coord[1]) + ")")
        print("=================================")


# Used for debugging purposes
def drawBoxes(path, frames):
    im = Image.open(path)
    draw = ImageDraw.Draw(im)

    for frame in frames:
        firstCoord = [-1, -1]
        lastCoord = [-1, -1]
        for thisCoord in frame:
            if lastCoord[0] == -1 and lastCoord[1] == -1:  # do this for the first iteration
                firstCoord = thisCoord
                lastCoord = thisCoord
                continue
            # else:
            draw.line((lastCoord[0],lastCoord[1], thisCoord[0],thisCoord[1]), fill=(238, 250, 15))
            lastCoord = thisCoord

        # Draw a line from the last vertex to the first to complete the box
        draw.line((lastCoord[0], lastCoord[1], firstCoord[0], firstCoord[1]), fill=(238, 250, 15))


    # draw.line((100,200, 150,300), fill=128)
    im.show()
    # input("Press enter to continue")


# makes a copy of the image passed to it and flips the logos within the frames
def flipLogos(path, frames):
    original_im = Image.open(path)
    copy_im = original_im.copy()

    for frame in frames:
        copy_frame = copy_im.copy()  # copy the copy of the image

        box = (frame[0][0], frame[0][1], frame[2][0], frame[2][1])  # crop using upper left and lower right coords
        copy_frame = copy_frame.crop(box)  # crop the image to show just the box
        copy_frame = copy_frame.rotate(180)
        copy_im.paste(copy_frame, (frame[0][0], frame[0][1]))  # paste the rotated & cropped image, passing the top left corner
    copy_im.show()
    file_ext = path.split('.')[1]
    new_path = path.split('.')[0] + "_logos_flipped." + file_ext
    copy_im.save(new_path)

# ======================
# main
# ---------------------

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'putNameOfJsonFileHere.json'
image_path = "test_images/test4.jfif"

frames2 = detect_logos(image_path)
if (len(frames2) != 0):
    # printFrameCoords(frames2)
    # drawBoxes("test3.jpg", frames2)
    flipLogos(image_path, frames2)

# ======================
