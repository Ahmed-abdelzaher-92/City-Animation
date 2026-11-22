"""live.py: عرض الأنيميشن لايف بـ Matplotlib من غير ffmpeg خالص.

    python live.py                     # يفتح نافذة فيها المشهد بيتحرك
    python live.py --seconds 15        # مدة اللفة قبل ما يعيد
    python live.py --save-gif out.gif  # حفظ GIF بدل العرض (بيستخدم Pillow مش ffmpeg)

ده وضع العرض المناسب للمناقشة: Matplotlib بيعرض كل إطار أول بأول،
وفي الخلفية كل إطار لسه بيترسم بنفس خوارزميات الرسم بيكسل بيكسل.
"""

import argparse

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from scene import render_frame


def main():
    parser = argparse.ArgumentParser(description="Live city animation (no ffmpeg)")
    parser.add_argument("--seconds", type=float, default=10)
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--scale", type=int, default=2,
                        help="تكبير العرض (2 مناسب للعرض اللايف)")
    parser.add_argument("--save-gif", type=str, default=None,
                        help="حفظ GIF بالمسار ده بدل فتح نافذة العرض")
    args = parser.parse_args()

    total = int(args.seconds * args.fps)
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.axis("off")
    ax.set_title("City Animation - drawn pixel by pixel")
    img = ax.imshow(render_frame(0, scale=args.scale), interpolation="nearest")

    def update(i):
        img.set_data(render_frame((i % total) / total, scale=args.scale))
        return [img]

    anim = FuncAnimation(fig, update, frames=total,
                         interval=1000 / args.fps, blit=True)

    if args.save_gif:
        anim.save(args.save_gif, writer="pillow", fps=args.fps)
        print(f"Saved: {args.save_gif}")
    else:
        plt.show()


if __name__ == "__main__":
    main()
