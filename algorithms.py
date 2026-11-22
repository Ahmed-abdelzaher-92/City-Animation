"""
algorithms.py
=============
خوارزميات الرسم الكلاسيكية مكتوبة من الصفر (من غير أي أشكال جاهزة).
كل دالة بترجع قائمة بيكسلات (x, y) بنظام إحداثيات الشاشة: (0, 0) فوق على الشمال، و y بتزيد لتحت.

المحتوى:
  - dda_line          رسم خط بخوارزمية DDA
  - bresenham_line    رسم خط بخوارزمية Bresenham
  - midpoint_circle   رسم / تلوين دايرة بخوارزمية نقطة المنتصف
  - midpoint_ellipse  رسم / تلوين إهليج (بيضاوي) بخوارزمية نقطة المنتصف
  - bezier_curve      رسم منحنى Bezier (أي درجة) بمعادلة Bernstein
  - scanline_fill     تلوين أي مضلع بخوارزمية Scanline (قاعدة even-odd)
"""

from math import comb


# ---------------------------------------------------------------------------
# 1) رسم الخطوط
# ---------------------------------------------------------------------------

def dda_line(x0, y0, x1, y1):
    """Digital Differential Analyzer: بنمشي على المحور الأطول خطوة خطوة."""
    x0, y0, x1, y1 = map(float, (x0, y0, x1, y1))
    dx, dy = x1 - x0, y1 - y0
    steps = int(max(abs(dx), abs(dy)))
    if steps == 0:
        return [(round(x0), round(y0))]
    x_inc, y_inc = dx / steps, dy / steps
    points = []
    x, y = x0, y0
    for _ in range(steps + 1):
        points.append((round(x), round(y)))
        x += x_inc
        y += y_inc
    return points


def bresenham_line(x0, y0, x1, y1):
    """Bresenham: قرار صحيح (integer) من غير أي كسور، شغال في كل الاتجاهات."""
    x0, y0, x1, y1 = (int(round(v)) for v in (x0, y0, x1, y1))
    points = []
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    return points


# ---------------------------------------------------------------------------
# 2) رسم الدايرة والإهليج
# ---------------------------------------------------------------------------

def midpoint_circle(cx, cy, r, filled=False):
    """خوارزمية نقطة المنتصف للدايرة بتناظر 8 أجزاء.
    filled=True بترجع كل بيكسلات الدايرة مليانة (بامتدادات أفقية بين النقط المتناظرة)."""
    cx, cy, r = (int(round(v)) for v in (cx, cy, r))
    if r <= 0:
        return [(cx, cy)]
    points = []
    spans = {}  # row -> [min_x, max_x] للتلوين

    def emit(px, py):
        if filled:
            if py not in spans:
                spans[py] = [px, px]
            else:
                spans[py][0] = min(spans[py][0], px)
                spans[py][1] = max(spans[py][1], px)
        else:
            points.append((px, py))

    x, y = r, 0
    p = 1 - r
    while x >= y:
        for dx, dy in ((x, y), (y, x), (-y, x), (-x, y),
                       (-x, -y), (-y, -x), (y, -x), (x, -y)):
            emit(cx + dx, cy + dy)
        y += 1
        if p <= 0:
            p += 2 * y + 1
        else:
            x -= 1
            p += 2 * (y - x) + 1

    if filled:
        for row, (x_min, x_max) in spans.items():
            for px in range(x_min, x_max + 1):
                points.append((px, row))
    return points


def midpoint_ellipse(cx, cy, rx, ry, filled=False):
    """خوارزمية نقطة المنتصف للإهليج (منطقتين: ميل أقل ثم أكبر من 1)."""
    cx, cy, rx, ry = (int(round(v)) for v in (cx, cy, rx, ry))
    if rx <= 0 or ry <= 0:
        return [(cx, cy)]
    points = []
    spans = {}

    def emit(x, y):
        if filled:
            for row in (cy + y, cy - y):
                if row not in spans:
                    spans[row] = [cx - x, cx + x]
                else:
                    spans[row][0] = min(spans[row][0], cx - x)
                    spans[row][1] = max(spans[row][1], cx + x)
        else:
            points.extend([(cx + x, cy + y), (cx - x, cy + y),
                           (cx + x, cy - y), (cx - x, cy - y)])

    rx2, ry2 = rx * rx, ry * ry
    x, y = 0, ry
    # المنطقة الأولى
    p = ry2 - rx2 * ry + 0.25 * rx2
    dx, dy = 0.0, 2.0 * rx2 * y
    while dx < dy:
        emit(x, y)
        x += 1
        dx += 2 * ry2
        if p < 0:
            p += ry2 + dx
        else:
            y -= 1
            dy -= 2 * rx2
            p += ry2 + dx - dy
    # المنطقة التانية
    p = ry2 * (x + 0.5) ** 2 + rx2 * (y - 1) ** 2 - rx2 * ry2
    while y >= 0:
        emit(x, y)
        y -= 1
        dy -= 2 * rx2
        if p > 0:
            p += rx2 - dy
        else:
            x += 1
            dx += 2 * ry2
            p += rx2 - dy + dx

    if filled:
        for row, (x_min, x_max) in spans.items():
            for px in range(x_min, x_max + 1):
                points.append((px, row))
    return points


# ---------------------------------------------------------------------------
# 3) رسم المنحنيات
# ---------------------------------------------------------------------------

def bezier_curve(control_points, steps=120):
    """منحنى Bezier من أي درجة بمعادلة Bernstein (de Casteljau برضه ممكن).
    بيرجع نقاط float على المنحنى؛ التحويل لبيكسلات بيحصل في المشهد."""
    n = len(control_points) - 1
    points = []
    for i in range(steps + 1):
        t = i / steps
        x = y = 0.0
        for k, (px, py) in enumerate(control_points):
            basis = comb(n, k) * (1 - t) ** (n - k) * t ** k
            x += basis * px
            y += basis * py
        points.append((x, y))
    return points


# ---------------------------------------------------------------------------
# 4) تلوين المضلعات
# ---------------------------------------------------------------------------

def scanline_fill(vertices, width, height):
    """تلوين مضلع (قائمة رؤوس float) بخوارزمية Scanline بقاعدة even-odd."""
    n = len(vertices)
    ys = [v[1] for v in vertices]
    y_min = max(0, int(min(ys)))
    y_max = min(height - 1, int(max(ys)) + 1)

    edges = []  # (y_top, y_bottom, x_at_top, inverse_slope)
    for i in range(n):
        x0, y0 = vertices[i]
        x1, y1 = vertices[(i + 1) % n]
        if y0 == y1:
            continue
        if y0 > y1:
            x0, y0, x1, y1 = x1, y1, x0, y0
        edges.append((y0, y1, x0, (x1 - x0) / (y1 - y0)))

    pixels = []
    for y in range(y_min, y_max + 1):
        xs = []
        for y0, y1, x_top, inv_slope in edges:
            if y0 <= y < y1:
                xs.append(x_top + inv_slope * (y - y0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            x_start = max(0, round(xs[i]))
            x_end = min(width - 1, round(xs[i + 1]))
            for x in range(x_start, x_end + 1):
                pixels.append((x, y))
    return pixels
