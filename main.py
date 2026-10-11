import pygame, sys, os, asyncio

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

from config       import load_config, save_config
from localization import load_language
from constants    import RESOLUTIONS, SHIPS, WEAPONS

def build_fonts(screen=None):
    scale = 1.0
    if screen is not None:
        sw, sh = screen.get_size()
        scale  = min(sw / 1280, sh / 720)

    def pf(base_size):
        size = max(8, round(base_size * scale))
        font_path = os.path.join(BASE_DIR, "assets", "fonts", "pixel.ttf")
        if os.path.exists(font_path):
            return pygame.font.Font(font_path, size)
        try:    return pygame.font.SysFont("Consolas", size)
        except: return pygame.font.Font(None, size)
    return {"title":pf(52),"big":pf(38),"med":pf(24),"small":pf(17),"ui":pf(15)}

def auto_adapt_resolution(cfg):
    info   = pygame.display.Info()
    dw, dh = info.current_w, info.current_h
    if dw <= 0 or dh <= 0:
        return

    stored_w, stored_h = cfg["resolution"]

    if stored_w > dw or stored_h > dh:
        best = RESOLUTIONS[0]
        for res in RESOLUTIONS:
            if res[0] <= dw and res[1] <= dh:
                best = res
        cfg["resolution"] = list(best)

def create_window(cfg):
    w, h  = cfg["resolution"]
    flags = pygame.SCALED
    if cfg.get("fullscreen"): flags |= pygame.FULLSCREEN
    pygame.display.quit()
    pygame.display.init()
    pygame.display.set_caption("AstroSurvivor")
    icon_path = os.path.join(BASE_DIR, "assets", "icon.png")
    if os.path.exists(icon_path):
        pygame.display.set_icon(pygame.image.load(icon_path))
    pygame.mouse.set_visible(True)
    if cfg.get("vsync", True):
        return pygame.display.set_mode((w, h), flags, vsync=1)
    return pygame.display.set_mode((w, h), flags)

async def main():
    pygame.init()
    pygame.display.set_caption("AstroSurvivor")
    icon_path = os.path.join(BASE_DIR, "assets", "icon.png")
    if os.path.exists(icon_path):
        pygame.display.set_icon(pygame.image.load(icon_path))
    pygame.mouse.set_visible(False)

    cfg    = load_config()
    auto_adapt_resolution(cfg)
    save_config(cfg)
    load_language(cfg.get("language", "de"))
    screen = create_window(cfg)
    fonts  = build_fonts(screen)
    state  = "menu"

    from menus    import MainMenu, HangarMenu, SettingsMenu
    from gameplay import GamePlay

    try:
        import sounds as _snd
        _snd.init_sounds()
    except Exception:
        pass

    fps_font = pygame.font.SysFont("Consolas", 14)
    gp       = None

    while True:
        if state == "menu":
            pygame.mouse.set_visible(True)
            result = await MainMenu(screen, fonts, cfg).run()
            if result == "quit":       break
            elif result == "play":     state = "game"
            elif result == "hangar":   state = "hangar"
            elif result == "settings": state = "settings"

        elif state == "hangar":
            result = await HangarMenu(screen, fonts, cfg).run()
            if result == "quit":  break
            elif result == "play": state = "game"
            else:                  state = "menu"

        elif state == "settings":
            result = await SettingsMenu(screen, fonts, cfg).run()
            if result == "quit": break
            if result == "apply":
                auto_adapt_resolution(cfg)
                screen = create_window(cfg)
                fonts  = build_fonts(screen)
            load_language(cfg.get("language", "de"))
            state = "menu"

        elif state == "game":
            pygame.mouse.set_visible(False)
            pq         = cfg.get("particle_quality", "high")
            ship_idx   = min(cfg.get("selected_ship", 0), len(SHIPS) - 1)
            weapon_idx = min(cfg.get("selected_weapon", 0), len(WEAPONS) - 1)
            gp         = GamePlay(screen, fonts, cfg, ship_idx, weapon_idx, pq)
            try:
                import sounds as _snd
                _snd.start_music(master=cfg.get("master_volume", 80),
                                 music=cfg.get("music_volume", 70))
            except Exception:
                pass

            game_clock = pygame.time.Clock()
            running    = True
            while running:
                fps_cap = cfg.get("fps_cap", 0)
                raw = game_clock.tick(fps_cap) if fps_cap > 0 else game_clock.tick()
                dt = min(raw / 1000.0, 0.05)

                gp.mouse_pos = pygame.mouse.get_pos()

                result = gp.handle_events()
                if result == "quit":
                    save_config(cfg)
                    pygame.quit(); return
                elif result == "menu":
                    try:
                        import sounds as _snd; _snd.stop_music()
                    except Exception: pass
                    state = "menu"; running = False; break
                elif result == "pause_settings":
                    from menus import SettingsMenu
                    pygame.mouse.set_visible(True)
                    sr = await SettingsMenu(screen, fonts, cfg).run()
                    if sr == "apply":
                        auto_adapt_resolution(cfg)
                        screen = create_window(cfg)
                        fonts  = build_fonts(screen)
                        gp.screen = screen
                        gp.sw, gp.sh = screen.get_size()
                    load_language(cfg.get("language", "de"))
                    try:
                        import sounds as _snd
                        _snd.set_music_volume(cfg.get("master_volume",80), cfg.get("music_volume",70))
                    except Exception: pass
                    gp.state = "paused"
                    pygame.mouse.set_visible(True)

                if gp.state == "menu_return":
                    try:
                        import sounds as _snd; _snd.stop_music()
                    except Exception: pass
                    state = "menu"; running = False; break
                elif gp.state == "restart":
                    pygame.mouse.set_visible(False)
                    gp = GamePlay(screen, fonts, cfg, ship_idx, weapon_idx, pq)
                    continue

                if gp.state == "playing":
                    gp.update(dt)

                gp.draw()

                if cfg.get("show_fps"):
                    fps_s = fps_font.render(f"FPS: {int(game_clock.get_fps())}", True, (160,160,160))
                    screen.blit(fps_s, (screen.get_width()-80, 4))

                pygame.display.flip()
                await asyncio.sleep(0)

    save_config(cfg)
    pygame.quit()

asyncio.run(main())
