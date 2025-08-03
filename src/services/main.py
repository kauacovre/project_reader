# Import de library from reade video
import cv2


# Let's open a video file
video = cv2.VideoCapture("video.mp4") 


if video.isOpened():
    print("Sucess! Videos is opened.")


    # Let's read the first frame!
    ret, frame = video.read()


    # if and Else, if frame true or false
    if ret:
        print("Great frame!")
        
        print(f"frame size: {frame.shape}" ) # Shows the dimensions of the video frame.

       
        cv2.imshow("My first frame", frame)  # Show the frame in a window
        cv2.waitKey(0)                       # Wait for any key press
        cv2.destroyAllWindows()              # Close all windows after pressing the key


    else:
        print("Couldn't read frame")
else:
    print("Oops! Couldn't open video")