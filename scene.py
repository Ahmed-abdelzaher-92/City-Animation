"""
scene.py
========
بناء مشهد "مدينة نهارها جميل" إطار بإطار.
كل عنصر في المشهد بيترسم بخوارزمياتنا (خطوط، دوائر، إهليج، منحنيات، تلوين)
ومفيش ولا استدعاء لأي شكل جاهز من Matplotlib.

العناصر المتحركة:
  - عربية ماشية على طريق مرسوم بمنحنى Bezier وعجلاتها بتلف (خطوط Bresenham)
  - شمس أشعتها بتدور (دايرة Midpoint + خطوط Bresenham)
  - سحاب بيتحرك (إهليجات Midpoint مليانة)
  - عصافير بتخفق (خطوط DDA)
  - خطوط الطريق المتقطعة بتتحرك على امتداد المنحنى
"""

from math import sin, cos, pi

from algorithms import (dda_line, bresenham_line, midpoint_circle,
                        midpoint_ellipse, bezier_curve)

WIDTH, HEIGHT = 320, 180
GROUND_Y = 96  # بداية الجزارة (الأرض الخضرا)

# لوحة الألوان
SKY_TOP = (84, 138, 212)
SKY_BOTTOM = (176, 218, 242)
SUN = (255, 213, 79)
SUN_RAY = (255, 186, 56)
CLOUD = (245, 248, 251)
CLOUD_SHADE = (219, 229, 238)
GRASS = (74, 148, 74)
GRASS_LIGHT = (96, 172, 86)
ROAD = (64, 64, 74)
ROAD_EDGE = (196, 196, 204)
ROAD_DASH = (250, 240, 180)
CAR_BODY = (214, 58, 58)
CAR_CABIN = (188, 46, 50)
CAR_WINDOW = (168, 219, 236)
CAR_WHEEL = (30, 30, 36)
CAR_HUB = (206, 206, 212)
HEADLIGHT = (255, 240, 160)
BIRD = (52, 58, 72)
BUILDINGS = [
    # (x البداية, العرض, أعلى نقطة y, اللون, لون الشبابيك)
    (8,   26, 58, (74, 94, 124),  (244, 224, 138)),
    (40,  20, 72, (94, 114, 144), (214, 226, 240)),
    (64,  30, 46, (62, 82, 112),  (244, 224, 138)),
    (100, 22, 66, (104, 124, 154), (214, 226, 240)),
    (128, 28, 54, (74, 94, 124),  (244, 224, 138)),
    (162, 20, 76, (94, 114, 144), (214, 226, 240)),
    (188, 30, 50, (62, 82, 112),  (244, 224, 138)),
    (224, 24, 68, (104, 124, 154), (214, 226, 240)),
    (254, 30, 56, (74, 94, 124),  (244, 224, 138)),
    (290, 24, 70, (94, 114, 144), (214, 226, 240)),
]
FLOWERS = [(14, 132, (240, 130, 170)), (52, 150, (250, 220, 90)),
           (120, 138, (240, 130, 170)), (236, 146, (250, 220, 90)),
           (276, 160, (240, 130, 170)), (304, 136, (250, 220, 90))]

# الطريق: منحنى Bezier تكعيبي هو العمود الفقري للمشهد
ROAD_CURVE = bezier_curve([(-30, 140), (80, 100), (210, 172), (350, 128)], steps=240)
ROAD_HALF_WIDTH = 15

# حساب طول المنحنى تراكميًا (عشان حركة العربية والعجلات والخطوط المتقطعة)
_arc = [0.0]
for i in range(1, len(ROAD_CURVE)):
    x0, y0 = ROAD_CURVE[i - 1]
    x1, y1 = ROAD_CURVE[i]
    _arc.append(_arc[-1] + ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5)
ROAD_LENGTH = _arc[-1]


