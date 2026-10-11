import pygame

BLACK       = (  0,   0,   0)
DARK_BG     = (  8,   8,  12)
PANEL_BG    = ( 18,  18,  26)
PANEL_DARK  = ( 12,  12,  18)
GRAY_DARK   = ( 40,  40,  52)
GRAY_MID    = ( 80,  80,  96)
GRAY_LIGHT  = (160, 160, 176)
WHITE       = (255, 255, 255)
ORANGE      = (255, 120,   0)
ORANGE_DARK = (200,  80,   0)
ORANGE_GLOW = (255, 160,  40)
ORANGE_DIM  = (120,  55,   0)
CYAN        = (  0, 220, 255)
RED         = (220,  40,  40)
GREEN       = ( 40, 200,  80)
YELLOW      = (255, 220,   0)
PURPLE      = (160,  40, 220)
BLUE        = ( 40, 100, 220)
GOLD        = (255, 195,   0)

SHIPS = [
    {
        "key": "fighter", "name_key": "ship_fighter",
        "hp": 100, "shield": 30, "speed": 4.5, "fire_rate": 0.22,
        "color": ORANGE, "accent": ORANGE_GLOW, "size": (28, 36),
        "desc": "Schnell & ausgewogen",
        "unlock_wave": 0,
    },
    {
        "key": "tank", "name_key": "ship_tank",
        "hp": 200, "shield": 80, "speed": 2.8, "fire_rate": 0.35,
        "color": GRAY_MID, "accent": GRAY_LIGHT, "size": (34, 42),
        "desc": "Viel Leben, langsam",
        "unlock_wave": 5,
    },
    {
        "key": "speeder", "name_key": "ship_speeder",
        "hp": 70, "shield": 15, "speed": 6.5, "fire_rate": 0.15,
        "color": CYAN, "accent": WHITE, "size": (22, 30),
        "desc": "Extrem schnell",
        "unlock_wave": 10,
    },
    {
        "key": "ghost", "name_key": "ship_ghost",
        "hp": 85, "shield": 50, "speed": 5.0, "fire_rate": 0.18,
        "color": PURPLE, "accent": (200, 100, 255), "size": (26, 34),
        "desc": "Hoher Schild",
        "unlock_wave": 15,
    },
    {
        "key": "viper", "name_key": "ship_viper",
        "hp": 75, "shield": 18, "speed": 7.4, "fire_rate": 0.13,
        "color": GREEN, "accent": (140, 255, 90), "size": (20, 28),
        "desc": "Blitzschnell, hohe Feuerrate",
        "unlock_wave": 18,
    },
    {
        "key": "colossus", "name_key": "ship_colossus",
        "hp": 280, "shield": 120, "speed": 2.2, "fire_rate": 0.46,
        "color": GRAY_LIGHT, "accent": WHITE, "size": (38, 48),
        "desc": "Massiv gepanzert & stark",
        "unlock_wave": 22,
    },
    {
        "key": "wraith", "name_key": "ship_wraith",
        "hp": 88, "shield": 105, "speed": 7.9, "fire_rate": 0.15,
        "color": PURPLE, "accent": (230, 130, 255), "size": (24, 32),
        "desc": "Schnellstes Schiff + Hoher Schild",
        "unlock_wave": 28,
    },
]

