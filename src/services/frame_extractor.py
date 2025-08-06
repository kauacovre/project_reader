# Import de library from reade video
import cv2

# For creating folders
import os


# This creates a function that can extract key frames from any video
def extract_key_frames(video_path, num_frames = 5, output_folder="extracted_frames"):
    """Extract frames at regular intervals"""


    frames_folder = "extracted_frames"

    # Create a folder for frames
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created folder: {output_folder}")


    # Open the video file (same as before)
    video = cv2.VideoCapture(video_path)


    # Check if the video opened successfully
    if not video.isOpened():
        print("Ops!, couldn't open the file")
        return
    

    # Get total frames
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Total frames: {total_frames}")


    # Calculate which frames to extract
    frame_interval = total_frames // num_frames
    frame_count = 0
    saved_count = 0


    # Loop to the read and show many frames!
    while True:

        # Read the next frame
        ret, frame = video.read()

        # If no more frames, stop
        if not ret: 
            break
        

        # Check if this is a frame we want to save
        if frame_count % frame_interval == 0:
            filename = os.path.join(frames_folder, f"summary_frame_{saved_count}.jpg")
            cv2.imwrite(filename, frame)
            print(f"Saved: {filename}")
            saved_count += 1
        
        frame_count += 1


        # Stop when we have enough key frames
        if saved_count >= num_frames:
            break
        

    # Close the video file properly
    video.release()
    print(f"Summary complete! Saved {saved_count} key frames in '{frames_folder}' folder")

extract_key_frames("../../video.mp4", 5)