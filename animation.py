"""
animation.py
============
التشغيل الرئيسي: بيبني كل إطارات المشهد ويصدّرها فيديو MP4.

التشغيل:
    python animation.py            # 10 ثواني، 24 إطار/ثانية
    python animation.py --seconds 6 --fps 20

المخرجات:
    output/city_animation.mp4
"""

import argparse
import os
import shutil
import subprocess

import matplotlib.image as mpimg

from scene import render_frame

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
FRAMES_DIR = os.path.join(OUTPUT_DIR, "frames")


def main():
    parser = argparse.ArgumentParser(description="Maze-free city animation renderer")
    parser.add_argument("--seconds", type=float, default=10)
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--scale", type=int, default=4)
    parser.add_argument("--keep-frames", action="store_true")
    args = parser.parse_args()

    total = int(args.seconds * args.fps)
    os.makedirs(FRAMES_DIR, exist_ok=True)
    print(f"Rendering {total} frames ...")
    for i in range(total):
        img = render_frame(i / total, scale=args.scale)
        mpimg.imsave(os.path.join(FRAMES_DIR, f"frame_{i:04d}.png"), img)
        if (i + 1) % 24 == 0 or i == total - 1:
            print(f"  {i + 1}/{total}")

    video_path = os.path.join(OUTPUT_DIR, "city_animation.mp4")
    print("Encoding video with ffmpeg ...")
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(args.fps),
        "-i", os.path.join(FRAMES_DIR, "frame_%04d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        video_path,
    ], check=True)

    if not args.keep_frames:
        shutil.rmtree(FRAMES_DIR)
    print(f"Done: {video_path}")


if __name__ == "__main__":
    main()