WEAPONS = [
    {
        "key": "blaster",  "name_key": "weapon_blaster",
        "damage": 20, "speed": 9,  "fire_rate": 0.22, "spread": 0,  "shots": 1,
        "color": ORANGE, "pierce": 0, "desc": "Klassischer Blaster", "cost": 0,
    },
    {
        "key": "laser",    "name_key": "weapon_laser",
        "damage": 14, "speed": 14, "fire_rate": 0.12, "spread": 0,  "shots": 1,
        "color": CYAN,   "pierce": 1, "desc": "Schnell, durchdringend", "cost": 110,
    },
    {
        "key": "missile",  "name_key": "weapon_missile",
        "damage": 65, "speed": 7,  "fire_rate": 0.58, "spread": 0,  "shots": 1,
        "color": RED,    "pierce": 0, "desc": "Hoher Schaden, langsam", "cost": 130,
    },
    {
        "key": "shotgun",  "name_key": "weapon_shotgun",
        "damage": 14, "speed": 8,  "fire_rate": 0.42, "spread": 18, "shots": 5,
        "color": YELLOW, "pierce": 0, "desc": "5 Projektile, Streuung", "cost": 95,
    },
    {
        "key": "plasma",   "name_key": "weapon_plasma",
        "damage": 40, "speed": 7,  "fire_rate": 0.38, "spread": 0,  "shots": 1,
        "color": PURPLE, "pierce": 1, "desc": "Plasma & AoE", "cost": 180,
    },
    {
        "key": "railgun",  "name_key": "weapon_railgun",
        "damage": 135, "speed": 22, "fire_rate": 1.15, "spread": 0, "shots": 1,
        "color": CYAN,   "pierce": 6, "desc": "Alles durchdringen, langsam", "cost": 260,
    },
    {
        "key": "chaingun", "name_key": "weapon_chaingun",
        "damage": 7,  "speed": 11, "fire_rate": 0.08, "spread": 5, "shots": 1,
        "color": (255, 140, 20), "pierce": 0, "desc": "Extrem schnelle Feuerrate", "cost": 215,
    },
]

SKILL_POOL = [
    {"key": "speed",        "name_key": "skill_speed",        "color": CYAN,          "rarity": "common", "max_level": 4},
    {"key": "damage",       "name_key": "skill_damage",       "color": ORANGE,        "rarity": "common", "max_level": 4},
    {"key": "shield",       "name_key": "skill_shield",       "color": BLUE,          "rarity": "common", "max_level": 4},
    {"key": "regen",        "name_key": "skill_regen",        "color": GREEN,         "rarity": "common", "max_level": 3},
    {"key": "coin_bonus",   "name_key": "skill_coin_bonus",   "color": GOLD,          "rarity": "common", "max_level": 3},
    {"key": "xp_bonus",     "name_key": "skill_xp_bonus",     "color": (80, 255, 130),"rarity": "common", "max_level": 3},
    {"key": "shield_regen", "name_key": "skill_shield_regen", "color": (60, 180, 255),"rarity": "common", "max_level": 3},
    {"key": "multishot",    "name_key": "skill_multishot",    "color": YELLOW,        "rarity": "rare",   "max_level": 2},
    {"key": "pierce",       "name_key": "skill_pierce",       "color": PURPLE,        "rarity": "rare",   "max_level": 2},
    {"key": "magnet",       "name_key": "skill_magnet",       "color": GRAY_LIGHT,    "rarity": "rare",   "max_level": 4},
    {"key": "homing",       "name_key": "skill_homing",       "color": RED,           "rarity": "rare",   "max_level": 2},
    {"key": "crit",         "name_key": "skill_crit",         "color": ORANGE_GLOW,   "rarity": "rare",   "max_level": 3},
    {"key": "slow",         "name_key": "skill_slow",         "color": (80, 180, 255),"rarity": "rare",   "max_level": 2},
    {"key": "vampiric",     "name_key": "skill_vampiric",     "color": (180, 20, 20), "rarity": "rare",   "max_level": 3},
    {"key": "ricochet",     "name_key": "skill_ricochet",     "color": YELLOW,        "rarity": "rare",   "max_level": 2},
    {"key": "thorns",       "name_key": "skill_thorns",       "color": (200, 80, 40), "rarity": "rare",   "max_level": 3},
    {"key": "dodge",        "name_key": "skill_dodge",        "color": (180, 220, 255),"rarity": "rare",  "max_level": 2},
    {"key": "area_magnet",  "name_key": "skill_area_magnet",  "color": (200, 200, 255),"rarity": "rare",  "max_level": 2},
    {"key": "lucky",        "name_key": "skill_lucky",        "color": GOLD,          "rarity": "rare",   "max_level": 3},
    {"key": "explosion",    "name_key": "skill_explosion",    "color": RED,           "rarity": "epic",   "max_level": 3},
    {"key": "chain",        "name_key": "skill_chain",        "color": CYAN,          "rarity": "epic",   "max_level": 2},
    {"key": "lifesteal",    "name_key": "skill_lifesteal",    "color": GREEN,         "rarity": "epic",   "max_level": 3},
    {"key": "aura",         "name_key": "skill_aura",         "color": PURPLE,        "rarity": "epic",   "max_level": 3},
    {"key": "dash",         "name_key": "skill_dash",         "color": CYAN,          "rarity": "epic",   "max_level": 2},
    {"key": "overcharge",   "name_key": "skill_overcharge",   "color": ORANGE_GLOW,   "rarity": "epic",   "max_level": 2},
    {"key": "deathblow",    "name_key": "skill_deathblow",    "color": RED,           "rarity": "epic",   "max_level": 2},
    {"key": "freeze",       "name_key": "skill_freeze",       "color": (120, 220, 255),"rarity": "epic",  "max_level": 2},
    {"key": "berserker",    "name_key": "skill_berserker",    "color": (220, 30, 30), "rarity": "epic",   "max_level": 2},
]

