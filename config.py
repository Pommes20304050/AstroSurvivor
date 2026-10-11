import json, os, sys

def _save_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

SAVE_PATH = os.path.join(_save_dir(), "save.json")

DEFAULT_CONFIG = {
    "resolution": [1280, 720],
    "fullscreen": False,
    "master_volume": 80,
    "music_volume": 70,
    "sfx_volume": 90,
    "language": "de",
    "show_fps": False,
    "vsync": True,
    "particle_quality": "high",
    "screen_shake": True,
    "selected_ship": 0,
    "selected_weapon": 0,
    "coins": 0,
    "max_wave_reached": 0,
    "unlocked_weapons": ["blaster"],
    "skill_tree": {},
    "ship_upgrades": {},
    "weapon_upgrades": {},
    "achievements": [],
    "autoaim_enabled": True,
}

def load_config():
    if os.path.exists(SAVE_PATH):
        try:
            with open(SAVE_PATH, "r") as f:
                data = json.load(f)
                cfg = DEFAULT_CONFIG.copy()
                cfg.update(data)
                if "skill_tree" not in cfg:
                    cfg["skill_tree"] = {}
                if "unlocked_weapons" not in cfg:
                    cfg["unlocked_weapons"] = ["blaster"]
                return cfg
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
    try:
        with open(SAVE_PATH, "w") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass
