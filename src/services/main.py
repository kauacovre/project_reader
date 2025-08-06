# main.py - The main entry point
from frame_extractor import extract_key_frames
from scene_detector import extract_smart_frames
from video_player import play_video

def main():
    video_path = "../../video.mp4"
    
    print("🎬 Professional Video Analyzer")
    print("1. Extract regular frames")
    print("2. Smart scene detection")
    print("3. Play video")
    
    choice = input("Choose option (1-3): ")
    
    if choice == "1":
        extract_key_frames(video_path, 5)
    elif choice == "2":
        extract_smart_frames(video_path, 5)
    elif choice == "3":
        play_video(video_path)
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()