def road_point(distance):
    """نقطة على خط منتصف الطريق على مسافة معينة (بالبيكسل) من بدايته."""
    d = distance % ROAD_LENGTH
    for i in range(1, len(_arc)):
        if _arc[i] >= d:
            seg = _arc[i] - _arc[i - 1]
            t = 0 if seg == 0 else (d - _arc[i - 1]) / seg
            x0, y0 = ROAD_CURVE[i - 1]
            x1, y1 = ROAD_CURVE[i]
            return x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
    return ROAD_CURVE[-1]


def draw_sky(frame):
    bands = 60
    for i in range(bands):
        t = i / (bands - 1)
        color = tuple(round(SKY_TOP[c] + (SKY_BOTTOM[c] - SKY_TOP[c]) * t)
                      for c in range(3))
        y0 = round(i * HEIGHT / bands)
        y1 = round((i + 1) * HEIGHT / bands)
        frame.fill_rect(0, y0, WIDTH - 1, y1, color)


def draw_sun(frame, t):
    cx, cy, r = 266, 34, 15
    frame.plot(midpoint_circle(cx, cy, r, filled=True), SUN)
    frame.plot(midpoint_circle(cx, cy, r), (235, 178, 50))
    # 8 أشعة بتدور ببطء بخطوط Bresenham
    for k in range(8):
        ang = 2 * pi * t + k * pi / 4
        x0, y0 = cx + (r + 3) * cos(ang), cy + (r + 3) * sin(ang)
        x1, y1 = cx + (r + 9) * cos(ang), cy + (r + 9) * sin(ang)
        frame.plot(bresenham_line(x0, y0, x1, y1), SUN_RAY)


def draw_cloud(frame, cx, cy):
    # السحابة عبارة عن إهليجات مليانة بخوارزمية نقطة المنتصف
    frame.plot(midpoint_ellipse(cx + 2, cy + 3, 17, 6, filled=True), CLOUD_SHADE)
    frame.plot(midpoint_ellipse(cx, cy, 15, 7, filled=True), CLOUD)
    frame.plot(midpoint_ellipse(cx - 11, cy + 2, 9, 5, filled=True), CLOUD)
    frame.plot(midpoint_ellipse(cx + 12, cy + 1, 10, 6, filled=True), CLOUD)


def draw_clouds(frame, t):
    speed = 9  # بيكسل لكل ثانية
    span = WIDTH + 90
    for cx0, cy in ((30, 24), (150, 44), (250, 18)):
        cx = (cx0 + speed * t * 10 + 45) % span - 45
        draw_cloud(frame, cx, cy)


def draw_buildings(frame):
    for x0, w, top, color, win_color in BUILDINGS:
        frame.fill_rect(x0, top, x0 + w, GROUND_Y, color)
        frame.plot(bresenham_line(x0, top, x0 + w, top), (44, 56, 78))
        # شبابيك مضيئة في شبكة منتظمة
        for wy in range(top + 5, GROUND_Y - 4, 8):
            for wx in range(x0 + 4, x0 + w - 4, 8):
                frame.fill_rect(wx, wy, wx + 2, wy + 3, win_color)
    # عمود إنارة على أعلى مبنى (خط + دايرة صغيرة)
    frame.plot(bresenham_line(194, 50, 194, 40), (40, 50, 70))
    frame.plot(midpoint_circle(194, 38, 2, filled=True), (240, 90, 90))


def draw_ground(frame):
    frame.fill_rect(0, GROUND_Y, WIDTH - 1, HEIGHT - 1, GRASS)
    frame.fill_rect(0, GROUND_Y, WIDTH - 1, GROUND_Y + 4, GRASS_LIGHT)
    for fx, fy, color in FLOWERS:
        frame.plot(dda_line(fx, fy, fx, fy + 4), (40, 110, 48))       # الساق
        frame.plot(midpoint_circle(fx, fy, 2, filled=True), color)    # الوردة


