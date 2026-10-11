import pygame, random, math
from constants import ORANGE, ORANGE_GLOW, RED, CYAN, WHITE, YELLOW, PURPLE, GREEN


class Particle:
    __slots__ = ("x","y","vx","vy","life","max_life","color","size","gravity","circle")

    def __init__(self, x, y, vx, vy, life, color, size=2, gravity=0.0, circle=False):
        self.x, self.y     = float(x), float(y)
        self.vx, self.vy   = float(vx), float(vy)
        self.life = self.max_life = float(life)
        self.color  = color
        self.size   = size
        self.gravity = gravity
        self.circle  = circle

    def update(self, dt):
        self.x  += self.vx * dt * 60
        self.y  += self.vy * dt * 60
        self.vy += self.gravity * dt * 60
        self.life -= dt
        return self.life > 0

    def draw(self, surf):
        a   = self.life / self.max_life
        sz  = max(1, int(self.size * (0.25 + 0.75 * a)))
        r, g, b = self.color
        col = (int(r * a), int(g * a), int(b * a))
        ix, iy = int(self.x), int(self.y)
        if self.circle and sz >= 2:
            pygame.draw.circle(surf, col, (ix, iy), sz)
        else:
            pygame.draw.rect(surf, col, (ix - sz // 2, iy - sz // 2, sz, sz))


class RingExplosion:
    __slots__ = ("x","y","r","max_r","life","max_life","color","w")

    def __init__(self, x, y, max_r, life, color, w=2):
        self.x, self.y   = float(x), float(y)
        self.r           = 2.0
        self.max_r       = float(max_r)
        self.life        = float(life)
        self.max_life    = float(life)
        self.color       = color
        self.w           = w

    def update(self, dt):
        self.life -= dt
        t      = 1.0 - (self.life / self.max_life)
        self.r = self.max_r * (1.0 - (1.0 - t) ** 2.5)
        return self.life > 0

    def draw(self, surf):
        if self.r < 1:
            return
        a = (self.life / self.max_life) ** 0.6
        r, g, b = self.color
        col = (int(r * a), int(g * a), int(b * a))
        w   = max(1, int(self.w * a))
        pygame.draw.circle(surf, col, (int(self.x), int(self.y)), max(1, int(self.r)), w)


class ParticleSystem:
    def __init__(self, quality="high"):
        self.particles    = []
        self.rings        = []
        self.max_particles = {"high": 1400, "medium": 650, "low": 200}[quality]
        self.q_mul        = {"high": 1.0,  "medium": 0.55, "low": 0.25}[quality]

        self.flash_color = (255, 255, 255)
        self.flash_alpha = 0.0
        self.flash_max   = 0.0
        self.flash_dur   = 0.001


    def _add(self, p):
        if len(self.particles) < self.max_particles:
            self.particles.append(p)

    def emit(self, x, y, count, color, speed=2.0, life=0.5, size=3,
             gravity=0.0, spread=360, circle=False):
        n = max(1, int(count * self.q_mul))
        room = self.max_particles - len(self.particles)
        if room <= 0:
            return
        n = min(n, room)
        full = spread >= 360
        half = math.radians(spread / 2)
        for _ in range(n):
            angle = random.uniform(0, math.tau) if full else random.uniform(-half, half)
            spd   = random.uniform(speed * 0.35, speed * 1.15)
            vx    = math.cos(angle) * spd
            vy    = math.sin(angle) * spd
            l     = random.uniform(life * 0.55, life * 1.1)
            s     = random.randint(max(1, size - 1), size + 1)
            self._add(Particle(x, y, vx, vy, l, color, s, gravity, circle))

    def emit_ring(self, x, y, max_r, life, color, w=2):
        if len(self.rings) < 200:
            self.rings.append(RingExplosion(x, y, max_r, life, color, w))


    def explosion(self, x, y, color=ORANGE, big=False):
        n = max(10, int((100 if big else 50) * self.q_mul))
        sz = 6 if big else 4

        self.emit(x, y, n,       color,          speed=6.5,  life=0.85, size=sz,   circle=True)
        self.emit(x, y, n // 2,  ORANGE_GLOW,    speed=9.5,  life=0.52, size=3)
        self.emit(x, y, n // 3,  WHITE,          speed=5.0,  life=0.35, size=2)
        self.emit(x, y, n // 2,  color,          speed=3.0,  life=1.40, size=sz-1, gravity=0.06)
        self.emit(x, y, n // 4,  (255, 200, 80), speed=5.5,  life=0.65, size=3,    gravity=0.04)

        if big:
            self.emit_ring(x, y, 120, 0.60, color,       w=4)
            self.emit_ring(x, y,  68, 0.42, WHITE,       w=2)
            self.emit_ring(x, y, 185, 0.88, color,       w=2)
            self.emit_ring(x, y,  92, 0.66, ORANGE_GLOW, w=2)
            self.emit_ring(x, y, 148, 0.72, ORANGE,      w=1)
        else:
            self.emit_ring(x, y, 55, 0.45, color, w=2)
            self.emit_ring(x, y, 30, 0.32, WHITE, w=1)
            self.emit_ring(x, y, 80, 0.58, color, w=1)

    def engine_trail(self, x, y, color=ORANGE):
        n = max(2, int(5 * self.q_mul))
        self.emit(x, y, n, color,       speed=2.2, life=0.45, size=4, spread=32, circle=True)
        self.emit(x, y, 2, ORANGE_GLOW, speed=1.0, life=0.28, size=3, spread=20, circle=True)
        self.emit(x, y, 1, WHITE,       speed=0.5, life=0.16, size=2, spread=12, circle=True)

    def hit_spark(self, x, y, color=WHITE):
        n = max(2, int(9 * self.q_mul))
        self.emit(x, y, n,      color, speed=4.5, life=0.28, size=2)
        self.emit(x, y, max(1, n//3), WHITE, speed=2.5, life=0.18, size=2, circle=True)

    def shield_hit(self, x, y):
        n = max(3, int(14 * self.q_mul))
        self.emit(x, y, n, CYAN, speed=4.0, life=0.32, size=2, circle=True)
        self.emit_ring(x, y, 36, 0.30, CYAN, w=2)

    def levelup_burst(self, x, y):
        if self.q_mul <= 0.25:
            self.emit(x, y, 8, YELLOW, speed=4.0, life=0.6, size=3)
            return
        self.emit(x, y, 45, YELLOW,      speed=6.5, life=0.85, size=5, circle=True)
        self.emit(x, y, 25, WHITE,       speed=9.0, life=0.55, size=3)
        self.emit(x, y, 25, ORANGE_GLOW, speed=4.5, life=0.80, size=6, circle=True)
        self.emit_ring(x, y,  85, 0.50, YELLOW,      w=3)
        self.emit_ring(x, y, 130, 0.72, ORANGE,      w=2)
        self.emit_ring(x, y,  55, 0.38, WHITE,        w=2)

    def coin_collect(self, x, y):
        n = max(2, int(8 * self.q_mul))
        self.emit(x, y, n, (255, 195, 0), speed=2.2, life=0.42, size=3, circle=True)

    def xp_collect(self, x, y):
        n = max(2, int(6 * self.q_mul))
        self.emit(x, y, n, GREEN, speed=1.8, life=0.32, size=2, circle=True)

    def warp_in(self, x, y, color):
        n = max(5, int(16 * self.q_mul))
        self.emit(x, y, n,      color, speed=3.8, life=0.60, size=4, circle=True)
        self.emit(x, y, n // 2, WHITE, speed=5.5, life=0.32, size=2)
        self.emit_ring(x, y, 30, 0.38, color, w=2)
        self.emit_ring(x, y, 52, 0.52, color, w=1)

    def burn_tick(self, x, y):
        n = max(1, int(4 * self.q_mul))
        fire_col = random.choice([(255, 80, 0), (255, 140, 0), (255, 200, 0)])
        self.emit(x + random.uniform(-6, 6), y,
                  n, fire_col, speed=1.4, life=0.55, size=3,
                  gravity=-0.04, spread=60, circle=True)

    def chain_arc(self, x1, y1, x2, y2):
        steps = max(3, int(math.hypot(x2-x1, y2-y1) / 20))
        for i in range(steps):
            t  = i / max(1, steps - 1)
            px = x1 + (x2 - x1) * t + random.uniform(-8, 8)
            py = y1 + (y2 - y1) * t + random.uniform(-8, 8)
            self.emit(px, py, max(1, int(3 * self.q_mul)),
                      CYAN, speed=1.2, life=0.25, size=2, circle=True)

    def bomb_blast(self, cx, cy, radius):
        n = max(20, int(120 * self.q_mul))
        self.emit(cx, cy, n,       ORANGE_GLOW, speed=12.0, life=1.10, size=6, circle=True)
        self.emit(cx, cy, n // 2,  WHITE,       speed=18.0, life=0.65, size=4)
        self.emit(cx, cy, n // 2,  YELLOW,      speed=8.0,  life=1.40, size=5, gravity=0.02)
        self.emit(cx, cy, n // 3,  RED,         speed=6.0,  life=1.80, size=7, gravity=0.03, circle=True)
        self.emit_ring(cx, cy, radius * 0.25, 0.50, WHITE,       w=4)
        self.emit_ring(cx, cy, radius * 0.50, 0.70, ORANGE_GLOW, w=3)
        self.emit_ring(cx, cy, radius * 0.75, 0.90, ORANGE,      w=2)
        self.emit_ring(cx, cy, radius,        1.10, RED,         w=2)

    def powerup_collect(self, x, y, color):
        n = max(5, int(20 * self.q_mul))
        self.emit(x, y, n,      color, speed=5.0, life=0.60, size=4, circle=True)
        self.emit(x, y, n // 2, WHITE, speed=8.0, life=0.35, size=3)
        self.emit_ring(x, y, 40, 0.40, color, w=2)
        self.emit_ring(x, y, 65, 0.55, WHITE, w=1)


    def screen_flash(self, color, duration=0.15, alpha=120):
        self.flash_color = color
        self.flash_alpha = float(alpha)
        self.flash_max   = float(alpha)
        self.flash_dur   = max(0.001, float(duration))

    def damage_flash(self):
        self.screen_flash(RED, 0.22, 110)

    def shield_flash(self):
        self.screen_flash(CYAN, 0.14, 75)

    def wave_clear_flash(self):
        self.screen_flash(ORANGE_GLOW, 0.35, 85)

    def levelup_flash(self):
        self.screen_flash(YELLOW, 0.28, 95)


    def update(self, dt):
        self.particles = [p for p in self.particles if p.update(dt)]
        self.rings     = [r for r in self.rings     if r.update(dt)]
        if self.flash_alpha > 0:
            decay = (self.flash_max / self.flash_dur) * dt
            self.flash_alpha = max(0.0, self.flash_alpha - decay)

    def draw(self, surf):
        for r in self.rings:     r.draw(surf)
        for p in self.particles: p.draw(surf)

    def draw_flash(self, surf):
        if self.flash_alpha < 0.5:
            return
        sz = surf.get_size()
        if not hasattr(self, '_flash_surf') or self._flash_surf.get_size() != sz:
            self._flash_surf = pygame.Surface(sz, pygame.SRCALPHA)
        rc, gc, bc = self.flash_color
        self._flash_surf.fill((rc, gc, bc, int(self.flash_alpha)))
        surf.blit(self._flash_surf, (0, 0))
