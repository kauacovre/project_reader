import cv2
import os
import numpy as np

def extract_smart_frames(video_path, num_frames=5, threshold=30, output_folders="smart_frames"):
    """Extract frames when scenes change significantly"""

    # Create folder for frames
    frames_folder = "smart_frames"
    if not os.path.exists(frames_folder):
        os.makedirs(frames_folder)
        print(f"Created folder: {frames_folder}")

    video = cv2.VideoCapture(video_path)

    if not video.isOpened():
        print("Ops! Couldn't open the file")
        return
    
    print("Analyzing video for scene changes")

    ret, prev_frame = video.read()
    if not ret:
        print("Can't read first frame")
        return

    # Convert to grayscale for comparison
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

    filename = os.path.join(frames_folder, f"scene_change_0.jpg")
    cv2.imwrite(filename, prev_frame)
    print(f"saved: {filename}")

    saved_count = 1
    frame_count = 1

    while saved_count < num_frames:
        ret, current_frame = video.read()
        if not ret:
            break

        current_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(prev_gray, current_gray)
        change_score = np.mean(diff)


        if change_score > threshold:
            filename = os.path.join(frames_folder, f"scene_change_{saved_count}.jpg")
            cv2.imwrite(filename, current_frame)
            print(f"Saved: {filename} (change score: {change_score:.1f})")
            saved_count += 1

            prev_gray = current_gray
        
        frame_count += 1

    video.release()
    print(f"Smart extraction complete! Found {saved_count} scene changes")

extract_smart_frames("../../video.mp4", 30, threshold=30)