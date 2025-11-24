import os 
import glob
import sys
import cv2 as cv 
import numpy as np
from pathlib import Path
import time
import random as rand
import hashlib

################ VARIABLES ###################
DESIRED_WIDTH = 480
DESIRED_HEIGHT = 640
ANALYZE_IMG_ORD = 'q'
IMAGE_TAKER_ORD = 32
CLEAR_IMAGES_ORD = 'c'

########## CREATE_FOLDER ######################
### Creates the folder for the photos to be saves in
### Parameters ###
# name - the desired name of the folder
### Returns ###
# folder - the name of the folder
def create_folder(name):
    #Creates a folder for saved photos if captured_photos is not there already 
        #(default: it should be there)
        folder = name
        if not os.path.exists(folder):
            os.makedirs(folder)
        return folder

############   SPACE_BAR_COMMAND   ######################
### If space bar, then take photos
### Parameters ###
# num_photos - number of photos to be taken
# capture - capture video instance
# save_folder - name of the folder to be saved to 
# delay - defined time delay for photos
# counter - for loop/name of file
### Returns ###
# counter - updated counter
def image_taker(num_photos, capture, save_folder, delay, counter):
    for i in range(num_photos):
        ret, frame = capture.read() #Reads frame

        if not ret:
            print("Read error while capturing photos!")
            break

        img_name = os.path.join(save_folder, f"opencv_frame_{counter}.png")  #Names image  and joins it to the save folder (captured_images)
        cv.imwrite(img_name, frame)  #Writes the image into save folder

        print("{} written!".format(img_name))  #Debugging  #Debugging
        counter += 1  #Adds to image counter for naming purposes.
        time.sleep(delay) #Delay with photos being taken.

    return counter  # return updated counter

################ CLEAR_IMAGES #################
### If C used on keyboard, then delete images from the image folder directory
### Parameters ###
# save_folder - the name of the file 
### Returns ###
# N/A
def clear_images(save_folder):
    for fileName in os.listdir(save_folder):
        if fileName.startswith("opencv_frame_") and fileName.endswith(".png"):
            os.remove(os.path.join(save_folder, fileName))

#Starts up OpenCV webcam, takes photos from the webcam that will be used to collect data from. 
def createImages():
        #Set number of photos taken
        numberOfPhotos = 20
        #Image counter used for file naming process/debugging
        counter = 0
        #Timer for photos being taken after each iteration
        delay = 0.5

        ##create the save folder
        save_folder = create_folder("captured_images")
        
        #Captures video
        cap = cv.VideoCapture(0)

        cap.set(cv.CAP_PROP_FRAME_WIDTH, DESIRED_WIDTH)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, DESIRED_HEIGHT)
      
        #While video is playing...
        while True:
            #Reads a frame
            ret, frame = cap.read()

            #Error checking
            if not ret:
                print("Error!")
                break
        
            # Display the resulting frame (live feed from camera)
            cv.imshow('Frame_final', frame)
            key = cv.waitKey(1) & 0xFF  # READ KEY ONCE

            #If the user presses the space bar, it takes PNG images of the frame being captured via webcam.
            if key == IMAGE_TAKER_ORD:
                counter = image_taker(numberOfPhotos, cap, save_folder, delay, counter)

            #If the user presses q, it analyzes images and leaves the webcam.
            elif key == ord(ANALYZE_IMG_ORD):
                analyzeImages()
                break
                

            #If the user presses c, it will clear out the captured_images directory in case the user wants to restart/retakes images.
            if key == ord(CLEAR_IMAGES_ORD):
                clear_images(save_folder)
        
        cap.release()
        cv.destroyAllWindows
        
        
#Takes images from captured_images directory and gets random data 
#NOTE: 
def analyzeImages():
        counter = 0 #To label images
        p_value = [] #To store all random pixel values
        rgb_values = [] #To put in RGB format
        save_folder = "captured_images"
        directory = os.listdir(save_folder)
        if len(directory) > 0: #If there are photo in captured_images directory.
            for files in directory:
                img_name = os.path.join(save_folder, f"opencv_frame_{counter}.png") 
                imgData = cv.imread(img_name, cv.IMREAD_COLOR_RGB)
                height, width, channels = imgData.shape #Gets the dimensions of the PNG
                randRow = rand.randint(0, height - 1) #Randomize the row pixel value that will be evaluated
                randCol = rand.randint(0, width - 1) #Randomize the col pixel value that will be evaluated
                p_value = (imgData[randRow, randCol]) #Stores BGR image data
                blueValue = p_value[0] #Blue value
                redValue = p_value[1] #Red value
                greenValue = p_value[2] #Green value
                rgb_values.append(redValue)
                rgb_values.append(greenValue)
                rgb_values.append(blueValue)
                stringRGBvalue = "".join(str(i) for i in rgb_values ) 
                
            print("Raw Key: ")
            print(stringRGBvalue)
            string_len = len(stringRGBvalue)
            print("Key Length: ")
            print (string_len)
            entropy()
            return stringRGBvalue
           
                

        else:
             print("No images in directory")

def entropy():
       save_folder = "captured_images"
       directory = os.listdir(save_folder)
       entropy = 0.0
       counter = 0
       if len(directory) > 0:
            for files in directory:
                  img_name = os.path.join(save_folder, f"opencv_frame_{counter}.png") 
                  img = cv.imread(img_name, cv.IMREAD_GRAYSCALE) #Convert the image to greyscale
                  image_pixels = img.size #Size of image
                  histogram = cv.calcHist([img], [0], None, [256], [0,256]) #frequency of each pixel intensity value
                  prob = histogram/image_pixels
                 
                 #Shannon Entropy
                  for p in prob.flatten():
                       if p > 0:
                            entropy -= p * np.log2(p)

            print("Average Entropy: ")
            print(entropy/ 20.0)
                
    

                 
    
 
def main():
    try:
        createImages()
    except KeyboardInterrupt:
        print("\n[!] Program stopped by user.")
  
    
if __name__ == "__main__":
    main()