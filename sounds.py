import pygame, math, array, random

_mixer_ok = False
_sounds   = {}

def init_sounds():
    global _mixer_ok
    if _mixer_ok:
        return
    try:
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.init()
        pygame.mixer.set_num_channels(32)
        _mixer_ok = True
        _build_all()
    except Exception:
        _mixer_ok = False

SAMPLE_RATE = 44100

def _make_buf(n):
    return array.array('h', [0] * (n * 2))

def _env(i, n, attack=0.01, release=0.15):
    t = i / max(n, 1)
    a = min(t / attack, 1.0) if attack > 0 else 1.0
    r = max(0.0, 1.0 - (t - (1 - release)) / release) if t > (1 - release) else 1.0
    return a * r

def _sine(f, t):   return math.sin(2 * math.pi * f * t)
def _square(f, t): return 1.0 if math.sin(2 * math.pi * f * t) >= 0 else -1.0
def _saw(f, t):    return 2 * ((f * t) % 1.0) - 1.0
def _noise():      return random.uniform(-1, 1)

def _make_sound(gen_fn, duration, volume=0.4):
    n = int(SAMPLE_RATE * duration)
    buf = _make_buf(n)
    for i in range(n):
        t   = i / SAMPLE_RATE
        val = int(gen_fn(i, t) * volume * 32767)
        val = max(-32767, min(32767, val))
        buf[i * 2]     = val
        buf[i * 2 + 1] = val
    return pygame.mixer.Sound(buffer=buf)

def _snd_blaster():
    def gen(i, t):
        freq = 420 * (1 - t * 4)
        s = _sine(max(60, freq), t) * 0.75 + _sine(max(60, freq) * 1.5, t) * 0.25
        return s * _env(i, int(SAMPLE_RATE * 0.09), attack=0.005, release=0.55)
    return _make_sound(gen, 0.09, 0.22)

def _snd_laser():
    def gen(i, t):
        freq = 1200 + 400 * math.sin(t * 80)
        return _sine(freq, t) * _env(i, int(SAMPLE_RATE * 0.08), release=0.5)
    return _make_sound(gen, 0.08, 0.3)

def _snd_missile():
    def gen(i, t):
        n  = _noise() * 0.4
        sw = _saw(120 * (1 - t * 0.5), t) * 0.6
        return (n + sw) * _env(i, int(SAMPLE_RATE * 0.25), attack=0.05, release=0.3)
    return _make_sound(gen, 0.25, 0.45)

def _snd_shotgun():
    def gen(i, t):
        n = _noise()
        return n * _env(i, int(SAMPLE_RATE * 0.10), attack=0.0, release=0.6)
    return _make_sound(gen, 0.10, 0.5)

def _snd_plasma():
    def gen(i, t):
        freq = 200 + 600 * (1 - t)
        return (_sine(freq, t) * 0.7 + _sine(freq * 1.5, t) * 0.3) * _env(i, int(SAMPLE_RATE * 0.20))
    return _make_sound(gen, 0.20, 0.4)

def _snd_hit():
    def gen(i, t):
        return _noise() * _env(i, int(SAMPLE_RATE * 0.06), attack=0.0, release=0.8)
    return _make_sound(gen, 0.06, 0.3)

def _snd_player_hit():
    def gen(i, t):
        freq = 120 * (1 - t * 0.5)
        return (_noise() * 0.5 + _square(freq, t) * 0.5) * _env(i, int(SAMPLE_RATE * 0.18), release=0.4)
    return _make_sound(gen, 0.18, 0.5)

def _snd_explosion():
    def gen(i, t):
        return _noise() * _env(i, int(SAMPLE_RATE * 0.40), attack=0.01, release=0.5)
    return _make_sound(gen, 0.40, 0.55)

def _snd_levelup():
    notes = [523, 659, 784, 1047]
    dur   = 0.10
    total = dur * len(notes)
    n     = int(SAMPLE_RATE * total)
    def gen(i, t):
        note_i = min(int(t / dur), len(notes) - 1)
        f = notes[note_i]
        local_t = t - note_i * dur
        env = min(local_t / 0.005, 1.0) * max(0.0, 1.0 - (local_t - 0.07) / 0.03)
        return _sine(f, t) * env
    return _make_sound(gen, total, 0.45)