RARITY_COLORS = {"common": GRAY_LIGHT, "rare": CYAN, "epic": PURPLE}

COMBO_STREAK_WINDOW = 3.0
COMBO_THRESHOLDS    = [6, 12, 25, 40]
COMBO_MULTIPLIERS   = [1, 2,  3,  5, 10]

BOMB_MAX_CHARGES  = 3
BOMB_RADIUS       = 500

POWERUP_DROP_CHANCE = 0.10
POWERUP_DEFS = {
    "heal":   ("HEAL",   GREEN,  0),
    "shield": ("SHIELD", CYAN,   0),
    "speed":  ("SPEED",  YELLOW, 5.0),
    "invuln": ("INVULN", WHITE,  3.0),
}

SKILL_TREE = [
    {"key": "hp_up",      "cat": "health",  "name": "Max HP",        "icon": "shield",
     "color": GREEN,  "max_level": 4,
     "costs":   [25, 45, 70, 100],
     "bonuses": ["+20 HP", "+25 HP", "+35 HP", "+40 HP"],
     "requires": None},

    {"key": "regen_up",   "cat": "health",  "name": "Regeneration",  "icon": "regen",
     "color": GREEN,  "max_level": 3,
     "costs":   [40, 70, 110],
     "bonuses": ["+0.8/s", "+1.5/s", "+2.5/s"],
     "requires": ("hp_up", 2)},

    {"key": "armor_up",   "cat": "defense", "name": "Rüstung",       "icon": "shield",
     "color": BLUE,   "max_level": 4,
     "costs":   [25, 45, 65, 90],
     "bonuses": ["-5% Dmg", "-5% Dmg", "-5% Dmg", "-5% Dmg"],
     "requires": None},

    {"key": "shield_up",  "cat": "defense", "name": "Schild-Kap.",   "icon": "shield",
     "color": CYAN,   "max_level": 3,
     "costs":   [35, 60, 90],
     "bonuses": ["+30 Shld", "+35 Shld", "+50 Shld"],
     "requires": ("armor_up", 2)},

    {"key": "dmg_up",     "cat": "offense", "name": "Schaden",       "icon": "damage",
     "color": ORANGE, "max_level": 4,
     "costs":   [30, 50, 75, 105],
     "bonuses": ["+8%", "+10%", "+12%", "+15%"],
     "requires": None},

    {"key": "crit_up",    "cat": "offense", "name": "Krit-Chance",   "icon": "explosion",
     "color": RED,    "max_level": 3,
     "costs":   [55, 95, 140],
     "bonuses": ["+5% Krit", "+7% Krit", "+10% Krit"],
     "requires": ("dmg_up", 2)},

    {"key": "pierce_up",  "cat": "offense", "name": "Durchdringung", "icon": "pierce",
     "color": PURPLE, "max_level": 2,
     "costs":   [55, 95],
     "bonuses": ["+1 Pierce", "+1 Pierce"],
     "requires": ("dmg_up", 2)},

    {"key": "firerate_up","cat": "offense", "name": "Feuerrate",     "icon": "multishot",
     "color": YELLOW, "max_level": 3,
     "costs":   [35, 60, 90],
     "bonuses": ["-6% CD", "-7% CD", "-8% CD"],
     "requires": None},

    {"key": "multishot_up","cat":"offense", "name": "Mehrfachschuss","icon": "multishot",
     "color": YELLOW, "max_level": 2,
     "costs":   [80, 140],
     "bonuses": ["+1 Shot", "+1 Shot"],
     "requires": ("firerate_up", 2)},

    {"key": "speed_up",   "cat": "movement","name": "Geschwindigkeit","icon": "speed",
     "color": CYAN,   "max_level": 4,
     "costs":   [22, 40, 62, 88],
     "bonuses": ["+0.3 Spd", "+0.3 Spd", "+0.4 Spd", "+0.4 Spd"],
     "requires": None},

    {"key": "magnet_up",  "cat": "movement","name": "Anziehung",     "icon": "magnet",
     "color": GRAY_LIGHT,"max_level": 3,
     "costs":   [30, 55, 80],
     "bonuses": ["+50 Mag", "+60 Mag", "+80 Mag"],
     "requires": ("speed_up", 2)},

    {"key": "autoaim_up", "cat": "movement", "name": "Auto-Ziel",   "icon": "autoaim",
     "color": CYAN,   "max_level": 3,
     "costs":   [65, 115, 175],
     "bonuses": ["120px Snap", "220px Snap", "360px Snap"],
     "requires": ("speed_up", 1)},

    {"key": "aura_up",    "cat": "offense", "name": "Schadensaura", "icon": "aura",
     "color": PURPLE, "max_level": 3,
     "costs":   [60, 100, 150],
     "bonuses": ["+Aura Lvl1", "+Aura Lvl2", "+Aura Lvl3"],
     "requires": ("dmg_up", 1)},

    {"key": "aura_dmg_up","cat": "offense", "name": "Aura-Schaden", "icon": "aura",
     "color": PURPLE, "max_level": 3,
     "costs":   [55, 95, 145],
     "bonuses": ["+20% Aura", "+25% Aura", "+30% Aura"],
     "requires": ("aura_up", 1)},
]

