import pygame, math, random
from constants import *

_nebula_cache = {}
_vignette_cache = {}

def make_nebula_surface(sw, sh):
    key = (sw, sh)
    if key in _nebula_cache:
        return _nebula_cache[key]
    surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
    defs = [
        (0.15, 0.30, 210, (80,   0, 130), 22),
        (0.78, 0.58, 250, ( 0,  45, 130), 18),
        (0.45, 0.82, 175, (90,  25,   0), 15),
        (0.85, 0.14, 220, ( 0,  70, 100), 17),
        (0.30, 0.65, 155, (70,   0, 110), 20),
        (0.62, 0.35, 185, (20,  55,  20), 12),
        (0.50, 0.18, 135, (50,   0,  80), 14),
        (0.08, 0.80, 165, ( 0,  30,  90), 16),
        (0.93, 0.70, 140, (40,   0,  60), 18),
        (0.35, 0.10, 190, ( 0,  20,  70), 13),
    ]
    for xf, yf, r, col, base_a in defs:
        cx = int(sw * xf); cy = int(sh * yf)
        for dr in range(r, 4, -10):
            ratio = dr / r
            alpha = int(base_a * (1.0 - math.sqrt(ratio)))
            if alpha < 1:
                continue
            pygame.draw.circle(surf, (*col, alpha), (cx, cy), dr)
    _nebula_cache[key] = surf
    return surf


def make_vignette_surface(sw, sh, strength=170):
    key = (sw, sh, strength)
    if key in _vignette_cache:
        return _vignette_cache[key]
    surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
    edge = min(sw, sh) // 3
    for i in range(edge):
        t     = 1.0 - i / edge
        alpha = int(strength * t ** 2.4)
        if alpha < 1:
            continue
        pygame.draw.line(surf, (0, 0, 0, alpha), (0,      i),      (sw, i))
        pygame.draw.line(surf, (0, 0, 0, alpha), (0,      sh-1-i), (sw, sh-1-i))
        pygame.draw.line(surf, (0, 0, 0, alpha), (i,      0),      (i,  sh))
        pygame.draw.line(surf, (0, 0, 0, alpha), (sw-1-i, 0),      (sw-1-i, sh))
    _vignette_cache[key] = surf
    return surf

def draw_stars(surf, stars):
    for st in stars:
        c = int(st[2] * 40 + 40)
        pygame.draw.rect(surf, (c, c, c), (int(st[0]), int(st[1]), st[3], st[3]))

