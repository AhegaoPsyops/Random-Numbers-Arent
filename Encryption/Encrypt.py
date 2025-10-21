import os 
import glob
import sys
import cv2 as cv 
import numpy as np
from pathlib import Path
import time




    
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
                     img_name = os.path.join(save_folder, f"opencv_frame_{counter}.png") #Names image  and joins it to the save folder (captured_images)
                     imgData = cv.imwrite(img_name, frame) #Writes the image into save folder
                     print("{} written!".format(img_name))  #Debugging
                     print(counter)
                     counter += 1  #Adds to image counter for naming purposes.
                     time.sleep(delay)
            

        #If the user presses q, it leaves the webcam and deletes the PNGs from the captured_images directory. (Will be updated with GUI later)
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
        
        

        
#Takes images from captured_images directory and analyzes it (in progress)   
def analyzeImages():
        counter = 0
        save_folder = "captured_images"
        directory = os.listdir(save_folder)
        if len(directory) > 0:
            for files in directory:
                img_name = os.path.join(save_folder, f"opencv_frame_{counter}.png")
                imgData = cv.imread(img_name, cv.IMREAD_COLOR)
                print(f"Image data type: {imgData.dtype}")
        else:
             print("No images in directory")
               
                
      
        

def main():
    createImages()
    
    

if __name__ == "__main__":
    main()