SHIP_UPG_COSTS  = [45, 85, 135, 200, 285]
SHIP_UPG_BONUS  = [
    {"hp": 20,  "speed": 0.4, "shield": 10},
    {"hp": 35,  "speed": 0.6, "shield": 25},
    {"hp": 55,  "speed": 0.8, "shield": 40},
    {"hp": 75,  "speed": 1.0, "shield": 58},
    {"hp": 100, "speed": 1.3, "shield": 80},
]

WEAPON_UPG_COSTS  = [35, 65, 105, 160, 230]
WEAPON_UPG_BONUS  = [
    {"dmg_pct": 0.18, "rate_pct": 0.0,  "pierce": 0},
    {"dmg_pct": 0.32, "rate_pct": 0.10, "pierce": 0},
    {"dmg_pct": 0.50, "rate_pct": 0.18, "pierce": 1},
    {"dmg_pct": 0.72, "rate_pct": 0.25, "pierce": 1},
    {"dmg_pct": 1.00, "rate_pct": 0.35, "pierce": 2},
]

BASE_ENEMIES_PER_WAVE = 7
ENEMY_SCALE_PER_WAVE  = 0.26
ENEMY_COUNT_CAP       = 50
BOSS_EVERY_N_WAVES    = 5

def wave_duration(wave_num):
    if wave_num <= 4:   return 90.0
    if wave_num <= 8:   return 78.0
    if wave_num <= 13:  return 65.0
    if wave_num <= 20:  return 55.0
    if wave_num <= 30:  return 48.0
    if wave_num <= 40:  return 42.0
    if wave_num <= 50:  return 37.0
    return 33.0


