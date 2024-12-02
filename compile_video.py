import imageio
import os

def compile_gif_to_video(gif_path, video_path):
    reader = imageio.get_reader(gif_path)
    fps = 10
    writer = imageio.get_writer(video_path, fps=fps)
    for frame in reader:
        writer.append_data(frame)
    writer.close()
    print(f"Video saved to {video_path}")

if __name__ == "__main__":
    gif_path = "models/frames/training.gif"
    video_path = "models/training.mp4"
    compile_gif_to_video(gif_path, video_path)