def draw_road(frame, t):
    # جسم الطريق: مضلع بين منحنيين مزاحين (فوق وتحت خط المنتصف) متلوّن بـ Scanline
    upper = [(x, y - ROAD_HALF_WIDTH) for x, y in ROAD_CURVE]
    lower = [(x, y + ROAD_HALF_WIDTH) for x, y in reversed(ROAD_CURVE)]
    frame.fill_polygon(upper + lower, ROAD)
    # حرفة الطريق: الخطين العلوي والسفلي بـ DDA
    for pts in (upper, list(reversed(lower))):
        for i in range(len(pts) - 1):
            frame.plot(dda_line(*pts[i], *pts[i + 1]), ROAD_EDGE)
    # الخطوط المتقطعة في المنتصف: قطع DDA قصيرة بتتحرك على امتداد المنحنى
    dash_len, gap = 10, 12
    offset = (t * 34) % (dash_len + gap)
    d = -offset
    while d < ROAD_LENGTH:
        p0 = road_point(d)
        p1 = road_point(d + dash_len)
        frame.plot(dda_line(p0[0], p0[1], p1[0], p1[1]), ROAD_DASH)
        d += dash_len + gap


def draw_car(frame, t):
    dist = t * (ROAD_LENGTH + 120) - 60  # العربية بتعدي الشاشة كلها في اللفة
    cx, cy = road_point(dist)
    wheel_r = 5
    wheel_y = cy - wheel_r
    rear_x, front_x = cx - 10, cx + 10
    # جسم العربية وكابينة (شبه منحرف متلوّن بـ Scanline)
    frame.fill_rect(cx - 19, cy - 17, cx + 19, cy - 8, CAR_BODY)
    frame.fill_polygon([(cx - 11, cy - 17), (cx - 6, cy - 25),
                        (cx + 7, cy - 25), (cx + 12, cy - 17)], CAR_CABIN)
    frame.fill_rect(cx - 8, cy - 23, cx - 1, cy - 18, CAR_WINDOW)
    frame.fill_rect(cx + 2, cy - 23, cx + 9, cy - 18, CAR_WINDOW)
    frame.fill_rect(cx + 17, cy - 15, cx + 19, cy - 12, HEADLIGHT)
    frame.plot(bresenham_line(cx - 19, cy - 17, cx + 19, cy - 17), (150, 34, 38))
    # العجل: دوائر Midpoint مليانة + 3 خطوط Bresenham بتلف كأذرع
    wheel_angle = -dist / wheel_r  # زاوية اللف مربوطة بالمسافة الفعلية
    for wx in (rear_x, front_x):
        frame.plot(midpoint_circle(wx, wheel_y, wheel_r, filled=True), CAR_WHEEL)
        frame.plot(midpoint_circle(wx, wheel_y, wheel_r), (12, 12, 16))
        frame.plot(midpoint_circle(wx, wheel_y, 1, filled=True), CAR_HUB)
        for k in range(3):
            ang = wheel_angle + k * pi / 3
            x1 = wx + (wheel_r - 1) * cos(ang)
            y1 = wheel_y + (wheel_r - 1) * sin(ang)
            frame.plot(bresenham_line(wx, wheel_y, x1, y1), CAR_HUB)


def draw_birds(frame, t):
    flap = round(2.5 * sin(2 * pi * 3 * t))  # رفرفة
    for bx0, by in ((250, 26), (278, 38)):
        bx = (bx0 - 26 * t * 10) % (WIDTH + 40) - 20
        for dx in (0, 1):  # سماكة الجناح 2 بيكسل
            frame.plot(dda_line(bx - 6, by - 3 - flap, bx, by + dx), BIRD)
            frame.plot(dda_line(bx, by + dx, bx + 6, by - 3 - flap), BIRD)


def render_frame(t, scale=4):
    """بناء إطار كامل عند اللحظة t (من 0 لـ 1) وإرجاع صورة NumPy مكبرة."""
    from raster import Frame
    frame = Frame(WIDTH, HEIGHT)
    draw_sky(frame)
    draw_sun(frame, t)
    draw_clouds(frame, t)
    draw_buildings(frame)
    draw_ground(frame)
    draw_road(frame, t)
    draw_car(frame, t)
    draw_birds(frame, t)
    return frame.to_image(scale)
