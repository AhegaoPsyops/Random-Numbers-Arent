import cv2 as cv
import numpy as np

class Encrypt:
    #Starts up OpenCV webcam. Use contour movement detection in order to see the changes of 
    def startOpenCV():
        #Captures video
        cap = cv.VideoCapture(0)

        while True:
            #Reads a frame
            ret, frame = cap.read()

            if not ret:
                print("Error!")
                break
       
        # Display the resulting frame
            cv.imshow('Frame_final', frame)
            if cv.waitKey(1) == ord('q'):
                exit()
    
        cap.release()
        cv.destroyAllWindows
            

    def collectData():
        pass



def main():
    object = Encrypt
    object.startOpenCV()

if __name__ == "__main__":
    main()
