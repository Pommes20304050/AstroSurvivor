import pygame, math, random
from constants import *
from constants import (ACHIEVEMENTS, between_wave_delay, get_difficulty_tier,
                       pick_wave_modifier, WAVE_MODIFIERS,
                       DANGER_DECAY_RATE, DANGER_HIT_RESET, DANGER_MAX,
                       DANGER_GRACE_PERIOD, DANGER_START_WAVE, danger_multiplier)
from entities import Player, Enemy, XPOrb, CoinOrb, PowerOrb, pick_enemy_type, ENEMY_TYPES
from particles import ParticleSystem
from draw_utils import (draw_stars, draw_bar, draw_panel, draw_glow_text,
                        draw_skill_icon, draw_weapon_icon, draw_button,
                        make_nebula_surface, make_vignette_surface)
from localization import t
from config import save_config

def make_stars(count, sw, sh):
    stars = []
    for _ in range(count):
        layer = random.choices([0, 1, 2], weights=[50, 30, 20])[0]
        brightness = random.uniform(0.2 + layer * 0.25, 0.6 + layer * 0.35)
        size       = layer + 1
        speed      = brightness * (0.6 + layer * 0.4)
        tint = random.choice(["white","white","white","white","cyan","blue","yellow"])
        stars.append([random.uniform(0, sw), random.uniform(0, sh),
                      brightness, size, speed, tint])
    return stars

def scroll_stars(stars, dt, sw, sh):
    for s in stars:
        s[1] += s[4] * dt * 60
        if s[1] > sh:
            s[1] = -4; s[0] = random.uniform(0, sw)

def draw_stars(surf, stars, t=0.0):
    for s in stars:
        x, y, bright, size, spd, tint = s
        twinkle = 0.78 + 0.22 * math.sin(t * 2.8 + x * 0.031 + y * 0.019)
        c = min(255, int(bright * 220 * twinkle))
        if   tint == "cyan":   col = (int(c*0.5), c, c)
        elif tint == "blue":   col = (int(c*0.4), int(c*0.6), c)
        elif tint == "yellow": col = (c, c, int(c*0.4))
        else:                  col = (c, c, c)
        pygame.draw.rect(surf, col, (int(x), int(y), size, size))
        if size >= 2 and bright > 0.75 and twinkle > 0.96:
            cv = min(255, c + 40)
            sc = (int(cv*0.5), cv, cv) if tint == "cyan" else (cv, cv, cv)
            pygame.draw.rect(surf, sc, (int(x) - 1, int(y),      1, size))
            pygame.draw.rect(surf, sc, (int(x),      int(y) - 1, size, 1))

