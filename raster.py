"""
raster.py
=========
إطار بيكسل بسيط: كل الرسم في المشروع بيحصل على مصفوفة NumPy،
وكل شكل بيتكتب بيكسل بيكسل عن طريق الخوارزميات اللي في algorithms.py.
"""

import numpy as np

from algorithms import scanline_fill


class Frame:
    def __init__(self, width, height, bg=(0, 0, 0)):
        self.width = width
        self.height = height
        self.pixels = np.zeros((height, width, 3), dtype=np.uint8)
        self.pixels[:] = bg

    def plot(self, points, color):
        """رسم قائمة بيكسلات (x, y) بلون معين مع تجاهل اللي بره الشاشة."""
        w, h = self.width, self.height
        for x, y in points:
            if 0 <= x < w and 0 <= y < h:
                self.pixels[y, x] = color

    def fill_rect(self, x0, y0, x1, y1, color):
        """مستطيل مصمت (يُستخدم للخلفيات والمباني)."""
        x0, x1 = sorted((int(round(x0)), int(round(x1))))
        y0, y1 = sorted((int(round(y0)), int(round(y1))))
        x0, x1 = max(0, x0), min(self.width - 1, x1)
        y0, y1 = max(0, y0), min(self.height - 1, y1)
        if x0 <= x1 and y0 <= y1:
            self.pixels[y0:y1 + 1, x0:x1 + 1] = color

    def fill_polygon(self, vertices, color):
        """تلوين مضلع حر بخوارزمية Scanline."""
        self.plot(scanline_fill(vertices, self.width, self.height), color)

    def to_image(self, scale=1):
        """تكبير الإطار بأقرب جوار (بيحافظ على شكل البيكسل آرت)."""
        img = self.pixels
        if scale > 1:
            img = np.repeat(np.repeat(img, scale, axis=0), scale, axis=1)
        return img