def _snd_wave_done():
    notes = [392, 523, 659, 784]
    dur   = 0.12
    total = dur * len(notes)
    def gen(i, t):
        ni  = min(int(t / dur), len(notes) - 1)
        f   = notes[ni]
        lt  = t - ni * dur
        env = min(lt / 0.01, 1.0) * max(0.0, 1.0 - (lt - 0.09) / 0.03)
        return (_sine(f, t) + _sine(f * 2, t) * 0.3) * env * 0.5
    return _make_sound(gen, total, 0.4)

def _snd_gameover():
    notes = [523, 440, 349, 262]
    dur   = 0.20
    total = dur * len(notes)
    def gen(i, t):
        ni  = min(int(t / dur), len(notes) - 1)
        f   = notes[ni]
        lt  = t - ni * dur
        env = min(lt / 0.01, 1.0) * max(0.0, 1.0 - (lt - 0.15) / 0.05)
        return _sine(f, t) * env
    return _make_sound(gen, total, 0.5)

def _snd_click():
    def gen(i, t):
        return _sine(800 * (1 - t * 5), t) * _env(i, int(SAMPLE_RATE * 0.05), release=0.6)
    return _make_sound(gen, 0.05, 0.25)

def _snd_shield():
    def gen(i, t):
        return _sine(1800 - t * 3000, t) * _env(i, int(SAMPLE_RATE * 0.08), release=0.5)
    return _make_sound(gen, 0.08, 0.28)

def _snd_bomb():
    def gen(i, t):
        sub  = _sine(55 * (1 - t * 0.8), t) * 0.5
        mid  = _sine(110 * (1 - t * 1.2), t) * 0.3
        noise = _noise() * 0.6
        env  = _env(i, int(SAMPLE_RATE * 0.55), attack=0.003, release=0.55)
        return (sub + mid + noise) * env
    return _make_sound(gen, 0.55, 0.85)

def _snd_combo():
    notes = [660, 880, 1100]
    dur   = 0.06
    total = dur * len(notes)
    def gen(i, t):
        ni  = min(int(t / dur), len(notes) - 1)
        f   = notes[ni]
        lt  = t - ni * dur
        env = min(lt / 0.005, 1.0) * max(0.0, 1.0 - (lt - 0.04) / 0.02)
        return _sine(f, t) * env
    return _make_sound(gen, total, 0.35)

def _snd_powerup():
    def gen(i, t):
        f1 = _sine(880, t) * 0.6
        f2 = _sine(1320, t) * 0.4
        return (f1 + f2) * _env(i, int(SAMPLE_RATE * 0.18), attack=0.01, release=0.45)
    return _make_sound(gen, 0.18, 0.38)

def _snd_burn():
    def gen(i, t):
        return _noise() * 0.4 * _env(i, int(SAMPLE_RATE * 0.12), attack=0.0, release=0.7)
    return _make_sound(gen, 0.12, 0.18)