def spawn_wave(wave_num, sw, sh, px=None, py=None):
    enemies = []

    if wave_num <= 20:
        count = int(BASE_ENEMIES_PER_WAVE * (1 + ENEMY_SCALE_PER_WAVE * (wave_num - 1)))
    else:
        count_at_20 = int(BASE_ENEMIES_PER_WAVE * (1 + ENEMY_SCALE_PER_WAVE * 19))
        count = int(count_at_20 + 8 * math.log(wave_num - 19))
    count = min(count, ENEMY_COUNT_CAP)

    is_boss = (wave_num % BOSS_EVERY_N_WAVES == 0)

    if wave_num <= 20:
        hp_s = 1 + 0.22 * (wave_num - 1)
    else:
        hp_at_20 = 1 + 0.22 * 19
        hp_s = hp_at_20 * (1.04 ** (wave_num - 20))

    if wave_num <= 20:
        dmg_s = 1.0 + 0.03 * max(0, wave_num - 5)
    else:
        dmg_at_20 = 1.0 + 0.03 * 15
        dmg_s = dmg_at_20 * (1.08 ** (wave_num - 20))

    spd_s = 1.0 + 1.2 * (1 - math.exp(-0.04 * (wave_num - 1)))

    flank_chance = min(0.35, 0.04 * max(0, wave_num - 5))

    for _ in range(count):
        if px is not None and wave_num >= 6 and random.random() < flank_chance:
            angle = random.uniform(0, math.pi * 2)
            spawn_r = random.uniform(sw * 0.45, sw * 0.65)
            fx = px + math.cos(angle) * spawn_r
            fy = py + math.sin(angle) * spawn_r
            x = max(-28, min(sw + 28, fx))
            y = max(-28, min(sh + 28, fy))
        else:
            edge = random.randint(0, 3)
            if   edge == 0: x, y = random.uniform(0, sw), -20
            elif edge == 1: x, y = random.uniform(0, sw), sh + 20
            elif edge == 2: x, y = -20, random.uniform(0, sh)
            else:           x, y = sw + 20, random.uniform(0, sh)

        etype = pick_enemy_type(wave_num)
        ecfg  = ENEMY_TYPES[etype]
        color = random.choice(ecfg["colors"])
        sz_lo, sz_hi = ecfg["sz"]
        size  = random.randint(sz_lo, sz_hi)
        hp    = random.uniform(28, 52) * hp_s * ecfg["hp"]
        spd   = random.uniform(0.9, 1.6) * spd_s * ecfg["spd"]
        val   = int(XP_PER_KILL * (1 + wave_num * XP_KILL_WAVE_SCALE))
        e = Enemy(x, y, hp, spd, color, size, val, False, wave_num, etype)
        e.dmg = int(e.dmg * dmg_s)
        enemies.append(e)

    if is_boss:
        is_elite = (wave_num % 10 == 0)

        boss_extra = max(1.0, 1.0 + 0.24 * max(0, (wave_num - 5) // 5))
        base_boss_hp = 1050 * hp_s * boss_extra
        if wave_num > 20:
            base_boss_hp *= 1.02 ** (wave_num - 20)
        if is_elite:
            base_boss_hp *= 1.5

        boss_size = min(52 if is_elite else 44, 30 + (wave_num // 10) * 3)
        boss_spd  = (1.05 + 0.02 * max(0, wave_num - 10)) * spd_s
        boss_color = PURPLE if is_elite else RED

        boss_enemy = Enemy(sw/2, -60, base_boss_hp, boss_spd, boss_color,
                           boss_size, int(XP_PER_KILL*9*(1+wave_num*XP_KILL_WAVE_SCALE)),
                           True, wave_num, 0)
        boss_enemy.is_elite = is_elite
        boss_enemy.dmg = int(boss_enemy.dmg * dmg_s)

        if wave_num >= 20:
            shield_pct = min(0.30, 0.12 + 0.004 * (wave_num - 20))
            boss_enemy.boss_shield     = base_boss_hp * shield_pct
            boss_enemy.boss_shield_max = boss_enemy.boss_shield
        else:
            boss_enemy.boss_shield     = 0.0
            boss_enemy.boss_shield_max = 0.0

        enemies.append(boss_enemy)
    return enemies

def xp_for_level(lvl):
    gentle_ramp = 1.0 + 0.03 * (lvl - 1)
    return int(XP_LEVEL_BASE * lvl * math.sqrt(lvl) * gentle_ramp)

def calc_skill_tree_bonuses(skill_tree: dict) -> dict:
    b = {"hp":0,"shield":0,"armor":0.0,"speed":0.0,"damage_pct":0.0,
         "firerate_pct":0.0,"pierce":0,"multishot":0,"regen":0.0,"crit":0.0,
         "magnet":0,"autoaim":0,"aura":0,"aura_dmg":0.0}
    for node in SKILL_TREE:
        lvl = skill_tree.get(node["key"], 0)
        if lvl <= 0: continue
        k = node["key"]
        if   k == "hp_up":        b["hp"]          += [20, 45, 80, 120][min(lvl,4)-1]
        elif k == "regen_up":     b["regen"]        += [0.8, 2.3, 4.8][min(lvl,3)-1]
        elif k == "armor_up":     b["armor"]        += lvl * 0.05
        elif k == "shield_up":    b["shield"]       += [30, 65, 115][min(lvl,3)-1]
        elif k == "dmg_up":       b["damage_pct"]   += [0.08, 0.18, 0.30, 0.45][min(lvl,4)-1]
        elif k == "crit_up":      b["crit"]         += [0.05, 0.12, 0.22][min(lvl,3)-1]
        elif k == "pierce_up":    b["pierce"]       += min(lvl, 2)
        elif k == "firerate_up":  b["firerate_pct"] += lvl * 0.065
        elif k == "multishot_up": b["multishot"]    += min(lvl, 2)
        elif k == "speed_up":     b["speed"]        += [0.3, 0.6, 1.0, 1.4][min(lvl,4)-1]
        elif k == "magnet_up":    b["magnet"]       += lvl
        elif k == "autoaim_up":   b["autoaim"]      += lvl
        elif k == "aura_up":      b["aura"]         += lvl
        elif k == "aura_dmg_up":  b["aura_dmg"]     += [0.20, 0.45, 0.75][min(lvl,3)-1]
    return b


XP_ORB_LIFETIME   = 8.0
COIN_ORB_LIFETIME = 12.0
ORB_MERGE_INTERVAL = 0.5
XP_ORB_MAX   = 40
COIN_ORB_MAX = 30
XP_MERGE_DIST   = 20
COIN_MERGE_DIST = 25
BOMB_BATCH_MAX  = 8


def _merge_index_list(orbs, indices, dist_sq):
    n = len(indices)
    for i in range(n):
        a = orbs[indices[i]]
        if not a.alive:
            continue
        for j in range(i + 1, n):
            b = orbs[indices[j]]
            if not b.alive:
                continue
            dx = a.x - b.x
            dy = a.y - b.y
            if dx * dx + dy * dy <= dist_sq:
                a.value += b.value
                a.x = (a.x + b.x) * 0.5
                a.y = (a.y + b.y) * 0.5
                a.age = min(a.age, b.age)
                b.alive = False


def _merge_cross(orbs, indices_a, indices_b, dist_sq):
    for i in indices_a:
        a = orbs[i]
        if not a.alive:
            continue
        for j in indices_b:
            b = orbs[j]
            if not b.alive:
                continue
            dx = a.x - b.x
            dy = a.y - b.y
            if dx * dx + dy * dy <= dist_sq:
                a.value += b.value
                a.x = (a.x + b.x) * 0.5
                a.y = (a.y + b.y) * 0.5
                a.age = min(a.age, b.age)
                b.alive = False


def merge_orbs(orbs, merge_dist, max_count):
    n = len(orbs)
    if n <= 1:
        return orbs

    cell = merge_dist
    grid = {}

    for i, o in enumerate(orbs):
        if not o.alive:
            continue
        key = (int(o.x // cell), int(o.y // cell))
        if key in grid:
            grid[key].append(i)
        else:
            grid[key] = [i]

    dist_sq = merge_dist * merge_dist
    neighbour_offsets = [(1, 0), (0, 1), (1, 1), (-1, 1)]

    for (gx, gy), indices in grid.items():
        _merge_index_list(orbs, indices, dist_sq)
        for dx, dy in neighbour_offsets:
            nkey = (gx + dx, gy + dy)
            if nkey in grid:
                _merge_cross(orbs, indices, grid[nkey], dist_sq)

    result = [o for o in orbs if o.alive]

    if len(result) > max_count:
        result.sort(key=lambda o: o.value)
        while len(result) > max_count and len(result) >= 2:
            a, b = result[0], result[1]
            a.value += b.value
            a.x = (a.x + b.x) * 0.5
            a.y = (a.y + b.y) * 0.5
            a.age = min(a.age, b.age)
            result.pop(1)

    return result


def batch_spawn_orbs(kills, OrbClass, max_orbs=BOMB_BATCH_MAX):
    if not kills:
        return []
    if len(kills) <= max_orbs:
        return [OrbClass(x, y, v) for x, y, v in kills]

    cx = sum(k[0] for k in kills) / len(kills)
    cy = sum(k[1] for k in kills) / len(kills)
    kills_sorted = sorted(kills, key=lambda k: math.atan2(k[1] - cy, k[0] - cx))
    bucket_size = max(1, len(kills_sorted) // max_orbs)
    result = []
    for start in range(0, len(kills_sorted), bucket_size):
        bucket = kills_sorted[start:start + bucket_size]
        bx = sum(k[0] for k in bucket) / len(bucket)
        by = sum(k[1] for k in bucket) / len(bucket)
        bv = sum(k[2] for k in bucket)
        result.append(OrbClass(bx, by, bv))
    return result


class GamePlay:
    def __init__(self, screen, fonts, cfg, ship_idx, weapon_idx, particles_quality):
        self.screen = screen
        self.fonts  = fonts
        self.cfg    = cfg
        self.sw, self.sh = screen.get_size()

        ship_data  = SHIPS[ship_idx].copy()
        ship_upg   = cfg.get("ship_upgrades", {}).get(ship_data["key"], 0)
        if ship_upg > 0:
            for lvl in range(min(ship_upg, len(SHIP_UPG_BONUS))):
                b = SHIP_UPG_BONUS[lvl]
                ship_data["hp"]     += b["hp"]
                ship_data["speed"]  += b["speed"]
                ship_data["shield"] += b["shield"]

        weapon_data = WEAPONS[weapon_idx].copy()
        weapon_upg  = cfg.get("weapon_upgrades", {}).get(weapon_data["key"], 0)
        if weapon_upg > 0:
            b = WEAPON_UPG_BONUS[min(weapon_upg, len(WEAPON_UPG_BONUS)) - 1]
            weapon_data["damage"]    = int(weapon_data["damage"] * (1 + b["dmg_pct"]))
            weapon_data["fire_rate"] = weapon_data["fire_rate"] * (1 - b["rate_pct"])
            weapon_data["pierce"]   += b["pierce"]

        stb = calc_skill_tree_bonuses(cfg.get("skill_tree", {}))

        try:
            import sounds as _snd
            _snd.init_sounds()
            self.snd = _snd
        except Exception:
            self.snd = None

        self.player    = Player(ship_data, weapon_data, self.sw, self.sh, stb)
        self.player.autoaim_enabled = bool(self.cfg.get("autoaim_enabled", True))
        self.particles = ParticleSystem(particles_quality)

        self.nebula   = make_nebula_surface(self.sw, self.sh)
        self.vignette = make_vignette_surface(self.sw, self.sh)
        self.stars    = make_stars(220, self.sw, self.sh)
        self._glow_surf = pygame.Surface((self.sw, self.sh))
        self._canvas    = pygame.Surface((self.sw, self.sh))

        self.bullets       = []
        self.enemy_bullets = []
        self.enemies       = []
        self.xp_orbs       = []
        self.coin_orbs     = []
        self.power_orbs    = []
        self._orb_merge_timer = 0.0

        self.wave       = 1
        self.wave_timer = wave_duration(1)
        self.wave_alive = True
        self.between_timer = 0.0
        self.between_waves = False
        self.enemy_count_start = 0

        self.level     = 1
        self.xp        = 0
        self.xp_needed = xp_for_level(1)
        self.score     = 0
        self.kills     = 0
        self.session_coins = 0

        self.state = "playing"

        self.upgrade_choices  = []
        self.upgrade_selected = None

        self.screen_shake = 0.0
        self.do_shake     = cfg.get("screen_shake", True)
        self.mouse_pos    = (self.sw // 2, 0)

        self.floating_texts   = []
        self._wave_kills      = 0
        self._last_wave_kills = 0

        self._achiev_popup    = []
        self._achiev_unlocked = set(cfg.get("achievements", []))
        self._check_achiev_timer = 0.0

        self.session_time       = 0.0
        self._boss_killed       = False
        self._bosses_killed     = 0
        self._boss_wave_nodmg   = True
        self._wave_took_damage  = False
        self._nodmg_streak      = 0
        self._bombs_used        = 0
        self._bomb_used         = False
        self._close_call        = False

        self.danger_level     = 0.0
        self._danger_grace    = 0.0

        self.wave_modifier    = None

        self.kill_streak      = 0
        self.combo_timer      = 0.0
        self.combo_mult       = 1
        self.combo_display    = 0.0
        self._prev_combo_mult = 1

        self.bomb_charges     = 0
        self.bomb_cooldown    = 0.0
        self._bomb_used       = False

        self.reinforce_timer  = 999.0

        self.wave_announce_timer = 2.5
        self.wave_announce_wave  = 1
        self.danger_pulse        = 0.0
        self.score_flash         = 0.0
        self.kill_flash          = 0.0
        self.upgrade_glow        = 0.0
        self.global_time         = 0.0
        self.boss_present        = False

        self.fn = fonts["big"]
        self.fm = fonts["med"]
        self.fs = fonts["small"]
        self.fu = fonts["ui"]

        self._check_achievements()

        self._spawn_wave()

    def _spawn_wave(self):
        self._wave_kills       = 0

        self.wave_modifier = pick_wave_modifier(self.wave)

        self.enemies           = spawn_wave(self.wave, self.sw, self.sh,
                                            self.player.x, self.player.y)

        if self.wave_modifier:
            mod = WAVE_MODIFIERS[self.wave_modifier]
            cnt_mult = mod.get("enemy_count_mult", 1.0)
            hp_mult  = mod.get("enemy_hp_mult", 1.0)
            dmg_mult = mod.get("enemy_dmg_mult", 1.0)
            spd_mult = mod.get("enemy_spd_mult", 1.0)
            force_t  = mod.get("force_type", None)

            non_boss = [e for e in self.enemies if not e.boss]
            bosses   = [e for e in self.enemies if e.boss]
            target   = max(3, int(len(non_boss) * cnt_mult))
            if target > len(non_boss):
                from copy import copy
                for _ in range(target - len(non_boss)):
                    src = random.choice(non_boss)
                    ne = copy(src)
                    ne.x += random.uniform(-60, 60)
                    ne.y += random.uniform(-60, 60)
                    non_boss.append(ne)
            elif target < len(non_boss):
                non_boss = random.sample(non_boss, target)
            self.enemies = bosses + non_boss

            for e in self.enemies:
                if e.boss:
                    continue
                e.hp = e.max_hp = e.max_hp * hp_mult
                e.dmg = int(e.dmg * dmg_mult)
                e.speed *= spd_mult
                if force_t is not None:
                    e.enemy_type = force_t

        self.enemy_count_start = len(self.enemies)
        self.wave_timer        = wave_duration(self.wave)
        self.wave_alive        = True
        self.between_waves     = False
        self.boss_present      = any(e.boss for e in self.enemies)
        self.reinforce_timer   = random.uniform(13, 20)
        self._wave_took_damage = False
        self._danger_grace     = DANGER_GRACE_PERIOD
        for e in self.enemies:
            self.particles.warp_in(e.x, e.y, e.color)

    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return "quit"
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    if self.state == "playing":
                        self.state = "paused"
                        pygame.mouse.set_visible(True)
                    elif self.state == "paused":
                        self.state = "playing"
                        pygame.mouse.set_visible(False)
                    elif self.state in ("gameover", "upgrade"):
                        return "menu"
                if ev.key in (pygame.K_SPACE, pygame.K_q) and self.state == "playing":
                    self._use_bomb()
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                result = self._click(pygame.mouse.get_pos())
                if result:
                    return result
            if ev.type == pygame.MOUSEMOTION:
                self.mouse_pos = pygame.mouse.get_pos()
        return None

    def _click(self, pos):
        if self.state == "upgrade":  return self._click_upgrade(pos)
        if self.state == "paused":   return self._click_pause(pos)
        if self.state == "gameover": return self._click_gameover(pos)
        return None

    def update(self, dt):
        self.screen_shake = max(0, self.screen_shake - dt * 2.5)
        self.global_time += dt

        if self.state != "playing":
            return
        self.session_time += dt
        self.danger_pulse += dt * 4
        scroll_stars(self.stars, dt, self.sw, self.sh)

        if self.wave >= DANGER_START_WAVE and self.wave_alive:
            if self._danger_grace > 0:
                self._danger_grace -= dt
            else:
                self.danger_level = min(DANGER_MAX,
                                        self.danger_level + DANGER_DECAY_RATE * dt)
                _dh, _dd, ds = danger_multiplier(self.danger_level)
                for e in self.enemies:
                    if not e.alive or not hasattr(e, '_base_speed'):
                        continue
                    e.speed = e._base_speed * ds

        if self.kill_streak > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.kill_streak = 0
                self.combo_mult  = 1
        self.combo_display = max(0, self.combo_display - dt * 1.2)
        self.bomb_cooldown = max(0, self.bomb_cooldown - dt)

        if self.wave_announce_timer > 0:
            self.wave_announce_timer -= dt

        keys = pygame.key.get_pressed()
        self.player.update(dt, keys, self.mouse_pos)

        if self.player.skill_dash > 0:
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                if self.player.dash_cd <= 0:
                    dash_dist = 110 + self.player.skill_dash * 30
                    dash_cd   = 3.5 - self.player.skill_dash * 0.5
                    self.player.x = max(20, min(self.sw - 20,
                                    self.player.x + self.player.aim_dx * dash_dist))
                    self.player.y = max(20, min(self.sh - 20,
                                    self.player.y + self.player.aim_dy * dash_dist))
                    self.player.dash_cd      = dash_cd
                    self.player._dash_active = 0.18
                    self.particles.levelup_burst(self.player.x, self.player.y)

        aa_enemies = self.enemies if (self.player.skill_autoaim > 0 or self.player.autoaim_enabled) else []
        self.player.shoot(self.bullets, self.particles, self.snd, aa_enemies)

        tx = self.player.x - self.player.aim_dx * 18
        ty = self.player.y - self.player.aim_dy * 18
        self.particles.engine_trail(tx, ty, self.player.color)

        for b in self.bullets:
            if b.homing > 0 and self.enemies:
                best_d, best_e = 320, None
                for e in self.enemies:
                    if not e.alive: continue
                    d = math.hypot(e.x - b.x, e.y - b.y)
                    if d < best_d:
                        best_d, best_e = d, e
                if best_e is not None:
                    tdx = best_e.x - b.x; tdy = best_e.y - b.y
                    td  = math.hypot(tdx, tdy)
                    if td > 0:
                        turn = 0.10 + b.homing * 0.06
                        b.dx += (tdx / td - b.dx) * turn
                        b.dy += (tdy / td - b.dy) * turn
                        bd = math.hypot(b.dx, b.dy)
                        if bd > 0: b.dx /= bd; b.dy /= bd

        for b  in self.bullets:       b.update(dt, self.sw, self.sh)
        for eb in self.enemy_bullets: eb.update(dt, self.sw, self.sh)
        self.bullets       = [b  for b  in self.bullets       if b.alive]
        self.enemy_bullets = [eb for eb in self.enemy_bullets if eb.alive]

        for e in self.enemies:
            e.update(dt, self.player.x, self.player.y, self.enemy_bullets)
            if e.enemy_type == 6 and getattr(e, '_do_heal_nearby', False):
                e._do_heal_nearby = False
                for e2 in self.enemies:
                    if e2 is e or not e2.alive: continue
                    if math.hypot(e2.x - e.x, e2.y - e.y) < 110:
                        heal_amt = e2.max_hp * 0.08
                        e2.hp = min(e2.max_hp, e2.hp + heal_amt)
                        self.floating_texts.append([e2.x, e2.y - 10, f"+{int(heal_amt)}",
                                                    GREEN, 0.8, -0.6])
            if e.boss and getattr(e, '_wants_summon', False):
                e._wants_summon = False
                num_minions = 4 if getattr(e, 'is_elite', False) else 3
                for _ in range(num_minions):
                    angle = random.uniform(0, math.tau)
                    mx = e.x + math.cos(angle) * 60
                    my = e.y + math.sin(angle) * 60
                    hp_s = 1 + 0.22 * (self.wave - 1)
                    m_hp = random.uniform(28, 52) * hp_s * 0.6
                    m_spd = random.uniform(1.4, 2.0)
                    minion = Enemy(mx, my, m_hp, m_spd, ORANGE, 12,
                                   int(XP_PER_KILL * 0.5), False, self.wave, 0)
                    self.enemies.append(minion)
                self.floating_texts.append([e.x, e.y - 30, "SUMMON!",
                                            PURPLE, 1.2, -0.8])

        if self.wave_alive:
            self.wave_timer -= dt
            if self.wave_timer <= 0:
                self.wave_timer = 0
                self._end_wave()

        if self.wave_alive and not self.between_waves and self.wave >= 5:
            self.reinforce_timer -= dt
            if self.reinforce_timer <= 0:
                self.reinforce_timer = random.uniform(11, 18)
                n_rf = 1 + self.wave // 10
                w = self.wave
                if w <= 20:
                    hp_s = 1 + 0.22 * (w - 1)
                else:
                    hp_s = (1 + 0.22 * 19) * (1.04 ** (w - 20))
                dmg_s = 1.0 + 0.03 * max(0, w - 5)
                spd_s = 1.0 + 1.2 * (1 - math.exp(-0.04 * (w - 1)))
                for _ in range(n_rf):
                    if len(self.enemies) >= ENEMY_COUNT_CAP:
                        break
                    angle = random.uniform(0, math.pi * 2)
                    r = random.uniform(min(self.sw, self.sh) * 0.48, min(self.sw, self.sh) * 0.60)
                    rx = max(-25, min(self.sw + 25, self.player.x + math.cos(angle) * r))
                    ry = max(-25, min(self.sh + 25, self.player.y + math.sin(angle) * r))
                    etype = random.choice([pick_enemy_type(self.wave), 1, 8])
                    if ENEMY_TYPES[etype]["min_wave"] > self.wave:
                        etype = 1
                    ecfg  = ENEMY_TYPES[etype]
                    hp    = random.uniform(28, 48) * hp_s * ecfg["hp"] * 0.75
                    spd   = random.uniform(0.9, 1.4) * spd_s * ecfg["spd"]
                    color = random.choice(ecfg["colors"])
                    sz    = random.randint(*ecfg["sz"])
                    val   = int(XP_PER_KILL * (1 + self.wave * XP_KILL_WAVE_SCALE))
                    re    = Enemy(rx, ry, hp, spd, color, sz, val, False, self.wave, etype)
                    re.dmg = int(re.dmg * dmg_s)
                    self.enemies.append(re)
                    self.particles.warp_in(rx, ry, color)
                self.floating_texts.append([self.player.x, self.player.y - 40,
                                            "FLANKERS!", RED, 1.4, -0.7])

        enemies_snapshot = list(self.enemies)
        for b in self.bullets:
            if not b.alive: continue
            for e in enemies_snapshot:
                if not e.alive: continue
                if math.hypot(b.x - e.x, b.y - e.y) < e.size + 4:
                    crit_chance = self.player.skill_crit * 0.10 + self.player._tree_crit
                    is_crit     = random.random() < min(0.60, crit_chance)
                    actual_dmg  = b.damage * (1.80 if is_crit else 1.0)

                    killed = e.hit(actual_dmg)
                    self.particles.hit_spark(e.x, e.y, b.color)

                    if is_crit:
                        self.particles.hit_spark(e.x, e.y, ORANGE_GLOW)
                        self.particles.hit_spark(e.x, e.y, WHITE)
                        self.floating_texts.append([e.x, e.y - 14,
                                                    f"CRIT! {int(actual_dmg)}",
                                                    ORANGE_GLOW, 0.9, -1.1])
                        if self.do_shake: self.screen_shake = max(self.screen_shake, 0.12)

                    if self.player.skill_lifesteal > 0:
                        steal_pct = self.player.skill_lifesteal * 0.05
                        heal_amt  = actual_dmg * steal_pct
                        self.player.heal(heal_amt)

                    if self.player.skill_slow > 0 and not e.boss:
                        slow_dur = 1.2 + self.player.skill_slow * 0.6
                        e.apply_slow(slow_dur)

                    if self.player.skill_explosion > 0 and not e.boss:
                        burn_dps = 6 + self.player.skill_explosion * 4
                        burn_dur = 1.8 + self.player.skill_explosion * 0.6
                        e.apply_burn(burn_dps, burn_dur)
                        if self.snd: self.snd.play("burn")

                    if self.player.skill_freeze > 0 and not e.boss:
                        freeze_ch = 0.08 + self.player.skill_freeze * 0.04
                        if random.random() < freeze_ch:
                            freeze_dur = 1.2 + self.player.skill_freeze * 0.4
                            e.apply_freeze(freeze_dur)
                            self.particles.hit_spark(e.x, e.y, (120, 220, 255))
                            self.floating_texts.append([e.x, e.y - 12, "FROZEN!",
                                                        (120, 220, 255), 0.7, -0.9])

                    if self.player.skill_chain > 0 and not getattr(b, '_chained', False):
                        chain_count = self.player.skill_chain
                        cx_src, cy_src = e.x, e.y
                        hit_set = {id(e)}
                        for _ in range(chain_count):
                            best_d, best_e2 = 200, None
                            for e2 in enemies_snapshot:
                                if not e2.alive or id(e2) in hit_set: continue
                                d2 = math.hypot(e2.x - cx_src, e2.y - cy_src)
                                if d2 < best_d:
                                    best_d, best_e2 = d2, e2
                            if best_e2 is not None:
                                chain_dmg = b.damage * 0.6
                                chain_killed = best_e2.hit(chain_dmg)
                                self.particles.chain_arc(cx_src, cy_src, best_e2.x, best_e2.y)
                                self.particles.hit_spark(best_e2.x, best_e2.y, CYAN)
                                hit_set.add(id(best_e2))
                                cx_src, cy_src = best_e2.x, best_e2.y
                                if chain_killed:
                                    self._on_kill(best_e2)

                    if killed:
                        self._on_kill(e)
                    if b.pierce <= b.hits:
                        b.alive = False
                        break
                    else:
                        b.hits += 1

        _dh, danger_dd, _ds = danger_multiplier(self.danger_level)
        for eb in self.enemy_bullets:
            if math.hypot(eb.x - self.player.x, eb.y - self.player.y) < 14:
                if self.player.skill_dodge > 0 and random.random() < self.player.skill_dodge * 0.10:
                    self.floating_texts.append([self.player.x, self.player.y - 20,
                                                "DODGE!", (180, 220, 255), 0.8, -1.0])
                    eb.alive = False
                    continue
                result = self.player.take_damage(int(eb.damage * danger_dd))
                if result == "shield":
                    self.particles.shield_hit(self.player.x, self.player.y)
                    self.particles.shield_flash()
                    if self.snd: self.snd.play("shield")
                elif result:
                    self.particles.hit_spark(self.player.x, self.player.y, RED)
                    self.particles.damage_flash()
                    if self.snd: self.snd.play("player_hit")
                    if self.do_shake: self.screen_shake = 0.25
                    self._wave_took_damage = True
                    self.danger_level = max(0.0, self.danger_level + DANGER_HIT_RESET)
                eb.alive = False

        for e in enemies_snapshot:
            if not e.alive: continue
            if math.hypot(e.x - self.player.x, e.y - self.player.y) < e.size + 14 and e.contact_cd <= 0:
                if self.player.skill_dodge > 0 and random.random() < self.player.skill_dodge * 0.10:
                    self.floating_texts.append([self.player.x, self.player.y - 20,
                                                "DODGE!", (180, 220, 255), 0.8, -1.0])
                    e.contact_cd = 1.0
                    continue
                result = self.player.take_damage(int(e.dmg * danger_dd))
                if result == "shield":
                    self.particles.shield_hit(self.player.x, self.player.y)
                    self.particles.shield_flash()
                elif result:
                    self.particles.damage_flash()
                    if self.do_shake: self.screen_shake = 0.25
                    self._wave_took_damage = True
                    self.danger_level = max(0.0, self.danger_level + DANGER_HIT_RESET)
                if self.player.skill_thorns > 0 and result and result != "shield":
                    thorn_pct = 0.10 + self.player.skill_thorns * 0.05
                    thorn_dmg = e.dmg * thorn_pct
                    killed_t = e.hit(thorn_dmg)
                    self.particles.hit_spark(e.x, e.y, (200, 80, 40))
                    if killed_t:
                        self._on_kill(e)
                e.contact_cd = 1.0

        px, py = self.player.x, self.player.y
        mag = self.player.magnet_range
        for o in self.xp_orbs:
            o.update(dt, px, py, mag)
            if o.age >= XP_ORB_LIFETIME:
                o.x, o.y = px, py
            if math.hypot(o.x - px, o.y - py) < 18:
                xp_bonus = 1.0 + self.player.skill_xp_bonus * 0.10
                xp_val = int(o.value * xp_bonus)
                self.xp += xp_val; o.alive = False
                self.particles.xp_collect(o.x, o.y)
                self.floating_texts.append([o.x, o.y - 8, f"+{xp_val} XP",
                                            (80, 255, 130), 1.0, -0.75])
        self.xp_orbs = [o for o in self.xp_orbs if o.alive]

        for c in self.coin_orbs:
            c.update(dt, px, py, mag)
            if c.age >= COIN_ORB_LIFETIME:
                c.x, c.y = px, py
            if math.hypot(c.x - px, c.y - py) < 18:
                bonus = 1.0 + self.player.skill_coin_bonus * 0.05
                coin_val = int(c.value * bonus)
                self.session_coins += coin_val; c.alive = False
                self.particles.coin_collect(c.x, c.y)
                self.score_flash = 0.5
                self.floating_texts.append([c.x, c.y - 8, f"+{coin_val}",
                                            GOLD, 0.9, -0.85])
        self.coin_orbs = [c for c in self.coin_orbs if c.alive]

        self._orb_merge_timer -= dt
        if self._orb_merge_timer <= 0:
            self._orb_merge_timer = ORB_MERGE_INTERVAL
            if len(self.xp_orbs) > 3:
                self.xp_orbs = merge_orbs(self.xp_orbs, XP_MERGE_DIST, XP_ORB_MAX)
            if len(self.coin_orbs) > 3:
                self.coin_orbs = merge_orbs(self.coin_orbs, COIN_MERGE_DIST, COIN_ORB_MAX)

        for po in self.power_orbs:
            po.update(dt, self.player.x, self.player.y, self.player.magnet_range)
            if math.hypot(po.x - self.player.x, po.y - self.player.y) < 22:
                self._collect_powerup(po)
        self.power_orbs = [po for po in self.power_orbs if po.alive]

        if self.player.skill_area_magnet > 0:
            am_pull = 1.2 + self.player.skill_area_magnet * 0.8
            for o in self.xp_orbs:
                dx = px - o.x; dy = py - o.y
                d = math.hypot(dx, dy)
                if d > 20:
                    o.x += (dx / d) * am_pull * dt * 60
                    o.y += (dy / d) * am_pull * dt * 60
            for c in self.coin_orbs:
                dx = px - c.x; dy = py - c.y
                d = math.hypot(dx, dy)
                if d > 20:
                    c.x += (dx / d) * am_pull * dt * 60
                    c.y += (dy / d) * am_pull * dt * 60
            for po in self.power_orbs:
                dx = px - po.x; dy = py - po.y
                d = math.hypot(dx, dy)
                if d > 20:
                    po.x += (dx / d) * am_pull * dt * 60
                    po.y += (dy / d) * am_pull * dt * 60

        total_aura = self.player.skill_aura + self.player._tree_aura
        if total_aura > 0:
            aura_lvl = min(total_aura, 3)
            aura_r   = [85, 110, 145][aura_lvl - 1]
            aura_dps = [6,  13,  24 ][aura_lvl - 1]
            aura_dps *= (1.0 + self.player._tree_aura_dmg)
            for e in self.enemies:
                if not e.alive: continue
                if math.hypot(e.x - self.player.x, e.y - self.player.y) < aura_r:
                    killed = e.hit(aura_dps * dt)
                    if killed:
                        self._on_kill(e)

        for e in self.enemies:
            if e.burn_timer > 0 and random.random() < 0.3:
                self.particles.burn_tick(e.x, e.y)

        for ft in self.floating_texts:
            ft[1] += ft[5] * dt * 60
            ft[4] -= dt
        self.floating_texts = [ft for ft in self.floating_texts if ft[4] > 0]

        for ap in self._achiev_popup:
            ap[2] -= dt
        self._achiev_popup = [ap for ap in self._achiev_popup if ap[2] > 0]

        while self.xp >= self.xp_needed:
            self.xp       -= self.xp_needed
            self.level    += 1
            self.xp_needed = xp_for_level(self.level)
            self._trigger_upgrade()
            self.particles.levelup_burst(self.player.x, self.player.y)
            self.particles.levelup_flash()
            if self.snd: self.snd.play("levelup")
            if self.state == "upgrade":
                break

        for e in self.enemies:
            if not e.alive and not getattr(e, '_kill_processed', False):
                self._on_kill(e)

        self.enemies = [e for e in self.enemies if e.alive]
        if hasattr(self, '_pending_spawns') and self._pending_spawns:
            self.enemies.extend(self._pending_spawns)
            self._pending_spawns.clear()
        self.boss_present = any(e.boss for e in self.enemies)

        if not self.enemies and self.wave_alive:
            self._end_wave()

        if self.between_waves:
            self.between_timer -= dt
            if self.between_timer <= 0:
                self.wave += 1
                if self.wave - 1 > self.cfg.get("max_wave_reached", 0):
                    self.cfg["max_wave_reached"] = self.wave - 1
                self.wave_announce_timer = 2.5
                self.wave_announce_wave  = self.wave
                self._spawn_wave()

        self.score_flash   = max(0, self.score_flash   - dt * 2)
        self.kill_flash    = max(0, self.kill_flash    - dt * 2)
        self.upgrade_glow += dt * 3

        if self.player.hp <= 0:
            self._on_gameover()

        self.particles.update(dt)

    def _on_kill(self, e, skip_orbs=False):
        if getattr(e, '_kill_processed', False):
            return
        e._kill_processed = True

        big = e.boss
        self.particles.explosion(e.x, e.y, e.color, big)
        if self.do_shake: self.screen_shake = 0.40 if big else 0.18
        if self.snd: self.snd.play("explosion" if big else "hit")
        if not skip_orbs:
            self.xp_orbs.append(XPOrb(e.x, e.y, e.value))
            self.coin_orbs.append(CoinOrb(e.x, e.y, e.coin_value))

        self.kill_streak  += 1
        self.combo_timer   = COMBO_STREAK_WINDOW
        old_mult = self.combo_mult
        new_mult = COMBO_MULTIPLIERS[0]
        for i, threshold in enumerate(COMBO_THRESHOLDS):
            if self.kill_streak >= threshold:
                new_mult = COMBO_MULTIPLIERS[i + 1]
        self.combo_mult = new_mult
        if new_mult > old_mult:
            self.combo_display = 2.5
            self.floating_texts.append([e.x, e.y - 24,
                                        f"COMBO ×{new_mult}!", ORANGE_GLOW, 1.8, -1.0])
            if self.snd: self.snd.play("combo")

        score_gain = e.value * 10 * self.combo_mult
        self.score       += score_gain
        self.kills       += 1
        self._wave_kills += 1
        self.kill_flash   = 0.6
        self.score_flash  = 0.6

        if getattr(e, 'wants_split', False):
            if not hasattr(self, '_pending_spawns'):
                self._pending_spawns = []
            num_splits = random.randint(2, 3)
            for _ in range(num_splits):
                angle = random.uniform(0, math.tau)
                sx = e.x + math.cos(angle) * 20
                sy = e.y + math.sin(angle) * 20
                child_hp    = e.max_hp * 0.18
                child_spd   = e._base_speed * 1.8
                child_size  = random.randint(7, 10)
                child_val   = max(1, e.value // 3)
                child = Enemy(sx, sy, child_hp, child_spd, ORANGE,
                              child_size, child_val, False, self.wave, 0)
                child.coin_value = max(1, e.coin_value // 3)
                self._pending_spawns.append(child)
                self.particles.warp_in(sx, sy, ORANGE)

        if big:
            self._boss_killed = True
            self._bosses_killed += 1

        if self.player.skill_vampiric > 0 and not big:
            heal_v = [2, 4, 7][min(self.player.skill_vampiric - 1, 2)]
            self.player.heal(heal_v)

        if self.player.skill_deathblow > 0 and not big and not getattr(e, '_chain_exploded', False):
            blast_r  = [90, 135][min(self.player.skill_deathblow - 1, 1)]
            blast_d  = e.max_hp * 0.18
            for e2 in list(self.enemies):
                if not e2.alive or e2 is e: continue
                d = math.hypot(e2.x - e.x, e2.y - e.y)
                if d < blast_r:
                    e2._chain_exploded = True
                    fall_off = 1.0 - d / blast_r * 0.5
                    killed2  = e2.hit(blast_d * fall_off)
                    self.particles.hit_spark(e2.x, e2.y, ORANGE)
                    if killed2:
                        self._on_kill(e2)
            self.particles.explosion(e.x, e.y, ORANGE, False)

        if not big and random.random() < POWERUP_DROP_CHANCE:
            kind = random.choice(list(POWERUP_DEFS.keys()))
            self.power_orbs.append(PowerOrb(e.x, e.y, kind))

        self._check_achievements()

    def _end_wave(self):
        if not self.wave_alive: return
        self._last_wave_kills = self._wave_kills
        self.wave_alive    = False
        self.between_waves = True
        self.between_timer = between_wave_delay(self.wave)
        self.xp           += XP_PER_WAVE
        self.particles.wave_clear_flash()
        wave_enemies = list(self.enemies)
        for e in wave_enemies:
            e.alive = False
        for e in wave_enemies:
            self._on_kill(e)
        self.enemies = []
        if self.snd: self.snd.play("wave_done")
        if self.bomb_charges < BOMB_MAX_CHARGES:
            self.bomb_charges += 1
            self.floating_texts.append([self.sw // 2, self.sh // 2 - 60,
                                        "BOMB CHARGE +1", ORANGE_GLOW, 2.0, -0.5])
        if not self._wave_took_damage and self.wave >= 2:
            self._nodmg_streak += 1
            self._check_achievements(force_key="no_damage_wave")
        else:
            self._nodmg_streak = 0
        if self.wave % BOSS_EVERY_N_WAVES == 0:
            self._boss_wave_nodmg = not self._wave_took_damage

    def _on_gameover(self):
        self.state = "gameover"
        pygame.mouse.set_visible(True)
        if self.snd: self.snd.play("gameover")
        self._go_session_coins = self.session_coins
        self.cfg["coins"] = self.cfg.get("coins", 0) + self.session_coins
        mw = self.cfg.get("max_wave_reached", 0)
        reached = max(self.wave - 1, 1)
        if reached > mw:
            self.cfg["max_wave_reached"] = reached

        import time
        entry = {
            "score": self.score,
            "wave": reached,
            "kills": self.kills,
            "coins": self._go_session_coins,
            "time": round(self.session_time, 1),
            "date": time.strftime("%Y-%m-%d %H:%M"),
        }
        lb = self.cfg.get("leaderboard", [])
        lb.append(entry)
        lb.sort(key=lambda e: e["score"], reverse=True)
        self.cfg["leaderboard"] = lb[:10]
        self._go_lb_rank = next((i for i, e in enumerate(self.cfg["leaderboard"])
                                 if e is entry), -1)

        save_config(self.cfg)
        self.session_coins = 0

    def _trigger_upgrade(self):
        available = [s for s in SKILL_POOL
                     if getattr(self.player, f"skill_{s['key']}", 0) < s["max_level"]]
        if not available:
            self.score += 500
            self.floating_texts.append([self.sw // 2, self.sh // 2 - 40,
                                        "ALL SKILLS MAXED! +500 SCORE", GOLD, 2.0, -0.6])
            self.state = "playing"
            pygame.mouse.set_visible(False)
            return
        lucky_lvl = self.player.skill_lucky
        if lucky_lvl > 0:
            rarity_weights = {"common": 1.0, "rare": 1.0 + lucky_lvl * 0.5,
                              "epic": 1.0 + lucky_lvl * 1.0}
            weighted = []
            for s in available:
                w = rarity_weights.get(s.get("rarity", "common"), 1.0)
                weighted.append((s, w))
            picks = []
            pool = list(weighted)
            for _ in range(min(3, len(pool))):
                total = sum(w for _, w in pool)
                r = random.uniform(0, total)
                acc = 0
                for idx, (s, w) in enumerate(pool):
                    acc += w
                    if r <= acc:
                        picks.append(s)
                        pool.pop(idx)
                        break
            self.upgrade_choices = picks
        else:
            random.shuffle(available)
            self.upgrade_choices = available[:3]
        self.upgrade_selected = None
        self.state = "upgrade"
        self.upgrade_glow = 0.0
        pygame.mouse.set_visible(True)

    def _click_upgrade(self, pos):
        mx, my = pos
        sw, sh = self.sw, self.sh
        cw, ch = 250, 380
        gap    = 20
        total  = cw * 3 + gap * 2
        sx     = sw // 2 - total // 2
        cy_    = sh // 2 - ch // 2 - 20

        def _apply():
            self.player.apply_skill(self.upgrade_choices[self.upgrade_selected]["key"])
            self.upgrade_selected = None
            self.state = "playing"
            pygame.mouse.set_visible(False)

        for i in range(len(self.upgrade_choices)):
            rx = sx + i * (cw + gap)
            r  = pygame.Rect(rx - 4, cy_ - 4, cw + 8, ch + 8)
            if r.collidepoint(mx, my):
                if self.upgrade_selected == i:
                    _apply(); return None
                self.upgrade_selected = i
                return None

        bw, bh = 220, 54
        bx = sw // 2 - bw // 2
        by = cy_ + ch + 18
        if bx <= mx <= bx + bw and by <= my <= by + bh:
            if self.upgrade_selected is not None:
                _apply()
                return None

        rr_w, rr_h = 140, 54
        rr_x = bx + bw + 16
        rr_y = by
        reroll_cost = max(5, int(self.session_coins * 0.05))
        if rr_x <= mx <= rr_x + rr_w and rr_y <= my <= rr_y + rr_h:
            if self.session_coins >= reroll_cost:
                self.session_coins -= reroll_cost
                self._reroll_upgrade()
                return None
        return None

    def _reroll_upgrade(self):
        available = [s for s in SKILL_POOL
                     if getattr(self.player, f"skill_{s['key']}", 0) < s["max_level"]]
        if not available:
            return
        lucky_lvl = self.player.skill_lucky
        if lucky_lvl > 0:
            rarity_weights = {"common": 1.0, "rare": 1.0 + lucky_lvl * 0.5,
                              "epic": 1.0 + lucky_lvl * 1.0}
            weighted = [(s, rarity_weights.get(s.get("rarity", "common"), 1.0)) for s in available]
            picks = []
            pool = list(weighted)
            for _ in range(min(3, len(pool))):
                total = sum(w for _, w in pool)
                r = random.uniform(0, total)
                acc = 0
                for idx, (s, w) in enumerate(pool):
                    acc += w
                    if r <= acc:
                        picks.append(s)
                        pool.pop(idx)
                        break
            self.upgrade_choices = picks
        else:
            random.shuffle(available)
            self.upgrade_choices = available[:3]
        self.upgrade_selected = None

    def _click_pause(self, pos):
        mx, my = pos
        sw, sh = self.sw, self.sh
        bw, bh = 220, 50
        bx = sw // 2 - bw // 2
        if bx <= mx <= bx+bw and sh//2-30 <= my <= sh//2-30+bh:
            self.state = "playing"; pygame.mouse.set_visible(False)
        elif bx <= mx <= bx+bw and sh//2+40 <= my <= sh//2+40+bh:
            return "pause_settings"
        elif bx <= mx <= bx+bw and sh//2+110 <= my <= sh//2+110+bh:
            self._save_and_return_coins()
            self.state = "menu_return"
        return None

    def _click_gameover(self, pos):
        mx, my = pos
        sw, sh = self.sw, self.sh
        bw, bh = 220, 50
        bx = sw // 2 - bw // 2
        if bx <= mx <= bx+bw and sh//2+145 <= my <= sh//2+145+bh:
            self.state = "restart"
        elif bx <= mx <= bx+bw and sh//2+210 <= my <= sh//2+210+bh:
            self._save_and_return_coins()
            self.state = "menu_return"
        return None

    def _save_and_return_coins(self):
        self.cfg["coins"] = self.cfg.get("coins", 0) + self.session_coins
        mw = self.cfg.get("max_wave_reached", 0)
        reached = max(self.wave - 1, 1)
        if reached > mw:
            self.cfg["max_wave_reached"] = reached
        save_config(self.cfg)
        self.session_coins = 0

    def _use_bomb(self):
        if self.bomb_charges <= 0: return
        self.bomb_charges -= 1
        self._bomb_used = True
        self._bombs_used += 1
        cx, cy = self.sw // 2, self.sh // 2
        self.particles.bomb_blast(cx, cy, BOMB_RADIUS)
        if self.snd: self.snd.play("bomb")
        if self.do_shake: self.screen_shake = 0.85
        xp_kills  = []
        coin_kills = []
        for e in list(self.enemies):
            if not e.alive: continue
            dist = math.hypot(e.x - cx, e.y - cy)
            if dist < BOMB_RADIUS:
                dmg_factor = 1.0 - dist / BOMB_RADIUS * 0.5
                if e.boss:
                    killed = e.hit(e.max_hp * 0.4 * dmg_factor)
                else:
                    killed = e.hit(9999)
                if killed:
                    xp_kills.append((e.x, e.y, e.value))
                    coin_kills.append((e.x, e.y, e.coin_value))
                    self._on_kill(e, skip_orbs=True)
        self.xp_orbs.extend(batch_spawn_orbs(xp_kills, XPOrb))
        self.coin_orbs.extend(batch_spawn_orbs(coin_kills, CoinOrb))
        self.enemies = [e for e in self.enemies if e.alive]
        self.boss_present = any(e.boss for e in self.enemies)
        self.floating_texts.append([cx, cy - 40, "BOMB!", ORANGE_GLOW, 1.5, -0.8])

    def _check_achievements(self, force_key=None):
        all_wpn_keys   = {w["key"] for w in WEAPONS}
        unlocked_wpns  = set(self.cfg.get("unlocked_weapons", ["blaster"]))
        total_coins    = self.cfg.get("coins", 0) + self.session_coins
        ship_upgs      = self.cfg.get("ship_upgrades", {})
        weapon_upgs    = self.cfg.get("weapon_upgrades", {})
        skill_tree     = self.cfg.get("skill_tree", {})
        tree_nodes     = sum(1 for v in skill_tree.values() if v > 0)
        tree_full      = all(skill_tree.get(n["key"], 0) >= n["max_level"]
                             for n in SKILL_TREE) if skill_tree else False
        any_ship_max   = any(v >= 5 for v in ship_upgs.values())
        any_wpn_max    = any(v >= 5 for v in weapon_upgs.values())
        all_skills_max = all(
            getattr(self.player, f"skill_{s['key']}", 0) >= s["max_level"]
            for s in SKILL_POOL)
        if self.player.hp > 0 and self.player.hp < self.player.max_hp * 0.10:
            self._close_call = True

        ACHIEV = [
            ("first_blood",     self.kills >= 1,                          "FIRST BLOOD!",            ORANGE),
            ("ten_kills",       self.kills >= 10,                         "10 KILLS",                ORANGE),
            ("fifty_kills",     self.kills >= 50,                         "KILLING SPREE (50)",      RED),
            ("hundred",         self.kills >= 100,                        "CENTURION (100)",         GOLD),
            ("five_hundred",    self.kills >= 500,                        "KRIEGSGOTT (500)",        GOLD),
            ("thousand",        self.kills >= 1000,                       "VERNICHTER (1000)!",      PURPLE),
            ("two_thousand",    self.kills >= 2000,                       "APOKALYPSE (2000)!",      PURPLE),
            ("five_thousand",   self.kills >= 5000,                       "EXTINCTION (5000)!",      (255,50,50)),
            ("ten_thousand",    self.kills >= 10000,                      "GENOZID (10000)!",        (255,50,50)),
            ("wave3",           self.wave >= 3,                           "WELLE 3!",                GREEN),
            ("wave5",           self.wave >= 5,                           "WELLE 5 — REKRUT!",      CYAN),
            ("wave10",          self.wave >= 10,                          "WAVE 10 — VETERAN!",      CYAN),
            ("wave15",          self.wave >= 15,                          "WAVE 15 — KOMMANDANT!",   BLUE),
            ("wave20",          self.wave >= 20,                          "WAVE 20 — ELITE!",        PURPLE),
            ("wave25",          self.wave >= 25,                          "WAVE 25 — ADMIRAL!",      PURPLE),
            ("wave30",          self.wave >= 30,                          "WAVE 30 — LEGENDE!",      GOLD),
            ("wave40",          self.wave >= 40,                          "WAVE 40 — MYTHOS!",       GOLD),
            ("wave50",          self.wave >= 50,                          "WAVE 50 — UNSTERBLICH!",  (255,50,50)),
            ("combo3",          self.combo_mult >= 3,                     "COMBO ×3!",               YELLOW),
            ("combo5",          self.combo_mult >= 5,                     "COMBO ×5 MASTER!",        ORANGE_GLOW),
            ("combo10",         self.combo_mult >= 10,                    "UNAUFHALTBAR ×10!",       ORANGE_GLOW),
            ("streak20",        self.kill_streak >= 20,                   "20er STREAK!",            RED),
            ("streak40",        self.kill_streak >= 40,                   "40er STREAK — MASSAKER!", PURPLE),
            ("collector",       total_coins >= 500,                       "500 COINS GESAMMELT!",    GOLD),
            ("hoarder",         total_coins >= 2000,                      "2000 COINS!",             GOLD),
            ("tycoon",          total_coins >= 5000,                      "5000 COINS — TYCOON!",    GOLD),
            ("mogul",           total_coins >= 10000,                     "10000 COINS — MOGUL!",    (255,215,0)),
            ("coins100_session",self.session_coins >= 100,                "100 COINS IM RUN!",       GOLD),
            ("coins300_session",self.session_coins >= 300,                "300 COINS IM RUN!",       GOLD),
            ("score5k",         self.score >= 5000,                       "5000 PUNKTE!",            CYAN),
            ("score10k",        self.score >= 10000,                      "10K SCORE!",              CYAN),
            ("score25k",        self.score >= 25000,                      "25K SCORE — KÖNIG!",      PURPLE),
            ("score50k",        self.score >= 50000,                      "50K — SCORE-LEGENDE!",    GOLD),
            ("score100k",       self.score >= 100000,                     "100K — GÖTTLICH!",        (255,50,50)),
            ("boss_slayer",     self._boss_killed,                        "BOSS BESIEGT!",           GOLD),
            ("boss5",           self._bosses_killed >= 5,                 "5 BOSSE VERNICHTET!",     GOLD),
            ("boss10",          self._bosses_killed >= 10,                "10 BOSSE — TITAN!",       PURPLE),
            ("boss_no_damage",  self._boss_killed and self._boss_wave_nodmg, "BOSS OHNE SCHADEN!",  (255,50,50)),
            ("level5",          self.level >= 5,                          "LEVEL 5!",                GREEN),
            ("level10",         self.level >= 10,                         "LEVEL 10!",               GREEN),
            ("level15",         self.level >= 15,                         "LEVEL 15 — EXPERTE!",     CYAN),
            ("level20",         self.level >= 20,                         "LEVEL 20 — MEISTER!",     PURPLE),
            ("level30",         self.level >= 30,                         "LEVEL 30 — GROSSMEISTER!",GOLD),
            ("all_skills",      all_skills_max,                           "ALLE SKILLS MAXED!",      (255,50,50)),
            ("survivor2min",    self.session_time >= 120,                 "2 MIN ÜBERLEBT!",         GREEN),
            ("survivor5min",    self.session_time >= 300,                 "5 MIN ÜBERLEBT!",         GREEN),
            ("survivor10min",   self.session_time >= 600,                 "10 MIN — EISERNER WILLE!",CYAN),
            ("survivor15min",   self.session_time >= 900,                 "15 MIN — UNZERSTÖRBAR!",  PURPLE),
            ("close_call",      self._close_call,                         "HAARSCHARF!",             RED),
            ("full_hp_wave",    force_key == "no_damage_wave" and self.player.hp >= self.player.max_hp,
                                                                          "MAKELLOS — VOLLES HP!",   GREEN),
            ("no_damage_wave",  force_key == "no_damage_wave",            "UNBERÜHRT!",              CYAN),
            ("no_damage_3wave", self._nodmg_streak >= 3,                  "3 WELLEN GEISTERHAFT!",   PURPLE),
            ("bomb_user",       self._bomb_used,                          "BOMBE EINGESETZT!",       RED),
            ("bomb10",          self._bombs_used >= 10,                   "10 BOMBEN — SPRENGMEISTER!", RED),
            ("all_weapons",     all_wpn_keys <= unlocked_wpns,            "VOLLES ARSENAL!",         ORANGE),
            ("max_ship",        any_ship_max,                             "SCHIFF VOLL AUFGERÜSTET!",GOLD),
            ("max_weapon",      any_wpn_max,                              "WAFFE MAXED!",            GOLD),
            ("first_skill_tree",tree_nodes >= 1,                          "ERSTER SKILL-KNOTEN!",    GREEN),
            ("tree5",           tree_nodes >= 5,                          "5 KNOTEN — VERZWEIGT!",   CYAN),
            ("tree_full",       tree_full,                                "SKILL-TREE KOMPLETT!",    (255,50,50)),
        ]
        newly_unlocked = []
        for key, cond, label, col in ACHIEV:
            if cond and key not in self._achiev_unlocked:
                self._achiev_unlocked.add(key)
                self._achiev_popup.append([label, col, 3.5])
                if self.snd: self.snd.play("levelup")
                newly_unlocked.append(key)
        if newly_unlocked:
            saved = set(self.cfg.get("achievements", []))
            saved.update(newly_unlocked)
            self.cfg["achievements"] = list(saved)
            save_config(self.cfg)

    def _collect_powerup(self, po):
        po.alive = False
        col = po.color
        self.particles.powerup_collect(po.x, po.y, col)
        if self.snd: self.snd.play("powerup")
        if po.kind == "heal":
            heal_amt = self.player.max_hp * 0.25
            self.player.heal(heal_amt)
            self.floating_texts.append([po.x, po.y - 10, f"+{int(heal_amt)} HP",
                                        GREEN, 1.5, -0.8])
        elif po.kind == "shield":
            self.player.shield = self.player.max_shield
            self.floating_texts.append([po.x, po.y - 10, "SHIELD FULL",
                                        CYAN, 1.5, -0.8])
        elif po.kind == "speed":
            self.player.speed_boost_cd = POWERUP_DEFS["speed"][2]
            self.floating_texts.append([po.x, po.y - 10, "SPEED BOOST!",
                                        YELLOW, 1.5, -0.8])
        elif po.kind == "invuln":
            self.player.invuln_cd_buff = POWERUP_DEFS["invuln"][2]
            self.floating_texts.append([po.x, po.y - 10, "INVINCIBLE!",
                                        WHITE, 1.5, -0.8])

    def draw(self):
        ox, oy = self._shake_offset()
        canvas = self._canvas
        canvas.fill(DARK_BG)

        canvas.blit(self.nebula, (0, 0))
        draw_stars(canvas, self.stars, self.global_time)

        self.particles.draw(canvas)

        for o  in self.xp_orbs:      o.draw(canvas)
        for c  in self.coin_orbs:    c.draw(canvas)
        for po in self.power_orbs:   po.draw(canvas)
        for eb in self.enemy_bullets: eb.draw(canvas)
        for b  in self.bullets:      b.draw(canvas)
        for e  in self.enemies:      e.draw(canvas)

        if self.player.skill_autoaim > 0 or self.player.autoaim_enabled:
            aa_ranges = [120, 220, 360]
            if self.player.skill_autoaim > 0:
                aa_r = aa_ranges[min(self.player.skill_autoaim - 1, 2)]
            else:
                aa_r = aa_ranges[-1]
            px, py = int(self.player.x), int(self.player.y)
            ring = pygame.Surface((aa_r*2+8, aa_r*2+8), pygame.SRCALPHA)
            rc = aa_r + 4
            if self.player.autoaim_locked:
                pulse_a = int(80 + 50 * abs(math.sin(self.global_time * 8)))
                pygame.draw.circle(ring, (0, 220, 255, pulse_a), (rc, rc), aa_r, 2)
                for ang in range(0, 360, 45):
                    rad = math.radians(ang + self.global_time * 60)
                    mx2 = rc + int(math.cos(rad) * aa_r)
                    my2 = rc + int(math.sin(rad) * aa_r)
                    pygame.draw.rect(ring, (0, 255, 255, 200), (mx2-2, my2-2, 4, 4))
            else:
                idle_a = int(50 + 20 * abs(math.sin(self.global_time * 2)))
                seg_count = 24
                for seg in range(seg_count):
                    if seg % 2 == 0:
                        a1 = math.radians(seg * (360 / seg_count) + self.global_time * 20)
                        a2 = math.radians((seg + 1) * (360 / seg_count) + self.global_time * 20)
                        p1 = (rc + int(math.cos(a1) * aa_r), rc + int(math.sin(a1) * aa_r))
                        p2 = (rc + int(math.cos(a2) * aa_r), rc + int(math.sin(a2) * aa_r))
                        pygame.draw.line(ring, (0, 180, 220, idle_a), p1, p2, 1)
                for ang in [0, 90, 180, 270]:
                    rad = math.radians(ang)
                    mx2 = rc + int(math.cos(rad) * aa_r)
                    my2 = rc + int(math.sin(rad) * aa_r)
                    pygame.draw.circle(ring, (0, 220, 255, idle_a + 30), (mx2, my2), 2)
            canvas.blit(ring, (px - rc, py - rc))

        self.player.draw(canvas)

        self._glow_surf.fill((0, 0, 0))
        for b  in self.bullets:       b.draw(self._glow_surf)
        for eb in self.enemy_bullets: eb.draw(self._glow_surf)
        for o  in self.xp_orbs:       o.draw(self._glow_surf)
        for c  in self.coin_orbs:     c.draw(self._glow_surf)
        for po in self.power_orbs:    po.draw(self._glow_surf)
        self.particles.draw(self._glow_surf)
        _total_aura = self.player.skill_aura + self.player._tree_aura
        if _total_aura > 0:
            aura_r  = [85, 110, 145][min(_total_aura - 1, 2)]
            pulse   = abs(math.sin(self.global_time * 2.5)) * 0.4 + 0.3
            aura_s  = pygame.Surface((aura_r * 2 + 4, aura_r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(aura_s, (80, 0, int(140 * pulse)),
                               (aura_r + 2, aura_r + 2), aura_r, 3)
            pygame.draw.circle(aura_s, (50, 0, int(90 * pulse)),
                               (aura_r + 2, aura_r + 2), aura_r - 6, 2)
            self._glow_surf.blit(aura_s,
                (int(self.player.x) - aura_r - 2, int(self.player.y) - aura_r - 2))
        canvas.blit(self._glow_surf, (0, 0), special_flags=pygame.BLEND_ADD)

        bloom = pygame.transform.smoothscale(self._glow_surf, (self.sw // 4, self.sh // 4))
        bloom = pygame.transform.smoothscale(bloom, (self.sw, self.sh))
        canvas.blit(bloom, (0, 0), special_flags=pygame.BLEND_ADD)

        for ft in self.floating_texts:
            a   = min(1.0, ft[4] / 0.35)
            col = tuple(int(c * a) for c in ft[3])
            fts = self.fu.render(ft[2], True, col)
            canvas.blit(fts, fts.get_rect(center=(int(ft[0]), int(ft[1]))))

        canvas.blit(self.vignette, (0, 0))

        hp_pct = self.player.hp / max(1, self.player.max_hp)
        if hp_pct < 0.25 and self.state == "playing":
            danger_a = int(abs(math.sin(self.danger_pulse)) * 45 * (1 - hp_pct * 4))
            if danger_a > 0:
                danger_surf = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
                danger_surf.fill((180, 0, 0, danger_a))
                canvas.blit(danger_surf, (0, 0))

        for e in self.enemies:
            if e.boss:
                self._draw_boss_bar(canvas, e)
                break

        self._draw_hud(canvas)

        self.particles.draw_flash(canvas)

        if self.state == "upgrade":
            self._draw_upgrade(canvas)
        elif self.state == "paused":
            self._draw_pause(canvas)
        elif self.state == "gameover":
            self._draw_gameover(canvas)
        elif self.between_waves:
            self._draw_between_waves(canvas)
        elif self.wave_announce_timer > 0:
            self._draw_wave_announce(canvas)

        if self._achiev_popup:
            for ai, (label, col, timer) in enumerate(self._achiev_popup[:3]):
                alpha = min(1.0, timer / 0.5) if timer < 0.5 else min(1.0, (3.5 - timer) / 0.3 + (timer > 3.0))
                alpha = max(0.0, min(1.0, alpha))
                ay    = self.sh // 4 - 40 + ai * 46
                pill_w = 340; pill_h = 38
                ax = self.sw // 2 - pill_w // 2
                pill = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
                pygame.draw.rect(pill, (10, 8, 4, int(220 * alpha)), (0, 0, pill_w, pill_h),
                                 border_radius=12)
                canvas.blit(pill, (ax, ay))
                oc = tuple(int(c * alpha) for c in col)
                pygame.draw.rect(canvas, oc, (ax, ay, pill_w, pill_h), 2, border_radius=12)
                tcx, tcy = ax + 20, ay + pill_h // 2
                for k in range(5):
                    ang = math.radians(-90 + k * 72)
                    ang2 = math.radians(-90 + k * 72 + 36)
                    px1 = tcx + int(math.cos(ang) * 8 * alpha)
                    py1 = tcy + int(math.sin(ang) * 8 * alpha)
                    px2 = tcx + int(math.cos(ang2) * 4 * alpha)
                    py2 = tcy + int(math.sin(ang2) * 4 * alpha)
                    pygame.draw.line(canvas, oc, (tcx, tcy), (px1, py1), 2)
                    pygame.draw.line(canvas, oc, (tcx, tcy), (px2, py2), 1)
                a_col = tuple(int(c * alpha) for c in col)
                as_ = self.fm.render(label, True, a_col)
                canvas.blit(as_, as_.get_rect(midleft=(ax + 36, ay + pill_h // 2)))

        self.screen.blit(canvas, (ox, oy))

    def _draw_offscreen_indicators(self, surf):
        margin = 28
        sw, sh = self.sw, self.sh
        cx, cy = sw * 0.5, sh * 0.5
        for e in self.enemies:
            if not e.alive: continue
            if margin < e.x < sw - margin and margin < e.y < sh - margin:
                continue
            dx, dy = e.x - cx, e.y - cy
            dist   = math.hypot(dx, dy)
            if dist < 1: continue
            ndx, ndy = dx / dist, dy / dist
            ts = []
            if abs(ndx) > 0.001:
                ts.append(((margin - cx) / ndx) if ndx < 0 else ((sw - margin - cx) / ndx))
            if abs(ndy) > 0.001:
                ts.append(((margin - cy) / ndy) if ndy < 0 else ((sh - margin - cy) / ndy))
            if not ts: continue
            positives = [tv for tv in ts if tv > 0]
            if not positives: continue
            t_edge = min(positives)
            ax = max(margin, min(sw - margin, int(cx + ndx * t_edge)))
            ay = max(margin, min(sh - margin, int(cy + ndy * t_edge)))
            angle = math.atan2(ndy, ndx)
            sz  = 9
            tip = (ax + int(math.cos(angle) * sz),       ay + int(math.sin(angle) * sz))
            lft = (ax + int(math.cos(angle + 2.5) * sz * 0.55),
                   ay + int(math.sin(angle + 2.5) * sz * 0.55))
            rgt = (ax + int(math.cos(angle - 2.5) * sz * 0.55),
                   ay + int(math.sin(angle - 2.5) * sz * 0.55))
            col = RED if e.boss else e.color
            pygame.draw.polygon(surf, col, [tip, lft, rgt])
            pygame.draw.polygon(surf, WHITE, [tip, lft, rgt], 1)

    def _draw_boss_bar(self, surf, boss):
        sw = self.sw
        bw = sw - 80
        bx = 40
        by = self.sh - 38
        has_shield = boss.boss_shield_max > 0
        panel_h = 44 if has_shield else 28
        panel = pygame.Surface((bw + 16, panel_h), pygame.SRCALPHA)
        panel.fill((*PANEL_BG, 220))
        surf.blit(panel, (bx - 8, by - 4 - (16 if has_shield else 0)))
        border_col = PURPLE if getattr(boss, 'is_elite', False) else RED
        pygame.draw.rect(surf, border_col,
                         (bx - 8, by - 4 - (16 if has_shield else 0), bw + 16, panel_h), 1)

        if has_shield:
            shield_r = boss.boss_shield / max(1, boss.boss_shield_max)
            shield_col = (0, int(180 * shield_r + 40), 255)
            draw_bar(surf, bx, by - 12, bw, 8, boss.boss_shield, boss.boss_shield_max,
                     shield_col, DARK_BG, border=True, glow=True)

        hp_r = boss.hp / max(1, boss.max_hp)
        bar_col = (min(255, int(220*(1-hp_r))), min(255, int(220*hp_r*2)), 0) if hp_r > 0.5 else \
                  (220, min(255, int(220*(hp_r*2))), 0)
        draw_bar(surf, bx, by + 4, bw, 14, boss.hp, boss.max_hp, bar_col,
                 DARK_BG, border=True, glow=True)

        pulse = abs(math.sin(self.global_time * 4))
        boss_col = tuple(int(c * (0.7 + 0.3 * pulse)) for c in border_col)
        elite_tag = "ELITE BOSS" if getattr(boss, 'is_elite', False) else "BOSS"
        shield_txt = f"  [{int(boss.boss_shield)}]" if boss.boss_shield > 0 else ""
        bl = self.fu.render(
            f"{elite_tag}  {int(boss.hp)}/{int(boss.max_hp)}{shield_txt}", True, boss_col)
        surf.blit(bl, bl.get_rect(center=(sw // 2, by + 11)))

    def _draw_hud(self, surf):
        p      = self.player
        sw, sh = self.sw, self.sh

        top_h = 36
        top_panel = pygame.Surface((sw, top_h), pygame.SRCALPHA)
        top_panel.fill((*PANEL_BG, 215))
        surf.blit(top_panel, (0, 0))
        pygame.draw.line(surf, ORANGE_DARK, (0, top_h), (sw, top_h), 1)

        total_dur = wave_duration(self.wave)
        timer_s   = int(self.wave_timer)
        pct       = self.wave_timer / max(1, total_dur)
        bar_col   = ORANGE if pct > 0.35 else (YELLOW if pct > 0.15 else RED)

        bar_x = 180
        bar_w = sw - 380
        br_t = 8
        pygame.draw.rect(surf, (5, 5, 8), (bar_x, 9, bar_w, 18), border_radius=br_t)
        if int(bar_w * pct) > 0:
            pygame.draw.rect(surf, bar_col, (bar_x, 9, int(bar_w * pct), 18), border_radius=br_t)
            bright = tuple(min(255, c + 60) for c in bar_col)
            pygame.draw.rect(surf, bright, (bar_x, 9, int(bar_w * pct), 6), border_radius=br_t)
        pygame.draw.rect(surf, GRAY_MID, (bar_x, 9, bar_w, 18), 1, border_radius=br_t)
        for tick in [0.25, 0.5, 0.75]:
            tx = bar_x + int(bar_w * tick)
            pygame.draw.line(surf, GRAY_MID, (tx, 10), (tx, 26), 1)

        wl = self.fm.render(f"Wave {self.wave}", True, ORANGE)
        surf.blit(wl, (bar_x - wl.get_width() - 10, 9))

        timer_txt = f"{timer_s//60:02d}:{timer_s%60:02d}" if timer_s >= 60 else f"00:{timer_s:02d}"
        t_col = bar_col
        if pct < 0.15:
            flash_t = abs(math.sin(self.global_time * 6))
            t_col   = (int(220 * flash_t + 35), 0, 0) if pct < 0.08 else RED
        tr = self.fm.render(timer_txt, True, t_col)
        surf.blit(tr, (bar_x + bar_w + 10, 9))

        lp_x, lp_y, lp_w, lp_h = 8, top_h + 6, 220, 96
        lp = pygame.Surface((lp_w, lp_h), pygame.SRCALPHA)
        pygame.draw.rect(lp, (*PANEL_DARK, 215), (0, 0, lp_w, lp_h), border_radius=10)
        surf.blit(lp, (lp_x, lp_y))
        pygame.draw.rect(surf, ORANGE_DARK, (lp_x, lp_y, lp_w, lp_h), 1, border_radius=10)

        hp_pct = p.hp / max(1, p.max_hp)
        hp_col = GREEN if hp_pct > 0.5 else (YELLOW if hp_pct > 0.25 else RED)
        draw_bar(surf, lp_x+38, lp_y+8,  lp_w-46, 14, p.hp, p.max_hp, hp_col, glow=True)
        hl = self.fu.render("HP", True, hp_col)
        surf.blit(hl, (lp_x+6, lp_y+9))
        hv = self.fu.render(f"{int(p.hp)}/{int(p.max_hp)}", True, GRAY_LIGHT)
        surf.blit(hv, (lp_x+38, lp_y+23))

        draw_bar(surf, lp_x+38, lp_y+37, lp_w-46, 12, p.shield, max(1, p.max_shield),
                 CYAN, glow=True)
        sl = self.fu.render("SH", True, CYAN)
        surf.blit(sl, (lp_x+6, lp_y+38))
        sv = self.fu.render(f"{int(p.shield)}/{int(p.max_shield)}", True, GRAY_LIGHT)
        surf.blit(sv, (lp_x+38, lp_y+50))

        draw_bar(surf, lp_x+38, lp_y+64, lp_w-46, 10, self.xp, self.xp_needed, YELLOW)
        xl = self.fu.render("XP", True, YELLOW)
        surf.blit(xl, (lp_x+6, lp_y+65))
        lv_col = ORANGE_GLOW if self.xp / max(1, self.xp_needed) > 0.8 else ORANGE
        lv = self.fu.render(f"Lv {self.level}", True, lv_col)
        surf.blit(lv, (lp_x+38, lp_y+75))
        xv = self.fu.render(f"{self.xp}/{self.xp_needed}", True, GRAY_MID)
        surf.blit(xv, (lp_x+88, lp_y+75))

        remaining   = len(self.enemies)
        total_coins = self.cfg.get("coins", 0) + self.session_coins
        score_col   = ORANGE_GLOW if self.score_flash > 0 else GRAY_LIGHT
        kill_col    = WHITE if self.kill_flash > 0 else GRAY_LIGHT
        enemy_col   = RED if remaining > 0 else GREEN

        right_stats = [
            (f"Score  {self.score}",              score_col),
            (f"{t('kills')}   {self.kills}",      kill_col),
            (f"Coins  {total_coins}",             GOLD),
            (f"{t('enemies')} {remaining}",       enemy_col),
        ]
        line_h = 18
        rp_w   = 162
        rp_h   = len(right_stats) * line_h + 10
        rp_x   = sw - rp_w - 8
        rp_y   = top_h + 6
        rp_s   = pygame.Surface((rp_w, rp_h), pygame.SRCALPHA)
        pygame.draw.rect(rp_s, (*PANEL_DARK, 215), (0, 0, rp_w, rp_h), border_radius=10)
        surf.blit(rp_s, (rp_x, rp_y))
        pygame.draw.rect(surf, ORANGE_DARK, (rp_x, rp_y, rp_w, rp_h), 1, border_radius=10)

        for i, (txt, col) in enumerate(right_stats):
            rs = self.fu.render(txt, True, col)
            surf.blit(rs, (rp_x + 8, rp_y + 5 + i * line_h))

        active = [(s["key"], s["color"]) for s in SKILL_POOL
                  if getattr(p, f"skill_{s['key']}", 0) > 0]
        if active:
            sk_y = lp_y + lp_h + 5
            for si, (sk_key, sk_col) in enumerate(active[:8]):
                sx_  = lp_x + si * 28
                lvl  = getattr(p, f"skill_{sk_key}", 0)
                bg_  = pygame.Surface((24, 24), pygame.SRCALPHA)
                pygame.draw.rect(bg_, (*PANEL_DARK, 215), (0, 0, 24, 24), border_radius=6)
                surf.blit(bg_, (sx_, sk_y))
                pygame.draw.rect(surf, sk_col, (sx_, sk_y, 24, 24), 1, border_radius=6)
                draw_skill_icon(surf, sx_ + 12, sk_y + 12, 20, sk_key, sk_col)
                lp_s = self.fu.render(str(lvl), True, WHITE)
                surf.blit(lp_s, (sx_ + 14, sk_y + 13))

        bomb_y = sh - 44
        bomb_x = 12
        bomb_label = self.fu.render("[SPACE] BOMB", True, GRAY_MID)
        surf.blit(bomb_label, (bomb_x, bomb_y - 14))
        for bi in range(BOMB_MAX_CHARGES):
            bx2  = bomb_x + bi * 28
            filled = bi < self.bomb_charges
            bc2  = ORANGE_GLOW if filled else GRAY_DARK
            bg2  = pygame.Surface((22, 22), pygame.SRCALPHA)
            pygame.draw.rect(bg2, (*PANEL_DARK, 215), (0, 0, 22, 22), border_radius=6)
            surf.blit(bg2, (bx2, bomb_y))
            pygame.draw.rect(surf, bc2, (bx2, bomb_y, 22, 22), 2 if filled else 1, border_radius=6)
            if filled:
                dc = (bx2 + 11, bomb_y + 11)
                pygame.draw.polygon(surf, ORANGE_GLOW, [
                    (dc[0], dc[1]-5), (dc[0]+5, dc[1]),
                    (dc[0], dc[1]+5), (dc[0]-5, dc[1])])

        if self.combo_mult > 1 or self.combo_display > 0:
            a   = min(1.0, self.combo_display / 0.6) if self.combo_display < 0.6 else 1.0
            cmb = f"×{self.combo_mult} COMBO"
            pulse_t = abs(math.sin(self.global_time * 6))
            c_col   = tuple(int(c * a * (0.7 + 0.3 * pulse_t)) for c in ORANGE_GLOW)
            g_col   = tuple(int(c * a) for c in ORANGE_DARK)
            draw_glow_text(surf, cmb, self.fm, c_col, g_col,
                           sw // 2, top_h + 58, True, glow_radius=3)
            streak_w = 180
            streak_x = sw // 2 - streak_w // 2
            streak_y = top_h + 74
            if self.combo_mult >= COMBO_MULTIPLIERS[-1]:
                frac = 1.0
            else:
                tier   = COMBO_MULTIPLIERS.index(self.combo_mult) if self.combo_mult in COMBO_MULTIPLIERS else 0
                t_next = COMBO_THRESHOLDS[tier]     if tier < len(COMBO_THRESHOLDS) else COMBO_THRESHOLDS[-1]
                t_prev = COMBO_THRESHOLDS[tier - 1] if tier > 0                     else 0
                frac   = (self.kill_streak - t_prev) / max(1, t_next - t_prev)
            pygame.draw.rect(surf, GRAY_DARK, (streak_x, streak_y, streak_w, 6), border_radius=3)
            if int(streak_w * min(1.0, frac)) > 0:
                pygame.draw.rect(surf, ORANGE_GLOW,
                                 (streak_x, streak_y, int(streak_w * min(1.0, frac)), 6),
                                 border_radius=3)
            pygame.draw.rect(surf, GRAY_MID, (streak_x, streak_y, streak_w, 6), 1, border_radius=3)

        buff_y = top_h + 6
        buff_x = sw // 2 + 240
        if p.speed_boost_cd > 0:
            bs3 = self.fu.render(f"SPEED ×2  {p.speed_boost_cd:.1f}s", True, YELLOW)
            surf.blit(bs3, (buff_x, buff_y)); buff_y += 16
        if p.invuln_cd_buff > 0:
            iv3 = self.fu.render(f"INVULN  {p.invuln_cd_buff:.1f}s", True, WHITE)
            surf.blit(iv3, (buff_x, buff_y)); buff_y += 16
        if p.skill_dash > 0:
            dash_txt = ("DASH READY" if p.dash_cd <= 0
                        else f"DASH  {p.dash_cd:.1f}s")
            dc = CYAN if p.dash_cd <= 0 else GRAY_MID
            ds3 = self.fu.render(dash_txt, True, dc)
            surf.blit(ds3, (buff_x, buff_y)); buff_y += 16
        if p.skill_overcharge > 0:
            if p._overcharge_shots > 0:
                oc3 = self.fu.render(f"OVERCHARGE ×{p._overcharge_shots}", True, ORANGE_GLOW)
                surf.blit(oc3, (buff_x, buff_y)); buff_y += 16
            elif p._overcharge_cd > 0:
                oc3 = self.fu.render(f"OVERCHARGE  {p._overcharge_cd:.1f}s", True, GRAY_MID)
                surf.blit(oc3, (buff_x, buff_y)); buff_y += 16

        if self.wave >= DANGER_START_WAVE and self.danger_level > 0.15:
            d_pct = self.danger_level / DANGER_MAX
            d_pulse = abs(math.sin(self.global_time * 4))
            d_alpha = 0.5 + 0.5 * d_pct
            d_col = (int(220 * d_alpha * (0.7 + 0.3 * d_pulse)),
                     int(40 * (1 - d_pct) * d_alpha), 0)
            d_label = f"DANGER {d_pct*100:.0f}%"
            dt_s = self.fu.render(d_label, True, d_col)
            surf.blit(dt_s, (sw - dt_s.get_width() - 12, sh - 32))

        if self.wave_modifier and self.wave_alive:
            mod = WAVE_MODIFIERS[self.wave_modifier]
            mod_col = mod["color"]
            mod_txt = self.fu.render(mod["label"], True, mod_col)
            mx2 = sw // 2 - mod_txt.get_width() // 2
            my2 = 42
            bg_mod = pygame.Surface((mod_txt.get_width() + 12, 20), pygame.SRCALPHA)
            pygame.draw.rect(bg_mod, (*PANEL_DARK, 200), (0, 0, bg_mod.get_width(), 20),
                             border_radius=6)
            surf.blit(bg_mod, (mx2 - 6, my2 - 2))
            pygame.draw.rect(surf, mod_col, (mx2 - 6, my2 - 2,
                             bg_mod.get_width(), 20), 1, border_radius=6)
            surf.blit(mod_txt, (mx2, my2))

        tier_key, tier_info = get_difficulty_tier(self.wave)
        if tier_key != "easy":
            tier_s = self.fu.render(tier_info["label"], True, tier_info["color"])
            surf.blit(tier_s, (sw - tier_s.get_width() - 12, sh - 48))

        if self.state == "playing":
            self._draw_offscreen_indicators(surf)

        mx, my = self.mouse_pos
        cs = 11
        pygame.draw.line(surf, WHITE,  (mx - cs, my), (mx + cs, my), 1)
        pygame.draw.line(surf, WHITE,  (mx, my - cs), (mx, my + cs), 1)
        pygame.draw.line(surf, ORANGE, (mx - cs + 4, my), (mx + cs - 4, my), 1)
        pygame.draw.line(surf, ORANGE, (mx, my - cs + 4), (mx, my + cs - 4), 1)
        pygame.draw.rect(surf, ORANGE_GLOW, (mx - 2, my - 2, 4, 4))
        pygame.draw.rect(surf, WHITE,       (mx - 1, my - 1, 2, 2))

    def _draw_wave_announce(self, surf):
        t_left = self.wave_announce_timer
        if t_left > 2.0:
            alpha = min(1.0, (2.5 - t_left) / 0.5)
        else:
            alpha = min(1.0, t_left / 0.5)
        if alpha < 0.01: return

        sw, sh = self.sw, self.sh
        slide  = int((1.0 - alpha) * 35) if t_left > 2.0 else 0
        cy     = sh // 2 - 30 - slide

        pill_w, pill_h = 380, 68
        px = sw // 2 - pill_w // 2
        py = cy - pill_h // 2
        pill = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
        pygame.draw.rect(pill, (10, 8, 4, int(210 * alpha)), (0, 0, pill_w, pill_h),
                         border_radius=34)
        surf.blit(pill, (px, py))
        oc = tuple(int(c * alpha) for c in ORANGE_DARK)
        pygame.draw.rect(surf, oc, (px, py, pill_w, pill_h), 2, border_radius=34)
        ac = tuple(int(c * alpha) for c in ORANGE_GLOW)
        pygame.draw.rect(surf, ac, (px + 3, py + 3, pill_w - 6, 3), border_radius=6)

        txt   = f"— WAVE {self.wave_announce_wave} —"
        pulse = abs(math.sin(self.global_time * 6)) * 0.3
        col   = tuple(int(c * alpha * (0.7 + 0.3 * pulse)) for c in ORANGE)
        gc    = (int(80 * alpha), int(30 * alpha), 0)
        draw_glow_text(surf, txt, self.fn, col, gc, sw // 2, cy, True, glow_radius=4)

        if self.wave_modifier:
            mod = WAVE_MODIFIERS[self.wave_modifier]
            mod_c = tuple(int(c * alpha) for c in mod["color"])
            mod_s = self.fs.render(mod["label"], True, mod_c)
            surf.blit(mod_s, mod_s.get_rect(center=(sw // 2, cy + 26)))
        else:
            sub_col = tuple(int(c * alpha) for c in GRAY_LIGHT)
            sub = self.fs.render(t("good_luck"), True, sub_col)
            surf.blit(sub, sub.get_rect(center=(sw // 2, cy + 26)))

    def _draw_between_waves(self, surf):
        sw, sh = self.sw, self.sh
        cw  = min(420, sw - 60)
        ch  = 110
        cx  = sw // 2 - cw // 2
        cy  = sh // 2 - ch // 2 - 30

        card_s = pygame.Surface((cw, ch), pygame.SRCALPHA)
        pygame.draw.rect(card_s, (*PANEL_BG, 230), (0, 0, cw, ch), border_radius=16)
        surf.blit(card_s, (cx, cy))
        pygame.draw.rect(surf, ORANGE, (cx, cy, cw, ch), 2, border_radius=16)
        pygame.draw.rect(surf, ORANGE_GLOW, (cx + 3, cy + 3, cw - 6, 3), border_radius=6)

        msg = f"{t('wave')} {self.wave}  —  {t('survived')}!"
        draw_glow_text(surf, msg, self.fn, ORANGE_GLOW, ORANGE_DARK,
                       sw // 2, cy + 32, True, glow_radius=3)

        kills_col = WHITE if self._last_wave_kills > 0 else GRAY_MID
        ks = self.fm.render(f"{self._last_wave_kills}  {t('kills')}", True, kills_col)
        surf.blit(ks, ks.get_rect(center=(sw // 2, cy + 70)))

        pct  = 1.0 - self.between_timer / max(0.1, between_wave_delay(self.wave))
        cd_w = min(300, cw - 60)
        cd_x = sw // 2 - cd_w // 2
        cd_y = cy + ch + 16
        pygame.draw.rect(surf, GRAY_DARK, (cd_x, cd_y, cd_w, 10), border_radius=5)
        if int(cd_w * pct) > 0:
            pygame.draw.rect(surf, CYAN, (cd_x, cd_y, int(cd_w * pct), 10), border_radius=5)
        pygame.draw.rect(surf, GRAY_MID, (cd_x, cd_y, cd_w, 10), 1, border_radius=5)
        sec_txt = f"{t('next_wave_in')}  {max(0, self.between_timer):.1f}s"
        ns = self.fs.render(sec_txt, True, GRAY_LIGHT)
        surf.blit(ns, ns.get_rect(center=(sw // 2, cd_y + 20)))

    def _draw_upgrade(self, surf):
        overlay = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        surf.blit(overlay, (0, 0))

        sw, sh = self.sw, self.sh
        draw_glow_text(surf, t("choose_upgrade"), self.fn, ORANGE, ORANGE_DARK,
                       sw//2, sh//2 - 220, True, glow_radius=4)

        cw, ch = 250, 380
        gap    = 20
        total  = cw * 3 + gap * 2
        sx     = sw // 2 - total // 2
        cy_    = sh // 2 - ch // 2 - 20
        mx, my = pygame.mouse.get_pos()
        glow_t = abs(math.sin(self.upgrade_glow))

        for i, skill in enumerate(self.upgrade_choices):
            rx       = sx + i * (cw + gap)
            r        = pygame.Rect(rx, cy_, cw, ch)
            hover    = r.collidepoint(mx, my)
            selected = (i == self.upgrade_selected)
            rc       = RARITY_COLORS[skill["rarity"]]

            if hover or selected:
                glow_s = pygame.Surface((cw + 20, ch + 20), pygame.SRCALPHA)
                ga     = int(60 + 40 * glow_t) if selected else 35
                glow_s.fill((*rc, ga))
                surf.blit(glow_s, (rx - 10, cy_ - 10))

            panel = pygame.Surface((cw, ch), pygame.SRCALPHA)
            pygame.draw.rect(panel, (*PANEL_BG, 240), (0, 0, cw, ch), border_radius=14)
            surf.blit(panel, (rx, cy_))

            border = ORANGE_GLOW if selected else (ORANGE if hover else rc)
            bw_    = 3 if selected else 2
            if selected:
                pulse_c = tuple(min(255, c + int(80 * glow_t)) for c in rc)
                pygame.draw.rect(surf, pulse_c, r, bw_, border_radius=14)
            else:
                pygame.draw.rect(surf, border, r, bw_, border_radius=14)

            rb = self.fu.render(skill["rarity"].upper(), True, rc)
            surf.blit(rb, rb.get_rect(center=(rx+cw//2, cy_+16)))

            icon_size = 64
            draw_skill_icon(surf, rx+cw//2, cy_+65, icon_size, skill["key"], skill["color"])
            pygame.draw.rect(surf, GRAY_DARK, (rx+cw//2-34, cy_+33, 68, 68), 1)

            ns = self.fm.render(t(skill["name_key"]), True, WHITE)
            surf.blit(ns, ns.get_rect(center=(rx+cw//2, cy_+118)))

            pl   = getattr(self.player, f"skill_{skill['key']}", 0)
            ml   = skill["max_level"]
            dw_  = 22; dgap = 4
            dtot = ml * (dw_ + dgap) - dgap
            dot_x = rx + cw//2 - dtot//2
            for li in range(ml):
                col_ = ORANGE if li < pl else GRAY_DARK
                pygame.draw.rect(surf, col_, (dot_x + li*(dw_+dgap), cy_+142, dw_, 10))
            ls = self.fu.render(f"Lv {pl}/{ml}", True, GRAY_LIGHT)
            surf.blit(ls, ls.get_rect(center=(rx+cw//2, cy_+165)))

            desc_key = f"skilldesc_{skill['key']}"
            desc_txt = t(desc_key)
            if desc_txt == desc_key:
                desc_txt = ""
            pygame.draw.line(surf, GRAY_DARK, (rx + 14, cy_ + 182), (rx + cw - 14, cy_ + 182), 1)
            if desc_txt:
                words = desc_txt.split()
                lines = []
                cur = ""
                for w in words:
                    test = (cur + " " + w).strip()
                    if self.fu.size(test)[0] <= cw - 28:
                        cur = test
                    else:
                        if cur: lines.append(cur)
                        cur = w
                if cur: lines.append(cur)
                for li_idx, line in enumerate(lines[:3]):
                    ds = self.fu.render(line, True, GRAY_LIGHT)
                    surf.blit(ds, ds.get_rect(center=(rx + cw//2, cy_ + 198 + li_idx * 18)))

            if skill["key"] == "aura":
                preview_y = cy_ + 260
                aura_lvl = pl + 1
                aura_r = [60, 90, 130][min(aura_lvl - 1, 2)]
                preview_r = min(aura_r // 2, 38)
                pulse_a = 0.5 + 0.5 * math.sin(self.upgrade_glow * 3)
                ring_a = int(40 + 35 * pulse_a)
                ring_s = pygame.Surface((preview_r*2+20, preview_r*2+20), pygame.SRCALPHA)
                rc2 = preview_r + 10
                pygame.draw.circle(ring_s, (*PURPLE, ring_a), (rc2, rc2), preview_r, 2)
                pygame.draw.circle(ring_s, (*PURPLE, int(ring_a * 0.4)), (rc2, rc2), preview_r - 4)
                pygame.draw.circle(ring_s, ORANGE, (rc2, rc2), 4)
                pygame.draw.circle(ring_s, WHITE, (rc2, rc2), 2)
                surf.blit(ring_s, (rx + cw//2 - rc2, preview_y - rc2))
                aura_lbl = self.fu.render(f"Radius: {aura_r}px", True, PURPLE)
                surf.blit(aura_lbl, aura_lbl.get_rect(center=(rx + cw//2, preview_y + preview_r + 14)))

            elif skill["key"] in ("explosion", "chain", "homing", "ricochet"):
                preview_y = cy_ + 270
                preview_col = skill["color"]
                if skill["key"] == "explosion":
                    er = 18
                    es = pygame.Surface((er*2+8, er*2+8), pygame.SRCALPHA)
                    ec = er + 4
                    for ri in range(er, 4, -4):
                        a = int(80 * (ri / er))
                        pygame.draw.circle(es, (*RED, a), (ec, ec), ri)
                    pygame.draw.circle(es, (*ORANGE_GLOW, 120), (ec, ec), 6)
                    surf.blit(es, (rx + cw//2 - ec, preview_y - ec))
                elif skill["key"] == "chain":
                    pts = [(rx+cw//2-20, preview_y-8), (rx+cw//2-6, preview_y+2),
                           (rx+cw//2+2, preview_y-4), (rx+cw//2+20, preview_y+8)]
                    pygame.draw.lines(surf, CYAN, False, pts, 2)
                    for p in [pts[0], pts[-1]]:
                        pygame.draw.circle(surf, WHITE, p, 3)
                elif skill["key"] == "homing":
                    arc_r = pygame.Rect(rx+cw//2-18, preview_y-12, 36, 24)
                    pygame.draw.arc(surf, RED, arc_r, 0.3, math.pi + 0.3, 2)
                    pygame.draw.polygon(surf, RED, [
                        (rx+cw//2+16, preview_y-2), (rx+cw//2+10, preview_y-8),
                        (rx+cw//2+10, preview_y+4)])
                elif skill["key"] == "ricochet":
                    pts = [(rx+cw//2-22, preview_y+10), (rx+cw//2-4, preview_y-10),
                           (rx+cw//2+4, preview_y+6), (rx+cw//2+22, preview_y-8)]
                    pygame.draw.lines(surf, YELLOW, False, pts, 2)
                    for p in pts[1:-1]:
                        pygame.draw.circle(surf, WHITE, p, 2)

            if selected:
                hl = pygame.Surface((cw - 4, ch - 4), pygame.SRCALPHA)
                pygame.draw.rect(hl, (255, 120, 0, 20), (0, 0, cw - 4, ch - 4), border_radius=12)
                surf.blit(hl, (rx + 2, cy_ + 2))

        bw_, bh_ = 220, 54
        bx_ = sw // 2 - bw_ // 2
        by_ = cy_ + ch + 18
        can = self.upgrade_selected is not None
        bc  = ORANGE_GLOW if can else GRAY_DARK
        bg_ = ORANGE_DARK if can else PANEL_BG
        if can:
            pulse_a = int(20 + 15 * glow_t)
            pb = pygame.Surface((bw_+8, bh_+8), pygame.SRCALPHA)
            pb.fill((*ORANGE, pulse_a))
            surf.blit(pb, (bx_-4, by_-4))
        pygame.draw.rect(surf, bg_, (bx_, by_, bw_, bh_), border_radius=9)
        pygame.draw.rect(surf, bc,  (bx_, by_, bw_, bh_), 2, border_radius=9)
        hint_txt = "Bestätigen  (oder Karte 2× klicken)" if can else "← Karte anklicken"
        cs  = self.fu.render(hint_txt, True, WHITE if can else GRAY_MID)
        surf.blit(cs, cs.get_rect(center=(bx_+bw_//2, by_+bh_//2)))

        rr_w, rr_h = 140, 54
        rr_x = bx_ + bw_ + 16
        rr_y = by_
        reroll_cost = max(5, int(self.session_coins * 0.05))
        can_rr = self.session_coins >= reroll_cost
        rr_bg = (80, 60, 20) if can_rr else PANEL_BG
        rr_bc = GOLD if can_rr else GRAY_DARK
        pygame.draw.rect(surf, rr_bg, (rr_x, rr_y, rr_w, rr_h), border_radius=9)
        pygame.draw.rect(surf, rr_bc, (rr_x, rr_y, rr_w, rr_h), 2, border_radius=9)
        rr_txt = self.fu.render(f"Reroll", True, WHITE if can_rr else GRAY_MID)
        rr_cost_txt = self.fu.render(f"{reroll_cost} Coins", True, GOLD if can_rr else GRAY_MID)
        surf.blit(rr_txt, rr_txt.get_rect(center=(rr_x + rr_w // 2, rr_y + 18)))
        surf.blit(rr_cost_txt, rr_cost_txt.get_rect(center=(rr_x + rr_w // 2, rr_y + 38)))

        coins_txt = self.fu.render(f"Coins: {self.session_coins}", True, GOLD)
        surf.blit(coins_txt, coins_txt.get_rect(center=(sw // 2, by_ + bh_ + 14)))

    def _draw_pause(self, surf):
        overlay = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 165))
        surf.blit(overlay, (0, 0))
        sw, sh = self.sw, self.sh
        draw_glow_text(surf, t("paused"), self.fn, ORANGE, ORANGE_DARK,
                       sw//2, sh//2-110, True, glow_radius=4)
        mx, my = pygame.mouse.get_pos()
        bw, bh = 220, 50
        bx = sw // 2 - bw // 2
        for label, by_ in [(t("resume"),    sh//2-30),
                           (t("settings"),  sh//2+40),
                           (t("main_menu"), sh//2+110)]:
            r_ = pygame.Rect(bx, by_, bw, bh)
            draw_button(surf, r_, label, self.fm, r_.collidepoint(mx, my))

    def _draw_gameover(self, surf):
        overlay = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 185))
        surf.blit(overlay, (0, 0))
        sw, sh = self.sw, self.sh

        pulse = abs(math.sin(self.global_time * 2.5))
        title_col = (int(180 + 40 * pulse), int(30 * pulse), 0)
        draw_glow_text(surf, t("game_over"), self.fn, title_col, (80, 0, 0),
                       sw//2, sh//2-150, True, glow_radius=5)

        stars_earned = (1 if self.wave >= 5  else 0) + \
                       (1 if self.wave >= 10 else 0) + \
                       (1 if self.wave >= 20 else 0)
        star_x = sw//2 - 30
        for si in range(3):
            s_col = YELLOW if si < stars_earned else GRAY_DARK
            sx_ = star_x + si * 30
            sy_ = sh//2 - 105
            for pt_angle in range(0, 360, 72):
                a1 = math.radians(pt_angle - 90)
                a2 = math.radians(pt_angle + 36 - 90)
                p1 = (sx_ + int(12 * math.cos(a1)), sy_ + int(12 * math.sin(a1)))
                p2 = (sx_ + int(5  * math.cos(a2)), sy_ + int(5  * math.sin(a2)))
                pygame.draw.line(surf, s_col, (sx_, sy_), p1, 2)
                pygame.draw.line(surf, s_col, (sx_, sy_), p2, 1)

        card_w, card_h = 340, 210
        card_x = sw//2 - card_w//2
        card_y = sh//2 - 80
        card_s = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        pygame.draw.rect(card_s, (*PANEL_BG, 240), (0, 0, card_w, card_h), border_radius=14)
        surf.blit(card_s, (card_x, card_y))
        pygame.draw.rect(surf, ORANGE_DARK, (card_x, card_y, card_w, card_h), 2, border_radius=14)
        pygame.draw.rect(surf, ORANGE_DARK, (card_x+3, card_y+3, card_w-6, 3), border_radius=6)

        total_coins = self.cfg.get("coins", 0)
        lines = [
            (f"{t('score')}:   {self.score}",                      ORANGE),
            (f"{t('wave')}:    {self.wave}",                       ORANGE),
            (f"{t('level')}:   {self.level}",                      CYAN),
            (f"{t('kills')}:   {self.kills}",                      GRAY_LIGHT),
            (f"Coins:   +{getattr(self, '_go_session_coins', 0)}", GOLD),
            (f"Total:   {total_coins}",                            GOLD),
        ]
        for i, (line, col) in enumerate(lines):
            ts = self.fm.render(line, True, col)
            surf.blit(ts, ts.get_rect(center=(sw//2, card_y + 22 + i * 31)))

        lb = self.cfg.get("leaderboard", [])
        if lb:
            lb_x = sw // 2 + card_w // 2 + 24
            lb_y = card_y
            lb_w = 240
            lb_title = self.fm.render("LEADERBOARD", True, GOLD)
            surf.blit(lb_title, lb_title.get_rect(center=(lb_x + lb_w // 2, lb_y - 12)))
            for ri, entry in enumerate(lb[:8]):
                ey = lb_y + 10 + ri * 24
                is_current = (ri == getattr(self, '_go_lb_rank', -1))
                row_col = ORANGE_GLOW if is_current else GRAY_LIGHT
                rank_s = self.fu.render(f"#{ri+1}", True, GOLD if ri < 3 else GRAY_MID)
                surf.blit(rank_s, (lb_x, ey))
                score_s = self.fu.render(f"{entry['score']}", True, row_col)
                surf.blit(score_s, (lb_x + 32, ey))
                wave_s = self.fu.render(f"W{entry.get('wave', '?')}", True, CYAN)
                surf.blit(wave_s, (lb_x + 120, ey))
                kills_s = self.fu.render(f"{entry.get('kills', 0)}K", True, GRAY_MID)
                surf.blit(kills_s, (lb_x + 170, ey))

        mx, my = pygame.mouse.get_pos()
        bw, bh = 220, 50
        bx = sw//2 - bw//2
        for label, by_ in [(t("restart"),   sh//2+145),
                           (t("main_menu"), sh//2+210)]:
            r_ = pygame.Rect(bx, by_, bw, bh)
            draw_button(surf, r_, label, self.fm, r_.collidepoint(mx, my))

    def _shake_offset(self):
        if self.screen_shake > 0 and self.do_shake:
            amp = int(self.screen_shake * 12)
            return random.randint(-amp, amp), random.randint(-amp, amp)
        return 0, 0