def between_wave_delay(wave_num):
    if wave_num <= 10:  return 3.0
    if wave_num <= 25:  return 2.5
    if wave_num <= 40:  return 2.0
    return 1.5


DIFFICULTY_TIERS = {
    "easy":      {"range": (1, 10),  "color": (40, 200, 80),   "label": "EASY"},
    "medium":    {"range": (11, 20), "color": (255, 220, 0),   "label": "MEDIUM"},
    "hard":      {"range": (21, 35), "color": (255, 120, 0),   "label": "HARD"},
    "nightmare": {"range": (36, 50), "color": (220, 40, 40),   "label": "NIGHTMARE"},
    "hell":      {"range": (51, 999),"color": (160, 40, 220),  "label": "HELL"},
}

def get_difficulty_tier(wave_num):
    for key, t in DIFFICULTY_TIERS.items():
        lo, hi = t["range"]
        if lo <= wave_num <= hi:
            return key, t
    return "hell", DIFFICULTY_TIERS["hell"]


import random as _rng

WAVE_MODIFIERS = {
    "swarm": {
        "label": "SWARM WAVE",
        "desc":  "Double enemies, half HP",
        "color": (255, 220, 0),
        "enemy_count_mult": 2.0,
        "enemy_hp_mult":    0.5,
        "enemy_dmg_mult":   0.8,
        "enemy_spd_mult":   1.2,
        "min_wave": 6,
    },
    "elite": {
        "label": "ELITE WAVE",
        "desc":  "Fewer but deadly enemies",
        "color": (160, 40, 220),
        "enemy_count_mult": 0.5,
        "enemy_hp_mult":    2.5,
        "enemy_dmg_mult":   1.6,
        "enemy_spd_mult":   0.85,
        "min_wave": 11,
    },
    "blitz": {
        "label": "BLITZ WAVE",
        "desc":  "Everything is fast",
        "color": (0, 220, 255),
        "enemy_count_mult": 1.2,
        "enemy_hp_mult":    0.8,
        "enemy_dmg_mult":   1.0,
        "enemy_spd_mult":   1.7,
        "min_wave": 8,
    },
    "armored": {
        "label": "ARMORED WAVE",
        "desc":  "Heavily armored enemies",
        "color": (160, 160, 176),
        "enemy_count_mult": 0.7,
        "enemy_hp_mult":    3.0,
        "enemy_dmg_mult":   1.2,
        "enemy_spd_mult":   0.7,
        "min_wave": 14,
    },
    "meteor": {
        "label": "METEOR STORM",
        "desc":  "Kamikaze-heavy wave",
        "color": (255, 60, 0),
        "enemy_count_mult": 1.5,
        "enemy_hp_mult":    0.6,
        "enemy_dmg_mult":   1.4,
        "enemy_spd_mult":   1.5,
        "min_wave": 10,
        "force_type": 8,
    },
}

_MODIFIER_CHANCE_BY_TIER = {
    "easy": 0.0, "medium": 0.25, "hard": 0.35, "nightmare": 0.45, "hell": 0.55,
}

def pick_wave_modifier(wave_num):
    if wave_num % BOSS_EVERY_N_WAVES == 0:
        return None
    if wave_num <= 4:
        return None
    tier_key, _ = get_difficulty_tier(wave_num)
    chance = _MODIFIER_CHANCE_BY_TIER.get(tier_key, 0.0)
    if _rng.random() >= chance:
        return None
    eligible = [k for k, m in WAVE_MODIFIERS.items() if m["min_wave"] <= wave_num]
    if not eligible:
        return None
    return _rng.choice(eligible)


DANGER_DECAY_RATE       = 0.12
DANGER_HIT_RESET        = -0.6
DANGER_MAX              = 3.0
DANGER_GRACE_PERIOD     = 8.0
DANGER_START_WAVE       = 8

def danger_multiplier(danger_level):
    t = max(0.0, min(danger_level, DANGER_MAX)) / DANGER_MAX
    return (
        1.0 + 0.5 * t,
        1.0 + 1.0 * t,
        1.0 + 0.3 * t,
    )

XP_PER_KILL       = 10
XP_PER_WAVE       = 80
XP_LEVEL_BASE     = 80
XP_KILL_WAVE_SCALE = 0.22

import math as _math

_COIN_BASE_MIN   = 3
_COIN_BASE_MAX   = 9
_COIN_DECAY      = 0.018
_COIN_FLOOR_MIN  = 1
_COIN_FLOOR_MAX  = 2

_BOSS_BASE       = (18, 30)
_BOSS_SCALE      = (8, 14)

def coin_drop_range(wave: int) -> tuple:
    decay = _math.exp(-_COIN_DECAY * wave)
    mn = max(_COIN_FLOOR_MIN, round(_COIN_BASE_MIN * decay))
    mx = max(_COIN_FLOOR_MAX, round(_COIN_BASE_MAX * decay))
    return mn, mx

def coin_drop_boss_range(wave: int) -> tuple:
    factor = min(2.0, _math.sqrt(wave / 5))
    mn = int(_BOSS_BASE[0] + _BOSS_SCALE[0] * factor)
    mx = int(_BOSS_BASE[1] + _BOSS_SCALE[1] * factor)
    return mn, mx

COIN_DROP_MIN  = _COIN_BASE_MIN
COIN_DROP_MAX  = _COIN_BASE_MAX
COIN_DROP_BOSS = (22, 38)

RESOLUTIONS = [(1280, 720),(1366, 768),(1600, 900),(1920, 1080),(2560, 1440),(3440, 1440),(3840, 2160)]

