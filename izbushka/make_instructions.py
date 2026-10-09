#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор схемы сборки «Избушка на курьих ножках» из LEGO.
Только системные детали (без Technic). Высота модели ~15 см.

Выход (папка out/):
  - izbushka_instructions.pdf  — пошаговая схема сборки (PDF)
  - pages/page_XX.png          — страницы схемы (PNG)
  - izbushka_final.png         — финальное изображение собранной модели

Единицы: x, y — в стенах (студах, 8 мм), z — в пластинах (3.2 мм),
1 брусок = 3 пластины.
"""

import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ----------------------------------------------------------------------------
# Константы и палитра
# ----------------------------------------------------------------------------
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
PAGES_DIR = os.path.join(OUT_DIR, "pages")

PLATE_MM = 3.2
SLOPE_H = 3      # высота ската 45° в пластинах
BRICK_H = 3

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(sz, bold=False):
    return ImageFont.truetype(FONT_BOLD_PATH if bold else FONT_PATH, sz)


RGB = {
    "dark_tan":      (150, 133, 96),
    "reddish_brown": (92, 45, 20),
    "dark_orange":   (176, 92, 4),
    "dark_gray":     (92, 94, 88),
    "light_gray":    (176, 180, 176),
    "glass":         (158, 201, 226, 170),
    "black":         (34, 32, 30),
}

# ----------------------------------------------------------------------------
# Модель: список деталей
# ----------------------------------------------------------------------------
# kind: brick | plate | tile | glass | slope | corner_slope | cheese
#       | round_brick | cone | round_plate
# slope rot: направление спуска: 'N'(−y) 'S'(+y) 'W'(−x) 'E'(+x)
# corner_slope high: в каком углу footprint высокая точка: 'NE','NW','SE','SW'

PARTS = []


def add(kind, x, y, z, w, d, color, step, name, pn, rot=None, high=None):
    PARTS.append(dict(kind=kind, x=x, y=y, z=z, w=w, d=d, color=color,
                      step=step, name=name, pn=pn, rot=rot, high=high))


def brick(x, y, z, w, d, c, step, name, pn):
    add("brick", x, y, z, w, d, c, step, name, pn)


def plate(x, y, z, w, d, c, step, name, pn):
    add("plate", x, y, z, w, d, c, step, name, pn)


def tile(x, y, z, w, d, c, step, name, pn):
    add("tile", x, y, z, w, d, c, step, name, pn)


def glass(x, y, z, w, d, step):
    add("glass", x, y, z, w, d, "glass", step, "Брусок 1×2 прозрачный (окно)", "3004")


def slope(x, y, z, rot, c, step, name, pn):
    add("slope", x, y, z, 2, 2, c, step, name, pn, rot=rot)


def corner_slope(x, y, z, high, c, step, name, pn):
    add("corner_slope", x, y, z, 2, 2, c, step, name, pn, high=high)


def cheese(x, y, z, rot, c, step):
    add("cheese", x, y, z, 1, 1, c, step, "Скат 1×1 «сыр» (2/3)", "54200", rot=rot)


def build_model():
    """Собрать спецификацию модели по шагам."""
    DT, RB, RO, DG, LG, BK = ("dark_tan", "reddish_brown", "dark_orange",
                              "dark_gray", "light_gray", "black")
    N20 = "Пластина 2×4"
    N22 = "Пластина 2×2"
    N23 = "Пластина 2×3"
    N44 = "Пластина 4×4"
    N11 = "Брусок 1×1"
    N12 = "Брусок 1×2"
    N14 = "Брусок 1×4"
    N16 = "Брусок 1×6"
    N22b = "Брусок 2×2"
    NS2 = "Скат 2×2 45°"
    NSC = "Скат угловой 2×2 45°"

    # ---- Шаг 1: стопы (2 шт) ----
    for lx in (1, 5):
        plate(lx, 2, 0, 2, 4, DT, 1, N20, "3020")
        cheese(lx, 2, 1, "N", DT, 1)       # два передних пальца
        cheese(lx + 1, 2, 1, "N", DT, 1)
        cheese(lx + 1, 5, 1, "S", DT, 1)   # задний палец

    # ---- Шаг 2: голени (2 шт по 3 бруска) ----
    for lx in (1, 5):
        for i in range(3):
            brick(lx, 3, 1 + 3 * i, 2, 2, DT, 2, N22b, "3003")

    # ---- Шаг 3: колени и бёдра (2 шт) ----
    for lx in (1, 5):
        plate(lx, 2, 10, 2, 3, DT, 3, N23, "3021")   # колено (со смещением)
        brick(lx, 2, 11, 2, 2, DT, 3, N22b, "3003")
        brick(lx, 2, 14, 2, 2, DT, 3, N22b, "3003")
        plate(lx, 2, 17, 2, 3, DT, 3, N23, "3021")   # тазобедренная пластина

    # ---- Шаг 4: платформа 8×8 (2 слоя) ----
    for z in (18, 19):
        for px in (0, 4):
            for py in (0, 4):
                plate(px, py, z, 4, 4, RB, 4, N44, "3031")

    # ---- Шаг 5: венец 1 (проём двери x=3..4) ----
    brick(1, 1, 20, 2, 1, RB, 5, N12, "3004")
    brick(5, 1, 20, 2, 1, RB, 5, N12, "3004")
    brick(1, 6, 20, 6, 1, RB, 5, N16, "3009")
    brick(1, 2, 20, 1, 4, RB, 5, N14, "3010")
    brick(6, 2, 20, 1, 4, RB, 5, N14, "3010")

    # ---- Шаг 6: венец 2 (окна по бокам) ----
    brick(1, 1, 23, 1, 2, RB, 6, N12, "3004")
    glass(1, 3, 23, 1, 2, 6)
    brick(1, 5, 23, 1, 2, RB, 6, N12, "3004")
    brick(6, 1, 23, 1, 2, RB, 6, N12, "3004")
    glass(6, 3, 23, 1, 2, 6)
    brick(6, 5, 23, 1, 2, RB, 6, N12, "3004")
    brick(2, 1, 23, 1, 1, RB, 6, N11, "3005")
    brick(5, 1, 23, 1, 1, RB, 6, N11, "3005")
    brick(2, 6, 23, 4, 1, RB, 6, N14, "3010")

    # ---- Шаг 7: венец 3 (окна продолжаются) ----
    brick(1, 1, 26, 2, 1, RB, 7, N12, "3004")
    brick(5, 1, 26, 2, 1, RB, 7, N12, "3004")
    brick(1, 6, 26, 6, 1, RB, 7, N16, "3009")
    brick(1, 2, 26, 1, 1, RB, 7, N11, "3005")
    glass(1, 3, 26, 1, 2, 7)
    brick(1, 5, 26, 1, 1, RB, 7, N11, "3005")
    brick(6, 2, 26, 1, 1, RB, 7, N11, "3005")
    glass(6, 3, 26, 1, 2, 7)
    brick(6, 5, 26, 1, 1, RB, 7, N11, "3005")

    # ---- Шаг 8: венец 4 (перемычка над дверью) ----
    brick(1, 1, 29, 1, 6, RB, 8, N16, "3009")
    brick(6, 1, 29, 1, 6, RB, 8, N16, "3009")
    brick(2, 1, 29, 4, 1, RB, 8, N14, "3010")
    brick(2, 6, 29, 4, 1, RB, 8, N14, "3010")

    # ---- Шаг 9: венец 5 ----
    brick(1, 1, 32, 6, 1, RB, 9, N16, "3009")
    brick(1, 6, 32, 6, 1, RB, 9, N16, "3009")
    brick(1, 2, 32, 1, 4, RB, 9, N14, "3010")
    brick(6, 2, 32, 1, 4, RB, 9, N14, "3010")

    # ---- Шаг 10: свес крыши 8×8 (2 слоя) ----
    for z in (35, 36):
        for px in (0, 4):
            for py in (0, 4):
                plate(px, py, z, 4, 4, RO, 10, N44, "3031")

    # ---- Шаг 11: нижний пояс скатов ----
    corner_slope(0, 0, 37, "SE", RO, 11, NSC, "3045")
    corner_slope(6, 0, 37, "SW", RO, 11, NSC, "3045")
    corner_slope(0, 6, 37, "NE", RO, 11, NSC, "3045")
    corner_slope(6, 6, 37, "NW", RO, 11, NSC, "3045")
    slope(0, 2, 37, "W", RO, 11, NS2, "3039")   # у (0,4) будет труба
    slope(6, 2, 37, "E", RO, 11, NS2, "3039")
    slope(6, 4, 37, "E", RO, 11, NS2, "3039")
    slope(2, 0, 37, "N", RO, 11, NS2, "3039")
    slope(4, 0, 37, "N", RO, 11, NS2, "3039")
    slope(2, 6, 37, "S", RO, 11, NS2, "3039")
    slope(4, 6, 37, "S", RO, 11, NS2, "3039")

    # ---- Шаг 12: заполнение центра + труба ----
    for i in range(3):
        plate(2, 2, 37 + i, 4, 4, RO, 12, N44, "3031")
    brick(0, 4, 37, 2, 2, DG, 12, N22b, "3003")
    brick(0, 4, 40, 2, 2, DG, 12, N22b, "3003")
    tile(0, 4, 43, 2, 2, DG, 12, "Плита 2×2 (без пипсов)", "3068b")
    add("round_plate", 0, 4, 44, 1, 1, LG, 12, "Круглая пластина 1×1", "6141")
    add("round_plate", 0, 4, 45, 1, 1, LG, 12, "Круглая пластина 1×1", "6141")
    add("round_plate", 0, 4, 46, 1, 1, LG, 12, "Круглая пластина 1×1", "6141")

    # ---- Шаг 13: верхние скаты + шпиль ----
    corner_slope(2, 2, 40, "SE", RO, 13, NSC, "3045")
    corner_slope(4, 2, 40, "SW", RO, 13, NSC, "3045")
    corner_slope(2, 4, 40, "NE", RO, 13, NSC, "3045")
    corner_slope(4, 4, 40, "NW", RO, 13, NSC, "3045")
    add("round_plate", 3, 3, 43, 1, 1, BK, 13, "Круглая пластина 1×1", "6141")
    add("cone", 3, 3, 44, 1, 1, BK, 13, "Конус 1×1", "4589")


STEP_TITLES = {
    1:  "Стопы (2 шт)",
    2:  "Голени (2 шт)",
    3:  "Колени и бёдра (2 шт)",
    4:  "Платформа",
    5:  "Первый венец стен",
    6:  "Второй венец и окна",
    7:  "Третий венец и окна",
    8:  "Перемычка над дверью",
    9:  "Верхний венец",
    10: "Свес крыши",
    11: "Нижний пояс скатов",
    12: "Крыша и труба",
    13: "Верх скатов и шпиль",
}

STEP_NOTES = {
    1:  "Соберите две одинаковые стопы — левую и правую.",
    2:  "Голени одинаковые: по три бруска 2×2 на каждую стопу.",
    3:  "Пластины «колена» смещены вперёд на 1 стену — так нога выглядит согнутой. Обе ноги одинаковы.",
    5:  "Проём двери — 2 стены в ширину, 3 венца в высоту.",
    11: "Обратите внимание: у левого ската на место ската встанет труба (шаг 12).",
    13: "Шпиль просто ставится сверху — детали удерживаются весом.",
}

# ----------------------------------------------------------------------------
# Изометрический рендер
# ----------------------------------------------------------------------------
C30 = math.cos(math.radians(30))


class Iso:
    def __init__(self, S):
        self.S = S

    def p(self, x, y, z):
        """Мировые координаты -> экранные (z — в пластинах)."""
        sx = (x - y) * C30 * self.S
        sy = (x + y) * 0.5 * self.S - z * 0.4 * self.S
        return (sx, sy)


def shade(c, f):
    if len(c) == 4:
        r, g, b, a = c
        return (min(255, int(r * f)), min(255, int(g * f)),
                min(255, int(b * f)), a)
    return (min(255, int(c[0] * f)), min(255, int(c[1] * f)),
            min(255, int(c[2] * f)))


def grayed(c):
    if len(c) == 4:
        r, g, b, a = c
        return (int(r * 0.22 + 190), int(g * 0.22 + 190),
                int(b * 0.22 + 190), a)
    return (int(c[0] * 0.22 + 190), int(c[1] * 0.22 + 190),
            int(c[2] * 0.22 + 190))


def poly_f(d, pts, fill, outline):
    d.polygon(pts, fill=fill, outline=outline)


def draw_studs(d, iso, p, z_top, color_top):
    """Пипсы на верхней грани (для brick/plate/glass)."""
    w, dd = p["w"], p["d"]
    f = 1.16
    stud_c = shade(color_top, f)
    side_c = shade(color_top, 0.78)
    rx = 0.30 * iso.S * 1.414 * C30
    ry = 0.30 * iso.S * 1.414 * 0.5
    hgt = 0.17 * iso.S
    for i in range(w):
        for j in range(dd):
            cx, cy = iso.p(p["x"] + i + 0.5, p["y"] + j + 0.5, z_top)
            d.ellipse([cx - rx, cy - ry + hgt, cx + rx, cy + ry + hgt],
                      fill=side_c)
            d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=stud_c)


def draw_box(d, iso, x, y, z, w, dd, h, color, studs=True):
    x1, y1, z1 = x + w, y + dd, z + h
    top = shade(color, 1.14)
    left = shade(color, 0.92)    # грань y+ (слева на экране)
    right = shade(color, 0.72)   # грань x+ (справа)
    out = shade(color, 0.42)
    P = iso.p
    poly_f(d, [P(x, y, z1), P(x1, y, z1), P(x1, y1, z1), P(x, y1, z1)], top, out)
    poly_f(d, [P(x1, y, z), P(x1, y1, z), P(x1, y1, z1), P(x1, y, z1)], right, out)
    poly_f(d, [P(x, y1, z), P(x1, y1, z), P(x1, y1, z1), P(x, y1, z1)], left, out)
    if studs:
        draw_studs(d, iso, dict(x=x, y=y, w=w, d=dd), z1, top)


def slope_heights(x, y, w, dd, z, h, rot):
    """Высоты углов footprint (низ, верх) в зависимости от направления спуска."""
    # углы: (x,y)=nw_local, (x+w,y), (x,y+dd), (x+w,y+dd) — в мировых осях:
    # N=−y, S=+y, W=−x, E=+x
    hi, lo = z + h, z
    if rot == "S":   # высокая грань на y, спуск в +y
        return {"N": hi, "S": lo, "W": hi, "E": hi}, \
               {"N": hi, "S": lo, "W": lo, "E": lo}
    if rot == "N":
        return {"N": lo, "S": hi, "W": lo, "E": lo}, \
               {"N": lo, "S": hi, "W": hi, "E": hi}
    if rot == "E":   # спуск в +x: высокая на x
        return {"N": lo, "S": lo, "W": hi, "E": lo}, \
               {"N": hi, "S": hi, "W": hi, "E": lo}
    # rot == "W": спуск в −x
    return {"N": hi, "S": hi, "W": lo, "E": hi}, \
           {"N": lo, "S": lo, "W": lo, "E": hi}


def draw_slope(d, iso, x, y, z, w, dd, h, color, rot):
    """Клиновидный скат: сплошная наклонная верхняя грань + видимые боковины."""
    top = shade(color, 1.14)
    left = shade(color, 0.92)
    right = shade(color, 0.72)
    out = shade(color, 0.42)
    P = iso.p
    # высоты в 4 углах: A=(x,y) B=(x+w,y) C=(x,y+dd) D=(x+w,y+dd)
    if rot == "S":      # спуск к +y: A,B высокие; C,D низкие
        hA = hB = z + h
        hC = hD = z
    elif rot == "N":
        hA = hB = z
        hC = hD = z + h
    elif rot == "E":    # спуск к +x: A,C высокие
        hA = hC = z + h
        hB = hD = z
    else:               # W
        hA = hC = z
        hB = hD = z + h
    A = P(x, y, hA)
    B = P(x + w, y, hB)
    C = P(x, y + dd, hC)
    D = P(x + w, y + dd, hD)
    poly_f(d, [A, B, D, C], top, out)  # наклонная верхняя грань
    # боковые грани (только видимые, высотой от z до высоты угла)
    # правая грань x+w: B,D + низ
    poly_f(d, [P(x + w, y, z), P(x + w, y + dd, z), D, B], right, out)
    # левая грань y+dd: C,D + низ
    poly_f(d, [P(x, y + dd, z), P(x + w, y + dd, z), D, C], left, out)
    # задняя грань у высокой кромки — если высота > 0 по всей кромке, рисуем
    if rot == "S":
        poly_f(d, [P(x, y, z), P(x + w, y, z), B, A], shade(color, 0.60), out)
    elif rot == "N":
        poly_f(d, [P(x, y + dd, z), P(x + w, y + dd, z), D, C],
               shade(color, 0.60), out)
    elif rot == "E":
        poly_f(d, [P(x + w, y, z), P(x + w, y + dd, z), D, B],
               shade(color, 0.60), out)
    else:
        poly_f(d, [P(x, y, z), P(x, y + dd, z), C, A], shade(color, 0.60), out)


def draw_corner_slope(d, iso, x, y, z, w, dd, h, color, high):
    """Угловой скат: шатровая четверть пирамиды, высокий угол — high."""
    top = shade(color, 1.14)
    left = shade(color, 0.92)
    right = shade(color, 0.72)
    out = shade(color, 0.42)
    P = iso.p
    # углы: NE=(x+w,y), NW=(x,y), SE=(x+w,y+dd), SW=(x,y+dd)
    corners = {
        "NE": (x + w, y), "NW": (x, y),
        "SE": (x + w, y + dd), "SW": (x, y + dd),
    }
    hx, hy = corners[high]
    opp = {"NE": "SW", "SW": "NE", "NW": "SE", "SE": "NW"}[high]
    ox, oy = corners[opp]
    rest = [corners[k] for k in ("NE", "NW", "SE", "SW") if k not in (high, opp)]
    HA = P(hx, hy, z + h)
    OA = P(ox, oy, z)
    R = [P(rx, ry, z) for rx, ry in rest]
    # две треугольные наклонные грани
    poly_f(d, [HA, OA, R[0]], top, out)
    poly_f(d, [HA, OA, R[1]], top, out)
    # видимые боковые грани: рисуем те, что на переднем плане (y+dd и x+w)
    for (rx, ry) in rest:
        if ry == y + dd or rx == x + w:
            base = [P(x if rx == x else x + w, ry, z)]  # не используется
    # правая грань x+w
    seg = [(x + w, y), (x + w, y + dd)]
    hs = []
    for (sx, sy) in seg:
        if (sx, sy) == (hx, hy):
            hs.append(z + h)
        else:
            hs.append(z)
    poly_f(d, [P(x + w, y, z), P(x + w, y + dd, z),
               P(x + w, y + dd, hs[1]), P(x + w, y, hs[0])], right, out)
    # левая грань y+dd
    seg = [(x, y + dd), (x + w, y + dd)]
    hs = []
    for (sx, sy) in seg:
        if (sx, sy) == (hx, hy):
            hs.append(z + h)
        else:
            hs.append(z)
    poly_f(d, [P(x, y + dd, z), P(x + w, y + dd, z),
               P(x + w, y + dd, hs[1]), P(x, y + dd, hs[0])], left, out)


def draw_cheese(d, iso, x, y, z, color, rot):
    draw_slope(d, iso, x, y, z, 1, 1, 2, color, rot)


def draw_cylinder(d, iso, x, y, z, w, dd, h, color, top_ellipse=True):
    """Круглая деталь (брусок/пластина/конус упрощённо)."""
    top = shade(color, 1.16)
    left = shade(color, 0.92)
    out = shade(color, 0.42)
    cx, cy = iso.p(x + w / 2.0, y + dd / 2.0, z + h)
    bx, by = iso.p(x + w / 2.0, y + dd / 2.0, z)
    r = 0.5 * min(w, dd)
    rx = r * 1.414 * C30 * iso.S
    ry = r * 1.414 * 0.5 * iso.S
    # корпус
    d.polygon([(cx - rx, cy), (bx - rx, by), (bx - rx, by + ry * 1.05),
               (cx - rx, cy + ry * 1.05)], fill=left, outline=out)
    d.polygon([(cx + rx, cy), (bx + rx, by), (bx + rx, by + ry * 1.05),
               (cx + rx, cy + ry * 1.05)], fill=shade(color, 0.78), outline=out)
    d.rectangle([cx - rx, cy, bx + rx, by + ry], fill=left, outline=None)
    # низ и верх
    d.ellipse([bx - rx, by - ry, bx + rx, by + ry], fill=shade(color, 0.78),
              outline=out)
    if top_ellipse:
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=top, outline=out)
        # пипс сверху
        draw_studs(d, iso, dict(x=x, y=y, w=1, d=1), z + h, top)


def draw_cone(d, iso, x, y, z, color):
    top = shade(color, 1.16)
    out = shade(color, 0.42)
    cx, cy = iso.p(x + 0.5, y + 0.5, z + 3)
    bx, by = iso.p(x + 0.5, y + 0.5, z)
    rx = 0.5 * 1.414 * C30 * iso.S
    ry = 0.5 * 1.414 * 0.5 * iso.S
    d.polygon([(bx - rx, by), (bx + rx, by), (cx, cy)], fill=shade(color, 0.92),
              outline=out)
    d.ellipse([bx - rx, by - ry, bx + rx, by + ry], fill=shade(color, 0.72),
              outline=out)
    d.ellipse([cx - rx * 0.22, cy - ry * 0.22, cx + rx * 0.22, cy + ry * 0.22],
              fill=top, outline=out)


def draw_part(d, iso, p, ghost=False):
    c = grayed(RGB[p["color"]]) if ghost else RGB[p["color"]]
    k = p["kind"]
    if k in ("brick", "plate", "tile", "glass"):
        h = 3 if k == "brick" or k == "glass" else 1
        draw_box(d, iso, p["x"], p["y"], p["z"], p["w"], p["d"], h, c,
                 studs=(k != "tile"))
    elif k == "slope":
        draw_slope(d, iso, p["x"], p["y"], p["z"], 2, 2, 3, c, p["rot"])
    elif k == "corner_slope":
        draw_corner_slope(d, iso, p["x"], p["y"], p["z"], 2, 2, 3, c, p["high"])
    elif k == "cheese":
        draw_cheese(d, iso, p["x"], p["y"], p["z"], c, p["rot"])
    elif k == "round_brick":
        draw_cylinder(d, iso, p["x"], p["y"], p["z"], 1, 1, 3, c)
    elif k == "round_plate":
        draw_cylinder(d, iso, p["x"], p["y"], p["z"], 1, 1, 1, c,
                      top_ellipse=True)
    elif k == "cone":
        draw_cone(d, iso, p["x"], p["y"], p["z"], c)


def sort_key(p):
    h = {"brick": 3, "glass": 3, "plate": 1, "tile": 1, "slope": 3,
         "corner_slope": 3, "cheese": 2, "round_brick": 3, "round_plate": 1,
         "cone": 3}[p["kind"]]
    return (p["z"], p["x"] + p["y"], p["x"])


def model_bounds(parts):
    xs, ys, zs = [], [], []
    for p in parts:
        xs += [p["x"], p["x"] + p["w"]]
        ys += [p["y"], p["y"] + p["d"]]
        zs += [p["z"], p["z"] + {"brick": 3, "glass": 3, "plate": 1, "tile": 1,
                                 "slope": 3, "corner_slope": 3, "cheese": 2,
                                 "round_brick": 3, "round_plate": 1,
                                 "cone": 3}[p["kind"]]]
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)


def render_model(parts, w_px, h_px, S=None, up_to_step=None, only_step=None,
                 bg=None, shadow=False, pad=60):
    """Отрисовать модель. Возвращает RGBA-изображение.

    up_to_step: рисовать детали шагов <= N (старые — серым, новые — цветом).
    only_step=None при up_to_step=None: всё цветом.
    """
    img = Image.new("RGBA", (w_px, h_px), bg or (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    if only_step is not None:
        vis = [p for p in parts if p["step"] == only_step]
        ghost = [p for p in parts if p["step"] < only_step]
    elif up_to_step is not None:
        vis = [p for p in parts if p["step"] == up_to_step]
        ghost = [p for p in parts if p["step"] < up_to_step]
    else:
        vis, ghost = list(parts), []

    allp = ghost + vis
    if not allp:
        return img

    if S is None:
        x0, x1, y0, y1, z0, z1 = model_bounds(allp)
        ext_x = (x1 + y1) * C30
        ext_y = (x1 + y1) * 0.5 + (z1 - z0) * 0.4
        S = min((w_px - 2 * pad) / max(ext_x, 0.1),
                (h_px - 2 * pad) / max(ext_y, 0.1))

    iso = Iso(S)
    # центрирование
    x0, x1, y0, y1, z0, z1 = model_bounds(allp)
    corners = []
    for xx in (x0, x1):
        for yy in (y0, y1):
            for zz in (z0, z1):
                corners.append(iso.p(xx, yy, zz))
    minx = min(c[0] for c in corners)
    maxx = max(c[0] for c in corners)
    miny = min(c[1] for c in corners)
    maxy = max(c[1] for c in corners)
    ox = (w_px - (minx + maxx)) / 2.0
    oy = (h_px - (miny + maxy)) / 2.0

    class ShiftIso(Iso):
        def p(self, x, y, z):
            sx, sy = Iso.p(self, x, y, z)
            return (sx + ox, sy + oy)

    iso = ShiftIso(S)

    if shadow:
        # мягкая тень под моделью
        g = Image.new("RGBA", (w_px, h_px), (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        cx0, cy0 = iso.p(x0, y0, 0)
        cx1, cy1 = iso.p(x1, y0, 0)
        cx2, cy2 = iso.p(x1, y1, 0)
        cx3, cy3 = iso.p(x0, y1, 0)
        gd.polygon([cx0, cx1, cx2, cx3], fill=(30, 24, 18, 70))
        g = g.filter(ImageFilter.GaussianBlur(18))
        img.alpha_composite(g)
        d = ImageDraw.Draw(img)

    order = sorted(ghost, key=sort_key) + sorted(vis, key=sort_key)
    for p in order:
        draw_part(d, iso, p, ghost=(p in ghost and only_step is not None) or
                  (up_to_step is not None and p["step"] < up_to_step))
    return img


def render_icon(kind, color, rot=None, high=None, w=2, d=2, size=130):
    """Иконка одной детали для спецификации."""
    spec = {
        "brick": dict(kind="brick", x=0, y=0, z=0, w=w, d=d, color=color),
        "plate": dict(kind="plate", x=0, y=0, z=0, w=w, d=d, color=color),
        "tile": dict(kind="tile", x=0, y=0, z=0, w=w, d=d, color=color),
        "glass": dict(kind="glass", x=0, y=0, z=0, w=w, d=d, color=color),
        "slope": dict(kind="slope", x=0, y=0, z=0, w=2, d=2, color=color,
                      rot=rot or "S"),
        "corner_slope": dict(kind="corner_slope", x=0, y=0, z=0, w=2, d=2,
                             color=color, high=high or "SE"),
        "cheese": dict(kind="cheese", x=0, y=0, z=0, w=1, d=1, color=color,
                       rot=rot or "S"),
        "round_brick": dict(kind="round_brick", x=0, y=0, z=0, w=1, d=1,
                            color=color),
        "round_plate": dict(kind="round_plate", x=0, y=0, z=0, w=1, d=1,
                            color=color),
        "cone": dict(kind="cone", x=0, y=0, z=0, w=1, d=1, color=color),
    }[kind]
    spec.update(step=0, name="", pn="")
    return render_model([spec], size, size, S=size / 3.4, pad=8)


# ----------------------------------------------------------------------------
# Страницы схемы
# ----------------------------------------------------------------------------
PAGE_W, PAGE_H = 1754, 1240
PAPER = (250, 246, 238)
INK = (48, 36, 26)
ACCENT = (150, 62, 22)
ACCENT2 = (184, 122, 48)


def page_base(title):
    img = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, PAGE_W, 108], fill=ACCENT)
    d.rectangle([0, 108, PAGE_W, 116], fill=ACCENT2)
    f_t = font(46, bold=True)
    d.text((46, 30), title, font=f_t, fill=(255, 244, 228))
    return img, d


def parts_for_step(step):
    """Группировка по типу+номеру+цвету (разные повороты объединяются)."""
    groups = {}
    for p in PARTS:
        if p["step"] != step:
            continue
        key = (p["kind"], p["pn"], p["color"], p["name"], p["w"], p["d"])
        if key not in groups:
            groups[key] = [0, p["rot"], p["high"]]
        groups[key][0] += 1
    return groups


def draw_parts_panel(img, step, x0=24, y0=150, w=388):
    d = ImageDraw.Draw(img)
    f_h = font(32, bold=True)
    f_n = font(22)
    f_q = font(24, bold=True)
    d.text((x0, y0), "Детали шага:", font=f_h, fill=INK)
    y = y0 + 52
    groups = parts_for_step(step)
    rows = sorted(groups.items(), key=lambda kv: -kv[1][0])
    for (kind, pn, color, name, pw, pd), (qty, rot, high) in rows:
        icon = render_icon(kind, color, rot=rot, high=high, w=pw, d=pd,
                           size=118)
        img.paste(icon, (x0, y), icon)
        txt = name if len(name) < 22 else name[:20] + "…"
        d.text((x0 + 130, y + 18), txt, font=f_n, fill=INK)
        d.text((x0 + 130, y + 52), f"№ {pn}", font=f_n, fill=(120, 95, 70))
        d.text((x0 + 130, y + 84), f"× {qty}", font=f_q, fill=ACCENT)
        y += 138
    return y


def step_page(step):
    title = f"Избушка на курьих ножках — шаг {step}"
    img, d = page_base(title)
    # крупный номер шага (справа, по правому краю)
    f_num = font(112, bold=True)
    f_sub = font(27, bold=True)
    d.text((PAGE_W - 40, 148), f"{step}", font=f_num, fill=(222, 200, 168),
           anchor="ra")
    sub = STEP_TITLES.get(step, "")
    d.text((PAGE_W - 40, 282), sub, font=f_sub, fill=ACCENT, anchor="ra")

    y_end = draw_parts_panel(img, step)

    # область рендера
    rx0, ry0, rx1, ry1 = 440, 150, PAGE_W - 40, PAGE_H - 120
    model_img = render_model(PARTS, rx1 - rx0, ry1 - ry0,
                             up_to_step=step, bg=(0, 0, 0, 0), pad=46)
    img.paste(model_img, (rx0, ry0), model_img)

    note = STEP_NOTES.get(step)
    if note:
        f_note = font(24)
        d.rectangle([440, PAGE_H - 108, PAGE_W - 40, PAGE_H - 34],
                    fill=(238, 226, 205))
        d.text((460, PAGE_H - 96), "▲ " + note, font=f_note, fill=INK)

    f_pg = font(22)
    d.text((PAGE_W - 130, PAGE_H - 66), f"{step} / 13", font=f_pg,
           fill=(120, 95, 70))
    return img


def cover_page():
    img, d = page_base("СХЕМА СБОРКИ LEGO® — Избушка на курьих ножках")
    f_big = font(64, bold=True)
    f_mid = font(32)
    d.text((470, 200), "Избушка на курьих ножках", font=f_big, fill=INK)
    d.text((470, 282), "Модель из системных деталей LEGO® (без Technic)",
           font=f_mid, fill=(120, 95, 70))

    model_img = render_model(PARTS, 900, 760, bg=(0, 0, 0, 0), shadow=True,
                             pad=40)
    img.paste(model_img, (420, 340), model_img)

    # статистика
    f_k = font(28, bold=True)
    f_v = font(28)
    stats = [
        ("Высота модели:", "≈ 15 см (47 пластин)"),
        ("Количество деталей:", f"{len(PARTS)} шт."),
        ("Шагов сборки:", "13"),
        ("Только системные детали:", "без элементов Technic"),
    ]
    y = 380
    for k, v in stats:
        d.text((60, y), k, font=f_k, fill=ACCENT)
        d.text((60, y + 38), v, font=f_v, fill=INK)
        y += 110
    f_pg = font(22)
    d.text((PAGE_W - 130, PAGE_H - 66), "1", font=f_pg, fill=(120, 95, 70))
    return img


def inventory_page():
    img, d = page_base("Спецификация деталей")
    f_h = font(30, bold=True)
    f_n = font(24)
    f_q = font(28, bold=True)

    groups = {}
    for p in PARTS:
        key = (p["kind"], p["pn"], p["color"], p["name"], p["w"], p["d"])
        if key not in groups:
            groups[key] = [0, p["rot"], p["high"]]
        groups[key][0] += 1
    rows = sorted(groups.items(), key=lambda kv: (kv[0][3], kv[0][1]))

    col_w = (PAGE_W - 80) // 3
    per_col = (len(rows) + 2) // 3
    for idx, ((kind, pn, color, name, pw, pd), (qty, rot, high)) in \
            enumerate(rows):
        col = idx // per_col
        row = idx % per_col
        x = 40 + col * col_w
        y = 160 + row * 168
        icon = render_icon(kind, color, rot=rot, high=high, w=pw, d=pd,
                           size=126)
        img.paste(icon, (x, y), icon)
        d.text((x + 140, y + 18), name, font=f_n, fill=INK)
        d.text((x + 140, y + 52), f"№ {pn}", font=f_n, fill=(120, 95, 70))
        d.text((x + 140, y + 88), f"× {qty}", font=f_q, fill=ACCENT)

    total = len(PARTS)
    d.text((40, PAGE_H - 92), f"Всего деталей: {total}", font=f_h, fill=INK)
    f_pg = font(22)
    d.text((PAGE_W - 130, PAGE_H - 66), "2", font=f_pg, fill=(120, 95, 70))
    return img


def rotate_part(p, turns):
    """Повернуть деталь на 90°*turns против часовой вокруг центра модели."""
    x0, x1, y0, y1, _, _ = model_bounds(PARTS)
    W, D = x1 - x0, y1 - y0
    q = dict(p)
    for _ in range(turns % 4):
        nx = y0 + (D - (q["y"] + q["d"] - y0))
        ny = x0 + (q["x"] - x0)
        q["x"], q["y"] = nx, ny
        q["w"], q["d"] = q["d"], q["w"]
        if q.get("rot"):
            q["rot"] = {"N": "W", "W": "S", "S": "E", "E": "N"}[q["rot"]]
        if q.get("high"):
            q["high"] = {"NE": "NW", "NW": "SW", "SW": "SE", "SE": "NE"}[q["high"]]
    return q


def final_page():
    img, d = page_base("Готовая модель")
    f_h = font(36, bold=True)
    f_n = font(26)
    views = [
        (PARTS, "общий вид"),
        ([rotate_part(p, 1) for p in PARTS], "вид сбоку"),
    ]
    positions = [(40, 170), (PAGE_W // 2 + 10, 170)]
    for (parts, label), (px, py) in zip(views, positions):
        v = render_model(parts, PAGE_W // 2 - 60, 800, bg=(0, 0, 0, 0),
                         shadow=True, pad=36)
        img.paste(v, (px, py), v)
        d.text((px + 24, py + 800), label, font=f_n, fill=(120, 95, 70))

    d.text((40, PAGE_H - 130),
           "Высота готовой модели: ≈ 15 см. Деталей: %d. Шпиль ставится сверху."
           % len(PARTS), font=f_h, fill=INK)
    f_pg = font(22)
    d.text((PAGE_W - 130, PAGE_H - 66), "—", font=f_pg, fill=(120, 95, 70))
    return img


# ----------------------------------------------------------------------------
# Финальный «постер»
# ----------------------------------------------------------------------------
def hero_image():
    W, H = 2200, 1700
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    # вертикальный градиент «небо»
    top = (196, 222, 236)
    bot = (238, 230, 212)
    for yy in range(H):
        t = yy / (H - 1)
        c = tuple(int(top[i] * (1 - t) + bot[i] * t) for i in range(3))
        d.line([(0, yy), (W, yy)], fill=c)
    # лесной силуэт
    for i, (tx, tw, th) in enumerate([(80, 220, 340), (300, 150, 250),
                                      (1680, 260, 380), (1950, 180, 270),
                                      (520, 120, 200), (1500, 130, 220)]):
        base = H - 120
        g = (108, 132, 112)
        d.polygon([(tx, base), (tx + tw, base), (tx + tw // 2, base - th)],
                  fill=g)
    d.rectangle([0, H - 130, W, H], fill=(186, 172, 142))

    model = render_model(PARTS, 1560, 1320, bg=(0, 0, 0, 0), shadow=True,
                         pad=60)
    img.paste(model, ((W - 1560) // 2, 180), model)

    f_t = font(72, bold=True)
    f_s = font(34)
    d.text((W / 2, 70), "Избушка на курьих ножках", font=f_t, fill=(58, 42, 28),
           anchor="mm")
    d.text((W / 2, H - 66),
           "Модель LEGO® из системных деталей · высота ≈ 15 см · %d деталей"
           % len(PARTS), font=f_s, fill=(82, 62, 42), anchor="mm")
    return img


# ----------------------------------------------------------------------------
def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(PAGES_DIR, exist_ok=True)
    build_model()
    # Повернуть модель на 180°, чтобы фасад (дверь, когти) смотрел на зрителя
    PARTS[:] = [rotate_part(p, 2) for p in PARTS]
    print(f"Деталей в модели: {len(PARTS)}")

    pages = [cover_page(), inventory_page()]
    for s in range(1, 14):
        pages.append(step_page(s))
    pages.append(final_page())

    for i, pg in enumerate(pages, 1):
        pg.save(os.path.join(PAGES_DIR, f"page_{i:02d}.png"))

    pdf_path = os.path.join(OUT_DIR, "izbushka_instructions.pdf")
    pages[0].save(pdf_path, save_all=True, append_images=pages[1:],
                  resolution=150)
    print("PDF:", pdf_path)

    hero = hero_image()
    hero_path = os.path.join(OUT_DIR, "izbushka_final.png")
    hero.save(hero_path, quality=95)
    print("PNG:", hero_path)


if __name__ == "__main__":
    main()