def _snd_music():
    BPM   = 135
    beat  = 60.0 / BPM
    total = beat * 16
    n     = int(SAMPLE_RATE * total)
    buf   = array.array('h', [0] * (n * 2))

    def add(freq, sb, db, wavefn, vol, atk=0.01, rel=0.3):
        t0 = sb * beat
        dur = db * beat
        si  = int(t0 * SAMPLE_RATE)
        ni  = min(n - si, int(dur * SAMPLE_RATE))
        if ni <= 0: return
        for j in range(ni):
            t   = j / SAMPLE_RATE
            e   = min(t / max(atk * dur, 1e-5), 1.0)
            e  *= max(0.0, 1.0 - max(0.0, t - dur * (1 - rel)) / (dur * rel + 1e-5))
            v   = int(wavefn(freq, t0 + t) * e * vol * 32767)
            v   = max(-32767, min(32767, v))
            idx = si + j
            buf[idx*2]   = max(-32767, min(32767, buf[idx*2]   + v))
            buf[idx*2+1] = max(-32767, min(32767, buf[idx*2+1] + v))

    def sw(f, t):  return _sine(f, t) * 0.6 + _sine(f * 1.004, t) * 0.4
    def sqb(f, t): return _square(f, t) * 0.5 + _sine(f * 0.5, t) * 0.5
    def ld(f, t):  return _square(f, t) * 0.55 + _sine(f * 2, t) * 0.3 + _sine(f * 3, t) * 0.15

    pads = [
        (220,0,2),(330,0,2),(440,0,2),
        (175,2,2),(262,2,2),(392,2,2),
        (220,4,2),(330,4,2),(523,4,2),
        (196,6,2),(294,6,2),(392,6,2),
        (220,8,2),(330,8,2),(440,8,2),
        (175,10,2),(262,10,2),(440,10,2),
        (131,12,2),(196,12,2),(330,12,2),
        (196,14,2),(294,14,2),(392,14,2),
    ]
    for f,sb,db in pads:
        add(f, sb, db, sw, 0.08, atk=0.12, rel=0.35)

    bass = [
        (110,0,0.8),(110,1,0.8),(165,2,0.6),(110,2.75,0.25),
        (88, 4,0.8),(88, 5,0.8),(131,6,0.8),(98, 7,0.8),
        (110,8,0.8),(110,9,0.8),(165,10,0.6),(220,10.75,0.25),
        (88,12,0.8),(131,13,0.8),(165,14,0.8),(110,15,0.8),
    ]
    for f,sb,db in bass:
        add(f, sb, db, sqb, 0.30, atk=0.01, rel=0.38)

    mel = [
        (440,0,0.75),(330,1,0.5),(440,1.5,0.5),
        (523,2,0.75),(440,3,0.9),
        (392,4,0.75),(330,5,0.5),(294,5.5,0.5),
        (330,6,1.0), (262,7,0.5),(220,7.5,0.5),
        (440,8,0.75),(330,9,0.5),(523,9.5,0.5),
        (587,10,0.75),(523,11,0.5),(440,11.5,0.5),
        (392,12,0.75),(440,13,0.5),(330,13.5,0.5),
        (220,14,2.0),
    ]
    for f,sb,db in mel:
        add(f, sb, db, ld, 0.26, atk=0.01, rel=0.28)

    arp = [440,659,880,659]
    for bar in range(4):
        for i in range(16):
            add(arp[i % 4], bar*4 + i*0.25, 0.18, _sine, 0.06, atk=0.02, rel=0.5)

    return pygame.mixer.Sound(buffer=buf)

_music_channel = None

def start_music(vol=0.45, master=80, music=70):
    global _music_channel
    if not _mixer_ok: return
    if "music" not in _sounds:
        try: _sounds["music"] = _snd_music()
        except Exception: return
    _music_channel = pygame.mixer.Channel(6)
    _music_channel.set_volume(vol * (master/100) * (music/100))
    _music_channel.play(_sounds["music"], loops=-1)

def stop_music():
    global _music_channel
    if _music_channel:
        _music_channel.fadeout(800)
        _music_channel = None

def set_music_volume(master, music_vol):
    if _music_channel:
        _music_channel.set_volume(0.45 * (master/100) * (music_vol/100))

def _build_all():
    global _sounds
    builders = {
        "blaster":  _snd_blaster,
        "laser":    _snd_laser,
        "missile":  _snd_missile,
        "shotgun":  _snd_shotgun,
        "plasma":   _snd_plasma,
        "hit":      _snd_hit,
        "player_hit": _snd_player_hit,
        "explosion":  _snd_explosion,
        "levelup":    _snd_levelup,
        "wave_done":  _snd_wave_done,
        "gameover":   _snd_gameover,
        "click":      _snd_click,
        "shield":     _snd_shield,
        "bomb":       _snd_bomb,
        "combo":      _snd_combo,
        "powerup":    _snd_powerup,
        "burn":       _snd_burn,
    }
    for key, fn in builders.items():
        try:
            _sounds[key] = fn()
        except Exception:
            pass

def play(key, volume_override=None):
    if not _mixer_ok:
        return
    snd = _sounds.get(key)
    if snd:
        if volume_override is not None:
            ch = snd.play()
            if ch:
                ch.set_volume(volume_override)
        else:
            snd.play()

def set_volumes(master, sfx, music):
    if not _mixer_ok:
        return
    sfx_v = (master / 100) * (sfx / 100)
    for key, snd in _sounds.items():
        if key == "music":
            continue
        snd.set_volume(sfx_v * 0.8)
    set_music_volume(master, music)

def play_weapon(weapon_key, master=80, sfx=90):
    vol = (master / 100) * (sfx / 100) * 0.6
    play(weapon_key, vol)