ACHIEVEMENTS = [
    {"key": "first_blood",    "name": "First Blood",         "desc": "Ersten Gegner töten",                    "color": ORANGE,      "cat": "combat"},
    {"key": "ten_kills",      "name": "Auf dem Kriegspfad",  "desc": "10 Gegner besiegen",                     "color": ORANGE,      "cat": "combat"},
    {"key": "fifty_kills",    "name": "Killing Spree",       "desc": "50 Gegner besiegen",                     "color": RED,         "cat": "combat"},
    {"key": "hundred",        "name": "Centurion",           "desc": "100 Gegner besiegen",                    "color": GOLD,        "cat": "combat"},
    {"key": "five_hundred",   "name": "Kriegsgott",          "desc": "500 Gegner besiegen",                    "color": GOLD,        "cat": "combat"},
    {"key": "thousand",       "name": "Vernichter",          "desc": "1.000 Gegner besiegen",                  "color": PURPLE,      "cat": "combat"},
    {"key": "two_thousand",   "name": "Apokalypse",          "desc": "2.000 Gegner besiegen",                  "color": PURPLE,      "cat": "combat"},
    {"key": "five_thousand",  "name": "Extinction Event",    "desc": "5.000 Gegner besiegen",                  "color": (255,50,50), "cat": "combat"},
    {"key": "ten_thousand",   "name": "Genozid",             "desc": "10.000 Gegner besiegen",                 "color": (255,50,50), "cat": "combat"},
    {"key": "wave3",          "name": "Anfänger",            "desc": "Welle 3 erreichen",                      "color": GREEN,       "cat": "waves"},
    {"key": "wave5",          "name": "Rekrut",              "desc": "Welle 5 erreichen",                      "color": CYAN,        "cat": "waves"},
    {"key": "wave10",         "name": "Veteran",             "desc": "Welle 10 erreichen",                     "color": CYAN,        "cat": "waves"},
    {"key": "wave15",         "name": "Kommandant",          "desc": "Welle 15 erreichen",                     "color": BLUE,        "cat": "waves"},
    {"key": "wave20",         "name": "Elite",               "desc": "Welle 20 erreichen",                     "color": PURPLE,      "cat": "waves"},
    {"key": "wave25",         "name": "Admiral",             "desc": "Welle 25 erreichen",                     "color": PURPLE,      "cat": "waves"},
    {"key": "wave30",         "name": "Legende",             "desc": "Welle 30 erreichen",                     "color": GOLD,        "cat": "waves"},
    {"key": "wave40",         "name": "Mythos",              "desc": "Welle 40 erreichen",                     "color": GOLD,        "cat": "waves"},
    {"key": "wave50",         "name": "Unsterblich",         "desc": "Welle 50 erreichen",                     "color": (255,50,50), "cat": "waves"},
    {"key": "combo3",         "name": "Combo-Starter",       "desc": "Combo ×3 erreichen",                     "color": YELLOW,      "cat": "combo"},
    {"key": "combo5",         "name": "Combo-Meister",       "desc": "Combo ×5 erreichen",                     "color": ORANGE_GLOW, "cat": "combo"},
    {"key": "combo10",        "name": "Unaufhaltbar",        "desc": "Combo ×10 erreichen",                    "color": ORANGE_GLOW, "cat": "combo"},
    {"key": "streak20",       "name": "Kettentöter",         "desc": "20er Kill-Streak erreichen",             "color": RED,         "cat": "combo"},
    {"key": "streak40",       "name": "Massaker",            "desc": "40er Kill-Streak erreichen",             "color": PURPLE,      "cat": "combo"},
    {"key": "collector",      "name": "Sammler",             "desc": "500 Coins insgesamt sammeln",            "color": GOLD,        "cat": "economy"},
    {"key": "hoarder",        "name": "Hamsterer",           "desc": "2.000 Coins insgesamt sammeln",          "color": GOLD,        "cat": "economy"},
    {"key": "tycoon",         "name": "Tycoon",              "desc": "5.000 Coins insgesamt sammeln",          "color": GOLD,        "cat": "economy"},
    {"key": "mogul",          "name": "Mogul",               "desc": "10.000 Coins insgesamt sammeln",         "color": (255,215,0), "cat": "economy"},
    {"key": "coins100_session","name": "Goldfieber",         "desc": "100 Coins in einem Run sammeln",         "color": GOLD,        "cat": "economy"},
    {"key": "coins300_session","name": "Münzregen",          "desc": "300 Coins in einem Run sammeln",         "color": GOLD,        "cat": "economy"},
    {"key": "score5k",        "name": "Punktesammler",       "desc": "5.000 Punkte erreichen",                 "color": CYAN,        "cat": "score"},
    {"key": "score10k",       "name": "Highscorer",          "desc": "10.000 Punkte erreichen",                "color": CYAN,        "cat": "score"},
    {"key": "score25k",       "name": "Score-König",         "desc": "25.000 Punkte erreichen",                "color": PURPLE,      "cat": "score"},
    {"key": "score50k",       "name": "Score-Legende",       "desc": "50.000 Punkte erreichen",                "color": GOLD,        "cat": "score"},
    {"key": "score100k",      "name": "Göttlicher Score",    "desc": "100.000 Punkte erreichen",               "color": (255,50,50), "cat": "score"},
    {"key": "boss_slayer",    "name": "Bossjäger",           "desc": "Ersten Boss besiegen",                   "color": GOLD,        "cat": "boss"},
    {"key": "boss5",          "name": "Bossvernichter",      "desc": "5 Bosse besiegen",                       "color": GOLD,        "cat": "boss"},
    {"key": "boss10",         "name": "Titanentöter",        "desc": "10 Bosse besiegen",                      "color": PURPLE,      "cat": "boss"},
    {"key": "boss_no_damage", "name": "Perfekter Kampf",     "desc": "Boss ohne Schaden besiegen",             "color": (255,50,50), "cat": "boss"},
    {"key": "level5",         "name": "Lehrling",            "desc": "Spielerlevel 5 erreichen",               "color": GREEN,       "cat": "leveling"},
    {"key": "level10",        "name": "Aufsteiger",          "desc": "Spielerlevel 10 erreichen",              "color": GREEN,       "cat": "leveling"},
    {"key": "level15",        "name": "Experte",             "desc": "Spielerlevel 15 erreichen",              "color": CYAN,        "cat": "leveling"},
    {"key": "level20",        "name": "Meister",             "desc": "Spielerlevel 20 erreichen",              "color": PURPLE,      "cat": "leveling"},
    {"key": "level30",        "name": "Großmeister",         "desc": "Spielerlevel 30 erreichen",              "color": GOLD,        "cat": "leveling"},
    {"key": "all_skills",     "name": "Alleskönner",         "desc": "Alle Skills auf Maximum",                "color": (255,50,50), "cat": "leveling"},
    {"key": "survivor2min",   "name": "Durchhalter",         "desc": "2 Minuten am Stück überleben",           "color": GREEN,       "cat": "survival"},
    {"key": "survivor5min",   "name": "Überlebenskünstler",  "desc": "5 Minuten am Stück überleben",           "color": GREEN,       "cat": "survival"},
    {"key": "survivor10min",  "name": "Eiserner Wille",      "desc": "10 Minuten am Stück überleben",          "color": CYAN,        "cat": "survival"},
    {"key": "survivor15min",  "name": "Unzerstörbar",        "desc": "15 Minuten am Stück überleben",          "color": PURPLE,      "cat": "survival"},
    {"key": "close_call",     "name": "Haarscharf",          "desc": "Mit unter 10% HP überleben",             "color": RED,         "cat": "survival"},
    {"key": "full_hp_wave",   "name": "Makellos",            "desc": "Welle mit vollem HP beenden",            "color": GREEN,       "cat": "survival"},
    {"key": "no_damage_wave", "name": "Unberührt",           "desc": "Eine Welle ohne Schaden überstehen",     "color": CYAN,        "cat": "survival"},
    {"key": "no_damage_3wave","name": "Geisterhaft",         "desc": "3 Wellen in Folge ohne Schaden",         "color": PURPLE,      "cat": "survival"},
    {"key": "bomb_user",      "name": "Bombenleger",         "desc": "Bombe im Kampf einsetzen",               "color": RED,         "cat": "equipment"},
    {"key": "bomb10",         "name": "Sprengmeister",       "desc": "10 Bomben insgesamt einsetzen",          "color": RED,         "cat": "equipment"},
    {"key": "all_weapons",    "name": "Arsenal",             "desc": "Alle Waffen freischalten",               "color": ORANGE,      "cat": "equipment"},
    {"key": "max_ship",       "name": "Voll aufgerüstet",    "desc": "Ein Schiff voll upgraden",               "color": GOLD,        "cat": "equipment"},
    {"key": "max_weapon",     "name": "Waffenschmied",       "desc": "Eine Waffe voll upgraden",               "color": GOLD,        "cat": "equipment"},
    {"key": "first_skill_tree","name": "Erster Knoten",      "desc": "Ersten Skill-Tree-Knoten kaufen",        "color": GREEN,       "cat": "progression"},
    {"key": "tree5",          "name": "Verzweigt",           "desc": "5 Skill-Tree-Knoten kaufen",             "color": CYAN,        "cat": "progression"},
    {"key": "tree_full",      "name": "Vollständiger Baum",  "desc": "Skill-Tree komplett freischalten",       "color": (255,50,50), "cat": "progression"},
]
