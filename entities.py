import pygame, math, random
from constants import *
from draw_utils import draw_pixel_ship, draw_pixel_enemy, draw_bar

class Bullet:
    def __init__(self, x, y, dx, dy, damage, speed, color, pierce=0,
                 explosive=False, weapon_key="blaster"):
        self.x, self.y    = float(x), float(y)
        self.dx, self.dy  = dx, dy
        self.damage       = damage
        self.speed        = speed
        self.color        = color
        self.pierce       = pierce
        self.explosive    = explosive
        self.weapon_key   = weapon_key
        self.alive        = True
        self.hits         = 0
        self.age          = 0.0
        self.homing       = 0
        self.bounces      = 0

    def update(self, dt, sw, sh):
        self.age += dt
        self.x  += self.dx * self.speed * dt * 60
        self.y  += self.dy * self.speed * dt * 60
        if self.bounces > 0:
            bounced = False
            if self.x < 5:
                self.x = 5; self.dx = abs(self.dx); bounced = True
            elif self.x > sw - 5:
                self.x = sw - 5; self.dx = -abs(self.dx); bounced = True
            if self.y < 5:
                self.y = 5; self.dy = abs(self.dy); bounced = True
            elif self.y > sh - 5:
                self.y = sh - 5; self.dy = -abs(self.dy); bounced = True
            if bounced:
                self.bounces -= 1
        elif self.x < -30 or self.x > sw + 30 or self.y < -30 or self.y > sh + 30:
            self.alive = False

    def draw(self, surf):
        angle_deg = math.degrees(math.atan2(self.dy, self.dx))
        ix, iy    = int(self.x), int(self.y)

        if self.weapon_key == "laser" or self.color == CYAN:
            length, width = 20, 3
            pad = 14
            s = pygame.Surface((width + pad, length + pad), pygame.SRCALPHA)
            p2 = pad // 2
            pygame.draw.rect(s, (*CYAN, 25),  (0, 0, width+pad, length+pad))
            pygame.draw.rect(s, (*CYAN, 55),  (2, 2, width+pad-4, length+pad-4))
            pygame.draw.rect(s, (*CYAN, 90),  (p2-1, p2-1, width+2, length+2))
            pygame.draw.rect(s, CYAN,          (p2, p2, width, length))
            pygame.draw.rect(s, WHITE,         (p2 + width//2 - 1, p2, 2, length//2))
            rotated = pygame.transform.rotate(s, -(angle_deg + 90))
            surf.blit(rotated, rotated.get_rect(center=(ix, iy)))

        elif self.weapon_key == "missile" or self.color == RED:
            length, width = 16, 6
            s = pygame.Surface((width + 8, length + 10), pygame.SRCALPHA)
            cx = (width + 8) // 2
            glow_r = (255, 120, 0)
            for gi in range(6, 0, -2):
                pygame.draw.rect(s, (*glow_r, 30 * gi),
                                 (cx - gi, length + 4, gi * 2, 6))
            pygame.draw.rect(s, (180, 30, 30), (cx-width//2, 4, width, length))
            pygame.draw.rect(s, RED,            (cx-width//2, 4, width, length), 1)
            pygame.draw.polygon(s, (255, 80, 0),
                                [(cx, 0), (cx-width//2, 6), (cx+width//2, 6)])
            pygame.draw.rect(s, (255, 100, 100), (cx-width//2+1, 5, 2, length//2))
            rotated = pygame.transform.rotate(s, -(angle_deg + 90))
            surf.blit(rotated, rotated.get_rect(center=(ix, iy)))

        elif self.weapon_key == "shotgun" or self.color == YELLOW:
            s = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(s, (*YELLOW, 70), (6, 6), 5)
            pygame.draw.circle(s, YELLOW,         (6, 6), 3)
            pygame.draw.circle(s, WHITE,           (6, 6), 1)
            surf.blit(s, (ix - 6, iy - 6))

        elif self.weapon_key == "plasma" or self.color == PURPLE:
            pulse = 0.15 * math.sin(self.age * 18)
            r_out = int(8 + pulse * 8)
            r_out = max(5, r_out)
            dim   = r_out * 2 + 8
            s = pygame.Surface((dim, dim), pygame.SRCALPHA)
            c = dim // 2
            pygame.draw.circle(s, (*PURPLE, 50), (c, c), r_out + 3)
            pygame.draw.circle(s, PURPLE,         (c, c), r_out)
            pygame.draw.circle(s, (220, 100, 255),(c, c), r_out - 2)
            pygame.draw.circle(s, (*CYAN, 80),    (c, c), r_out + 1, 1)
            pygame.draw.circle(s, WHITE,           (c, c), 2)
            surf.blit(s, (ix - c, iy - c))

        elif self.weapon_key == "railgun":
            length, width = 32, 4
            pad = 10
            s  = pygame.Surface((width + pad, length + pad), pygame.SRCALPHA)
            p2 = pad // 2
            cx2 = (width + pad) // 2
            pygame.draw.rect(s, (*CYAN, 18),   (0, 0, width+pad, length+pad))
            pygame.draw.rect(s, (*CYAN, 50),   (1, 1, width+pad-2, length+pad-2))
            pygame.draw.rect(s, (*CYAN, 100),  (p2-1, p2-1, width+2, length+2))
            pygame.draw.rect(s, WHITE,          (cx2-1, p2, 2, length))
            pygame.draw.rect(s, CYAN,           (cx2-2, p2, width, length//2))
            rotated = pygame.transform.rotate(s, -(angle_deg + 90))
            surf.blit(rotated, rotated.get_rect(center=(ix, iy)))

        elif self.weapon_key == "chaingun":
            length, width = 10, 3
            s = pygame.Surface((width + 6, length + 6), pygame.SRCALPHA)
            p2 = 3; cx2 = (width + 6) // 2
            pulse = abs(math.sin(self.age * 30))
            c_ = tuple(min(255, int(c * (0.7 + 0.3 * pulse))) for c in self.color)
            pygame.draw.rect(s, (*c_, 60), (0, 0, width+6, length+6))
            pygame.draw.rect(s, c_,    (p2, p2, width, length))
            pygame.draw.rect(s, WHITE, (cx2-1, p2, 1, length//2))
            rotated = pygame.transform.rotate(s, -(angle_deg + 90))
            surf.blit(rotated, rotated.get_rect(center=(ix, iy)))

        else:
            length, width = 15, 5
            pad = 14
            s   = pygame.Surface((width + pad, length + pad), pygame.SRCALPHA)
            p2  = pad // 2
            cx2 = (width + pad) // 2
            pygame.draw.rect(s, (*self.color, 28), (0, 0, width+pad, length+pad))
            pygame.draw.rect(s, (*self.color, 65), (2, 2, width+pad-4, length+pad-4))
            pygame.draw.rect(s, (*self.color, 110),(p2-1, p2-1, width+2, length+2))
            pygame.draw.rect(s, self.color,         (p2, p2, width, length))
            pygame.draw.rect(s, WHITE,              (cx2-1, p2, 2, length//2))
            pygame.draw.rect(s, ORANGE_GLOW,        (cx2-1, p2, 2, 4))
            rotated = pygame.transform.rotate(s, -(angle_deg + 90))
            surf.blit(rotated, rotated.get_rect(center=(ix, iy)))


class EnemyBullet:
    def __init__(self, x, y, dx, dy, damage=8, speed=3.5):
        self.x, self.y  = float(x), float(y)
        self.dx, self.dy = dx, dy
        self.damage = damage
        self.speed  = speed
        self.alive  = True
        self.age    = 0.0

    def update(self, dt, sw, sh):
        self.age += dt
        self.x  += self.dx * self.speed * dt * 60
        self.y  += self.dy * self.speed * dt * 60
        if self.x < -20 or self.x > sw + 20 or self.y < -40 or self.y > sh + 20:
            self.alive = False

    def draw(self, surf):
        ix, iy = int(self.x), int(self.y)
        pulse  = abs(math.sin(self.age * 14))
        r_     = int(5 + pulse * 2)
        s = pygame.Surface((r_*2+4, r_*2+4), pygame.SRCALPHA)
        c = r_ + 2
        pygame.draw.circle(s, (*RED, 55),       (c, c), r_ + 2)
        pygame.draw.circle(s, (220, 50, 0),     (c, c), r_)
        pygame.draw.circle(s, (255, 120, 0),    (c, c), r_ - 1)
        pygame.draw.circle(s, YELLOW,           (c, c), max(1, r_ - 3))
        pygame.draw.circle(s, WHITE,            (c, c), max(1, r_ - 5))
        surf.blit(s, (ix - c, iy - c))


class XPOrb:
    def __init__(self, x, y, value=10):
        self.x, self.y = float(x), float(y)
        self.value = value
        self.alive = True
        self.pulse = random.uniform(0, math.pi * 2)
        self.spin  = random.uniform(-2.0, 2.0)
        self.age   = 0.0

    def update(self, dt, px, py, magnet_range):
        self.pulse += dt * 4.5
        self.spin  += dt * 180
        self.age   += dt
        dist = math.hypot(self.x - px, self.y - py)
        if dist < magnet_range:
            dx = px - self.x; dy = py - self.y
            d  = max(1, dist)
            pull = 5.0 + (1.0 - dist / magnet_range) * 8.0
            self.x += (dx / d) * pull * dt * 60
            self.y += (dy / d) * pull * dt * 60

    def draw(self, surf):
        p  = abs(math.sin(self.pulse))
        gr = max(4, int(7 * (0.75 + 0.5 * p)))
        col = (int(50 + 100 * p), 220, int(70 + 80 * p))

        glow_r = gr + 5
        gs = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(gs, (*col, 35), (glow_r, glow_r), glow_r)
        surf.blit(gs, (int(self.x) - glow_r, int(self.y) - glow_r))

        s  = pygame.Surface((gr*2+4, gr*2+4), pygame.SRCALPHA)
        cx = cy = gr + 2
        pts = [(cx, cy - gr), (cx + gr, cy), (cx, cy + gr), (cx - gr, cy)]
        pygame.draw.polygon(s, col, pts)
        pygame.draw.polygon(s, WHITE, pts, 1)
        r2 = max(1, gr // 2)
        inner = [(cx, cy - r2), (cx + r2, cy), (cx, cy + r2), (cx - r2, cy)]
        bright = (min(255, col[0]+80), 255, min(255, col[2]+60))
        pygame.draw.polygon(s, bright, inner)
        pygame.draw.rect(s, WHITE, (cx - 1, cy - 1, 2, 2))
        surf.blit(s, (int(self.x) - cx, int(self.y) - cy))


class PowerOrb:
    COLORS = {"heal": GREEN, "shield": CYAN, "speed": YELLOW, "invuln": WHITE}
    ICONS  = {"heal": "+", "shield": "S", "speed": ">", "invuln": "*"}

    def __init__(self, x, y, kind="heal"):
        self.x, self.y = float(x), float(y)
        self.kind   = kind
        self.color  = self.COLORS.get(kind, GREEN)
        self.alive  = True
        self.pulse  = random.uniform(0, math.pi * 2)
        self.vx     = random.uniform(-1.0, 1.0)
        self.vy     = random.uniform(-1.0, 1.0)
        self.drift_t = 0.8
        self.lifetime = 12.0

    def update(self, dt, px, py, magnet_range):
        self.pulse    += dt * 5.0
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return
        if self.drift_t > 0:
            self.drift_t -= dt
            self.x += self.vx * dt * 60
            self.y += self.vy * dt * 60
        dist = math.hypot(self.x - px, self.y - py)
        pull_range = magnet_range + 60
        if dist < pull_range:
            dx = px - self.x; dy = py - self.y
            d  = max(1, dist)
            pull = 6.0 + (1.0 - dist / pull_range) * 9.0
            self.x += (dx / d) * pull * dt * 60
            self.y += (dy / d) * pull * dt * 60

    def draw(self, surf):
        p   = abs(math.sin(self.pulse)) * 0.5 + 0.5
        r_  = max(5, int(9 * p))
        col = self.color
        fade = min(1.0, self.lifetime / 3.0)
        col = tuple(int(c * fade) for c in col)

        gs = pygame.Surface((r_*2+14, r_*2+14), pygame.SRCALPHA)
        gc = r_ + 7
        pygame.draw.circle(gs, (*col, 50), (gc, gc), gc)
        surf.blit(gs, (int(self.x) - gc, int(self.y) - gc))

        s  = pygame.Surface((r_*2+4, r_*2+4), pygame.SRCALPHA)
        c2 = r_ + 2
        pts = [(c2 + int(r_ * math.cos(math.radians(60*i - 30))),
                c2 + int(r_ * math.sin(math.radians(60*i - 30)))) for i in range(6)]
        pygame.draw.polygon(s, (*col, 200), pts)
        pygame.draw.polygon(s, WHITE, pts, 1)
        surf.blit(s, (int(self.x) - c2, int(self.y) - c2))


class CoinOrb:
    def __init__(self, x, y, value=3):
        self.x, self.y = float(x), float(y)
        self.value  = value
        self.alive  = True
        self.pulse  = random.uniform(0, math.pi * 2)
        self.vx     = random.uniform(-0.6, 0.6)
        self.vy     = random.uniform(-0.6, 0.6)
        self.drift_t = 0.6
        self.age    = 0.0

    def update(self, dt, px, py, magnet_range):
        self.pulse += dt * 3.5
        self.age   += dt
        if self.drift_t > 0:
            self.drift_t -= dt
            self.x += self.vx * dt * 60
            self.y += self.vy * dt * 60
        dist = math.hypot(self.x - px, self.y - py)
        pull_range = magnet_range + 35
        if dist < pull_range:
            dx = px - self.x; dy = py - self.y
            d  = max(1, dist)
            pull = 5.0 + (1.0 - dist / pull_range) * 6.0
            self.x += (dx / d) * pull * dt * 60
            self.y += (dy / d) * pull * dt * 60

    def draw(self, surf):
        p  = abs(math.sin(self.pulse)) * 0.6 + 0.4
        r_ = 6
        col  = (int(255 * p), int(195 * p), 0)
        shine = (255, min(255, int(220 * p) + 30), 30)

        gs = pygame.Surface((r_*2+10, r_*2+10), pygame.SRCALPHA)
        gc = r_ + 5
        pygame.draw.circle(gs, (*col, 50), (gc, gc), r_ + 4)
        surf.blit(gs, (int(self.x) - gc, int(self.y) - gc))

        s  = pygame.Surface((r_*2+4, r_*2+4), pygame.SRCALPHA)
        c2 = r_ + 2
        pygame.draw.circle(s, col,   (c2, c2), r_)
        pygame.draw.circle(s, shine, (c2, c2), r_ - 2)
        pygame.draw.circle(s, WHITE, (c2, c2), max(1, r_ - 4))
        pygame.draw.circle(s, col, (c2, c2), max(1, r_ - 4), 1)
        surf.blit(s, (int(self.x) - c2, int(self.y) - c2))


ENEMY_TYPES = {
    0: dict(name="Drone",    min_wave=1,  hp=1.0, spd=1.0, sz=(10,14), dmg=15, shoot_w=99, colors=[RED, ORANGE_DARK, CYAN]),
    1: dict(name="Swarmer",  min_wave=3,  hp=0.5, spd=1.6, sz=(7, 10), dmg=10, shoot_w=99, colors=[CYAN, YELLOW, GREEN]),
    2: dict(name="Armored",  min_wave=4,  hp=2.2, spd=0.6, sz=(14,18), dmg=25, shoot_w=99, colors=[GRAY_MID, GRAY_LIGHT]),
    3: dict(name="Shooter",  min_wave=5,  hp=1.2, spd=0.9, sz=(11,14), dmg=18, shoot_w=5,  colors=[RED, ORANGE]),
    4: dict(name="Elite",    min_wave=7,  hp=1.8, spd=1.2, sz=(12,16), dmg=30, shoot_w=7,  colors=[PURPLE, (180,40,220)]),
    5: dict(name="Phantom",  min_wave=9,  hp=1.0, spd=1.4, sz=(10,13), dmg=20, shoot_w=9,  colors=[PURPLE, CYAN]),
    6: dict(name="Healer",   min_wave=8,  hp=0.8, spd=1.1, sz=(10,13), dmg=12, shoot_w=99, colors=[(40,220,120), GREEN]),
    7: dict(name="Splitter", min_wave=11, hp=2.5, spd=0.7, sz=(16,20), dmg=22, shoot_w=99, colors=[(220,80,20), ORANGE]),
    8: dict(name="Kamikaze", min_wave=6,  hp=0.4, spd=1.8, sz=(8, 11), dmg=40, shoot_w=99, colors=[(255,60,0), RED]),
}

def pick_enemy_type(wave):
    available = [t for t, cfg in ENEMY_TYPES.items() if cfg["min_wave"] <= wave]
    weights   = [max(1, 8 - (wave - ENEMY_TYPES[t]["min_wave"])) for t in available]
    total     = sum(weights)
    r         = random.uniform(0, total)
    acc       = 0
    for t, w in zip(available, weights):
        acc += w
        if r <= acc:
            return t
    return available[-1]


class Enemy:
    def __init__(self, x, y, hp, speed, color, size=14, value=10, boss=False, wave=1,
                 enemy_type=0):
        self.x, self.y  = float(x), float(y)
        self.hp = self.max_hp = float(hp)
        self.speed      = speed
        self.color      = color
        self.size       = size
        self.value      = value
        self.boss       = boss
        self.wave       = wave
        self.enemy_type = enemy_type
        self.alive      = True
        self.shoot_cd   = random.uniform(0, 2.5)
        self.face_angle = 0.0
        self.rot_speed  = 120.0 if boss else 0.0
        base_dmg        = (20 if not boss else 45) if enemy_type not in ENEMY_TYPES \
                          else ENEMY_TYPES[enemy_type]["dmg"]
        if boss:
            self.dmg = max(55 + wave * 3, base_dmg * 3.0)
        else:
            self.dmg = base_dmg
        self.contact_cd = 0.0
        if not boss:
            cmin, cmax = coin_drop_range(wave)
        else:
            cmin, cmax = coin_drop_boss_range(wave)
        self.coin_value = random.randint(cmin, cmax)
        self.hit_flash    = 0.0
        self.low_hp_pulse = 0.0
        self.burn_timer   = 0.0
        self.burn_dps     = 0.0
        self.slow_timer   = 0.0
        self._base_speed  = speed
        self._berserker   = False
        self.heal_cd      = random.uniform(2.5, 4.5)
        self.split_done   = False
        self.wants_split  = False
        self.kamikaze_active  = False
        self._do_heal_nearby  = False
        self.boss_phase   = 1
        self._phase2_entered = False
        self.boss_shield     = 0.0
        self.boss_shield_max = 0.0
        self.is_elite        = False
        self._summon_cd      = 0.0
        self._wants_summon   = False
        self.orbit_angle = random.uniform(0, math.tau)
        self.orbit_timer = random.uniform(1.8, 3.5) if enemy_type == 5 and not boss else 0.0
        self.orbit_dir   = 1 if random.random() < 0.5 else -1

    def apply_burn(self, dps, duration):
        if dps > self.burn_dps:
            self.burn_dps = dps
        self.burn_timer = max(self.burn_timer, duration)

    def apply_slow(self, duration):
        self.slow_timer = max(self.slow_timer, duration)
        self.speed = self._base_speed * 0.4

    def apply_freeze(self, duration):
        self.slow_timer = max(self.slow_timer, duration)
        self.speed = 0.0

    def update(self, dt, px, py, bullets_out):
        if self.burn_timer > 0:
            self.burn_timer -= dt
            self.hp -= self.burn_dps * dt
            if self.hp <= 0:
                self.alive = False
                return
            if self.burn_timer <= 0:
                self.burn_dps = 0.0

        if self.slow_timer > 0:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.speed = self._base_speed * (1.5 if self._berserker else 1.0)

        hp_ratio = self.hp / max(1, self.max_hp)
        if (not self.boss and not self._berserker and hp_ratio < 0.25 and hp_ratio > 0
                and self.enemy_type != 8):
            self._berserker = True
            if self.slow_timer <= 0:
                self.speed = self._base_speed * 1.50

        dx = px - self.x; dy = py - self.y
        dist = math.hypot(dx, dy)

        if self.enemy_type == 5 and self.orbit_timer > 0 and not self.boss:
            self.orbit_timer -= dt
            self.orbit_angle += self.orbit_dir * 1.7 * dt
            orbit_r = 185.0
            target_x = px + math.cos(self.orbit_angle) * orbit_r
            target_y = py + math.sin(self.orbit_angle) * orbit_r
            tx = target_x - self.x; ty = target_y - self.y
            td = math.hypot(tx, ty)
            if td > 1:
                self.x += (tx / td) * self.speed * dt * 60
                self.y += (ty / td) * self.speed * dt * 60
                ta = math.degrees(math.atan2(tx, -ty))
                diff = (ta - self.face_angle + 180) % 360 - 180
                self.face_angle += diff * min(1.0, dt * 8)
            if dist < 55:
                self.orbit_timer = random.uniform(1.2, 2.8)
                self.orbit_angle = math.atan2(self.y - py, self.x - px)
        elif dist > 1:
            self.x += (dx / dist) * self.speed * dt * 60
            self.y += (dy / dist) * self.speed * dt * 60
            target_angle = math.degrees(math.atan2(dx, -dy))
            diff = (target_angle - self.face_angle + 180) % 360 - 180
            self.face_angle += diff * min(1.0, dt * 8)

        if self.boss:
            hp_ratio = self.hp / max(1, self.max_hp)
            self.rot_speed = 90 + (1 - hp_ratio) * 180
            if not self._phase2_entered and hp_ratio < 0.50:
                self._phase2_entered = True
                self.boss_phase = 2
                self._base_speed *= 1.55
                if self.slow_timer <= 0:
                    self.speed = self._base_speed
                self._summon_cd = 2.0

            if self.boss_phase == 2:
                self._summon_cd -= dt
                if self._summon_cd <= 0:
                    self._summon_cd = 6.0
                    self._wants_summon = True

            self.shoot_cd -= dt
            if self.shoot_cd <= 0:
                if self.boss_phase == 1:
                    self.shoot_cd = 1.0 if not self.is_elite else 0.8
                    if dist > 1:
                        b_dmg = 35 if not self.is_elite else 45
                        bullets_out.append(EnemyBullet(self.x, self.y, dx/dist, dy/dist, b_dmg, 3.2))
                        for a in [-25, 25, -50, 50]:
                            rad = math.radians(a)
                            ndx = dx/dist*math.cos(rad) - dy/dist*math.sin(rad)
                            ndy = dx/dist*math.sin(rad) + dy/dist*math.cos(rad)
                            bullets_out.append(EnemyBullet(self.x, self.y, ndx, ndy, 22, 2.8))
                        if self.is_elite:
                            for a in range(0, 360, 45):
                                rad = math.radians(a)
                                bullets_out.append(EnemyBullet(
                                    self.x, self.y, math.cos(rad), math.sin(rad), 18, 2.4))
                else:
                    self.shoot_cd = 0.38 if not self.is_elite else 0.28
                    spiral_base = math.degrees(math.atan2(dy, dx)) if dist > 1 else 0
                    step = 24 if not self.is_elite else 18
                    for a_off in range(0, 360, step):
                        rad = math.radians(spiral_base + a_off)
                        bullets_out.append(EnemyBullet(
                            self.x, self.y, math.cos(rad), math.sin(rad), 28, 4.0))
                    if dist > 1:
                        for a in [-8, 0, 8]:
                            rad = math.radians(a)
                            ndx = dx/dist*math.cos(rad) - dy/dist*math.sin(rad)
                            ndy = dx/dist*math.sin(rad) + dy/dist*math.cos(rad)
                            bullets_out.append(EnemyBullet(self.x, self.y, ndx, ndy, 35, 4.5))
        elif self.enemy_type == 6:
            self.heal_cd -= dt
            if self.heal_cd <= 0:
                self.heal_cd = random.uniform(3.0, 5.0)
                self._do_heal_nearby = True
        elif self.enemy_type == 8:
            if dist < 220 and not self.kamikaze_active:
                self.kamikaze_active = True
                if self.slow_timer <= 0:
                    self.speed = self._base_speed * 2.4
        elif self.wave >= ENEMY_TYPES.get(self.enemy_type, {}).get("shoot_w", 99):
            self.shoot_cd -= dt
            if self.shoot_cd <= 0:
                self.shoot_cd = random.uniform(2.2, 3.8)
                if dist > 1:
                    bullets_out.append(EnemyBullet(self.x, self.y, dx/dist, dy/dist, 12, 3.5))

        self.contact_cd    = max(0, self.contact_cd - dt)
        self.hit_flash     = max(0, self.hit_flash - dt * 6)
        self.low_hp_pulse += dt * 6

    def hit(self, damage):
        if self.boss_shield > 0:
            if damage <= self.boss_shield:
                self.boss_shield -= damage
                self.hit_flash = 0.5
                return False
            else:
                damage -= self.boss_shield
                self.boss_shield = 0.0
        self.hp -= damage
        self.hit_flash = 1.0
        if self.hp <= 0:
            self.alive = False
            if self.enemy_type == 7 and not self.split_done:
                self.wants_split = True
                self.split_done  = True
            return True
        return False

    def draw(self, surf):
        angle = self.face_angle + (self.rot_speed * pygame.time.get_ticks() / 1000
                                    if self.boss else 0)
        draw_pixel_enemy(surf, int(self.x), int(self.y), self.size, self.color,
                         self.hp / max(1, self.max_hp), self.boss, self.enemy_type, angle)

        if self.boss:
            bw = self.size * 3
            draw_bar(surf, int(self.x) - bw//2, int(self.y) - self.size - 14,
                     bw, 6, self.hp, self.max_hp, RED, glow=True)

        if self.boss and self.boss_shield > 0:
            shield_r = self.size + 8
            pulse = abs(math.sin(pygame.time.get_ticks() / 300.0))
            alpha = int(100 + 80 * pulse)
            ss = pygame.Surface((shield_r * 2 + 4, shield_r * 2 + 4), pygame.SRCALPHA)
            c = shield_r + 2
            pygame.draw.circle(ss, (0, 180, 255, alpha), (c, c), shield_r, 3)
            pygame.draw.circle(ss, (0, 220, 255, int(alpha * 0.4)), (c, c), shield_r + 2, 1)
            surf.blit(ss, (int(self.x) - c, int(self.y) - c))

        if self.hit_flash > 0.02:
            flash_r = self.size + 4
            fs = pygame.Surface((flash_r * 2, flash_r * 2), pygame.SRCALPHA)
            alpha = int(200 * self.hit_flash)
            pygame.draw.circle(fs, (255, 255, 255, alpha), (flash_r, flash_r), flash_r)
            surf.blit(fs, (int(self.x) - flash_r, int(self.y) - flash_r))

        if self.hp / max(1, self.max_hp) < 0.30 and not self.boss:
            pulse_a = int(abs(math.sin(self.low_hp_pulse)) * 80)
            pulse_r = self.size + 6
            ps = pygame.Surface((pulse_r * 2, pulse_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(ps, (220, 40, 40, pulse_a), (pulse_r, pulse_r), pulse_r, 2)
            surf.blit(ps, (int(self.x) - pulse_r, int(self.y) - pulse_r))

        if self._berserker:
            ber_a = int(abs(math.sin(self.low_hp_pulse * 1.8)) * 120 + 30)
            ber_r = self.size + 9
            bs = pygame.Surface((ber_r * 2, ber_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(bs, (255, 60, 0, ber_a), (ber_r, ber_r), ber_r)
            surf.blit(bs, (int(self.x) - ber_r, int(self.y) - ber_r))

        if self.burn_timer > 0:
            fire_a = int(abs(math.sin(self.low_hp_pulse * 3.5)) * 100 + 60)
            fire_a = min(180, fire_a)
            fr = self.size + 4
            fs2 = pygame.Surface((fr * 2, fr * 2), pygame.SRCALPHA)
            pygame.draw.circle(fs2, (255, 120, 0, fire_a), (fr, fr), fr)
            surf.blit(fs2, (int(self.x) - fr, int(self.y) - fr))

        if self.slow_timer > 0:
            sl_a = int(90 * min(1.0, self.slow_timer))
            sl_r = self.size + 3
            ss = pygame.Surface((sl_r * 2, sl_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(ss, (80, 200, 255, sl_a), (sl_r, sl_r), sl_r, 2)
            surf.blit(ss, (int(self.x) - sl_r, int(self.y) - sl_r))


class Player:
    def __init__(self, ship_data, weapon_data, sw, sh, skill_tree_bonuses=None):
        self.sw, self.sh = sw, sh
        self.x = sw / 2
        self.y = sh / 2

        self.base_hp     = ship_data["hp"]
        self.base_shield = ship_data["shield"]
        self.base_speed  = ship_data["speed"]
        self.color       = ship_data["color"]
        self.accent      = ship_data["accent"]
        self.ship_size   = ship_data["size"]

        stb = skill_tree_bonuses or {}
        extra_hp   = stb.get("hp", 0)
        extra_shld = stb.get("shield", 0)
        self.armor_pct = stb.get("armor", 0.0)

        self.hp         = float(self.base_hp + extra_hp)
        self.max_hp     = float(self.base_hp + extra_hp)
        self.shield     = float(self.base_shield + extra_shld)
        self.max_shield = float(self.base_shield + extra_shld)
        self.shield_regen_cd = 0.0

        self._tree_speed     = stb.get("speed", 0.0)
        self._tree_damage    = stb.get("damage_pct", 0.0)
        self._tree_firerate  = stb.get("firerate_pct", 0.0)
        self._tree_pierce    = stb.get("pierce", 0)
        self._tree_multishot = stb.get("multishot", 0)
        self._tree_regen     = stb.get("regen", 0.0)
        self._tree_crit      = stb.get("crit", 0.0)
        self._tree_magnet    = stb.get("magnet", 0)
        self._tree_autoaim   = stb.get("autoaim", 0)
        self._tree_aura      = stb.get("aura", 0)
        self._tree_aura_dmg  = stb.get("aura_dmg", 0.0)

        self.weapon   = weapon_data.copy()
        self.shoot_cd = 0.0

        self.skill_speed       = 0
        self.skill_damage      = 0
        self.skill_shield      = 0
        self.skill_multishot   = 0
        self.skill_regen       = 0
        self.skill_explosion   = 0
        self.skill_pierce      = 0
        self.skill_magnet      = 0
        self.skill_chain       = 0
        self.skill_lifesteal   = 0
        self.skill_homing      = 0
        self.skill_crit        = 0
        self.skill_slow        = 0
        self.skill_vampiric    = 0
        self.skill_ricochet    = 0
        self.skill_aura        = 0
        self.skill_dash        = 0
        self.skill_overcharge  = 0
        self.skill_deathblow   = 0
        self.skill_coin_bonus   = 0
        self.skill_xp_bonus     = 0
        self.skill_shield_regen = 0
        self.skill_thorns       = 0
        self.skill_dodge        = 0
        self.skill_burn         = 0
        self.skill_freeze       = 0
        self.skill_orbital      = 0
        self.skill_area_magnet  = 0
        self.skill_lucky        = 0
        self.skill_berserker    = 0
        self.skill_autoaim     = self._tree_autoaim
        self.autoaim_locked    = False
        self.autoaim_enabled   = True
        self.invincible_cd     = 0.0
        self.speed_boost_cd    = 0.0
        self.invuln_cd_buff    = 0.0
        self._crit_anim        = 0.0
        self.dash_cd           = 0.0
        self._dash_active      = 0.0
        self._overcharge_cd    = 0.0
        self._overcharge_shots = 0

        self.aim_angle = 0.0
        self.aim_dx    = 0.0
        self.aim_dy    = -1.0

        self._heal_budget     = 0.0
        self._heal_budget_timer = 0.0

        self.engine_anim = 0.0

    @property
    def speed(self):
        boost = 1.4 if self.speed_boost_cd > 0 else 1.0
        return (self.base_speed + self.skill_speed * 0.45 + self._tree_speed) * boost

    @property
    def magnet_range(self):
        return 80 + self.skill_magnet * 35 + self._tree_magnet * 45

    def take_damage(self, dmg):
        if self.invincible_cd > 0 or self.invuln_cd_buff > 0 or self._dash_active > 0:
            return False
        dmg = dmg * (1.0 - min(0.50, self.armor_pct))
        if self.shield > 0:
            absorbed = min(self.shield, dmg)
            self.shield -= absorbed
            dmg -= absorbed
            if dmg <= 0:
                self.shield_regen_cd = 6.0
                return "shield"
        self.hp -= dmg
        self.hp = max(0, self.hp)
        self.invincible_cd   = 0.3
        self.shield_regen_cd = 6.0
        return True

    def heal(self, amount):
        cap = self.max_hp * 0.08
        remaining = max(0, cap - self._heal_budget)
        actual = min(amount, remaining)
        if actual > 0:
            self.hp = min(self.max_hp, self.hp + actual)
            self._heal_budget += actual

    def apply_skill(self, skill_key):
        attr = f"skill_{skill_key}"
        if hasattr(self, attr):
            setattr(self, attr, getattr(self, attr) + 1)
        if skill_key == "shield":
            bonus = 22
            self.max_shield += bonus
            self.shield = min(self.max_shield, self.shield + bonus)
        elif skill_key == "overcharge" and self._overcharge_cd <= 0:
            self._overcharge_cd = 14.0

    def update(self, dt, keys, mouse_pos):
        vx = vy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    vy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  vy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  vx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: vx += 1
        if vx and vy:
            vx *= 0.7071; vy *= 0.7071
        self.x = max(20, min(self.sw-20, self.x + vx * self.speed * dt * 60))
        self.y = max(20, min(self.sh-20, self.y + vy * self.speed * dt * 60))

        mx, my = mouse_pos
        dx = mx - self.x; dy = my - self.y
        dist = math.hypot(dx, dy)
        if dist > 1:
            self.aim_dx    = dx / dist
            self.aim_dy    = dy / dist
            self.aim_angle = math.degrees(math.atan2(dx, -dy))

        self.shoot_cd        = max(0, self.shoot_cd - dt)
        self.invincible_cd   = max(0, self.invincible_cd - dt)
        self.shield_regen_cd = max(0, self.shield_regen_cd - dt)
        self._heal_budget_timer += dt
        while self._heal_budget_timer >= 1.0:
            self._heal_budget_timer -= 1.0
            self._heal_budget = 0.0
        self.speed_boost_cd  = max(0, self.speed_boost_cd - dt)
        self.invuln_cd_buff  = max(0, self.invuln_cd_buff - dt)
        self.dash_cd         = max(0, self.dash_cd - dt)
        self._dash_active    = max(0, self._dash_active - dt)
        self.engine_anim    += dt * 8

        if self.skill_overcharge > 0:
            self._overcharge_cd = max(0, self._overcharge_cd - dt)
            if self._overcharge_cd <= 0 and self._overcharge_shots <= 0:
                interval = 10.0 if self.skill_overcharge >= 2 else 14.0
                self._overcharge_cd    = interval
                self._overcharge_shots = 4 + self.skill_overcharge * 2

        if self.shield_regen_cd <= 0 and self.shield < self.max_shield:
            regen_pct = 0.04 + self.skill_shield_regen * 0.03
            regen_rate = self.max_shield * regen_pct
            self.shield = min(self.max_shield, self.shield + regen_rate * dt)

        total_regen = self.skill_regen * 2.0 + self._tree_regen
        if total_regen > 0:
            self.heal(total_regen * dt)

    def shoot(self, bullets_list, particles, sounds=None, enemies=None):
        if self.shoot_cd > 0:
            return False

        base_cd  = self.weapon["fire_rate"] * (1.0 - min(0.35, self._tree_firerate))
        self.shoot_cd = max(0.03, base_cd)

        base_dmg  = self.weapon["damage"]
        base_dmg *= (1.0 + self._tree_damage + self.skill_damage * 0.10)
        if self.skill_berserker > 0 and self.hp / max(1, self.max_hp) < 0.30:
            base_dmg *= 1.0 + self.skill_berserker * 0.40
        overcharge_active = self._overcharge_shots > 0
        if overcharge_active:
            base_dmg *= 1.8
            self._overcharge_shots -= 1
        spd       = self.weapon["speed"]
        color     = self.weapon["color"] if not overcharge_active else ORANGE_GLOW
        pierce    = self.weapon["pierce"] + self.skill_pierce + self._tree_pierce
        explosive = self.skill_explosion > 0
        wk        = self.weapon["key"]

        base_shots  = self.weapon["shots"] + self._tree_multishot
        extra_shots = self.skill_multishot
        shots       = base_shots + extra_shots
        spread_deg  = self.weapon["spread"]
        if shots > 1:
            spread_deg = max(spread_deg, 15)

        aim_dx, aim_dy = self.aim_dx, self.aim_dy
        self.autoaim_locked = False
        _aa_active = self.skill_autoaim > 0 or self.autoaim_enabled
        if _aa_active and enemies:
            aa_ranges = [120, 220, 360]
            if self.skill_autoaim > 0:
                aa_range = aa_ranges[min(self.skill_autoaim - 1, 2)]
            else:
                aa_range = aa_ranges[-1]
            best_dist, best_target = aa_range, None
            for e in enemies:
                if not e.alive: continue
                d = math.hypot(e.x - self.x, e.y - self.y)
                if d < best_dist:
                    best_dist, best_target = d, e
            if best_target is not None:
                tdx = best_target.x - self.x
                tdy = best_target.y - self.y
                td  = math.hypot(tdx, tdy)
                if td > 0:
                    aim_dx = tdx / td
                    aim_dy = tdy / td
                    self.autoaim_locked = True

        base_angle = math.atan2(aim_dy, aim_dx)
        for i in range(shots):
            offset = math.radians((i/(shots-1)-0.5)*spread_deg) if shots > 1 else 0
            a  = base_angle + offset
            dx = math.cos(a); dy = math.sin(a)
            bx = self.x + aim_dx * 20
            by = self.y + aim_dy * 20
            shot_dmg = base_dmg * (0.80 if i >= base_shots else 1.0)
            b = Bullet(bx, by, dx, dy, shot_dmg, spd, color, pierce, explosive, wk)
            b.homing  = self.skill_homing
            b.bounces = self.skill_ricochet
            bullets_list.append(b)

        if sounds:
            sounds.play_weapon(self.weapon["key"])
        if particles:
            particles.hit_spark(self.x + aim_dx * 22, self.y + aim_dy * 22, color)
        return True

    def draw(self, surf):
        if self.invincible_cd > 0 and int(self.invincible_cd * 20) % 2 == 0:
            return

        pulse  = 0.55 + 0.45 * abs(math.sin(self.engine_anim * 0.85))
        eg_r   = int(14 * pulse)
        back_x = int(self.x - self.aim_dx * (self.ship_size[1] * 0.44))
        back_y = int(self.y - self.aim_dy * (self.ship_size[1] * 0.44))
        for gr, ga, gcol in [(eg_r + 10, 22, ORANGE), (eg_r + 5, 52, ORANGE),
                              (eg_r, 100, ORANGE_GLOW)]:
            es = pygame.Surface((gr * 2 + 2, gr * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(es, (*gcol, ga), (gr + 1, gr + 1), gr)
            surf.blit(es, (back_x - gr - 1, back_y - gr - 1))

        if self.shield > 0:
            sh_alpha = int(30 + 25 * abs(math.sin(self.engine_anim)))
            sh_r = max(self.ship_size) + 12
            sbs = pygame.Surface((sh_r*2, sh_r*2), pygame.SRCALPHA)
            pygame.draw.circle(sbs, (*CYAN, sh_alpha), (sh_r, sh_r), sh_r)
            pygame.draw.circle(sbs, (*CYAN, sh_alpha+20), (sh_r, sh_r), sh_r, 1)
            surf.blit(sbs, (int(self.x)-sh_r, int(self.y)-sh_r))

        draw_pixel_ship(surf, int(self.x), int(self.y), self.ship_size,
                        self.color, self.accent, self.aim_angle)
