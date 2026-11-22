"""preview.py: حفظ إطارات ثابتة من المشهد كصور PNG للمعاينة السريعة.

    python preview.py              # 4 لقطات موزعة على اللفة
    python preview.py 0 96 168     # أرقام إطارات محددة من أصل 240
"""

import os
import sys

import matplotlib.image as mpimg

from scene import render_frame

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def main(indices=(0, 60, 120, 180), total=240, scale=4):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for i in indices:
        img = render_frame(i / total, scale=scale)
        path = os.path.join(OUTPUT_DIR, f"preview_{i:04d}.png")
        mpimg.imsave(path, img)
        print(path)


if __name__ == "__main__":
    args = [int(a) for a in sys.argv[1:]]
    main(args or (0, 60, 120, 180))
