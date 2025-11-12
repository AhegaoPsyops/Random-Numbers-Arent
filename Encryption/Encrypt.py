import os 
import glob
import sys
import cv2 as cv 
import numpy as np
from pathlib import Path
import time
import random as rand
import hashlib


#Starts up OpenCV webcam, takes photos from the webcam that will be used to collect data from. 
def createImages():
        #Set number of photos taken
        numberOfPhotos = 10
        #Image counter used for file naming process/debugging
        counter = 0
        #Timer for photos being taken after each iteration
        delay = 0.5

        #Creates a folder for saved photos if captured_photos is not there already 
        #(default: it should be there)
        save_folder = "captured_images"
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        
        #Captures video
        cap = cv.VideoCapture(0)
      
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

        #If the user presses the space bar, it takes PNG images of the frame being captured via webcam.
            if cv.waitKey(1) % 256 == 32:
                for i in range(numberOfPhotos):
                     ret, frame = cap.read() #Reads frame
                     img_name = os.path.join(save_folder, f"opencv_frame_{counter}.png") #Names image  and joins it to the save folder (captured_images)
                     imgData = cv.imwrite(img_name, frame) #Writes the image into save folder
                     print("{} written!".format(img_name))  #Debugging
                     print(counter)
                     counter += 1  #Adds to image counter for naming purposes.
                     time.sleep(delay) #Delay with photos being taken.
            

        #If the user presses q, it analyzes images and leaves the webcam.
            if cv.waitKey(1) == ord('q'):
                analyzeImages()
                exit()
                

        #If the user presses c, it will clear out the captured_images directory in case the user wants to restart/retakes images.
            if cv.waitKey(1) == ord('c'):
                i = 0
                for fileName in os.listdir(save_folder):
                     if fileName.endswith('.png'):
                         os.remove(os.path.join(save_folder, f"opencv_frame_{i}.png"))
                         i+= 1
               
        
        cap.release()
        cv.destroyAllWindows
        
        
#Takes images from captured_images directory and gets random data and encrypts it with SHA-256 Hash
#NOTE: the image dimensions are 480 by 640!!
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
                randRow = rand.randint(0, height) #Randomize the row pixel value that will be evaluated
                randCol = rand.randint(0, width) #Randomize the col pixel value that will be evaluated
                p_value = (imgData[randRow, randCol]) #Stores BGR image data
                blueValue = p_value[0] #Blue value
                redValue = p_value[1] #Red value
                greenValue = p_value[2] #Green value
                rgb_values.append(redValue)
                rgb_values.append(greenValue)
                rgb_values.append(blueValue)
                stringRGBvalue = "".join(str(i) for i in rgb_values ) 
            
            print(stringRGBvalue)
            return stringRGBvalue
                
                
                

        else:
             print("No images in directory")


 
def main():
    createImages()
    
if __name__ == "__main__":
    main()