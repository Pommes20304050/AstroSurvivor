import pygame, math, random, asyncio
from constants import *
from constants import SHIP_UPG_COSTS, SHIP_UPG_BONUS, WEAPON_UPG_COSTS, WEAPON_UPG_BONUS, ACHIEVEMENTS
from draw_utils import (draw_stars as _draw_stars_fn, draw_panel, draw_glow_text,
                         draw_button, draw_pixel_ship, draw_bar,
                         draw_weapon_icon, draw_skill_icon, draw_flag)
from localization import t, LANGUAGES, load_language, current_lang
from config import save_config

def make_stars(count, sw, sh):
    return [[random.uniform(0,sw), random.uniform(0,sh),
             random.uniform(0.2,1.2), random.choice([1,1,2])] for _ in range(count)]

def scroll_stars(stars, dt, sw, sh):
    for s in stars:
        s[1] += s[2]*dt*60
        if s[1] > sh:
            s[1] = -4; s[0] = random.uniform(0, sw)

def draw_stars(surf, stars):
    _draw_stars_fn(surf, stars)

class MainMenu:
    def __init__(self, screen, fonts, cfg):
        self.screen = screen
        self.fonts  = fonts
        self.cfg    = cfg
        self.sw, self.sh = screen.get_size()
        self.scale  = min(self.sw / 1280, self.sh / 720)
        self.stars  = make_stars(120, self.sw, self.sh)
        self.anim   = 0.0

    def _buttons(self):
        return [("play",t("play")),("hangar",t("hangar")),
                ("settings",t("settings")),("quit",t("quit"))]

    def _btn_rect(self, i):
        s  = self.scale
        bw = int(260 * s); bh = int(56 * s)
        gap = int(14 * s)
        return pygame.Rect(self.sw//2-bw//2, self.sh//2 - int(60*s) + i*(bh+gap), bw, bh)

    async def run(self):
        pygame.event.clear()
        clock = pygame.time.Clock()
        while True:
            dt = clock.tick(60)/1000.0
            self.anim += dt
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: return "quit"
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    r = self._handle_click(pygame.mouse.get_pos())
                    if r: return r
            scroll_stars(self.stars, dt, self.sw, self.sh)
            self._draw()
            pygame.display.flip()
            await asyncio.sleep(0)

    def _handle_click(self, pos):
        for i, (action, _) in enumerate(self._buttons()):
            if self._btn_rect(i).collidepoint(pos): return action
        return None

    def _draw(self):
        surf = self.screen
        surf.fill(DARK_BG)
        draw_stars(surf, self.stars)

        glow = abs(math.sin(self.anim*1.2))*0.5+0.5
        gc   = (int(255*glow), int(100*glow), 0)
        draw_glow_text(surf, "ASTRO SURVIVOR", self.fonts["title"], ORANGE, gc,
                       self.sw//2, self.sh//2-200, True)
        sub = self.fonts["small"].render("v0.2  |  Space Survival Shooter", True, GRAY_MID)
        surf.blit(sub, sub.get_rect(center=(self.sw//2, self.sh//2-152)))

        best_wave = self.cfg.get("max_wave_reached", 0)
        if best_wave > 0:
            bw_txt = f"  {t('best_wave')}: {best_wave}  "
            bw_s   = self.fonts["small"].render(bw_txt, True, GOLD)
            bw_r   = bw_s.get_rect(center=(self.sw//2, self.sh//2-126))
            badge  = pygame.Surface((bw_r.w + 16, bw_r.h + 8), pygame.SRCALPHA)
            pygame.draw.rect(badge, (60, 45, 10, 180), (0, 0, bw_r.w+16, bw_r.h+8), border_radius=10)
            pygame.draw.rect(badge, GOLD, (0, 0, bw_r.w+16, bw_r.h+8), 1, border_radius=10)
            surf.blit(badge, (bw_r.x - 8, bw_r.y - 4))
            surf.blit(bw_s, bw_r)

        coins = self.cfg.get("coins", 0)
        cs = self.fonts["med"].render(f"  {coins} Coins", True, GOLD)
        surf.blit(cs, cs.get_rect(topright=(self.sw-20, 14)))
        pygame.draw.rect(surf, GOLD, (self.sw-cs.get_width()-38, 18, 14, 14))
        pygame.draw.rect(surf, DARK_BG, (self.sw-cs.get_width()-35, 21, 8, 8))

        for ix, iy, col, acc, sz in [
            (self.sw//4,     self.sh//3+int(math.sin(self.anim)*10),  ORANGE, ORANGE_GLOW, (22,30)),
            (self.sw*3//4,   self.sh//3+int(math.cos(self.anim)*12),  CYAN,   WHITE,       (20,28)),
        ]:
            draw_pixel_ship(surf, ix, iy, sz, col, acc)

        mx, my = pygame.mouse.get_pos()
        for i,(action,label) in enumerate(self._buttons()):
            r = self._btn_rect(i)
            draw_button(surf, r, label, self.fonts["med"], r.collidepoint(mx,my))

        ver = self.fonts["small"].render("© 2025 AstroSurvivor", True, GRAY_DARK)
        surf.blit(ver, (10, self.sh-22))

class HangarMenu:
    TABS = [("ship","select_ship"),("weapon","select_weapon"),("skilltree","Skill Tree"),("achievements","Erfolge")]

    def __init__(self, screen, fonts, cfg):
        self.screen = screen
        self.fonts  = fonts
        self.cfg    = cfg
        self.sw, self.sh = screen.get_size()
        self.scale  = min(self.sw / 1280, self.sh / 720)
        self.stars  = make_stars(100, self.sw, self.sh)
        self.anim   = 0.0
        self.tab    = "ship"
        self.ship_idx   = min(cfg.get("selected_ship",   0), max(0, len(SHIPS)   - 1))
        self.weapon_idx = min(cfg.get("selected_weapon", 0), max(0, len(WEAPONS) - 1))
        self.st_scroll  = 0
        self.st_hover   = None
        self.achiev_scroll = 0

    def _s(self, v):
        return int(v * self.scale)

    async def run(self):
        pygame.event.clear()
        clock = pygame.time.Clock()
        while True:
            dt = clock.tick(60)/1000.0
            self.anim += dt
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: return "quit"
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    self._save(); return "back"
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    r = self._click(pygame.mouse.get_pos())
                    if r: return r
                if ev.type == pygame.MOUSEWHEEL:
                    if self.tab == "achievements":
                        self.achiev_scroll = max(0, self.achiev_scroll - ev.y * 40)
                    else:
                        self.st_scroll = max(0, self.st_scroll - ev.y * 30)
            scroll_stars(self.stars, dt, self.sw, self.sh)
            self._draw()
            pygame.display.flip()
            await asyncio.sleep(0)

    def _save(self):
        self.cfg["selected_ship"]   = self.ship_idx
        self.cfg["selected_weapon"] = self.weapon_idx
        save_config(self.cfg)

    def _click(self, pos):
        mx, my = pos
        sw, sh = self.sw, self.sh

        tab_w = self._s(118); tab_h = self._s(38)
        tab_y = self._s(78);  tab_gap = self._s(126)
        total_tabs_w = len(self.TABS) * tab_w + (len(self.TABS) - 1) * (tab_gap - tab_w)
        tab_start_x  = sw // 2 - total_tabs_w // 2
        for i,(tab,_) in enumerate(self.TABS):
            tx = tab_start_x + i * tab_gap
            if pygame.Rect(tx, tab_y, tab_w, tab_h).collidepoint(mx,my):
                self.tab = tab
                return None

        if self.tab == "ship":
            self._click_ships(mx, my)
        elif self.tab == "weapon":
            self._click_weapons(mx, my)
        elif self.tab == "skilltree":
            self._click_skilltree(mx, my)

        btn_h = self._s(48); btn_y = sh - self._s(70)
        if pygame.Rect(self._s(30), btn_y, self._s(160), btn_h).collidepoint(mx,my):
            self._save(); return "back"
        if self.tab not in ("skilltree", "achievements") and pygame.Rect(sw-self._s(200), btn_y, self._s(170), btn_h).collidepoint(mx,my):
            self._save(); return "play"
        return None

    def _click_ships(self, mx, my):
        max_wave  = self.cfg.get("max_wave_reached", 0)
        ship_upgs = self.cfg.get("ship_upgrades", {})
        coins     = self.cfg.get("coins", 0)
        max_upg   = len(SHIP_UPG_COSTS)
        for i, ship in enumerate(SHIPS):
            r = self._ship_card_rect(i)
            if not r.collidepoint(mx, my): continue
            locked = ship["unlock_wave"] > max_wave
            if locked: continue
            upg_r   = pygame.Rect(r.x + self._s(8), r.y + r.h - self._s(30), r.w - self._s(16), self._s(22))
            upg_lvl = ship_upgs.get(ship["key"], 0)
            if upg_r.collidepoint(mx, my) and upg_lvl < max_upg:
                cost = SHIP_UPG_COSTS[upg_lvl]
                if coins >= cost:
                    self.cfg["coins"] -= cost
                    ship_upgs[ship["key"]] = upg_lvl + 1
                    self.cfg["ship_upgrades"] = ship_upgs
                    save_config(self.cfg)
            else:
                self.ship_idx = i

    def _ship_card_rect(self, i):
        cols    = 4
        cw      = self._s(250);  ch = self._s(238)
        gap     = self._s(18);   gap_row = self._s(16)
        total   = cw * cols + gap * (cols - 1)
        sx      = self.sw // 2 - total // 2
        row     = i // cols
        col     = i % cols
        n_ships = len(SHIPS)
        items_in_row = min(cols, n_ships - row * cols)
        row_offset   = (cols - items_in_row) * (cw + gap) // 2
        return pygame.Rect(sx + col * (cw + gap) + row_offset,
                           self._s(120) + row * (ch + gap_row), cw, ch)

    def _weapon_card_rect(self, i):
        cols    = 4
        cw      = self._s(250);  ch = self._s(244)
        gap     = self._s(18);   gap_row = self._s(14)
        total   = cw * cols + gap * (cols - 1)
        sx      = self.sw // 2 - total // 2
        row     = i // cols
        col     = i % cols
        n_wpns  = len(WEAPONS)
        items_in_row = min(cols, n_wpns - row * cols)
        row_offset   = (cols - items_in_row) * (cw + gap) // 2
        return pygame.Rect(sx + col * (cw + gap) + row_offset,
                           self._s(120) + row * (ch + gap_row), cw, ch)

    def _click_skilltree(self, mx, my):
        coins    = self.cfg.get("coins", 0)
        st       = self.cfg.get("skill_tree", {})
        cats     = self._st_categories()
        layout   = self._st_layout(cats)
        for node, rx, ry in layout:
            r = pygame.Rect(rx, ry - self.st_scroll, self._ST_CARD_W, self._ST_CARD_H)
            if r.collidepoint(mx, my):
                lvl     = st.get(node["key"], 0)
                max_lvl = node["max_level"]
                if lvl >= max_lvl:
                    break
                req = node.get("requires")
                if req:
                    req_key, req_min = req
                    if st.get(req_key, 0) < req_min:
                        break
                cost = node["costs"][lvl]
                if coins >= cost:
                    self.cfg["coins"] -= cost
                    st[node["key"]] = lvl + 1
                    self.cfg["skill_tree"] = st
                    save_config(self.cfg)
                break

    def _st_categories(self):
        cats = {}
        for node in SKILL_TREE:
            cats.setdefault(node["cat"], []).append(node)
        return cats

    _ST_CARD_W = 240
    _ST_COL_W  = 260
    _ST_CARD_H = 96
    _ST_NODE_H = 112

    def _st_layout(self, cats):
        layout   = []
        cat_list = list(cats.items())
        total_w  = len(cat_list) * self._ST_COL_W
        start_x  = self.sw // 2 - total_w // 2
        start_y  = self._s(152)

        for ci, (cat_name, nodes) in enumerate(cat_list):
            cx = start_x + ci * self._ST_COL_W
            for ri, node in enumerate(nodes):
                layout.append((node, cx, start_y + ri * self._ST_NODE_H))
        return layout

    def _draw(self):
        surf = self.screen
        surf.fill(DARK_BG)
        draw_stars(surf, self.stars)
        sw, sh = self.sw, self.sh
        s  = self.scale
        mx, my = pygame.mouse.get_pos()

        title = self.fonts["big"].render(t("hangar"), True, ORANGE)
        surf.blit(title, title.get_rect(center=(sw//2, self._s(42))))

        coins = self.cfg.get("coins", 0)
        cs = self.fonts["med"].render(f"{coins} Coins", True, GOLD)
        surf.blit(cs, (sw - cs.get_width() - self._s(20), self._s(14)))

        tab_w = self._s(118); tab_h = self._s(38)
        tab_y = self._s(78);  tab_gap = self._s(126)
        total_tabs_w = len(self.TABS) * tab_w + (len(self.TABS) - 1) * (tab_gap - tab_w)
        tab_start_x  = sw // 2 - total_tabs_w // 2
        for i, (tab, label_key) in enumerate(self.TABS):
            tx = tab_start_x + i * tab_gap
            r  = pygame.Rect(tx, tab_y, tab_w, tab_h)
            label = label_key if not label_key.startswith("select_") else t(label_key)
            draw_button(surf, r, label, self.fonts["small"], r.collidepoint(mx,my), self.tab==tab)

        if self.tab == "ship":
            self._draw_ships(surf, mx, my)
        elif self.tab == "weapon":
            self._draw_weapons(surf, mx, my)
        elif self.tab == "skilltree":
            self._draw_skilltree(surf, mx, my)
        elif self.tab == "achievements":
            self._draw_achievements(surf, mx, my)

        btn_h = self._s(48); btn_y = sh - self._s(70)
        back_r  = pygame.Rect(self._s(30), btn_y, self._s(160), btn_h)
        start_r = pygame.Rect(sw - self._s(200), btn_y, self._s(170), btn_h)
        draw_button(surf, back_r,  t("back"),       self.fonts["med"], back_r.collidepoint(mx,my))
        if self.tab not in ("skilltree", "achievements"):
            draw_button(surf, start_r, t("start_game"), self.fonts["med"], start_r.collidepoint(mx,my))

    def _draw_ships(self, surf, mx, my):
        max_wave  = self.cfg.get("max_wave_reached", 0)
        ship_upgs = self.cfg.get("ship_upgrades", {})
        coins     = self.cfg.get("coins", 0)
        max_upg   = len(SHIP_UPG_COSTS)
        tooltip_data = None

        for i, ship in enumerate(SHIPS):
            r        = self._ship_card_rect(i)
            locked   = ship["unlock_wave"] > max_wave
            selected = (i == self.ship_idx) and not locked
            hover    = r.collidepoint(mx, my)
            upg_lvl  = ship_upgs.get(ship["key"], 0)

            panel = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            bg_alpha = 225 if (hover or selected) else 192
            pygame.draw.rect(panel, (*PANEL_BG, bg_alpha), (0, 0, r.w, r.h), border_radius=13)
            surf.blit(panel, r.topleft)
            border = ORANGE_GLOW if selected else (ORANGE_DARK if hover else GRAY_DARK)
            pygame.draw.rect(surf, border, r, 3 if selected else 2, border_radius=13)

            if selected:
                ab = self.fonts["ui"].render("> AKTIV", True, ORANGE_GLOW)
                surf.blit(ab, ab.get_rect(center=(r.centerx, r.y + self._s(8))))

            bob      = int(math.sin(self.anim * 2 + i) * self._s(5)) if not locked else 0
            ship_col = ship["color"] if not locked else GRAY_MID
            ship_acc = ship["accent"] if not locked else GRAY_DARK
            sp_scale = 1.6 * self.scale
            sz_big   = (int(ship["size"][0] * sp_scale), int(ship["size"][1] * sp_scale))
            draw_pixel_ship(surf, r.centerx, r.y + self._s(74) + bob, sz_big, ship_col, ship_acc)

            if locked:
                ov = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
                pygame.draw.rect(ov, (0, 0, 0, 82), (0, 0, r.w, r.h), border_radius=13)
                surf.blit(ov, r.topleft)
                lx, ly = r.centerx, r.y + self._s(118)
                lk = self._s(10)
                pygame.draw.rect(surf, GRAY_MID,  (lx-lk, ly,            lk*2,        self._s(15)))
                pygame.draw.rect(surf, DARK_BG,   (lx-self._s(6), ly+self._s(3), self._s(12), self._s(9)))
                pygame.draw.arc(surf, GRAY_LIGHT, (lx-lk, ly-self._s(11), lk*2, self._s(22)), 0, math.pi, 2)
                req_s  = self.fonts["small"].render(f"Wave {ship['unlock_wave']}", True, ORANGE)
                surf.blit(req_s, req_s.get_rect(center=(r.centerx, r.y + self._s(145))))
                lock_s = self.fonts["ui"].render("Gesperrt", True, GRAY_MID)
                surf.blit(lock_s, lock_s.get_rect(center=(r.centerx, r.y + self._s(162))))
            else:
                ns = self.fonts["small"].render(t(ship["name_key"]), True, ship["color"])
                surf.blit(ns, ns.get_rect(center=(r.centerx, r.y + self._s(22))))
                desc_s = self.fonts["ui"].render(ship["desc"], True, GRAY_MID)
                surf.blit(desc_s, desc_s.get_rect(center=(r.centerx, r.y + self._s(36))))

                total_hp  = ship["hp"]     + sum(SHIP_UPG_BONUS[j]["hp"]    for j in range(upg_lvl))
                total_spd = ship["speed"]  + sum(SHIP_UPG_BONUS[j]["speed"] for j in range(upg_lvl))
                total_shd = ship["shield"] + sum(SHIP_UPG_BONUS[j]["shield"] for j in range(upg_lvl))
                fire_sps  = min(8.0, 1.0 / ship["fire_rate"])

                upg_r     = pygame.Rect(r.x + self._s(8), r.y + r.h - self._s(30), r.w - self._s(16), self._s(22))
                btn_hover = upg_r.collidepoint(mx, my)
                nxt_bonus = SHIP_UPG_BONUS[upg_lvl] if (btn_hover and upg_lvl < max_upg) else None

                bar_h = max(5, self._s(9))
                for si, (label, val, col, maxv, bkey) in enumerate([
                    ("HP",   total_hp,  GREEN,  380,  "hp"),
                    ("SPD",  total_spd, CYAN,   10.5, "speed"),
                    ("SHD",  total_shd, BLUE,   260,  "shield"),
                    ("RATE", fire_sps,  YELLOW, 8.0,  None),
                ]):
                    ly2 = r.y + self._s(116) + si * self._s(18)
                    surf.blit(self.fonts["ui"].render(label, True, GRAY_LIGHT), (r.x + self._s(8), ly2))
                    preview = (val + nxt_bonus[bkey]) if (nxt_bonus and bkey) else None
                    draw_bar(surf, r.x + self._s(48), ly2 + self._s(3), r.w - self._s(58), bar_h,
                             val, maxv, col, preview_val=preview)

                star_y   = r.y + self._s(193)
                pip_x    = r.x + self._s(8)
                for si in range(max_upg):
                    pc = GOLD if si < upg_lvl else GRAY_DARK
                    pygame.draw.rect(surf, pc,
                                     (pip_x + si * self._s(14), star_y, self._s(10), self._s(8)),
                                     border_radius=2)
                if upg_lvl > 0:
                    lv_s = self.fonts["ui"].render(f"Lv{upg_lvl}", True, ORANGE)
                    surf.blit(lv_s, (r.x + r.w - lv_s.get_width() - self._s(8), star_y))

                if upg_lvl >= max_upg:
                    upg_col = GOLD;  upg_txt = "MAX LEVEL"
                else:
                    cost    = SHIP_UPG_COSTS[upg_lvl]
                    can     = coins >= cost
                    upg_col = GREEN if can else GRAY_MID
                    upg_txt = f"Upgrade Lv{upg_lvl+1}  {cost}c"
                bg_col = (40, 32, 50, 255) if btn_hover else (*PANEL_DARK, 255)
                btn_surf = pygame.Surface((upg_r.w, upg_r.h), pygame.SRCALPHA)
                pygame.draw.rect(btn_surf, bg_col, (0, 0, upg_r.w, upg_r.h), border_radius=7)
                surf.blit(btn_surf, upg_r.topleft)
                pygame.draw.rect(surf, upg_col, upg_r, 1, border_radius=7)
                us = self.fonts["ui"].render(upg_txt, True, upg_col)
                surf.blit(us, us.get_rect(center=upg_r.center))

                if btn_hover and upg_lvl < max_upg:
                    bonus = SHIP_UPG_BONUS[upg_lvl]
                    tooltip_data = {
                        "title": "Nächstes Upgrade",
                        "bars": [
                            (f"+{bonus['hp']} HP",           GREEN, total_hp,  total_hp  + bonus["hp"],     380),
                            (f"+{bonus['speed']:.1f} Speed", CYAN,  total_spd, total_spd + bonus["speed"],  10.5),
                            (f"+{bonus['shield']} Schild",   BLUE,  total_shd, total_shd + bonus["shield"], 260),
                        ],
                    }
                elif hover and not selected and not btn_hover:
                    curr  = SHIPS[self.ship_idx]
                    c_upg = ship_upgs.get(curr["key"], 0)
                    c_hp  = curr["hp"]     + sum(SHIP_UPG_BONUS[j]["hp"]    for j in range(c_upg))
                    c_spd = curr["speed"]  + sum(SHIP_UPG_BONUS[j]["speed"] for j in range(c_upg))
                    c_shd = curr["shield"] + sum(SHIP_UPG_BONUS[j]["shield"] for j in range(c_upg))
                    tooltip_data = {
                        "title": "vs. Aktives Schiff",
                        "compare": [
                            ("HP",  c_hp,  total_hp,  380),
                            ("SPD", c_spd, total_spd, 10.5),
                            ("SHD", c_shd, total_shd, 260),
                        ],
                    }

        if tooltip_data:
            self._draw_rich_tooltip(surf, tooltip_data, mx, my)

    def _draw_rich_tooltip(self, surf, data, mx, my):
        font   = self.fonts["ui"]
        pad    = 10;  lh = 20
        bw     = self._s(88);  bh = 8
        lbl_w  = self._s(100)

        title = data.get("title", "")
        mode  = "bars" if "bars" in data else ("compare" if "compare" in data else "text")
        items = data.get(mode, [])

        has_bars = mode in ("bars", "compare")
        if has_bars:
            tw = pad * 2 + lbl_w + bw + self._s(4)
        else:
            tw = max((font.size(t2)[0] for t2, _ in items), default=0)
            tw = max(tw, font.size(title)[0]) + pad * 2 + 8
        th = pad * 2 + lh + len(items) * (lh + 3)

        tx = mx + 16;  ty = my - th - 8
        tx = max(4, min(tx, self.sw - tw - 4))
        ty = max(4, min(ty, self.sh - th - 4))

        panel = pygame.Surface((tw, th), pygame.SRCALPHA)
        pygame.draw.rect(panel, (10, 8, 18, 238), (0, 0, tw, th), border_radius=10)
        pygame.draw.rect(panel, ORANGE_DARK,       (0, 0, tw, th), 1, border_radius=10)
        surf.blit(panel, (tx, ty))

        surf.blit(font.render(title, True, WHITE), (tx + pad, ty + pad))
        yc = ty + pad + lh + 2

        if mode == "bars":
            for label, color, before, after, maxv in items:
                surf.blit(font.render(label, True, color), (tx + pad, yc))
                bx = tx + pad + lbl_w
                pygame.draw.rect(surf, GRAY_DARK, (bx, yc + (lh - bh) // 2, bw, bh), border_radius=3)
                b_fill = int(bw * min(1.0, before / max(0.001, maxv)))
                dark   = tuple(max(0, c - 80) for c in color[:3])
                pygame.draw.rect(surf, dark, (bx, yc + (lh - bh) // 2, b_fill, bh), border_radius=3)
                a_fill = int(bw * min(1.0, after / max(0.001, maxv)))
                if a_fill > b_fill:
                    pygame.draw.rect(surf, color,
                                     (bx + b_fill, yc + (lh - bh) // 2, a_fill - b_fill, bh))
                if b_fill > 0:
                    pygame.draw.line(surf, WHITE,
                                     (bx + b_fill, yc + (lh - bh) // 2),
                                     (bx + b_fill, yc + (lh + bh) // 2), 1)
                yc += lh + 3

        elif mode == "compare":
            for label, cur, new, maxv in items:
                diff = new - cur
                dc   = GREEN if diff > 0 else (RED if diff < 0 else GRAY_MID)
                ds   = f"+{diff:.1f}" if diff > 0 else (f"{diff:.1f}" if diff < 0 else "=")
                ds   = ds.rstrip('0').rstrip('.') if '.' in ds else ds
                surf.blit(font.render(f"{label}: {ds}", True, dc), (tx + pad, yc))
                bx = tx + pad + lbl_w
                pygame.draw.rect(surf, GRAY_DARK, (bx, yc + (lh - bh) // 2, bw, bh), border_radius=3)
                n_fill = int(bw * min(1.0, new / max(0.001, maxv)))
                pygame.draw.rect(surf, dc, (bx, yc + (lh - bh) // 2, n_fill, bh), border_radius=3)
                yc += lh + 3

        else:
            for text, color in items:
                surf.blit(font.render(text, True, color), (tx + pad, yc))
                yc += lh + 3

    def _click_weapons(self, mx, my):
        unlocked   = self.cfg.get("unlocked_weapons", ["blaster"])
        wpn_upgs   = self.cfg.get("weapon_upgrades", {})
        coins      = self.cfg.get("coins", 0)
        max_upg    = len(WEAPON_UPG_COSTS)
        for i, wp in enumerate(WEAPONS):
            r = self._weapon_card_rect(i)
            if not r.collidepoint(mx, my): continue
            is_unlk = wp["key"] in unlocked
            upg_r   = pygame.Rect(r.x + self._s(8), r.y + r.h - self._s(32), r.w - self._s(16), self._s(24))
            upg_lvl = wpn_upgs.get(wp["key"], 0)
            if upg_r.collidepoint(mx, my):
                if is_unlk and upg_lvl < max_upg:
                    cost = WEAPON_UPG_COSTS[upg_lvl]
                    if coins >= cost:
                        self.cfg["coins"] -= cost
                        wpn_upgs[wp["key"]] = upg_lvl + 1
                        self.cfg["weapon_upgrades"] = wpn_upgs
                        save_config(self.cfg)
                elif not is_unlk and wp["cost"] <= coins:
                    self.cfg["coins"] -= wp["cost"]
                    unlocked.append(wp["key"])
                    self.cfg["unlocked_weapons"] = unlocked
                    self.weapon_idx = i
                    save_config(self.cfg)
            elif is_unlk:
                self.weapon_idx = i

    def _draw_weapons(self, surf, mx, my):
        unlocked  = self.cfg.get("unlocked_weapons", ["blaster"])
        wpn_upgs  = self.cfg.get("weapon_upgrades", {})
        coins     = self.cfg.get("coins", 0)
        max_upg   = len(WEAPON_UPG_COSTS)
        tooltip_data = None

        for i, wp in enumerate(WEAPONS):
            r        = self._weapon_card_rect(i)
            is_unlk  = wp["key"] in unlocked
            selected = (i == self.weapon_idx) and is_unlk
            hover    = r.collidepoint(mx, my)
            can_buy  = (not is_unlk) and (wp["cost"] <= coins)
            upg_lvl  = wpn_upgs.get(wp["key"], 0)

            panel = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            bg_alpha = 225 if (hover or selected) else 195
            pygame.draw.rect(panel, (*PANEL_BG, bg_alpha), (0, 0, r.w, r.h), border_radius=13)
            surf.blit(panel, r.topleft)
            border = ORANGE_GLOW if selected else (ORANGE if hover else (GOLD if can_buy else GRAY_DARK))
            pygame.draw.rect(surf, border, r, 3 if selected else 2, border_radius=13)

            if not is_unlk:
                ov = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
                pygame.draw.rect(ov, (0, 0, 0, 70), (0, 0, r.w, r.h), border_radius=13)
                surf.blit(ov, r.topleft)

            if selected:
                ab = self.fonts["ui"].render("> AKTIV", True, ORANGE_GLOW)
                surf.blit(ab, ab.get_rect(center=(r.centerx, r.y + self._s(10))))

            icon_sz = max(28, self._s(62))
            icon_col = wp["color"] if is_unlk else GRAY_DARK
            draw_weapon_icon(surf, r.centerx, r.y + self._s(54), icon_sz, wp["key"], icon_col)

            name_col = wp["color"] if is_unlk else GRAY_MID
            ns = self.fonts["small"].render(t(wp["name_key"]), True, name_col)
            surf.blit(ns, ns.get_rect(center=(r.centerx, r.y + self._s(96))))
            desc_s = self.fonts["ui"].render(wp["desc"], True, GRAY_MID if is_unlk else GRAY_DARK)
            surf.blit(desc_s, desc_s.get_rect(center=(r.centerx, r.y + self._s(110))))

            dmg_mult = 1 + (WEAPON_UPG_BONUS[upg_lvl - 1]["dmg_pct"]  if upg_lvl > 0 else 0)
            rate_mul = 1 - (WEAPON_UPG_BONUS[upg_lvl - 1]["rate_pct"] if upg_lvl > 0 else 0)
            eff_dmg  = wp["damage"]    * dmg_mult
            eff_rate = wp["fire_rate"] * rate_mul
            eff_rps  = min(14.0, 1.0 / eff_rate)

            upg_r     = pygame.Rect(r.x + self._s(8), r.y + r.h - self._s(32), r.w - self._s(16), self._s(24))
            btn_hover = upg_r.collidepoint(mx, my)
            if is_unlk and btn_hover and upg_lvl < max_upg:
                nxt_wb      = WEAPON_UPG_BONUS[upg_lvl]
                nxt_dmg_m   = 1 + nxt_wb["dmg_pct"]
                nxt_rate_m  = 1 - nxt_wb["rate_pct"]
                prev_dmg    = wp["damage"]    * nxt_dmg_m
                prev_rps    = min(14.0, 1.0 / (wp["fire_rate"] * nxt_rate_m))
            else:
                prev_dmg = prev_rps = None

            bar_h = max(5, self._s(9))
            for si, (lbl, val, col, maxv, pv) in enumerate([
                ("DMG",  eff_dmg,      ORANGE, 140, prev_dmg),
                ("SPD",  wp["speed"],  CYAN,   22,  None),
                ("RATE", eff_rps,      GREEN,  14,  prev_rps),
            ]):
                ly = r.y + self._s(128) + si * self._s(18)
                surf.blit(self.fonts["ui"].render(lbl, True, GRAY_LIGHT), (r.x + self._s(8), ly))
                draw_bar(surf, r.x + self._s(50), ly + self._s(3), r.w - self._s(60), bar_h,
                         val, maxv, col, preview_val=pv)

            pierce_base  = wp["pierce"]
            pierce_bonus = WEAPON_UPG_BONUS[upg_lvl - 1]["pierce"] if upg_lvl > 0 else 0
            pierce_total = pierce_base + pierce_bonus
            info_y = r.y + self._s(182)

            if pierce_total > 0:
                ps = self.fonts["ui"].render("PIERCE", True, PURPLE)
                surf.blit(ps, (r.x + self._s(8), info_y))
                for pi in range(min(pierce_total, 8)):
                    pygame.draw.circle(surf, PURPLE,
                                       (r.x + self._s(56) + pi * self._s(11), info_y + self._s(6)),
                                       self._s(4))

            star_col = GOLD if upg_lvl > 0 else GRAY_DARK
            star_txt = ""
            for si in range(max_upg):
                star_txt += "+" if si < upg_lvl else "-"
            star_y = info_y + self._s(16)
            pip_x = r.x + self._s(8)
            for si in range(max_upg):
                pc = GOLD if si < upg_lvl else GRAY_DARK
                pygame.draw.rect(surf, pc,
                                 (pip_x + si * self._s(14), star_y, self._s(10), self._s(8)),
                                 border_radius=2)
            if upg_lvl > 0:
                lv_s = self.fonts["ui"].render(f"Lv{upg_lvl}", True, ORANGE)
                surf.blit(lv_s, (r.x + r.w - lv_s.get_width() - self._s(8), star_y))

            bg_c  = (40, 32, 50, 255) if btn_hover else (*PANEL_DARK, 255)
            btn_s = pygame.Surface((upg_r.w, upg_r.h), pygame.SRCALPHA)
            pygame.draw.rect(btn_s, bg_c, (0, 0, upg_r.w, upg_r.h), border_radius=7)
            surf.blit(btn_s, upg_r.topleft)

            if not is_unlk:
                bc  = GOLD if can_buy else GRAY_MID
                btx = f"Kaufen: {wp['cost']}c" if can_buy else f"Benötigt: {wp['cost']}c"
            elif upg_lvl >= max_upg:
                bc  = GOLD;  btx = "MAX LEVEL"
            else:
                cost = WEAPON_UPG_COSTS[upg_lvl]
                bc   = GREEN if coins >= cost else GRAY_MID
                btx  = f"Upgrade Lv{upg_lvl+1}  {cost}c"
            pygame.draw.rect(surf, bc, upg_r, 1, border_radius=7)
            bs = self.fonts["ui"].render(btx, True, bc)
            surf.blit(bs, bs.get_rect(center=upg_r.center))

            if is_unlk and btn_hover and upg_lvl < max_upg:
                next_b = WEAPON_UPG_BONUS[upg_lvl]
                cur_b  = WEAPON_UPG_BONUS[upg_lvl - 1] if upg_lvl > 0 else {"dmg_pct": 0.0, "rate_pct": 0.0, "pierce": 0}
                dmg_gain   = next_b["dmg_pct"]  - cur_b["dmg_pct"]
                rate_gain  = next_b["rate_pct"] - cur_b["rate_pct"]
                pierce_gain = next_b["pierce"]  - cur_b["pierce"]
                text_items = [(f"+{int(dmg_gain*100)}% Schaden", ORANGE)]
                if rate_gain > 0:
                    text_items.append((f"-{int(rate_gain*100)}% Cooldown", GREEN))
                if pierce_gain > 0:
                    text_items.append((f"+{pierce_gain} Pierce", PURPLE))
                tooltip_data = {"title": "Nächstes Upgrade", "text": text_items}

        if tooltip_data:
            self._draw_rich_tooltip(surf, tooltip_data, mx, my)

    _ACHIEV_CAT_COLORS = {
        "combat": ORANGE, "waves": CYAN, "combo": ORANGE_GLOW, "economy": GOLD,
        "score": CYAN, "boss": RED, "leveling": GREEN, "survival": GREEN,
        "equipment": RED, "progression": PURPLE,
    }
    _ACHIEV_CAT_LABELS = {
        "combat": "KAMPF", "waves": "WELLEN", "combo": "COMBO", "economy": "COINS",
        "score": "SCORE", "boss": "BOSS", "leveling": "LEVEL", "survival": "ÜBERLEBEN",
        "equipment": "AUSRÜSTUNG", "progression": "FORTSCHRITT",
    }

    def _draw_achievement_icon(self, surf, cx, cy, size, cat, color, unlocked):
        col  = color if unlocked else GRAY_DARK
        dim  = int(size * 0.82)
        half = dim // 2

        if cat == "combat":
            pygame.draw.line(surf, col, (cx - half, cy - half), (cx + half, cy + half), 3)
            pygame.draw.line(surf, col, (cx + half, cy - half), (cx - half, cy + half), 3)
            for px2, py2 in [(cx-half,cy-half),(cx+half,cy+half),(cx+half,cy-half),(cx-half,cy+half)]:
                pygame.draw.circle(surf, col, (px2, py2), 2)
        elif cat == "waves":
            pts = []
            for s in range(21):
                t2 = s / 20
                pts.append((cx - half + int(t2 * dim),
                            cy + int(math.sin(t2 * math.pi * 2.5) * half * 0.7)))
            if len(pts) > 1: pygame.draw.lines(surf, col, False, pts, 3)
        elif cat == "combo":
            bolt = [(cx+3,cy-half),(cx-3,cy-2),(cx+4,cy-2),
                    (cx-3,cy+half),(cx+3,cy+1),(cx-4,cy+1)]
            pygame.draw.polygon(surf, col, bolt)
        elif cat == "economy":
            pygame.draw.circle(surf, col, (cx, cy), half, 3)
            pygame.draw.circle(surf, col, (cx, cy), half // 2, 2)
        elif cat == "score":
            pygame.draw.polygon(surf, col, [(cx, cy - half), (cx - half, cy + 2), (cx + half, cy + 2)])
            pygame.draw.line(surf, col, (cx - half + 2, cy + half), (cx + half - 2, cy + half), 3)
        elif cat == "boss":
            pygame.draw.circle(surf, col, (cx, cy - 2), half - 1, 2)
            pygame.draw.circle(surf, col, (cx - half//3, cy - 3), 2)
            pygame.draw.circle(surf, col, (cx + half//3, cy - 3), 2)
            pygame.draw.line(surf, col, (cx - half//3, cy + half//2), (cx + half//3, cy + half//2), 2)
        elif cat == "leveling":
            pygame.draw.polygon(surf, col, [(cx, cy - half), (cx - half, cy), (cx + half, cy)])
            pygame.draw.rect(surf, col, (cx - half//3, cy, half*2//3, half))
        elif cat == "survival":
            h4 = half // 2
            pygame.draw.circle(surf, col, (cx - h4, cy - h4 + 1), h4)
            pygame.draw.circle(surf, col, (cx + h4, cy - h4 + 1), h4)
            pygame.draw.polygon(surf, col, [(cx - half, cy - 1), (cx, cy + half), (cx + half, cy - 1)])
        elif cat == "equipment":
            pygame.draw.circle(surf, col, (cx, cy + 2), half - 2, 2)
            pygame.draw.line(surf, col, (cx, cy - half + 4), (cx + half//2, cy - half), 2)
        elif cat == "progression":
            pygame.draw.line(surf, col, (cx, cy + half), (cx, cy - half//2), 3)
            pygame.draw.line(surf, col, (cx, cy - half//2), (cx - half, cy - half), 2)
            pygame.draw.line(surf, col, (cx, cy - half//2), (cx + half, cy - half), 2)
            pygame.draw.circle(surf, col, (cx - half, cy - half), 3)
            pygame.draw.circle(surf, col, (cx + half, cy - half), 3)
        else:
            points = []
            for k in range(10):
                ang = math.radians(-90 + k * 36)
                r2  = half if k % 2 == 0 else half // 2
                points.append((cx + int(math.cos(ang) * r2), cy + int(math.sin(ang) * r2)))
            pygame.draw.polygon(surf, col, points)

    def _draw_achievements(self, surf, mx, my):
        sw, sh   = self.sw, self.sh
        unlocked = set(self.cfg.get("achievements", []))
        total    = len(ACHIEVEMENTS)
        n_done   = len(unlocked)

        cols     = 3
        cw       = self._s(360)
        ch       = self._s(52)
        gap      = self._s(8)
        grid_w   = cols * cw + (cols - 1) * gap
        start_x  = sw // 2 - grid_w // 2
        header_y = self._s(128)
        start_y  = self._s(152)
        bottom_y = sh - self._s(72)

        pct_txt = f"{n_done} / {total} Erfolge"
        ps = self.fonts["small"].render(pct_txt, True, GOLD if n_done == total else GRAY_LIGHT)
        surf.blit(ps, ps.get_rect(center=(sw // 2 - self._s(80), header_y)))
        bar_x = sw // 2 + self._s(10)
        bar_w = self._s(200)
        bar_h = self._s(10)
        pygame.draw.rect(surf, GRAY_DARK, (bar_x, header_y - bar_h // 2, bar_w, bar_h), border_radius=4)
        fill_w = int(bar_w * n_done / max(1, total))
        if fill_w > 0:
            pygame.draw.rect(surf, GOLD, (bar_x, header_y - bar_h // 2, fill_w, bar_h), border_radius=4)

        rows     = math.ceil(total / cols)
        content_h = rows * (ch + gap)
        visible_h = bottom_y - start_y
        max_scroll = max(0, content_h - visible_h)
        self.achiev_scroll = min(self.achiev_scroll, max_scroll)
        scroll = self.achiev_scroll

        clip_rect = pygame.Rect(0, start_y, sw, visible_h)
        old_clip = surf.get_clip()
        surf.set_clip(clip_rect)

        for idx, achv in enumerate(ACHIEVEMENTS):
            col_i = idx % cols
            row_i = idx // cols
            rx    = start_x + col_i * (cw + gap)
            ry    = start_y + row_i * (ch + gap) - scroll

            if ry + ch < start_y or ry > bottom_y:
                continue

            r     = pygame.Rect(rx, ry, cw, ch)
            done  = achv["key"] in unlocked
            hover = r.collidepoint(mx, my) and clip_rect.collidepoint(mx, my)
            acol  = achv["color"]

            card = pygame.Surface((cw, ch), pygame.SRCALPHA)
            bg = (*PANEL_BG, 230) if done else (10, 10, 16, 200)
            pygame.draw.rect(card, bg, (0, 0, cw, ch), border_radius=8)
            surf.blit(card, r.topleft)

            border_col = acol if done else GRAY_DARK
            if hover: border_col = WHITE if done else GRAY_MID
            pygame.draw.rect(surf, border_col, r, 2, border_radius=8)

            icon_cx = rx + self._s(22)
            icon_cy = ry + ch // 2
            icon_sz = self._s(16)
            self._draw_achievement_icon(surf, icon_cx, icon_cy, icon_sz, achv["cat"], acol, done)

            tx = rx + self._s(46)
            name_col = acol if done else GRAY_MID
            ns = self.fonts["ui"].render(achv["name"], True, name_col)
            surf.blit(ns, (tx, ry + self._s(6)))
            desc_col = GRAY_LIGHT if done else GRAY_DARK
            ds = self.fonts["ui"].render(achv["desc"], True, desc_col)
            surf.blit(ds, (tx, ry + self._s(24)))

            if done:
                cx2 = rx + cw - self._s(18)
                cy2 = ry + ch // 2
                pygame.draw.line(surf, GREEN, (cx2 - 5, cy2), (cx2 - 2, cy2 + 4), 2)
                pygame.draw.line(surf, GREEN, (cx2 - 2, cy2 + 4), (cx2 + 4, cy2 - 5), 2)

        surf.set_clip(old_clip)

        if scroll > 0:
            for i in range(3):
                pygame.draw.circle(surf, GRAY_MID, (sw // 2 - 8 + i * 8, start_y - 4), 2)
        if scroll < max_scroll:
            for i in range(3):
                pygame.draw.circle(surf, GRAY_MID, (sw // 2 - 8 + i * 8, bottom_y + 4), 2)

    def _draw_skilltree(self, surf, mx, my):
        sw, sh = self.sw, self.sh
        st    = self.cfg.get("skill_tree", {})
        coins = self.cfg.get("coins", 0)
        cats  = self._st_categories()
        layout= self._st_layout(cats)

        cat_list   = list(cats.keys())
        cat_names  = {"health":"Gesundheit","defense":"Verteidigung",
                      "offense":"Angriff","movement":"Bewegung"}
        cat_colors = {"health":GREEN,"defense":BLUE,"offense":ORANGE,"movement":CYAN}
        total_w    = len(cat_list) * self._ST_COL_W
        start_x    = sw // 2 - total_w // 2

        hdr_y = self._s(120)
        for ci, cat in enumerate(cat_list):
            cx = start_x + ci * self._ST_COL_W
            cc = cat_colors.get(cat, GRAY_LIGHT)
            hp = pygame.Surface((self._ST_CARD_W, 28), pygame.SRCALPHA)
            pygame.draw.rect(hp, (*PANEL_DARK, 180), (0, 0, self._ST_CARD_W, 28), border_radius=8)
            surf.blit(hp, (cx, hdr_y))
            pygame.draw.rect(surf, cc, (cx, hdr_y, self._ST_CARD_W, 28), 1, border_radius=8)
            hs = self.fonts["small"].render(cat_names.get(cat, cat).upper(), True, cc)
            surf.blit(hs, hs.get_rect(center=(cx + self._ST_CARD_W // 2, hdr_y + 14)))

        clip_y = self._s(150)
        clip_h = sh - clip_y - 70
        surf.set_clip(pygame.Rect(0, clip_y, sw, clip_h))

        cw = self._ST_CARD_W
        ch = self._ST_CARD_H

        for node, rx, ry in layout:
            ry_s = ry - self.st_scroll
            if ry_s + ch < clip_y or ry_s > clip_y + clip_h:
                continue

            lvl     = st.get(node["key"], 0)
            max_lvl = node["max_level"]
            req     = node.get("requires")
            locked  = bool(req and st.get(req[0], 0) < req[1])
            cost    = node["costs"][lvl] if lvl < max_lvl else 0
            maxed   = (lvl >= max_lvl)
            can_buy = (not locked) and (not maxed) and (coins >= cost)
            hover   = pygame.Rect(rx, ry_s, cw, ch).collidepoint(mx, my)

            if req:
                for on, orx, ory in layout:
                    if on["key"] == req[0]:
                        mid_y = (ory - self.st_scroll + ch // 2 + ry_s) // 2
                        pygame.draw.line(surf, GRAY_DARK,
                                         (rx + cw//2, ry_s),
                                         (orx + cw//2, ory - self.st_scroll + ch), 1)
                        break

            border = (ORANGE_GLOW if hover and can_buy else
                      GREEN       if maxed   else
                      ORANGE_DARK if can_buy else
                      GRAY_DARK   if locked  else GRAY_MID)
            card_s = pygame.Surface((cw, ch), pygame.SRCALPHA)
            pygame.draw.rect(card_s, (*PANEL_BG, 225), (0, 0, cw, ch), border_radius=10)
            surf.blit(card_s, (rx, ry_s))
            pygame.draw.rect(surf, border, (rx, ry_s, cw, ch), 2, border_radius=10)

            if locked:
                ov = pygame.Surface((cw, ch), pygame.SRCALPHA)
                pygame.draw.rect(ov, (0, 0, 0, 100), (0, 0, cw, ch), border_radius=10)
                surf.blit(ov, (rx, ry_s))

            icon_cx = rx + 26
            icon_cy = ry_s + ch // 2
            draw_skill_icon(surf, icon_cx, icon_cy, 36, node["icon"], node["color"])
            pygame.draw.rect(surf, GRAY_DARK, (rx + 8, ry_s + 8, 36, 36), 1, border_radius=4)

            tx = rx + 54
            tw = cw - 58

            nc  = WHITE if not locked else GRAY_MID
            ns  = self.fonts["small"].render(node["name"], True, nc)
            surf.blit(ns, (tx, ry_s + 6))

            pip_w = min(14, (tw - 4) // max(1, max_lvl))
            for li in range(max_lvl):
                pc = ORANGE if li < lvl else GRAY_DARK
                pygame.draw.rect(surf, pc, (tx + li * (pip_w + 2), ry_s + 30, pip_w, 8), border_radius=3)

            next_lvl    = min(lvl, max_lvl - 1)
            bonus_txt   = node["bonuses"][next_lvl]
            bs = self.fonts["ui"].render(bonus_txt, True, node["color"])
            surf.blit(bs, (tx, ry_s + 44))

            if maxed:
                ms = self.fonts["small"].render("MAX", True, GREEN)
                surf.blit(ms, (tx, ry_s + 62))
            elif locked:
                req_node = next((n for n in SKILL_TREE if n["key"] == req[0]), None)
                rn_full  = req_node["name"] if req_node else req[0]
                rn_short = (rn_full[:12] + "..") if len(rn_full) > 12 else rn_full
                ls_txt   = self.fonts["ui"].render(f"Req: {rn_short} Lv{req[1]}", True, GRAY_MID)
                surf.blit(ls_txt, (tx, ry_s + 62))
            else:
                cost_col = GOLD if can_buy else GRAY_MID
                cs_ = self.fonts["small"].render(f"{cost} Coins", True, cost_col)
                surf.blit(cs_, (tx, ry_s + 62))

        surf.set_clip(None)

        grad = pygame.Surface((sw, 40), pygame.SRCALPHA)
        for gy in range(40):
            grad.fill((*DARK_BG, int(gy * 6)), (0, gy, sw, 1))
        surf.blit(grad, (0, sh - 110))

        hint = self.fonts["ui"].render("Mausrad zum Scrollen  |  Klick = Kaufen",
                                        True, GRAY_MID)
        surf.blit(hint, hint.get_rect(center=(sw // 2, sh - 82)))

class SettingsMenu:
    def __init__(self, screen, fonts, cfg):
        self.screen = screen
        self.fonts  = fonts
        self.cfg    = cfg
        self.sw, self.sh = screen.get_size()
        self.scale  = min(self.sw / 1280, self.sh / 720)
        self.stars  = make_stars(80, self.sw, self.sh)
        self.anim   = 0.0
        self.lang_list = list(LANGUAGES.keys())

    def _s(self, v):
        return int(v * self.scale)

    async def run(self):
        pygame.event.clear()
        clock = pygame.time.Clock()
        while True:
            dt = clock.tick(60)/1000.0
            self.anim += dt
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: return "quit"
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    save_config(self.cfg); return "back"
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    r = self._click(pygame.mouse.get_pos(), ev.button)
                    if r: return r
            scroll_stars(self.stars, dt, self.sw, self.sh)
            self._draw()
            pygame.display.flip()
            await asyncio.sleep(0)

    _ROW_H_BASE  = 56
    _Y0_BASE     = 100
    _LBL_X_BASE  = 80
    _CTRL_X_BASE = 320
    _CTRL_W_BASE = 560

    @property
    def _ROW_H(self):  return self._s(self._ROW_H_BASE)
    @property
    def _Y0(self):     return self._s(self._Y0_BASE)
    @property
    def _LBL_X(self):  return self._s(self._LBL_X_BASE)
    @property
    def _CTRL_X(self): return self._s(self._CTRL_X_BASE)
    @property
    def _CTRL_W(self): return self._s(self._CTRL_W_BASE)

    def _rows(self):
        return [
            {"kind": "resolution", "label": t("resolution")},
            {"kind": "toggle",     "label": t("fullscreen"),   "key": "fullscreen"},
            {"kind": "toggle",     "label": "FPS anzeigen",    "key": "show_fps"},
            {"kind": "fps_cap",    "label": "FPS Cap"},
            {"kind": "toggle",     "label": "Screen Shake",    "key": "screen_shake"},
            {"kind": "toggle",     "label": "VSync",           "key": "vsync"},
            {"kind": "toggle",     "label": "Auto-Ziel aktiv", "key": "autoaim_enabled"},
            {"kind": "slider",     "label": t("master_volume"),"key": "master_volume"},
            {"kind": "slider",     "label": t("music_volume"), "key": "music_volume"},
            {"kind": "slider",     "label": t("sfx_volume"),   "key": "sfx_volume"},
            {"kind": "language",   "label": t("language")},
        ]

    def _row_y(self, i):
        return self._Y0 + i * self._ROW_H

    def _click(self, pos, button):
        mx, my = pos
        sw, sh = self.sw, self.sh
        cx = self._CTRL_X
        cw = self._CTRL_W

        for i, row in enumerate(self._rows()):
            ry   = self._row_y(i)
            kind = row["kind"]

            if kind == "resolution":
                btn_w = min(self._s(88), cw // len(RESOLUTIONS) - self._s(4))
                for ri, res in enumerate(RESOLUTIONS):
                    bx = cx + ri * (btn_w + self._s(6))
                    if pygame.Rect(bx, ry + self._s(18), btn_w, self._s(30)).collidepoint(mx, my):
                        self.cfg["resolution"] = list(res)

            elif kind == "toggle":
                if pygame.Rect(cx, ry + self._s(16), self._s(80), self._s(30)).collidepoint(mx, my):
                    self.cfg[row["key"]] = not self.cfg.get(row["key"], False)

            elif kind == "fps_cap":
                _FPS_OPTIONS = [60, 120, 144, 165, 240, 0]
                btn_w = self._s(72)
                for fi, fval in enumerate(_FPS_OPTIONS):
                    bx = cx + fi * (btn_w + self._s(6))
                    if pygame.Rect(bx, ry + self._s(18), btn_w, self._s(30)).collidepoint(mx, my):
                        self.cfg["fps_cap"] = fval

            elif kind == "slider":
                slw = self._s(320)
                if cx <= mx <= cx + slw and ry + self._s(18) <= my <= ry + self._s(40):
                    self.cfg[row["key"]] = int((mx - cx) / slw * 100)

            elif kind == "language":
                for li, lc in enumerate(self.lang_list):
                    bx = cx + li * self._s(96)
                    if pygame.Rect(bx, ry + self._s(8), self._s(90), self._s(40)).collidepoint(mx, my):
                        self.cfg["language"] = lc
                        load_language(lc)

        btn_y = sh - self._s(68)
        bw = self._s(200); bh = self._s(48)
        if pygame.Rect(sw // 2 - self._s(230), btn_y, bw, bh).collidepoint(mx, my):
            save_config(self.cfg); return "back"
        if pygame.Rect(sw // 2 + self._s(30),  btn_y, bw, bh).collidepoint(mx, my):
            save_config(self.cfg); return "apply"
        return None

    def _draw(self):
        surf = self.screen
        surf.fill(DARK_BG)
        draw_stars(surf, self.stars)
        sw, sh = self.sw, self.sh
        mx, my = pygame.mouse.get_pos()

        title = self.fonts["big"].render(t("settings_title"), True, ORANGE)
        surf.blit(title, title.get_rect(center=(sw // 2, self._s(48))))
        pygame.draw.line(surf, ORANGE_DARK, (self._s(60), self._s(68)), (sw - self._s(60), self._s(68)), 1)

        cx = self._CTRL_X
        cw = self._CTRL_W

        for i, row in enumerate(self._rows()):
            ry   = self._row_y(i)
            kind = row["kind"]

            if i % 2 == 0:
                rb = pygame.Surface((sw - self._s(120), self._ROW_H - self._s(4)), pygame.SRCALPHA)
                rb.fill((*PANEL_DARK, 100))
                surf.blit(rb, (self._s(60), ry))

            ls = self.fonts["med"].render(row["label"], True, GRAY_LIGHT)
            surf.blit(ls, (self._LBL_X, ry + (self._ROW_H - ls.get_height()) // 2))

            if kind == "resolution":
                cur   = tuple(self.cfg.get("resolution", [1280, 720]))
                btn_w = min(self._s(88), cw // len(RESOLUTIONS) - self._s(4))
                for ri, res in enumerate(RESOLUTIONS):
                    bx = cx + ri * (btn_w + self._s(6))
                    r  = pygame.Rect(bx, ry + self._s(18), btn_w, self._s(30))
                    draw_button(surf, r, f"{res[0]}x{res[1]}",
                                self.fonts["ui"], r.collidepoint(mx, my), res == cur)

            elif kind == "toggle":
                val = self.cfg.get(row["key"], False)
                r   = pygame.Rect(cx, ry + self._s(16), self._s(80), self._s(30))
                draw_button(surf, r, t("on") if val else t("off"),
                            self.fonts["small"], r.collidepoint(mx, my), val)

            elif kind == "fps_cap":
                _FPS_OPTIONS = [60, 120, 144, 165, 240, 0]
                _FPS_LABELS  = ["60", "120", "144", "165", "240", "MAX"]
                cur_fps = self.cfg.get("fps_cap", 0)
                btn_w = self._s(72)
                for fi, (fval, flbl) in enumerate(zip(_FPS_OPTIONS, _FPS_LABELS)):
                    bx = cx + fi * (btn_w + self._s(6))
                    r  = pygame.Rect(bx, ry + self._s(18), btn_w, self._s(30))
                    draw_button(surf, r, flbl, self.fonts["ui"],
                                r.collidepoint(mx, my), fval == cur_fps)

            elif kind == "slider":
                val = self.cfg.get(row["key"], 80)
                slw = self._s(320)
                sy  = ry + self._s(22);  sh2 = self._s(14)
                pygame.draw.rect(surf, GRAY_DARK, (cx, sy, slw, sh2))
                pygame.draw.rect(surf, ORANGE,    (cx, sy, int(slw * val / 100), sh2))
                pygame.draw.rect(surf, GRAY_MID,  (cx, sy, slw, sh2), 1)
                for tick in [0.25, 0.5, 0.75]:
                    tx2 = cx + int(slw * tick)
                    pygame.draw.line(surf, GRAY_MID, (tx2, sy - self._s(2)), (tx2, sy + sh2 + self._s(2)), 1)
                kx  = cx + int(slw * val / 100)
                kw  = self._s(10);  kh = self._s(22)
                pygame.draw.rect(surf, WHITE,       (kx - kw//2, sy - self._s(4), kw, kh))
                pygame.draw.rect(surf, ORANGE_DARK, (kx - kw//2, sy - self._s(4), kw, kh), 1)
                vs  = self.fonts["small"].render(f"{val}%", True, WHITE)
                surf.blit(vs, (cx + slw + self._s(14), sy))

            elif kind == "language":
                cur_lang = self.cfg.get("language", "de")
                lbw = self._s(90);  lbh = self._s(40);  lbgap = self._s(96)
                for li, lc in enumerate(self.lang_list):
                    bx     = cx + li * lbgap
                    r      = pygame.Rect(bx, ry + self._s(8), lbw, lbh)
                    active = (lc == cur_lang)
                    hover  = r.collidepoint(mx, my)
                    bg     = ORANGE_DARK if active else (GRAY_DARK if hover else PANEL_BG)
                    pygame.draw.rect(surf, bg, r)
                    pygame.draw.rect(surf,
                                     ORANGE_GLOW if active else (ORANGE if hover else GRAY_DARK),
                                     r, 2)
                    draw_flag(surf, bx + self._s(5), ry + self._s(13), self._s(44), self._s(28), lc)
                    lc_s = self.fonts["small"].render(lc.upper(), True,
                                                       WHITE if active else GRAY_LIGHT)
                    surf.blit(lc_s, lc_s.get_rect(center=(bx + self._s(72), ry + self._s(28))))

        btn_y  = sh - self._s(68)
        bw     = self._s(200);  bh = self._s(48)
        pygame.draw.line(surf, GRAY_DARK, (self._s(60), btn_y - self._s(10)),
                         (sw - self._s(60), btn_y - self._s(10)), 1)

        back_r  = pygame.Rect(sw // 2 - self._s(230), btn_y, bw, bh)
        apply_r = pygame.Rect(sw // 2 + self._s(30),  btn_y, bw, bh)
        draw_button(surf, back_r,  t("back"),  self.fonts["med"], back_r.collidepoint(mx, my))
        draw_button(surf, apply_r, t("apply"), self.fonts["med"], apply_r.collidepoint(mx, my))

        hint = self.fonts["ui"].render("ESC = Zurück  |  Apply speichert und wendet an",
                                        True, GRAY_DARK)
        surf.blit(hint, hint.get_rect(center=(sw // 2, sh - self._s(16))))