def draw_bar(surf, x, y, w, h, value, max_value, color, bg_color=GRAY_DARK,
             border=True, glow=False, preview_val=None):
    br = min(h // 2, 5)
    pygame.draw.rect(surf, bg_color, (x, y, w, h), border_radius=br)
    fill = min(w, int(w * max(0, value) / max(1, max_value)))
    if fill > 0:
        pygame.draw.rect(surf, color, (x, y, fill, h), border_radius=br)
        if glow and h >= 5:
            bright = tuple(min(255, c + 70) for c in color)
            pygame.draw.rect(surf, bright, (x, y, fill, max(1, h // 3)), border_radius=br)
        shine = tuple(min(255, c + 40) for c in color)
        pygame.draw.rect(surf, shine, (x, y, fill, 1))
    if preview_val is not None:
        p_fill = min(w, int(w * max(0, preview_val) / max(1, max_value)))
        if p_fill > fill:
            pygame.draw.rect(surf, GOLD, (x + fill, y, p_fill - fill, h))
            if fill > 0:
                pygame.draw.line(surf, WHITE, (x + fill, y), (x + fill, y + h - 1), 1)
    if border:
        pygame.draw.rect(surf, GRAY_MID, (x, y, w, h), 1, border_radius=br)

def draw_panel(surf, rect, alpha=220, border_color=ORANGE_DARK, border_width=2, radius=10):
    panel = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(panel, (*PANEL_BG, alpha), (0, 0, rect.w, rect.h), border_radius=radius)
    surf.blit(panel, rect.topleft)
    pygame.draw.rect(surf, border_color, rect, border_width, border_radius=radius)

def draw_glow_text(surf, text, font, color, glow_color, x, y, center=True, glow_radius=3):
    for radius in range(glow_radius, 0, -1):
        alpha_factor = 0.4 + 0.6 * (1 - radius / glow_radius)
        gc = tuple(int(c * alpha_factor) for c in glow_color)
        for ox in range(-radius, radius + 1):
            for oy in range(-radius, radius + 1):
                if ox == 0 and oy == 0:
                    continue
                if abs(ox) == radius or abs(oy) == radius:
                    gs = font.render(text, True, gc)
                    r  = gs.get_rect()
                    if center: r.center = (x + ox, y + oy)
                    else:      r.topleft = (x + ox, y + oy)
                    surf.blit(gs, r)
    for ox, oy in [(-1,0),(1,0),(0,-1),(0,1)]:
        gs = font.render(text, True, glow_color)
        r  = gs.get_rect()
        if center: r.center = (x + ox, y + oy)
        else:      r.topleft = (x + ox, y + oy)
        surf.blit(gs, r)
    s = font.render(text, True, color)
    r = s.get_rect()
    if center: r.center = (x, y)
    else:      r.topleft = (x, y)
    surf.blit(s, r)

def draw_button(surf, rect, text, font, hover=False, active=False):
    r          = 9
    border_col = ORANGE_GLOW if (hover or active) else ORANGE_DARK
    bg_col     = (52, 44, 64) if hover else ((52, 30, 6) if active else (20, 20, 30))

    shad = pygame.Rect(rect.x + 2, rect.y + 3, rect.w, rect.h)
    pygame.draw.rect(surf, (6, 6, 10), shad, border_radius=r)

    pygame.draw.rect(surf, bg_col, rect, border_radius=r)

    if hover or active:
        hl_s = pygame.Surface((rect.w - 6, 3), pygame.SRCALPHA)
        hl_s.fill((*border_col, 80))
        surf.blit(hl_s, (rect.x + 3, rect.y + 3))

    pygame.draw.rect(surf, border_col, rect, 2, border_radius=r)

    text_col = WHITE if (hover or active) else GRAY_LIGHT
    ts = font.render(text, True, text_col)
    surf.blit(ts, ts.get_rect(center=rect.center))

def draw_pixel_ship(surf, x, y, size, color, accent, angle=0):
    w, h = size
    ship_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cx = w // 2

    for row in range(h):
        t = row / h
        width = max(2, int(cx * (1 - abs(t - 0.38) * 2.0)))
        pygame.draw.rect(ship_surf, color, (cx - width, row, width * 2, 1))

    cw = max(2, cx // 2)
    for row in range(h // 5):
        pygame.draw.rect(ship_surf, accent,
                         (cx - cw + row, row * 2, cw * 2 - row * 2, 2))

    for i in range(3):
        ex = cx - 4 + i * 4
        pygame.draw.rect(ship_surf, ORANGE_GLOW, (ex, h - 4, 3, 4))
        pygame.draw.rect(ship_surf, WHITE,        (ex + 1, h - 3, 1, 2))

    wy = h // 2
    wh = h // 3
    pygame.draw.polygon(ship_surf, color,  [(0, wy + wh), (cx - 2, wy), (cx - 2, wy + 4)])
    pygame.draw.polygon(ship_surf, color,  [(w, wy + wh), (cx + 2, wy), (cx + 2, wy + 4)])
    pygame.draw.polygon(ship_surf, accent, [(2, wy + wh - 2), (cx - 2, wy + 2), (cx - 2, wy + 5)])
    pygame.draw.polygon(ship_surf, accent, [(w - 2, wy + wh - 2), (cx + 2, wy + 2), (cx + 2, wy + 5)])

    rotated = pygame.transform.rotate(ship_surf, -angle)
    rect    = rotated.get_rect(center=(x, y))
    surf.blit(rotated, rect)

def _glow_layer(s, cx, cy, r, color, alpha=60):
    for d in range(3, 0, -1):
        gl = pygame.Surface(((r+d)*2, (r+d)*2), pygame.SRCALPHA)
        gl.fill((*color, alpha // d))
        s.blit(gl, (cx - r - d, cy - r - d))

def draw_pixel_enemy(surf, x, y, size, color, hp_ratio=1.0, boss=False,
                     enemy_type=0, face_angle=0.0):
    r   = size
    dim = r * 2 + 8
    off = 4
    s   = pygame.Surface((dim, dim), pygame.SRCALPHA)
    cx  = cy = r + off

    hp_col = color
    if hp_ratio < 0.4:
        hp_col = (min(255, color[0]+60), max(0, color[1]-40), max(0, color[2]-40))

    if boss:
        _draw_boss(s, cx, cy, r, color, hp_ratio)
    elif enemy_type == 0:
        _draw_drone(s, cx, cy, r, hp_col)
    elif enemy_type == 1:
        _draw_swarmer(s, cx, cy, r, hp_col)
    elif enemy_type == 2:
        _draw_armored(s, cx, cy, r, hp_col)
    elif enemy_type == 3:
        _draw_shooter(s, cx, cy, r, hp_col)
    elif enemy_type == 4:
        _draw_elite(s, cx, cy, r, hp_col)
    elif enemy_type == 5:
        _draw_phantom(s, cx, cy, r, hp_col)
    elif enemy_type == 6:
        _draw_healer(s, cx, cy, r, hp_col)
    elif enemy_type == 7:
        _draw_splitter(s, cx, cy, r, hp_col)
    elif enemy_type == 8:
        _draw_kamikaze(s, cx, cy, r, hp_col)
    else:
        _draw_drone(s, cx, cy, r, hp_col)

    rotated = pygame.transform.rotate(s, -face_angle)
    rect    = rotated.get_rect(center=(x, y))
    surf.blit(rotated, rect)

    if hp_ratio < 1.0:
        bw = r * 2
        bx = x - r
        by = y - r - off - 6
        pygame.draw.rect(surf, GRAY_DARK, (bx, by, bw, 4))
        hp_c = GREEN if hp_ratio > 0.5 else (YELLOW if hp_ratio > 0.25 else RED)
        pygame.draw.rect(surf, hp_c,    (bx, by, int(bw * hp_ratio), 4))
        pygame.draw.rect(surf, GRAY_MID,(bx, by, bw, 4), 1)


def _draw_drone(s, cx, cy, r, color):
    _glow_layer(s, cx, cy, r, color, 50)
    pts = [(cx, cy - r + 1), (cx + r - 3, cy + r - 3), (cx, cy + r//3), (cx - r + 3, cy + r - 3)]
    pygame.draw.polygon(s, color, pts)
    pygame.draw.polygon(s, DARK_BG, [(cx, cy - r//2), (cx + 4, cy + 2), (cx - 4, cy + 2)])
    pygame.draw.polygon(s, WHITE,  [(cx, cy - r + 1), (cx + r - 3, cy + r - 3)], 1)
    pygame.draw.rect(s, ORANGE_GLOW, (cx - 3, cy + r - 5, 6, 5))
    pygame.draw.rect(s, WHITE,       (cx - 1, cy + r - 4, 2, 3))


def _draw_swarmer(s, cx, cy, r, color):
    _glow_layer(s, cx, cy, r, color, 40)
    pts = [(cx, cy - r + 2), (cx + r - 1, cy + r - 1), (cx - r + 1, cy + r - 1)]
    pygame.draw.polygon(s, color, pts)
    pygame.draw.polygon(s, WHITE, pts, 1)
    ic = (min(255,color[0]+80), min(255,color[1]+80), min(255,color[2]+80))
    pygame.draw.polygon(s, ic, [(cx, cy - r//2), (cx + r//3, cy + r//2), (cx - r//3, cy + r//2)])


def _draw_armored(s, cx, cy, r, color):
    _glow_layer(s, cx, cy, r, color, 35)
    pts = [(cx + int(r * 0.92 * math.cos(math.radians(45 * i - 22.5))),
            cy + int(r * 0.92 * math.sin(math.radians(45 * i - 22.5)))) for i in range(8)]
    pygame.draw.polygon(s, GRAY_DARK, pts)
    pygame.draw.polygon(s, color,     pts, 3)
    for i in range(0, 8, 2):
        p1 = pts[i]; p2 = pts[(i+1)%8]
        pygame.draw.line(s, color, p1, p2, 2)
    pygame.draw.circle(s, color,    (cx, cy), r // 3)
    pygame.draw.circle(s, WHITE,    (cx, cy), r // 6)
    pygame.draw.circle(s, DARK_BG,  (cx, cy), r // 8)


def _draw_shooter(s, cx, cy, r, color):
    _glow_layer(s, cx, cy, r, color, 45)
    hw = r - 3
    pygame.draw.rect(s, GRAY_DARK, (cx - hw, cy - hw//2, hw*2, hw + hw//2))
    pygame.draw.rect(s, color,     (cx - hw, cy - hw//2, hw*2, hw + hw//2), 2)
    pygame.draw.rect(s, color,    (cx - 3, cy - r,   6, r - hw//2 + 2))
    pygame.draw.rect(s, DARK_BG,  (cx - 2, cy - r+1, 4, r - hw//2))
    pygame.draw.rect(s, RED,      (cx - 1, cy - r,   2, 4))
    for vx in [cx - hw + 3, cx + hw - 6]:
        pygame.draw.rect(s, color, (vx, cy, 3, 8))


def _draw_elite(s, cx, cy, r, color):
    _glow_layer(s, cx, cy, r, color, 55)
    for i in range(6):
        a1 = math.radians(i * 60)
        a2 = math.radians(i * 60 + 30)
        p1 = (cx + int(r * 0.95 * math.cos(a1)), cy + int(r * 0.95 * math.sin(a1)))
        p2 = (cx + int(r * 0.45 * math.cos(a2)), cy + int(r * 0.45 * math.sin(a2)))
        p3_a = math.radians((i+1) * 60)
        p3   = (cx + int(r * 0.95 * math.cos(p3_a)), cy + int(r * 0.95 * math.sin(p3_a)))
        pygame.draw.polygon(s, color, [p1, p2, p3])
    inner = [(cx + int(r * 0.42 * math.cos(math.radians(60*i))),
              cy + int(r * 0.42 * math.sin(math.radians(60*i)))) for i in range(6)]
    pygame.draw.polygon(s, DARK_BG, inner)
    pygame.draw.polygon(s, color,   inner, 1)
    pygame.draw.circle(s, color, (cx, cy), r // 4)
    pygame.draw.circle(s, WHITE, (cx, cy), r // 7)


def _draw_phantom(s, cx, cy, r, color):
    _glow_layer(s, cx, cy, r, color, 65)
    pts  = [(cx, cy - r + 2), (cx + r - 2, cy), (cx, cy + r - 2), (cx - r + 2, cy)]
    body = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
    bc   = (*color, 160)
    pygame.draw.polygon(body, bc,    [(r, 2), (r*2-2, r), (r, r*2-2), (2, r)])
    pygame.draw.polygon(body, WHITE, [(r, 2), (r*2-2, r), (r, r*2-2), (2, r)], 1)
    s.blit(body, (cx - r, cy - r))
    ic = (min(255,color[0]+100), min(255,color[1]+60), min(255,color[2]+100))
    inner = [(cx, cy - r//2), (cx + r//2, cy), (cx, cy + r//2), (cx - r//2, cy)]
    pygame.draw.polygon(s, ic, inner)
    pygame.draw.rect(s, WHITE, (cx-1, cy-1, 3, 3))


def _draw_healer(s, cx, cy, r, color):
    _glow_layer(s, cx, cy, r, color, 70)
    pygame.draw.rect(s, color,    (cx-3, cy-r+2, 6, r*2-4))
    pygame.draw.rect(s, color,    (cx-r+2, cy-3, r*2-4, 6))
    pygame.draw.rect(s, WHITE,    (cx-1, cy-r+3, 2, r*2-6))
    pygame.draw.rect(s, WHITE,    (cx-r+3, cy-1, r*2-6, 2))
    pygame.draw.circle(s, color, (cx, cy), r//3+1)
    pygame.draw.circle(s, WHITE, (cx, cy), max(1, r//5))
    pygame.draw.circle(s, (*color, 80), (cx, cy), r-1, 1)


def _draw_splitter(s, cx, cy, r, color):
    _glow_layer(s, cx, cy, r, color, 45)
    pts = [(cx + int(r * 0.9 * math.cos(math.radians(60*i))),
            cy + int(r * 0.9 * math.sin(math.radians(60*i)))) for i in range(6)]
    pygame.draw.polygon(s, color, pts)
    pygame.draw.polygon(s, DARK_BG, pts, 2)
    for i in range(6):
        a  = math.radians(i * 60 + 30)
        x2 = cx + int(r * 0.75 * math.cos(a))
        y2 = cy + int(r * 0.75 * math.sin(a))
        pygame.draw.line(s, DARK_BG, (cx, cy), (x2, y2), 2)
    pygame.draw.circle(s, DARK_BG, (cx, cy), r//3)
    pygame.draw.circle(s, color,   (cx, cy), r//4)
    pygame.draw.rect(s, WHITE, (cx-1, cy-1, 3, 3))


def _draw_kamikaze(s, cx, cy, r, color):
    _glow_layer(s, cx, cy, r, color, 75)
    pts = [(cx, cy-r+1), (cx+r-4, cy+r-1), (cx, cy+r//4), (cx-r+4, cy+r-1)]
    pygame.draw.polygon(s, color, pts)
    pygame.draw.polygon(s, WHITE, [(cx, cy-r+1), (cx+r-4, cy+r-1)], 1)
    pygame.draw.rect(s, (255,80,0), (cx-2, cy+r//3, 4, r//2))
    pygame.draw.rect(s, WHITE,      (cx-1, cy+r//3, 2, r//4))
    pygame.draw.rect(s, RED,  (cx-2, cy-r+1, 4, 5))
    pygame.draw.rect(s, WHITE,(cx-1, cy-r+1, 2, 3))


def _draw_boss(s, cx, cy, r, color, hp_ratio):
    _glow_layer(s, cx, cy, r, color, 80)
    for i in range(6):
        a = math.radians(i * 60)
        bx = cx + int(r * 0.88 * math.cos(a))
        by = cy + int(r * 0.88 * math.sin(a))
        pygame.draw.rect(s, color, (bx - 4, by - 4, 8, 8))
        pygame.draw.rect(s, WHITE, (bx - 2, by - 2, 4, 4))
    pts = [(cx + int(r * 0.82 * math.cos(math.radians(60*i - 30))),
            cy + int(r * 0.82 * math.sin(math.radians(60*i - 30)))) for i in range(6)]
    pygame.draw.polygon(s, color,    pts, 3)
    mid = [(cx + int(r * 0.55 * math.cos(math.radians(60*i))),
            cy + int(r * 0.55 * math.sin(math.radians(60*i)))) for i in range(6)]
    pygame.draw.polygon(s, DARK_BG, mid)
    pygame.draw.polygon(s, RED,     mid, 2)
    core_col = RED if hp_ratio < 0.35 else (ORANGE if hp_ratio < 0.65 else color)
    pygame.draw.circle(s, core_col, (cx, cy), r // 3 + 2)
    pygame.draw.circle(s, WHITE,    (cx, cy), r // 6)
    pygame.draw.circle(s, DARK_BG,  (cx, cy), r // 9)

def _px(surf, x, y, col, size=1):
    pygame.draw.rect(surf, col, (x, y, size, size))

def draw_weapon_icon(surf, cx, cy, size, weapon_key, color):
    s  = pygame.Surface((size, size), pygame.SRCALPHA)
    hs = size // 2
    c  = hs
    hi  = (180, 180, 200)
    sh  = (30, 30, 40)

    if weapon_key == "blaster":
        body_pts = [(c-5,c+4),(c+5,c+4),(c+5,c+8),(c-5,c+8)]
        pygame.draw.polygon(s, color, body_pts)
        pygame.draw.rect(s, color, (c-2, c-8, 4, 14))
        pygame.draw.rect(s, hi,    (c-1, c-8, 2,  4))
        pygame.draw.rect(s, color, (c+3, c+4, 4, 8))
        pygame.draw.rect(s, sh,    (c+3, c+4, 4, 8), 1)
        pygame.draw.rect(s, ORANGE_GLOW, (c-1, c-10, 2, 3))
        pygame.draw.rect(s, WHITE,       (c,   c-10, 1, 2))

    elif weapon_key == "laser":
        pygame.draw.rect(s, color, (c-1, c-12, 3, 20))
        pygame.draw.rect(s, color, (c-4, c+2,  9,  5))
        pygame.draw.rect(s, hi,    (c-1, c-12, 1, 12))
        pygame.draw.rect(s, CYAN,  (c-3, c-4,  6,  4))
        pygame.draw.rect(s, WHITE, (c-1, c-3,  2,  2))
        pygame.draw.rect(s, CYAN,  (c,   c-14, 1,  4))
        for i in range(3):
            pygame.draw.rect(s, (*CYAN[:2], 80-i*20), (c-3+i, c-13+i, 1, 1))

    elif weapon_key == "missile":
        pts = [(c, c-12),(c+4, c+2),(c, c+0),(c-4, c+2)]
        pygame.draw.polygon(s, color, pts)
        pygame.draw.rect(s, RED,   (c-1, c-12, 3,  4))
        pygame.draw.rect(s, hi,    (c-1, c-10, 1,  8))
        pygame.draw.polygon(s, color, [(c-4,c+2),(c-8,c+8),(c-1,c+4)])
        pygame.draw.polygon(s, color, [(c+4,c+2),(c+8,c+8),(c+1,c+4)])
        pygame.draw.rect(s, ORANGE, (c-2, c+4, 4, 4))
        pygame.draw.rect(s, WHITE,  (c-1, c+5, 2, 2))

    elif weapon_key == "shotgun":
        for bx in [c-5, c+2]:
            pygame.draw.rect(s, color, (bx, c-10, 3, 18))
            pygame.draw.rect(s, hi,    (bx, c-10, 1, 10))
        pygame.draw.rect(s, color, (c-6, c+2, 12, 6))
        pygame.draw.rect(s, sh,    (c-6, c+2, 12, 6), 1)
        pygame.draw.rect(s, color, (c-3, c+6, 6, 6))
        for i in range(2):
            bx = [c-5, c+2][i] + 1
            pygame.draw.rect(s, YELLOW, (bx, c-12, 1, 3))

    elif weapon_key == "plasma":
        pygame.draw.circle(s, color,  (c, c+2), 9)
        pygame.draw.circle(s, DARK_BG,(c, c+2), 6)
        pygame.draw.circle(s, color,  (c, c+2), 3)
        pygame.draw.rect(s, color,  (c-2, c-12, 5, 12))
        pygame.draw.rect(s, hi,     (c-1, c-12, 2,  8))
        pygame.draw.circle(s, PURPLE, (c, c-12), 4)
        pygame.draw.circle(s, WHITE,  (c-1, c-13), 2)
        for ri in range(1, 4):
            pygame.draw.circle(s, (*PURPLE, max(0, 120 - ri*30)), (c, c+2), 9+ri*2, 1)

    elif weapon_key == "railgun":
        pygame.draw.rect(s, color,  (c-1, c-14, 3, 24))
        pygame.draw.rect(s, hi,     (c,   c-14, 1, 14))
        pygame.draw.rect(s, color,  (c-5, c+4,  11, 6))
        pygame.draw.rect(s, sh,     (c-5, c+4,  11, 6), 1)
        for ry in [c-10, c-4, c+1]:
            pygame.draw.rect(s, CYAN, (c-3, ry, 7, 2))
            pygame.draw.rect(s, WHITE,(c-1, ry, 3, 1))
        pygame.draw.circle(s, CYAN,  (c, c-15), 3)
        pygame.draw.circle(s, WHITE, (c, c-15), 1)

    elif weapon_key == "chaingun":
        for bx_off, by_off in [(-3, 0), (3, 0), (0, -2)]:
            pygame.draw.rect(s, color, (c + bx_off - 1, c-12 + by_off, 3, 16))
            pygame.draw.rect(s, hi,    (c + bx_off,     c-12 + by_off, 1,  8))
        pygame.draw.circle(s, color,  (c, c+2), 7)
        pygame.draw.circle(s, DARK_BG,(c, c+2), 5)
        for i in range(3):
            mx_ = c + [-3, 3, 0][i]
            pygame.draw.rect(s, YELLOW, (mx_-1, c-14, 2, 4))

    surf.blit(s, (cx - hs, cy - hs))


def draw_skill_icon(surf, cx, cy, size, skill_key, color):
    s  = pygame.Surface((size, size), pygame.SRCALPHA)
    hs = size // 2
    c  = hs

    if skill_key == "speed":
        pts = [(c+3, c-12),(c-2, c-1),(c+2, c-1),(c-3, c+12),(c+1, c+1),(c-1, c+1)]
        pygame.draw.polygon(s, color, pts)
        pygame.draw.polygon(s, WHITE, [(c+3,c-12),(c+2,c-5),(c+4,c-5)], 1)

    elif skill_key == "damage":
        pygame.draw.line(s, color, (c-8, c-8), (c+8, c+8), 3)
        pygame.draw.line(s, color, (c+8, c-8), (c-8, c+8), 3)
        pygame.draw.rect(s, ORANGE, (c-2, c-1, 4, 3))
        pygame.draw.rect(s, WHITE,  (c-1, c-1, 2, 1))
        pygame.draw.polygon(s, hi := WHITE, [(c-8,c-8),(c-10,c-6),(c-6,c-10)])
        pygame.draw.polygon(s, WHITE,       [(c+8,c+8),(c+10,c+6),(c+6,c+10)])

    elif skill_key == "shield":
        pts = [(c, c-11),(c+9, c-5),(c+9, c+5),(c, c+11),(c-9, c+5),(c-9, c-5)]
        pygame.draw.polygon(s, color, pts)
        pygame.draw.polygon(s, WHITE, pts, 2)
        inner = [(c, c-7),(c+5, c-3),(c+5, c+3),(c, c+7),(c-5, c+3),(c-5, c-3)]
        pygame.draw.polygon(s, DARK_BG, inner)
        pygame.draw.rect(s, color, (c-1, c-5, 2, 10))
        pygame.draw.rect(s, color, (c-5, c-1, 10,  2))

    elif skill_key == "multishot":
        for i, (ax, aa) in enumerate([(-6, -20), (0, 0), (6, 20)]):
            rad  = math.radians(aa)
            ex   = c + ax + int(math.sin(rad) * 10)
            ey   = c - 12 + int(-math.cos(rad) * 2)
            pygame.draw.line(s, color, (c + ax, c + 6), (ex, ey), 2)
            pygame.draw.polygon(s, color, [
                (ex, ey),
                (ex + int(math.cos(rad) * 4 + math.sin(rad) * 2),
                 ey + int(math.sin(rad) * 4 - math.cos(rad) * 2)),
                (ex + int(math.cos(rad) * 4 - math.sin(rad) * 2),
                 ey + int(math.sin(rad) * 4 + math.cos(rad) * 2)),
            ])

    elif skill_key == "regen":
        pygame.draw.rect(s, color, (c-2, c-10, 4, 20))
        pygame.draw.rect(s, color, (c-10, c-2, 20,  4))
        pygame.draw.rect(s, WHITE, (c-1,  c-8,  2, 16))
        pygame.draw.rect(s, WHITE, (c-8,  c-1, 16,  2))
        for dx, dy in [(0,-11),(0,11),(-11,0),(11,0)]:
            pygame.draw.rect(s, WHITE, (c+dx-1, c+dy-1, 2, 2))

    elif skill_key == "explosion":
        for i in range(8):
            angle = math.radians(i * 45)
            x1 = c + int(math.cos(angle) * 4)
            y1 = c + int(math.sin(angle) * 4)
            x2 = c + int(math.cos(angle) * 12)
            y2 = c + int(math.sin(angle) * 12)
            pygame.draw.line(s, color, (x1, y1), (x2, y2), 2)
        pygame.draw.circle(s, color, (c, c), 5)
        pygame.draw.circle(s, WHITE, (c, c), 3)
        pygame.draw.circle(s, ORANGE_GLOW, (c, c), 2)

    elif skill_key == "pierce":
        pygame.draw.circle(s, color, (c, c), 9, 2)
        pygame.draw.line(s, color, (c, c-13), (c, c+13), 3)
        pygame.draw.polygon(s, color, [(c-4, c-8),(c+4, c-8),(c, c-14)])
        pygame.draw.polygon(s, color, [(c-4, c+8),(c+4, c+8),(c, c+14)])
        pygame.draw.rect(s, WHITE, (c-1, c-12, 2, 24))

    elif skill_key == "magnet":
        pygame.draw.arc(s, color, (c-9, c-9, 18, 18), math.radians(0), math.radians(180), 5)
        pygame.draw.rect(s, BLUE,  (c-9, c, 5, 10))
        pygame.draw.rect(s, WHITE, (c-9, c, 5,  4))
        pygame.draw.rect(s, RED,   (c+4, c, 5, 10))
        pygame.draw.rect(s, WHITE, (c+4, c, 5,  4))
        pygame.draw.arc(s, (*color, 120), (c-5, c-4, 10, 8), math.radians(0), math.radians(180), 1)

    elif skill_key == "autoaim":
        r1, r2 = 10, 6
        pygame.draw.circle(s, color, (c, c), r1, 2)
        pygame.draw.circle(s, color, (c, c), r2, 1)
        for dx2, dy2 in [(0,-1),(0,1),(-1,0),(1,0)]:
            x1 = c + dx2 * (r1 + 3)
            y1 = c + dy2 * (r1 + 3)
            x2 = c + dx2 * (r2 + 2)
            y2 = c + dy2 * (r2 + 2)
            pygame.draw.line(s, color, (x1, y1), (x2, y2), 2)
        pygame.draw.rect(s, WHITE, (c-1, c-1, 3, 3))
        for sx2, sy2 in [(-1,-1),(1,-1),(-1,1),(1,1)]:
            bx2 = c + sx2 * (r1 - 1)
            by2 = c + sy2 * (r1 - 1)
            pygame.draw.line(s, WHITE, (bx2, by2), (bx2 + sx2*4, by2), 1)
            pygame.draw.line(s, WHITE, (bx2, by2), (bx2, by2 + sy2*4), 1)

    elif skill_key == "chain":
        nodes = [(c, c-12), (c+5, c-4), (c-4, c+2), (c+4, c+8), (c, c+13)]
        for i in range(len(nodes)-1):
            pygame.draw.line(s, color, nodes[i], nodes[i+1], 3)
            pygame.draw.line(s, WHITE, nodes[i], nodes[i+1], 1)
        for nx, ny in [nodes[0], nodes[-1]]:
            pygame.draw.circle(s, color, (nx, ny), 4)
            pygame.draw.circle(s, WHITE, (nx, ny), 2)
        pygame.draw.arc(s, (*color, 180), (c-9, c-10, 18, 20),
                        math.radians(10), math.radians(170), 1)

    elif skill_key == "lifesteal":
        pygame.draw.circle(s, color, (c-4, c-5), 5)
        pygame.draw.circle(s, color, (c+4, c-5), 5)
        pts = [(c-9, c-3), (c+9, c-3), (c, c+10)]
        pygame.draw.polygon(s, color, pts)
        pygame.draw.circle(s, WHITE, (c-3, c-7), 2)
        pygame.draw.polygon(s, WHITE, [(c, c-2),(c-3, c+3),(c+3, c+3)])

    elif skill_key == "homing":
        pygame.draw.circle(s, color,  (c+7, c-6), 4)
        pygame.draw.circle(s, DARK_BG,(c+7, c-6), 2)
        pygame.draw.arc(s, color, (c-12, c-12, 20, 20),
                        math.radians(0), math.radians(135), 3)
        pygame.draw.polygon(s, color, [(c-12, c-3), (c-8, c-3), (c-10, c+3)])

    elif skill_key == "crit":
        pygame.draw.line(s, color, (c-10, c), (c+10, c), 3)
        pygame.draw.line(s, color, (c, c-10), (c, c+10), 3)
        pygame.draw.line(s, color, (c-7, c-7), (c+7, c+7), 2)
        pygame.draw.line(s, color, (c+7, c-7), (c-7, c+7), 2)
        pygame.draw.circle(s, color,  (c, c), 5)
        pygame.draw.circle(s, WHITE,  (c, c), 3)
        pygame.draw.circle(s, ORANGE_GLOW if color == ORANGE else WHITE, (c, c), 1)

    elif skill_key == "slow":
        for i in range(6):
            angle = math.radians(i * 60)
            x2 = c + int(math.cos(angle) * 11)
            y2 = c + int(math.sin(angle) * 11)
            pygame.draw.line(s, color, (c, c), (x2, y2), 2)
            for sign in [-1, 1]:
                br_a = angle + sign * math.radians(60)
                bx = c + int(math.cos(angle) * 7) + int(math.cos(br_a) * 4)
                by = c + int(math.sin(angle) * 7) + int(math.sin(br_a) * 4)
                pygame.draw.line(s, color,
                                 (c + int(math.cos(angle) * 7),
                                  c + int(math.sin(angle) * 7)),
                                 (bx, by), 1)
        pygame.draw.circle(s, WHITE, (c, c), 3)

    elif skill_key == "vampiric":
        pygame.draw.circle(s, color, (c-4, c-4), 5)
        pygame.draw.circle(s, color, (c+4, c-4), 5)
        pygame.draw.polygon(s, color, [(c-9, c-1),(c+9, c-1),(c, c+11)])
        pygame.draw.circle(s, WHITE, (c-3, c-6), 2)
        pygame.draw.polygon(s, (255, 80, 80), [(c-2, c+8),(c+2, c+8),(c, c+13)])

    elif skill_key == "ricochet":
        pygame.draw.line(s, GRAY_MID, (c-11, c-11), (c-11, c+11), 2)
        pygame.draw.line(s, GRAY_MID, (c+11, c+5),  (c+11, c+11), 2)
        pygame.draw.line(s, color, (c-8, c+8),  (c-2, c-6),  3)
        pygame.draw.line(s, color, (c-2, c-6),  (c+8, c+2),  3)
        pygame.draw.circle(s, WHITE, (c+8, c+2), 3)
        pygame.draw.circle(s, color, (c-8, c+8), 2)

    elif skill_key == "aura":
        for ri in [11, 7, 4]:
            alpha_c = max(40, 200 - ri * 12)
            pygame.draw.circle(s, color, (c, c), ri, 2)
        pygame.draw.circle(s, WHITE, (c, c), 3)
        for ang in [45, 135, 225, 315]:
            rad = math.radians(ang)
            ex = c + int(math.cos(rad) * 9)
            ey = c + int(math.sin(rad) * 9)
            pygame.draw.circle(s, color, (ex, ey), 2)

    elif skill_key == "dash":
        for off, alpha_f in [(0, 1.0), (-5, 0.5), (-10, 0.25)]:
            col_d = tuple(int(v * alpha_f) for v in color)
            pygame.draw.line(s, col_d, (c + off - 4, c), (c + off + 6, c), 2)
            pygame.draw.polygon(s, col_d,
                [(c + off + 6, c), (c + off + 2, c - 4), (c + off + 2, c + 4)])
        for ly in [-5, 0, 5]:
            pygame.draw.line(s, GRAY_MID, (c - 13, c + ly), (c - 6, c + ly), 1)

    elif skill_key == "overcharge":
        pygame.draw.rect(s, color,   (c-7, c-10, 14, 20), 2, border_radius=2)
        pygame.draw.rect(s, color,   (c-3, c-13, 6,   4))
        pts = [(c+2, c-7), (c-2, c-1), (c+2, c-1), (c-2, c+7)]
        pygame.draw.lines(s, WHITE, False, pts, 2)

    elif skill_key == "deathblow":
        pygame.draw.circle(s, color, (c, c-2), 8)
        pygame.draw.circle(s, DARK_BG, (c-3, c-3), 2)
        pygame.draw.circle(s, DARK_BG, (c+3, c-3), 2)
        pygame.draw.line(s, DARK_BG, (c-4, c+3), (c+4, c+3), 2)
        for ang in range(0, 360, 45):
            rad = math.radians(ang)
            x1 = c + int(math.cos(rad) * 9)
            y1 = c - 2 + int(math.sin(rad) * 9)
            x2 = c + int(math.cos(rad) * 13)
            y2 = c - 2 + int(math.sin(rad) * 13)
            pygame.draw.line(s, color, (x1, y1), (x2, y2), 2)

    elif skill_key == "coin_bonus":
        pygame.draw.circle(s, color, (c, c), 10)
        pygame.draw.circle(s, (200, 150, 0), (c, c), 8)
        pygame.draw.circle(s, WHITE, (c, c), 10, 2)
        pygame.draw.line(s, DARK_BG, (c, c-6), (c, c+6), 2)
        pygame.draw.line(s, DARK_BG, (c-4, c-3), (c+4, c-3), 2)
        pygame.draw.line(s, DARK_BG, (c-4, c+3), (c+4, c+3), 2)

    elif skill_key == "xp_bonus":
        pygame.draw.polygon(s, color, [(c, c-11), (c-8, c+2), (c+8, c+2)])
        pygame.draw.rect(s, color, (c-3, c+2, 6, 8))
        pygame.draw.polygon(s, WHITE, [(c, c-8), (c-4, c), (c+4, c)])
        pygame.draw.rect(s, WHITE, (c-1, c-2, 2, 2))

    elif skill_key == "shield_regen":
        pygame.draw.circle(s, color, (c, c), 10, 2)
        pygame.draw.arc(s, WHITE, (c-7, c-7, 14, 14), 0.3, 4.5, 2)
        pygame.draw.polygon(s, WHITE, [(c+6, c-4), (c+9, c), (c+3, c)])
        pygame.draw.rect(s, color, (c-1, c-1, 3, 3))

    elif skill_key == "thorns":
        for i in range(8):
            angle = math.radians(i * 45)
            x1 = c + int(math.cos(angle) * 5)
            y1 = c + int(math.sin(angle) * 5)
            x2 = c + int(math.cos(angle) * 12)
            y2 = c + int(math.sin(angle) * 12)
            pygame.draw.line(s, color, (x1, y1), (x2, y2), 2)
        pygame.draw.circle(s, color, (c, c), 5)
        pygame.draw.circle(s, DARK_BG, (c, c), 3)

    elif skill_key == "dodge":
        pygame.draw.circle(s, (*color[:3],), (c-4, c), 6, 2)
        pygame.draw.circle(s, WHITE, (c+4, c), 6)
        pygame.draw.circle(s, color, (c+4, c), 6, 2)
        pygame.draw.line(s, color, (c-8, c+6), (c-2, c+6), 1)

    elif skill_key == "freeze":
        for i in range(6):
            angle = math.radians(i * 60)
            x2 = c + int(math.cos(angle) * 11)
            y2 = c + int(math.sin(angle) * 11)
            pygame.draw.line(s, color, (c, c), (x2, y2), 2)
            for sign in [-1, 1]:
                br_a = angle + sign * math.radians(45)
                bx = c + int(math.cos(angle) * 7) + int(math.cos(br_a) * 4)
                by = c + int(math.sin(angle) * 7) + int(math.sin(br_a) * 4)
                pygame.draw.line(s, WHITE,
                    (c + int(math.cos(angle) * 7), c + int(math.sin(angle) * 7)),
                    (bx, by), 1)
        pygame.draw.circle(s, WHITE, (c, c), 3)

    elif skill_key == "area_magnet":
        for ri in [11, 8, 5]:
            pygame.draw.circle(s, color, (c, c), ri, 1)
        pygame.draw.circle(s, WHITE, (c, c), 2)
        for ang in [0, 90, 180, 270]:
            rad = math.radians(ang)
            ax = c + int(math.cos(rad) * 10)
            ay = c + int(math.sin(rad) * 10)
            pygame.draw.polygon(s, color, [
                (ax, ay),
                (ax + int(math.cos(rad) * 3 + math.sin(rad) * 2), ay + int(math.sin(rad) * 3 - math.cos(rad) * 2)),
                (ax + int(math.cos(rad) * 3 - math.sin(rad) * 2), ay + int(math.sin(rad) * 3 + math.cos(rad) * 2)),
            ])

    elif skill_key == "lucky":
        pygame.draw.circle(s, color, (c, c-5), 4)
        pygame.draw.circle(s, color, (c, c+5), 4)
        pygame.draw.circle(s, color, (c-5, c), 4)
        pygame.draw.circle(s, color, (c+5, c), 4)
        pygame.draw.circle(s, WHITE, (c, c), 3)
        pygame.draw.rect(s, (0, 100, 0), (c-1, c, 2, 8))

    elif skill_key == "berserker":
        pygame.draw.circle(s, color, (c, c), 10, 2)
        pygame.draw.line(s, color, (c-6, c-5), (c-2, c-3), 2)
        pygame.draw.line(s, color, (c+6, c-5), (c+2, c-3), 2)
        pygame.draw.circle(s, WHITE, (c-4, c-2), 2)
        pygame.draw.circle(s, WHITE, (c+4, c-2), 2)
        pygame.draw.arc(s, color, (c-5, c+2, 10, 6), 3.4, 6.0, 2)

    surf.blit(s, (cx - hs, cy - hs))


def draw_flag(surf, x, y, w, h, lang_code):
    r = pygame.Rect(x, y, w, h)
    t3 = h // 3

    if lang_code == "de":
        pygame.draw.rect(surf, (20,  20,  20),  (x, y,         w, t3))
        pygame.draw.rect(surf, (200, 30,  30),  (x, y + t3,    w, t3))
        pygame.draw.rect(surf, (220, 180,  20), (x, y + t3*2,  w, h - t3*2))

    elif lang_code == "en":
        pygame.draw.rect(surf, (0, 50, 160), r)
        pygame.draw.line(surf, WHITE, (x, y), (x+w, y+h), 4)
        pygame.draw.line(surf, WHITE, (x+w, y), (x, y+h), 4)
        pygame.draw.line(surf, RED, (x, y), (x+w, y+h), 2)
        pygame.draw.line(surf, RED, (x+w, y), (x, y+h), 2)
        pygame.draw.rect(surf, WHITE, (x + w//2 - 2, y,      4, h))
        pygame.draw.rect(surf, WHITE, (x,     y + h//2 - 2,  w, 4))
        pygame.draw.rect(surf, RED,   (x + w//2 - 1, y,      2, h))
        pygame.draw.rect(surf, RED,   (x,     y + h//2 - 1,  w, 2))

    elif lang_code == "es":
        t5 = h // 4
        pygame.draw.rect(surf, (180, 20, 20), (x, y,         w, t5))
        pygame.draw.rect(surf, (220,180, 20), (x, y + t5,    w, h - t5*2))
        pygame.draw.rect(surf, (180, 20, 20), (x, y+h-t5,    w, t5))
        pygame.draw.rect(surf, (150, 100, 30), (x + w//2 - 3, y + h//2 - 3, 6, 6))

    elif lang_code == "fr":
        t3w = w // 3
        pygame.draw.rect(surf, (0,  50, 160), (x,         y, t3w,      h))
        pygame.draw.rect(surf, WHITE,          (x + t3w,   y, t3w,      h))
        pygame.draw.rect(surf, (180, 20, 20),  (x + t3w*2, y, w-t3w*2, h))

    else:
        pygame.draw.rect(surf, GRAY_MID, r)

    pygame.draw.rect(surf, GRAY_MID, r, 1)
