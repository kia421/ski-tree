import pygame
import random
import math
import json
import os
import array
from datetime import date, timedelta

# ============================================================
# TINY TRAP RUN 10.0 - LEGENDARY EDITION
# Complete rebuilt version
# ============================================================

pygame.init()

WIDTH, HEIGHT = 1100, 680
FPS = 60
SAVE_FILE = "tiny_trap_run_10.json"

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TINY TRAP RUN 10.0 - LEGENDARY EDITION")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("consolas", 20, bold=True)
SMALL = pygame.font.SysFont("consolas", 14, bold=True)
BIG = pygame.font.SysFont("consolas", 40, bold=True)
HUGE = pygame.font.SysFont("consolas", 58, bold=True)

WHITE = (245, 246, 255)
BLACK = (10, 13, 25)
MUTED = (135, 150, 180)
GOLD = (255, 207, 80)
CYAN = (75, 225, 255)
PURPLE = (180, 115, 255)
RED = (255, 80, 100)
GREEN = (90, 235, 150)
PANEL = (28, 37, 62)

# ============================================================
# AUDIO
# ============================================================

AUDIO_OK = False
SOUNDS = {}

try:
    pygame.mixer.init(frequency=22050, size=-16, channels=1)
    AUDIO_OK = True
except pygame.error:
    pass


def make_tone(frequency, duration=0.1, volume=0.15):
    if not AUDIO_OK:
        return None

    rate = 22050
    count = int(rate * duration)
    samples = array.array("h")

    for i in range(count):
        fade = 1 - i / max(1, count)
        wave = math.sin(2 * math.pi * frequency * i / rate)
        samples.append(int(wave * 32767 * volume * fade))

    try:
        return pygame.mixer.Sound(buffer=samples.tobytes())
    except pygame.error:
        return None


if AUDIO_OK:
    SOUNDS = {
        "jump": make_tone(520),
        "coin": make_tone(880, 0.07),
        "gem": make_tone(1100, 0.13),
        "dash": make_tone(260, 0.12),
        "hit": make_tone(120, 0.18),
        "buy": make_tone(740, 0.14),
        "win": make_tone(980, 0.25),
        "checkpoint": make_tone(650, 0.15),
    }

# ============================================================
# BACKGROUND MUSIC - ADVENTURE 8-BIT
# ============================================================

MUSIC_TRACK = None
MUSIC_CHANNEL = None

def create_background_music():

    if not AUDIO_OK:
        return None

    sample_rate = 22050
    duration = 8.0
    total_samples = int(sample_rate * duration)

    # Adventure melody
    melody = [
        523, 659, 784, 659,
        587, 698, 880, 698,
        523, 659, 784, 988,
        880, 784, 659, 523
    ]

    bass = [
        131, 131, 165, 165,
        147, 147, 175, 175,
        131, 131, 196, 196,
        165, 165, 131, 131
    ]

    samples = array.array("h")

    for i in range(total_samples):

        t = i / sample_rate

        beat = int(t / 0.5) % 16
        beat_time = t % 0.5

        # Melody
        freq = melody[beat]

        melody_volume = (
            math.sin(math.pi * beat_time / 0.5) ** 0.7
        ) * 0.12

        melody_wave = math.sin(
            2 * math.pi * freq * t
        ) * melody_volume

        # Bass
        bass_freq = bass[beat]

        bass_wave = math.sin(
            2 * math.pi * bass_freq * t
        ) * 0.10

        # Soft background harmony
        harmony_wave = math.sin(
            2 * math.pi * (freq * 0.5) * t
        ) * 0.035

        final_wave = (
            melody_wave +
            bass_wave +
            harmony_wave
        )

        value = int(
            max(-1, min(1, final_wave)) * 32767
        )

        samples.append(value)

    try:
        return pygame.mixer.Sound(
            buffer=samples.tobytes()
        )
    except pygame.error:
        return None


def start_background_music():

    global MUSIC_TRACK, MUSIC_CHANNEL

    if not AUDIO_OK or not SAVE["sound"]:
        return

    if MUSIC_TRACK is None:
        MUSIC_TRACK = create_background_music()

    if MUSIC_TRACK is None:
        return

    try:
        if MUSIC_CHANNEL is None:
            pygame.mixer.set_num_channels(16)
            MUSIC_CHANNEL = pygame.mixer.Channel(15)

        if not MUSIC_CHANNEL.get_busy():
            MUSIC_CHANNEL.play(MUSIC_TRACK, loops=-1)
            MUSIC_CHANNEL.set_volume(0.45)

    except pygame.error:
        pass


def stop_background_music():

    if MUSIC_CHANNEL is not None:
        MUSIC_CHANNEL.stop()

# ============================================================
# SAVE SYSTEM
# ============================================================

DEFAULT_SAVE = {
    "coins": 0,
    "gems": 0,

    "level": 1,
    "best_level": 1,

    "rank": 0,

    "owned_skins": ["hero"],
    "owned_hats": ["none"],
    "owned_trails": ["none"],
    "owned_pets": ["none"],

    "skin": "hero",
    "hat": "none",
    "trail": "none",
    "pet": "none",

    "max_health": 3,
    "speed": 0,
    "dash": 0,

    "daily_date": "",
    "daily_streak": 0,

    "total_coins": 0,
    "total_gems": 0,

    "bosses_defeated": 0,
    "deaths": 0,
    "levels_completed": 0,

    "missions_date": "",
    "missions": [0, 0, 0],
    "mission_claimed": [False, False, False],

    "sound": True,
    "particles": True,
}


def load_game():
    data = {}

    # Load current save or older save
    for filename in (
        SAVE_FILE,
        "tiny_trap_run_9.json",
        "tiny_trap_run_8.json"
    ):
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    loaded = json.load(f)

                if isinstance(loaded, dict):
                    data = loaded
                    break

            except (OSError, ValueError, TypeError):
                print("Invalid save:", filename)

    result = DEFAULT_SAVE.copy()

    for key in (
        "owned_skins", "owned_hats",
        "owned_trails", "owned_pets",
        "missions", "mission_claimed"
    ):
        result[key] = DEFAULT_SAVE[key].copy()

    result.update(data)

    integer_fields = [
        "coins", "gems", "level", "best_level",
        "rank", "max_health", "speed", "dash",
        "daily_streak", "total_coins", "total_gems",
        "bosses_defeated", "deaths", "levels_completed"
    ]

    for key in integer_fields:
        try:
            result[key] = max(0, int(result[key]))
        except (ValueError, TypeError, OverflowError):
            result[key] = DEFAULT_SAVE[key]

    result["level"] = max(1, min(100, result["level"]))
    result["best_level"] = max(1, min(100, result["best_level"]))
    result["rank"] = min(6, result["rank"])
    result["max_health"] = max(3, min(6, result["max_health"]))
    result["speed"] = min(5, result["speed"])
    result["dash"] = min(3, result["dash"])

    for key in ("sound", "particles"):
        result[key] = bool(result[key])

    for key in (
        "owned_skins", "owned_hats",
        "owned_trails", "owned_pets"
    ):
        if not isinstance(result[key], list):
            result[key] = DEFAULT_SAVE[key].copy()

    for key in (
        "missions", "mission_claimed"
    ):
        if not isinstance(result[key], list) or len(result[key]) != 3:
            result[key] = DEFAULT_SAVE[key].copy()

    catalogs = {
        "skin": ("owned_skins", "hero"),
        "hat": ("owned_hats", "none"),
        "trail": ("owned_trails", "none"),
        "pet": ("owned_pets", "none"),
    }

    for equip, (owned, default) in catalogs.items():
        if result[equip] not in result[owned]:
            result[equip] = default

    safe_missions = []

    for value in result["missions"]:
        try:
            safe_missions.append(max(0, int(value)))
        except (ValueError, TypeError):
            safe_missions.append(0)

    result["missions"] = safe_missions
    result["mission_claimed"] = [
        bool(v) for v in result["mission_claimed"]
    ]

    return result


SAVE = load_game()


def save_game():
    temp = SAVE_FILE + ".tmp"

    try:
        with open(temp, "w", encoding="utf-8") as f:
            json.dump(SAVE, f, indent=2, ensure_ascii=False)

        os.replace(temp, SAVE_FILE)

    except (OSError, ValueError, TypeError) as error:
        print("Save error:", error)

        try:
            if os.path.exists(temp):
                os.remove(temp)
        except OSError:
            pass


def sound(name):
    if not SAVE["sound"]:
        return

    snd = SOUNDS.get(name)

    if snd:
        try:
            snd.play()
        except pygame.error:
            pass


# ============================================================
# HELPERS
# ============================================================

def clamp(value, low, high):
    return max(low, min(high, value))


def draw_text(surface, value, x, y, font=FONT,
              color=WHITE, center=False):

    img = font.render(str(value), True, color)
    rect = img.get_rect()

    if center:
        rect.center = (int(x), int(y))
    else:
        rect.topleft = (int(x), int(y))

    surface.blit(img, rect)
    return rect


def panel(surface, rect, color=PANEL, border=CYAN):
    pygame.draw.rect(surface, color, rect, border_radius=13)
    pygame.draw.rect(surface, border, rect, 2, border_radius=13)


def button(surface, rect, label, mouse,
           selected=False, disabled=False):

    hover = rect.collidepoint(mouse)

    color = (42, 58, 91)

    if hover:
        color = (58, 78, 119)

    if selected:
        color = (57, 81, 122)

    if disabled:
        color = (34, 38, 52)

    pygame.draw.rect(surface, color, rect, border_radius=9)

    pygame.draw.rect(
        surface,
        CYAN if selected or hover else (83, 102, 139),
        rect, 2, border_radius=9
    )

    draw_text(
        surface, label,
        rect.centerx, rect.centery,
        SMALL, MUTED if disabled else WHITE, True
    )


def glow(surface, position, color, radius=30, alpha=50):
    size = radius * 4
    layer = pygame.Surface((size, size), pygame.SRCALPHA)
    center = size // 2

    for i in range(5, 0, -1):
        r = int(radius * i / 5)
        a = int(alpha / (i * 0.75))

        pygame.draw.circle(
            layer, (*color, a),
            (center, center), r
        )

    surface.blit(
        layer,
        (int(position[0] - center), int(position[1] - center)),
        special_flags=pygame.BLEND_RGBA_ADD
    )


# ============================================================
# WORLDS
# ============================================================

WORLDS = [
    ("ENCHANTED FOREST", (27, 74, 62), (95, 235, 160)),
    ("EMBER KINGDOM", (90, 37, 42), (255, 115, 68)),
    ("FROZEN PEAKS", (33, 67, 110), (110, 220, 255)),
    ("GOLDEN DESERT", (115, 75, 35), (255, 207, 100)),
    ("SHADOW REALM", (48, 35, 83), (185, 120, 255)),
    ("SKY ISLANDS", (39, 83, 130), (150, 220, 255)),
    ("CRYSTAL CAVES", (43, 49, 105), (110, 255, 240)),
    ("VOLCANO", (105, 36, 30), (255, 90, 45)),
    ("VOID DIMENSION", (34, 27, 54), (215, 110, 255)),
    ("FINAL KINGDOM", (40, 40, 60), (255, 225, 115)),
]


def get_world(level):
    return WORLDS[min(9, (level - 1) // 10)]


# ============================================================
# SHOP CATALOGS
# ============================================================

SKINS = {
    "hero": ("Classic Adventurer", (65, 145, 245), 0),
    "ember": ("Ember Knight", (245, 85, 65), 180),
    "frost": ("Frost Mage", (105, 215, 255), 220),
    "royal": ("Royal Hero", (190, 105, 245), 350),
    "gold": ("Golden Legend", (255, 195, 55), 550),
    "forest": ("Forest Ranger", (75, 195, 115), 260),
    "shadow": ("Shadow Rogue", (95, 80, 140), 400),

    "ninja": ("Shadow Ninja", (45, 48, 65), 480),
    "ocean": ("Ocean Guardian", (45, 130, 210), 620),
    "lava": ("Lava Warrior", (230, 75, 35), 700),
    "angel": ("Sky Angel", (235, 235, 255), 850),
    "demon": ("Dark Demon", (130, 35, 65), 950),
    "neon": ("Neon Legend", (40, 255, 190), 1200),
    "cosmic": ("Cosmic Hero", (115, 75, 220), 1500),
}

HATS = {
    "none": ("No Hat", 0),
    "hood": ("Explorer Hood", 90),
    "crown": ("Tiny Crown", 250),
    "wizard": ("Wizard Hat", 180),
    "horns": ("Dragon Horns", 300),
    "pirate": ("Pirate Hat", 350),
    "samurai": ("Samurai Helmet", 500),
    "halo": ("Angel Halo", 650),
    "devil": ("Devil Horns", 700),
    "king": ("King Crown", 900),
    "legend": ("Legend Helmet", 1200),
}

TRAILS = {
    "none": ("No Trail", 0),
    "fire": ("Fire Trail", 130),
    "ice": ("Ice Trail", 150),
    "magic": ("Magic Trail", 200),
    "gold": ("Golden Trail", 280),
    "rainbow": ("Rainbow Trail", 400),
    "shadow": ("Shadow Trail", 450),
    "electric": ("Electric Trail", 550),
    "neon": ("Neon Trail", 650),
    "cosmic": ("Cosmic Trail", 900),
    "legend": ("Legend Trail", 1200),
}

PETS = {
    "none": ("No Pet", 0),
    "slime": ("Little Slime", 180),
    "bat": ("Night Bat", 240),
    "fox": ("Tiny Fox", 350),
    "dragon": ("Baby Dragon", 500),
    "owl": ("Magic Owl", 420),
    "wolf": ("Tiny Wolf", 550),
    "robot": ("Mini Robot", 650),
    "unicorn": ("Little Unicorn", 850),
    "phoenix": ("Baby Phoenix", 1100),
    "spirit": ("Cosmic Spirit", 1400),
}

CATALOGS = {
    "SKINS": SKINS,
    "HATS": HATS,
    "TRAILS": TRAILS,
    "PETS": PETS,
}

OWNED_KEYS = {
    "SKINS": "owned_skins",
    "HATS": "owned_hats",
    "TRAILS": "owned_trails",
    "PETS": "owned_pets",
}

EQUIP_KEYS = {
    "SKINS": "skin",
    "HATS": "hat",
    "TRAILS": "trail",
    "PETS": "pet",
}

RANKS = [
    ("BRONZE", (190, 120, 70)),
    ("SILVER", (190, 205, 220)),
    ("GOLD", GOLD),
    ("PLATINUM", (90, 225, 220)),
    ("DIAMOND", (100, 170, 255)),
    ("MASTER", (190, 100, 255)),
    ("LEGEND", (255, 100, 140)),
]

RANK_COSTS = [500, 1200, 2500, 5000, 9000, 15000]


# ============================================================
# PARTICLES
# ============================================================

particles = []


class Particle:
    def __init__(self, x, y, color, size=4):
        self.x = float(x)
        self.y = float(y)

        self.vx = random.uniform(-3.2, 3.2)
        self.vy = random.uniform(-4.5, 0.5)

        self.life = random.randint(20, 42)
        self.max_life = self.life

        self.color = color
        self.size = size

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.13
        self.life -= 1

    def draw(self, surface):
        if self.life <= 0:
            return

        size = max(
            1,
            int(self.size * self.life / self.max_life)
        )

        pygame.draw.rect(
            surface,
            self.color,
            (int(self.x), int(self.y), size, size)
        )


def burst(x, y, color, amount=12):
    if not SAVE["particles"]:
        return

    for _ in range(amount):
        particles.append(
            Particle(x, y, color, random.randint(2, 6))
        )


def update_particles():
    for p in particles[:]:
        p.update()

        if p.life <= 0:
            particles.remove(p)


# ============================================================
# CHARACTER DRAWING
# ============================================================

def draw_hero(surface, x, y, scale=1,
              skin_id=None, hat_id=None,
              frame=0, facing=1, airborne=False):

    skin_id = skin_id or SAVE["skin"]
    hat_id = hat_id or SAVE["hat"]

    body_color = SKINS.get(
        skin_id, SKINS["hero"]
    )[1]

    sprite = pygame.Surface((40, 55), pygame.SRCALPHA)

    bob = 0 if airborne else int(math.sin(frame * 0.22) * 1.2)
    cape_wave = int(math.sin(frame * 0.24) * 3)

    arm_wave = 0 if airborne else int(math.sin(frame * 0.32) * 3)
    leg_wave = 0 if airborne else int(math.sin(frame * 0.32) * 3)

    skin = (239, 187, 146)
    hair = (76, 43, 34)

    # Cape
    pygame.draw.polygon(sprite, (115, 42, 69), [
        (10, 14), (4, 20),
        (3 + cape_wave, 43),
        (19, 38), (23, 18)
    ])

    # Head and face
    pygame.draw.rect(sprite, skin, (16, 13, 9, 8))
    pygame.draw.rect(sprite, skin, (10, 4, 21, 16))

    pygame.draw.rect(
        sprite, (255, 213, 170),
        (13, 5, 15, 11)
    )

    pygame.draw.rect(sprite, hair, (9, 2, 23, 8))
    pygame.draw.rect(sprite, hair, (8, 6, 6, 12))
    pygame.draw.rect(sprite, hair, (27, 7, 5, 8))

    eye_x = 25 if facing >= 0 else 14

    pygame.draw.rect(
        sprite, (35, 36, 49),
        (eye_x, 10, 3, 3)
    )

    # Body
    pygame.draw.rect(sprite, (37, 42, 66), (11, 20, 20, 17))
    pygame.draw.rect(sprite, body_color, (10, 18, 20, 17))

    darker = tuple(max(0, c - 35) for c in body_color)

    pygame.draw.rect(sprite, darker, (10, 29, 20, 5))

    pygame.draw.rect(sprite, (105, 66, 39), (10, 31, 20, 3))
    pygame.draw.rect(sprite, GOLD, (19, 30, 4, 5))

    # Arms
    pygame.draw.rect(
        sprite, skin,
        (6, 21 + arm_wave, 5, 11)
    )

    pygame.draw.rect(
        sprite, skin,
        (30, 21 - arm_wave, 5, 11)
    )

    # Legs
    if airborne:
        left_leg, right_leg = -2, 2
    else:
        left_leg, right_leg = leg_wave, -leg_wave

    pygame.draw.rect(
        sprite, (43, 48, 69),
        (13 + left_leg, 35, 6, 9)
    )

    pygame.draw.rect(
        sprite, (43, 48, 69),
        (22 + right_leg, 35, 6, 9)
    )

    pygame.draw.rect(
        sprite, (93, 54, 35),
        (10 + left_leg, 42, 10, 6)
    )

    pygame.draw.rect(
        sprite, (93, 54, 35),
        (21 + right_leg, 42, 10, 6)
    )

    # Hats
    if hat_id == "hood":
        pygame.draw.rect(sprite, (44, 70, 100), (7, 2, 27, 9))

    elif hat_id in ("crown", "king"):
        pygame.draw.rect(sprite, GOLD, (12, 0, 18, 4))

        pygame.draw.polygon(sprite, GOLD, [
            (12, 2), (13, -5), (18, 1),
            (21, -6), (25, 1), (30, -4), (30, 3)
        ])

    elif hat_id == "wizard":
        pygame.draw.polygon(sprite, (104, 69, 175), [
            (7, 5), (21, -12), (34, 5)
        ])

        pygame.draw.rect(sprite, (104, 69, 175), (6, 4, 29, 4))

    elif hat_id in ("horns", "devil"):
        pygame.draw.polygon(sprite, RED, [
            (11, 6), (6, -3), (17, 4)
        ])

        pygame.draw.polygon(sprite, RED, [
            (27, 6), (34, -3), (22, 4)
        ])

    elif hat_id == "samurai":
        pygame.draw.rect(sprite, (65, 60, 75), (7, 0, 27, 7))
        pygame.draw.rect(sprite, GOLD, (17, 2, 7, 3))

    elif hat_id == "halo":
        pygame.draw.ellipse(sprite, GOLD, (10, -7, 21, 7), 3)

    elif hat_id == "pirate":
        pygame.draw.ellipse(sprite, BLACK, (7, 0, 28, 8))

    elif hat_id == "legend":
        pygame.draw.rect(sprite, (100, 80, 170), (7, 0, 27, 8))
        pygame.draw.rect(sprite, GOLD, (15, 1, 11, 4))

    if facing < 0:
        sprite = pygame.transform.flip(sprite, True, False)

    scaled = pygame.transform.scale(
        sprite,
        (int(40 * scale), int(55 * scale))
    )

    surface.blit(scaled, (int(x), int(y + bob * scale)))


# ============================================================
# PLATFORM
# ============================================================

class Platform:
    def __init__(self, x, y, width, height=20, kind="normal"):
        self.rect = pygame.Rect(x, y, width, height)

        self.kind = kind
        self.active = True

        self.origin_x = x
        self.previous_x = x

        self.phase = random.random() * math.pi * 2
        self.crumble = 0

    def update(self):
        self.previous_x = self.rect.x

        if self.kind == "moving":
            self.phase += 0.035

            self.rect.x = int(
                self.origin_x + math.sin(self.phase) * 65
            )

        if self.kind == "crumble" and self.crumble > 0:
            self.crumble += 1

            if self.crumble > 48:
                self.active = False

    def draw(self, surface, camera, accent):
        if not self.active:
            return

        r = self.rect.move(-int(camera), 0)

        colors = {
            "normal": (48, 77, 94),
            "moving": (60, 140, 170),
            "crumble": (145, 100, 70),
        }

        pygame.draw.rect(
            surface, colors[self.kind],
            r, border_radius=5
        )

        pygame.draw.rect(
            surface, accent,
            (r.x, r.y, r.w, 5),
            border_radius=3
        )

        if self.kind == "crumble":
            pygame.draw.line(
                surface, (225, 190, 135),
                (r.x + 15, r.y + 8),
                (r.x + 35, r.y + 17), 2
            )


# ============================================================
# LEVEL GENERATION
# ============================================================

class Level:
    def __init__(self, number):
        self.number = number

        self.name, self.bg, self.accent = get_world(number)

        self.length = 3900 + number * 75

        self.platforms = []
        self.coins = []
        self.gems = []
        self.spikes = []
        self.powerups = []
        self.checkpoints = []

        self.boss = None
        self.boss_hp = 0
        self.boss_max_hp = 0
        self.boss_timer = 0
        self.projectiles = []

        self.exit = pygame.Rect(0, 0, 45, 70)

        self.generate()

    def generate(self):
        # Safe starting platform
        self.platforms.append(
            Platform(0, 575, 500, 105)
        )

        x = 450
        y = 525

        while x < self.length - 600:

            gap = random.randint(45, 85)
            width = random.randint(150, 230)

            # Keep platform heights reachable
            y += random.randint(-35, 35)
            y = clamp(y, 405, 550)

            kind = random.choices(
                ["normal", "moving", "crumble"],
                weights=[72, 15, 13]
            )[0]

            px = x + gap

            platform = Platform(
                px, y, width, 20, kind
            )

            self.platforms.append(platform)

            # Coins
            if random.random() < 0.85:
                for j in range(random.randint(1, 3)):
                    self.coins.append(
                        pygame.Rect(
                            px + 35 + j * 30,
                            y - 42 - (j % 2) * 9,
                            16, 16
                        )
                    )

            # Gems
            if random.random() < 0.16:
                self.gems.append(
                    pygame.Rect(
                        px + width // 2,
                        y - 78,
                        18, 18
                    )
                )

            # Spikes
            if width > 175 and random.random() < 0.20:
                self.spikes.append(
                    pygame.Rect(
                        px + width // 2,
                        y - 19,
                        30, 19
                    )
                )

            # Health pickup
            if random.random() < 0.10:
                self.powerups.append(
                    pygame.Rect(
                        px + width // 2,
                        y - 88,
                        22, 22
                    )
                )

            x += gap + width

        # Safe ending platform
        self.platforms.append(
            Platform(
                self.length - 600,
                575, 650, 105
            )
        )

        self.exit = pygame.Rect(
            self.length - 170,
            505, 45, 70
        )

        # Checkpoints
        for p in self.platforms[3::5]:
            self.checkpoints.append(
                pygame.Rect(
                    p.rect.centerx,
                    p.rect.y - 54,
                    14, 54
                )
            )

        # Boss levels
        if self.number % 10 == 0:
            self.boss = pygame.Rect(
                self.length - 650,
                405, 105, 130
            )

            self.boss_max_hp = 5 + self.number // 10
            self.boss_hp = self.boss_max_hp


# ============================================================
# PLAYER
# ============================================================

class Player:
    def __init__(self):
        self.rect = pygame.Rect(90, 480, 40, 50)

        self.vx = 0.0
        self.vy = 0.0

        self.speed = 5.0 + SAVE["speed"] * 0.4
        self.jump_power = -12.5

        self.grounded = False
        self.standing_platform = None

        self.double_jump = True

        self.dash_ready = True
        self.dash_timer = 0

        self.facing = 1
        self.animation = 0

        self.health = SAVE["max_health"]
        self.invincible = 0

        self.checkpoint = (90, 480)
        self.last_checkpoint = -1

        self.dead = False

        self.trail = []

    def jump(self):
        if self.grounded:
            self.vy = self.jump_power

            self.grounded = False
            self.standing_platform = None

            sound("jump")
            burst(
                self.rect.centerx,
                self.rect.bottom,
                CYAN, 7
            )

        elif self.double_jump:
            self.vy = self.jump_power * 0.88
            self.double_jump = False

            sound("jump")

            burst(
                self.rect.centerx,
                self.rect.centery,
                PURPLE, 13
            )

    def dash(self):
        if not self.dash_ready:
            return

        self.dash_timer = 10 + SAVE["dash"] * 2

        self.vx = self.facing * (15 + SAVE["dash"])
        self.vy = 0

        self.dash_ready = False

        sound("dash")

        burst(
            self.rect.centerx,
            self.rect.centery,
            CYAN, 15
        )

    def respawn(self):
        self.rect.topleft = self.checkpoint

        self.vx = 0
        self.vy = 0

        self.health = SAVE["max_health"]

        self.invincible = 100

        self.dash_ready = True
        self.double_jump = True

        self.grounded = False
        self.standing_platform = None

        self.dead = False
        self.trail.clear()

    def update(self, platforms, keys):

        self.animation += 1

        if self.invincible > 0:
            self.invincible -= 1

        # Follow moving platform
        if (
            self.grounded
            and self.standing_platform
            and self.standing_platform.active
        ):
            p = self.standing_platform

            self.rect.x += p.rect.x - p.previous_x

        # Input
        if self.dash_timer > 0:
            self.dash_timer -= 1

        else:
            self.vx = 0

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.vx = -self.speed
                self.facing = -1

            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.vx = self.speed
                self.facing = 1

            self.vy = min(self.vy + 0.58, 15)

        # Horizontal movement
        self.rect.x += int(self.vx)

        for p in platforms:
            if not p.active:
                continue

            if not self.rect.colliderect(p.rect):
                continue

            if self.vx > 0:
                self.rect.right = p.rect.left

            elif self.vx < 0:
                self.rect.left = p.rect.right

        # Vertical movement
        old_bottom = self.rect.bottom
        old_top = self.rect.top

        self.rect.y += int(self.vy)

        self.grounded = False
        self.standing_platform = None

        for p in platforms:
            if not p.active:
                continue

            if not self.rect.colliderect(p.rect):
                continue

            # Landing
            if self.vy >= 0 and old_bottom <= p.rect.top + 14:

                self.rect.bottom = p.rect.top

                self.vy = 0
                self.grounded = True
                self.standing_platform = p

                self.double_jump = True
                self.dash_ready = True

                if p.kind == "crumble" and p.crumble == 0:
                    p.crumble = 1

            # Ceiling
            elif self.vy < 0 and old_top >= p.rect.bottom - 8:

                self.rect.top = p.rect.bottom
                self.vy = 1

        self.rect.left = max(0, self.rect.left)

        # Instant fall detection
        if self.rect.top >= HEIGHT:
            self.dead = True

        # Trail
        self.trail.append(
            (self.rect.centerx, self.rect.centery)
        )

        if len(self.trail) > 12:
            self.trail.pop(0)

    def draw(self, surface, camera):

        x = self.rect.x - camera
        y = self.rect.y

        trail_colors = {
            "fire": (255, 100, 55),
            "ice": (95, 215, 255),
            "magic": (185, 110, 255),
            "gold": GOLD,
            "rainbow": (255, 100, 200),
            "shadow": (100, 90, 150),
            "electric": CYAN,
            "neon": GREEN,
            "cosmic": PURPLE,
            "legend": GOLD,
        }

        trail_color = trail_colors.get(SAVE["trail"])

        if trail_color:
            for i, point in enumerate(self.trail):
                ratio = i / max(1, len(self.trail))
                radius = max(2, int(7 * ratio))

                pygame.draw.circle(
                    surface,
                    trail_color,
                    (
                        int(point[0] - camera),
                        int(point[1])
                    ),
                    radius
                )

        if self.invincible > 0 and self.invincible % 8 < 4:
            return

        # No unwanted circle around character
        draw_hero(
            surface,
            x, y,
            skin_id=SAVE["skin"],
            hat_id=SAVE["hat"],
            frame=self.animation,
            facing=self.facing,
            airborne=not self.grounded
        )

        # Pets
        pet = SAVE["pet"]

        if pet != "none":

            pet_colors = {
                "slime": GREEN,
                "bat": PURPLE,
                "fox": (255, 145, 65),
                "dragon": CYAN,
                "owl": (190, 155, 110),
                "wolf": (160, 170, 185),
                "robot": (100, 190, 210),
                "unicorn": (235, 180, 255),
                "phoenix": (255, 100, 45),
                "spirit": PURPLE,
            }

            color = pet_colors.get(pet, GREEN)

            px = int(x - 34)
            py = int(
                y + 20 + math.sin(self.animation * 0.12) * 7
            )

            pygame.draw.ellipse(
                surface, color,
                (px, py, 25, 19)
            )

            pygame.draw.circle(
                surface, WHITE,
                (px + 8, py + 7), 2
            )

            pygame.draw.circle(
                surface, WHITE,
                (px + 17, py + 7), 2
            )


# ============================================================
# BACKGROUND
# ============================================================

STARS = [
    (
        random.randrange(WIDTH),
        random.randrange(HEIGHT),
        random.randint(1, 3)
    )
    for _ in range(100)
]


def draw_background(surface, camera, level, tick):

    surface.fill(level.bg)

    color = tuple(
        int(level.bg[j] * 0.82 + level.accent[j] * 0.18)
        for j in range(3)
    )

    for i in range(12):
        pygame.draw.rect(
            surface, color,
            (0, i * 58, WIDTH, 58)
        )

    for sx, sy, size in STARS:
        px = (sx - int(camera * 0.10)) % WIDTH

        pygame.draw.circle(
            surface,
            (190, 215, 240),
            (px, sy), size
        )

    for i in range(-1, 9):
        x = i * 200 - int(camera * 0.22) % 200

        pygame.draw.polygon(
            surface, (30, 48, 65),
            [
                (x, 575),
                (x + 100, 330),
                (x + 200, 575)
            ]
        )

    for i in range(-1, 12):
        x = i * 140 - int(camera * 0.40) % 140

        pygame.draw.polygon(
            surface, (18, 35, 48),
            [
                (x, 575),
                (x + 55, 440),
                (x + 115, 575)
            ]
        )

    pygame.draw.rect(
        surface, (17, 29, 40),
        (0, 575, WIDTH, 105)
    )

    pygame.draw.line(
        surface, level.accent,
        (0, 575), (WIDTH, 575), 3
    )


# ============================================================
# BOSS
# ============================================================

def update_boss(level, player):

    if level.boss is None:
        return

    level.boss_timer += 1

    boss = level.boss

    if level.boss_timer >= 105:

        level.boss_timer = 0

        projectile = pygame.Rect(
            boss.centerx - 10,
            boss.centery,
            20, 20
        )

        direction = (
            -1 if player.rect.centerx < boss.centerx else 1
        )

        level.projectiles.append({
            "rect": projectile,
            "vx": direction * 5
        })

    for item in level.projectiles[:]:

        item["rect"].x += item["vx"]

        if abs(item["rect"].x - player.rect.x) > 1400:
            level.projectiles.remove(item)
            continue

        if item["rect"].colliderect(player.rect):

            if player.invincible == 0:
                player.health -= 1
                player.invincible = 85

                player.vx = -5 if item["vx"] > 0 else 5
                player.vy = -5

                sound("hit")

                burst(
                    player.rect.centerx,
                    player.rect.centery,
                    RED, 18
                )

            level.projectiles.remove(item)

    # Boss stomp
    if player.rect.colliderect(boss):

        if player.vy >= 0 and player.rect.bottom < boss.top + 35:

            player.rect.bottom = boss.top
            player.vy = -9

            level.boss_hp -= 1

            sound("hit")

            burst(
                boss.centerx,
                boss.centery,
                GOLD, 20
            )

            if level.boss_hp <= 0:

                level.boss = None
                level.projectiles.clear()

                SAVE["bosses_defeated"] += 1

                SAVE["gems"] += 10
                SAVE["total_gems"] += 10

                sound("win")
                save_game()


def draw_boss(surface, level, camera):

    if level.boss is None:
        return

    r = level.boss.move(-int(camera), 0)

    pygame.draw.rect(
        surface, (76, 37, 72),
        r, border_radius=18
    )

    pygame.draw.rect(
        surface, (180, 75, 110),
        r, 4, border_radius=18
    )

    pygame.draw.polygon(
        surface, (220, 90, 110),
        [
            (r.left + 18, r.top + 15),
            (r.left - 3, r.top - 17),
            (r.left + 40, r.top + 16)
        ]
    )

    pygame.draw.polygon(
        surface, (220, 90, 110),
        [
            (r.right - 18, r.top + 15),
            (r.right + 3, r.top - 17),
            (r.right - 40, r.top + 16)
        ]
    )

    pygame.draw.circle(
        surface, GOLD,
        (r.centerx - 20, r.y + 43), 8
    )

    pygame.draw.circle(
        surface, GOLD,
        (r.centerx + 20, r.y + 43), 8
    )

    bar = pygame.Rect(
        r.x - 5, r.y - 23,
        r.w + 10, 10
    )

    pygame.draw.rect(surface, (35, 25, 42), bar)

    ratio = level.boss_hp / max(1, level.boss_max_hp)

    pygame.draw.rect(
        surface, RED,
        (bar.x, bar.y, int(bar.w * ratio), bar.h)
    )


# ============================================================
# GAME
# ============================================================

class Game:

    def __init__(self):

        self.state = "menu"

        self.level_number = SAVE["level"]

        self.level = None
        self.player = None

        self.camera = 0
        self.tick = 0

        self.paused = False

        self.message = ""
        self.message_timer = 0

        self.shop_category = "SKINS"
        self.shop_index = 0
        self.shop_scroll = 0

        self.buttons = {}

    def notify(self, message):
        self.message = message
        self.message_timer = 130

    # --------------------------------------------------------
    # LEVEL
    # --------------------------------------------------------

    def start_level(self, number):

        number = clamp(number, 1, 100)

        self.level_number = number

        self.level = Level(number)
        self.player = Player()

        self.camera = 0
        self.paused = False

        self.state = "game"

    # --------------------------------------------------------
    # DAILY
    # --------------------------------------------------------

    def reset_daily_missions(self):

        today = date.today().isoformat()

        if SAVE["missions_date"] != today:

            SAVE["missions_date"] = today

            SAVE["missions"] = [0, 0, 0]
            SAVE["mission_claimed"] = [False, False, False]

            save_game()

    def claim_daily_reward(self):

        today = date.today().isoformat()

        if SAVE["daily_date"] == today:
            self.notify("DAILY REWARD ALREADY CLAIMED")
            return

        yesterday = (
            date.today() - timedelta(days=1)
        ).isoformat()

        if SAVE["daily_date"] not in ("", yesterday):
            SAVE["daily_streak"] = 0

        SAVE["daily_date"] = today
        SAVE["daily_streak"] += 1

        reward = 50 + min(
            200,
            SAVE["daily_streak"] * 10
        )

        SAVE["coins"] += reward
        SAVE["total_coins"] += reward

        SAVE["gems"] += 2
        SAVE["total_gems"] += 2

        sound("win")
        save_game()

        self.notify(
            f"DAILY GIFT: +{reward} COINS, +2 GEMS"
        )

    def claim_mission(self, index):

        goals = [20, 5, 1]
        rewards = [80, 4, 120]

        if SAVE["mission_claimed"][index]:
            self.notify("REWARD ALREADY CLAIMED")
            return

        if SAVE["missions"][index] < goals[index]:
            self.notify("MISSION NOT COMPLETE")
            return

        SAVE["mission_claimed"][index] = True

        if index == 1:
            SAVE["gems"] += rewards[index]
            SAVE["total_gems"] += rewards[index]

        else:
            SAVE["coins"] += rewards[index]
            SAVE["total_coins"] += rewards[index]

        sound("win")
        save_game()

        self.notify("MISSION REWARD CLAIMED")

    # --------------------------------------------------------
    # DEATH
    # --------------------------------------------------------

    def kill_player(self):

        SAVE["deaths"] += 1

        self.player.respawn()

        sound("hit")

        self.notify("YOU FELL! CHECKPOINT RESTORED")

        save_game()

    def damage_player(self):

        if self.player.invincible > 0:
            return

        self.player.health -= 1
        self.player.invincible = 90

        sound("hit")

        burst(
            self.player.rect.centerx - self.camera,
            self.player.rect.centery,
            RED, 18
        )

        if self.player.health <= 0:

            SAVE["deaths"] += 1

            self.player.respawn()

            self.notify("CHECKPOINT RESTORED")

            save_game()

    # --------------------------------------------------------
    # COMPLETION
    # --------------------------------------------------------

    def complete_level(self):

        reward = 30 + self.level_number * 2

        SAVE["coins"] += reward
        SAVE["total_coins"] += reward

        SAVE["levels_completed"] += 1

        SAVE["missions"][2] = min(
            1,
            SAVE["missions"][2] + 1
        )

        next_level = min(
            100,
            self.level_number + 1
        )

        SAVE["best_level"] = max(
            SAVE["best_level"],
            next_level
        )

        SAVE["level"] = next_level

        sound("win")
        save_game()

        self.state = "complete"

        self.notify(
            "LEVEL COMPLETE! +" + str(reward)
        )

    # --------------------------------------------------------
    # SHOP
    # --------------------------------------------------------

    def buy_or_equip(self, item_id):

        category = self.shop_category

        catalog = CATALOGS[category]

        owned_key = OWNED_KEYS[category]
        equip_key = EQUIP_KEYS[category]

        if item_id not in catalog:
            return

        if item_id in SAVE[owned_key]:

            SAVE[equip_key] = item_id

            sound("buy")
            save_game()

            self.notify("ITEM EQUIPPED")
            return

        data = catalog[item_id]

        price = (
            data[2] if category == "SKINS"
            else data[1]
        )

        if SAVE["coins"] < price:

            self.notify("NOT ENOUGH COINS")
            return

        SAVE["coins"] -= price

        SAVE[owned_key].append(item_id)
        SAVE[equip_key] = item_id

        sound("buy")
        save_game()

        self.notify("PURCHASE SUCCESSFUL!")

    # --------------------------------------------------------
    # UPGRADES AND RANK
    # --------------------------------------------------------

    def get_upgrade_cost(self, upgrade):

        costs = {
            "health": 150 + SAVE["max_health"] * 100,
            "speed": 120 + SAVE["speed"] * 100,
            "dash": 180 + SAVE["dash"] * 120,
        }

        if upgrade == "rank":

            rank = SAVE["rank"]

            if rank >= len(RANKS) - 1:
                return None

            return RANK_COSTS[rank]

        return costs.get(upgrade)

    def buy_upgrade(self, upgrade):

        fields = {
            "health": "max_health",
            "speed": "speed",
            "dash": "dash",
        }

        limits = {
            "health": 6,
            "speed": 5,
            "dash": 3,
        }

        if upgrade == "rank":

            if SAVE["rank"] >= len(RANKS) - 1:
                self.notify("MAX RANK REACHED")
                return

            cost = self.get_upgrade_cost("rank")

            if SAVE["coins"] < cost:
                self.notify(
                    f"NEED {cost - SAVE['coins']} MORE COINS"
                )
                return

            SAVE["coins"] -= cost
            SAVE["rank"] += 1

            sound("win")
            save_game()

            self.notify(
                "RANK UP: " + RANKS[SAVE["rank"]][0]
            )
            return

        field = fields.get(upgrade)

        if field is None:
            return

        if SAVE[field] >= limits[upgrade]:
            self.notify("UPGRADE MAXED")
            return

        cost = self.get_upgrade_cost(upgrade)

        if SAVE["coins"] < cost:
            self.notify(
                f"NEED {cost - SAVE['coins']} MORE COINS"
            )
            return

        SAVE["coins"] -= cost
        SAVE[field] += 1

        sound("buy")
        save_game()

        self.notify("UPGRADE PURCHASED")

    # --------------------------------------------------------
    # GAME UPDATE
    # --------------------------------------------------------

    def update_game(self, keys):

        if self.paused:
            return

        self.tick += 1

        for platform in self.level.platforms:
            platform.update()

        self.player.update(
            self.level.platforms,
            keys
        )

        # Instant fall
        if self.player.dead:
            self.kill_player()
            return

        # Camera
        target = (
            self.player.rect.centerx - WIDTH * 0.38
        )

        self.camera = clamp(
            self.camera + (target - self.camera) * 0.10,
            0,
            max(0, self.level.length - WIDTH)
        )

        # Coins
        for coin in self.level.coins[:]:

            if self.player.rect.colliderect(coin):

                self.level.coins.remove(coin)

                SAVE["coins"] += 1
                SAVE["total_coins"] += 1

                SAVE["missions"][0] += 1

                sound("coin")

                burst(
                    coin.centerx - self.camera,
                    coin.centery,
                    GOLD, 8
                )

        # Gems
        for gem in self.level.gems[:]:

            if self.player.rect.colliderect(gem):

                self.level.gems.remove(gem)

                SAVE["gems"] += 1
                SAVE["total_gems"] += 1

                SAVE["missions"][1] += 1

                sound("gem")

                burst(
                    gem.centerx - self.camera,
                    gem.centery,
                    PURPLE, 12
                )

        # Health pickups
        for pickup in self.level.powerups[:]:

            if self.player.rect.colliderect(pickup):

                self.level.powerups.remove(pickup)

                self.player.health = min(
                    SAVE["max_health"],
                    self.player.health + 1
                )

                sound("gem")

                burst(
                    pickup.centerx - self.camera,
                    pickup.centery,
                    GREEN, 15
                )

        # Checkpoints
        for index, checkpoint in enumerate(
            self.level.checkpoints
        ):

            if self.player.rect.colliderect(checkpoint):

                if self.player.last_checkpoint != index:

                    self.player.last_checkpoint = index

                    self.player.checkpoint = (
                        checkpoint.centerx - 20,
                        checkpoint.top + 4
                    )

                    self.notify("CHECKPOINT SAVED")

                    sound("checkpoint")

                    burst(
                        checkpoint.centerx - self.camera,
                        checkpoint.centery,
                        GOLD, 15
                    )

        # Spikes
        for spike in self.level.spikes:

            if self.player.rect.colliderect(spike):

                self.damage_player()
                break

        # Boss
        update_boss(
            self.level,
            self.player
        )

        # Death from boss
        if self.player.health <= 0:

            SAVE["deaths"] += 1

            self.player.respawn()

            self.notify("CHECKPOINT RESTORED")

            save_game()
            return

        # Exit
        if self.player.rect.colliderect(self.level.exit):

            if self.level.boss is None:
                self.complete_level()
                return

        update_particles()

        if self.message_timer > 0:
            self.message_timer -= 1

    # --------------------------------------------------------
    # HUD
    # --------------------------------------------------------

    def draw_hud(self, surface):

        panel(
            surface,
            pygame.Rect(15, 14, 365, 91),
            (20, 28, 47),
            (70, 112, 155)
        )

        draw_text(
            surface,
            f"LEVEL {self.level_number}/100",
            29, 23, SMALL
        )

        draw_text(
            surface,
            "COINS " + str(SAVE["coins"]),
            29, 53, SMALL, GOLD
        )

        draw_text(
            surface,
            "GEMS " + str(SAVE["gems"]),
            170, 53, SMALL, PURPLE
        )

        rank_name, rank_color = RANKS[SAVE["rank"]]

        draw_text(
            surface,
            "RANK " + rank_name,
            29, 77, SMALL, rank_color
        )

        # Health
        for i in range(SAVE["max_health"]):

            color = (
                RED if i < self.player.health
                else (65, 53, 65)
            )

            pygame.draw.rect(
                surface,
                color,
                (WIDTH - 38 - i * 27, 28, 18, 18),
                border_radius=5
            )

        draw_text(
            surface,
            "A/D MOVE   SPACE JUMP   SHIFT DASH   ESC PAUSE",
            WIDTH // 2,
            HEIGHT - 20,
            SMALL, WHITE, True
        )

        if self.level.boss:

            draw_text(
                surface,
                "BOSS BATTLE",
                WIDTH // 2,
                28, FONT, RED, True
            )

    # --------------------------------------------------------
    # GAME DRAW
    # --------------------------------------------------------

    def draw_game(self, surface):

        draw_background(
            surface,
            self.camera,
            self.level,
            self.tick
        )

        for platform in self.level.platforms:

            if platform.rect.right < self.camera - 100:
                continue

            if platform.rect.left > self.camera + WIDTH + 100:
                continue

            platform.draw(
                surface,
                self.camera,
                self.level.accent
            )

        # Spikes
        for spike in self.level.spikes:

            r = spike.move(-int(self.camera), 0)

            pygame.draw.polygon(
                surface, RED,
                [
                    (r.left, r.bottom),
                    (r.centerx, r.top),
                    (r.right, r.bottom)
                ]
            )

        # Coins
        for coin in self.level.coins:

            x = int(coin.centerx - self.camera)
            y = coin.centery

            pygame.draw.circle(
                surface, GOLD, (x, y), 8
            )

            pygame.draw.circle(
                surface, (255, 242, 175),
                (x - 2, y - 2), 3
            )

        # Gems
        for gem in self.level.gems:

            x = int(gem.centerx - self.camera)
            y = gem.centery

            pygame.draw.polygon(
                surface, PURPLE,
                [
                    (x, y - 11),
                    (x + 9, y),
                    (x, y + 11),
                    (x - 9, y)
                ]
            )

        # Health pickups
        for pickup in self.level.powerups:

            x = int(pickup.centerx - self.camera)
            y = pickup.centery

            pygame.draw.circle(
                surface, GREEN, (x, y), 10
            )

            draw_text(
                surface, "+",
                x, y, SMALL, WHITE, True
            )

        # Checkpoints
        for cp in self.level.checkpoints:

            r = cp.move(-int(self.camera), 0)

            pygame.draw.rect(
                surface, MUTED, r
            )

            pygame.draw.polygon(
                surface, GOLD,
                [
                    (r.x + 13, r.y),
                    (r.x + 35, r.y + 10),
                    (r.x + 13, r.y + 22)
                ]
            )

        # Exit
        exit_rect = self.level.exit.move(
            -int(self.camera), 0
        )

        pygame.draw.rect(
            surface, (25, 39, 64),
            exit_rect,
            border_radius=7
        )

        pygame.draw.rect(
            surface, self.level.accent,
            exit_rect,
            3,
            border_radius=7
        )

        draw_text(
            surface,
            "EXIT",
            exit_rect.centerx,
            exit_rect.centery,
            SMALL, WHITE, True
        )

        # Boss
        draw_boss(
            surface,
            self.level,
            self.camera
        )

        # Projectiles
        for item in self.level.projectiles:

            r = item["rect"].move(
                -int(self.camera), 0
            )

            pygame.draw.circle(
                surface, RED, r.center, 9
            )

        # Player
        self.player.draw(
            surface,
            self.camera
        )

        for p in particles:
            p.draw(surface)

        self.draw_hud(surface)

        if self.message_timer > 0:

            draw_text(
                surface,
                self.message,
                WIDTH // 2,
                135,
                BIG, GOLD, True
            )

        if self.paused:
            self.draw_pause(surface)

    # --------------------------------------------------------
    # PAUSE
    # --------------------------------------------------------

    def draw_pause(self, surface):

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill((5, 8, 20, 205))

        surface.blit(overlay, (0, 0))

        draw_text(
            surface,
            "PAUSED",
            WIDTH // 2,
            220,
            BIG, WHITE, True
        )

        mouse = pygame.mouse.get_pos()

        self.buttons["pause"] = [
            ("RESUME", pygame.Rect(410, 300, 280, 48), "resume"),
            ("RESTART", pygame.Rect(410, 360, 280, 48), "restart"),
            ("MAIN MENU", pygame.Rect(410, 420, 280, 48), "menu"),
        ]

        for label, rect, action in self.buttons["pause"]:
            button(surface, rect, label, mouse)

    # --------------------------------------------------------
    # MENU
    # --------------------------------------------------------

    def draw_menu(self, surface):

        surface.fill((16, 21, 42))

        for i in range(8):

            pygame.draw.circle(
                surface,
                (26 + i * 2, 36 + i * 2, 65 + i * 2),
                (WIDTH // 2, 210),
                80 + i * 55,
                2
            )

        draw_text(
            surface,
            "TINY TRAP",
            WIDTH // 2,
            95, HUGE, WHITE, True
        )

        draw_text(
            surface,
            "RUN",
            WIDTH // 2,
            160, HUGE, CYAN, True
        )

        draw_text(
            surface,
            "LEGENDARY EDITION 10.0",
            WIDTH // 2,
            225, SMALL, MUTED, True
        )

        draw_hero(
            surface,
            WIDTH // 2 - 40,
            265,
            scale=2,
            frame=self.tick
        )

        mouse = pygame.mouse.get_pos()

        menu = [
            ("PLAY", pygame.Rect(410, 375, 280, 43), "play"),
            ("ITEM SHOP", pygame.Rect(410, 423, 280, 43), "shop"),
            ("UPGRADES & RANK", pygame.Rect(410, 471, 280, 43), "upgrades"),
            ("WORLDS", pygame.Rect(410, 519, 135, 38), "worlds"),
            ("SETTINGS", pygame.Rect(555, 519, 135, 38), "settings"),
            ("PROFILE", pygame.Rect(410, 563, 135, 38), "profile"),
            ("MISSIONS", pygame.Rect(555, 563, 135, 38), "missions"),
        ]

        self.buttons["menu"] = menu

        for label, rect, action in menu:
            button(surface, rect, label, mouse)

        draw_text(
            surface,
            "BEST LEVEL: " + str(SAVE["best_level"]),
            WIDTH // 2,
            635, SMALL, MUTED, True
        )

        draw_text(
            surface,
            f"COINS: {SAVE['coins']}   GEMS: {SAVE['gems']}",
            WIDTH // 2,
            655, SMALL, GOLD, True
        )

    # --------------------------------------------------------
    # SHOP
    # --------------------------------------------------------

    def draw_shop(self, surface):

        surface.fill((16, 22, 42))

        draw_text(
            surface, "ITEM SHOP",
            40, 25, BIG
        )

        draw_text(
            surface,
            "COINS: " + str(SAVE["coins"]),
            WIDTH - 210, 35, FONT, GOLD
        )

        draw_text(
            surface,
            "GEMS: " + str(SAVE["gems"]),
            WIDTH - 210, 65, FONT, PURPLE
        )

        mouse = pygame.mouse.get_pos()

        categories = [
            "SKINS", "HATS", "TRAILS", "PETS"
        ]

        self.buttons["shop_categories"] = []

        for i, cat in enumerate(categories):

            rect = pygame.Rect(
                40 + i * 160,
                105,
                145, 42
            )

            self.buttons["shop_categories"].append(
                (rect, cat)
            )

            button(
                surface, rect,
                cat, mouse,
                selected=self.shop_category == cat
            )

        # Preview
        preview = pygame.Rect(
            40, 170, 400, 445
        )

        panel(
            surface, preview,
            (26, 35, 60), PURPLE
        )

        draw_text(
            surface,
            "LIVE CHARACTER PREVIEW",
            240, 195,
            SMALL, CYAN, True
        )

        draw_hero(
            surface,
            180, 285,
            scale=3,
            frame=self.tick
        )

        pet_colors = {
            "slime": GREEN,
            "bat": PURPLE,
            "fox": (255, 150, 70),
            "dragon": CYAN,
            "owl": (190, 155, 110),
            "wolf": (160, 170, 185),
            "robot": CYAN,
            "unicorn": PURPLE,
            "phoenix": RED,
            "spirit": PURPLE,
        }

        if SAVE["pet"] != "none":

            color = pet_colors.get(
                SAVE["pet"], GREEN
            )

            pygame.draw.ellipse(
                surface, color,
                (300, 405, 55, 38)
            )

        draw_text(
            surface,
            "SKIN: " + SAVE["skin"].upper(),
            70, 520, SMALL
        )

        draw_text(
            surface,
            "HAT: " + SAVE["hat"].upper(),
            70, 545, SMALL
        )

        draw_text(
            surface,
            "PET: " + SAVE["pet"].upper(),
            70, 570, SMALL
        )

        draw_text(
            surface,
            "TRAIL: " + SAVE["trail"].upper(),
            70, 595, SMALL
        )

        # Listing
        listing = pygame.Rect(
            470, 170, 590, 445
        )

        panel(surface, listing)

        catalog = CATALOGS[self.shop_category]

        owned_key = OWNED_KEYS[self.shop_category]
        equip_key = EQUIP_KEYS[self.shop_category]

        items = list(catalog.items())

        max_scroll = max(
            0,
            len(items) * 63 - 425
        )

        self.shop_scroll = clamp(
            self.shop_scroll,
            0,
            max_scroll
        )

        self.buttons["shop_items"] = []

        # Clip items to listing area
        old_clip = surface.get_clip()

        surface.set_clip(
            pygame.Rect(480, 178, 570, 425)
        )

        for i, (item_id, data) in enumerate(items):

            y = 188 + i * 63 - self.shop_scroll

            rect = pygame.Rect(
                490, y, 550, 51
            )

            self.buttons["shop_items"].append(
                (rect, item_id)
            )

            button(
                surface,
                rect,
                "",
                mouse,
                selected=i == self.shop_index
            )

            name = data[0]

            price = (
                data[2]
                if self.shop_category == "SKINS"
                else data[1]
            )

            owned = item_id in SAVE[owned_key]
            equipped = SAVE[equip_key] == item_id

            draw_text(
                surface,
                name,
                rect.x + 17,
                rect.y + 16,
                SMALL
            )

            if equipped:
                status, color = "EQUIPPED", GREEN

            elif owned:
                status, color = "OWNED", CYAN

            else:
                status, color = str(price) + " COINS", GOLD

            draw_text(
                surface,
                status,
                rect.right - 125,
                rect.y + 16,
                SMALL, color
            )

        surface.set_clip(old_clip)

        self.buttons["shop_back"] = pygame.Rect(
            40, 630, 150, 36
        )

        button(
            surface,
            self.buttons["shop_back"],
            "BACK",
            mouse
        )

    # --------------------------------------------------------
    # UPGRADES AND RANK
    # --------------------------------------------------------

    def draw_upgrades(self, surface):

        surface.fill((16, 22, 42))

        draw_text(
            surface,
            "UPGRADES & RANK",
            WIDTH // 2,
            35, BIG, WHITE, True
        )

        draw_text(
            surface,
            "COINS: " + str(SAVE["coins"]),
            WIDTH // 2,
            85, FONT, GOLD, True
        )

        mouse = pygame.mouse.get_pos()

        options = [
            ("MAX HEALTH", "health", SAVE["max_health"], 6),
            ("MOVE SPEED", "speed", SAVE["speed"], 5),
            ("DASH POWER", "dash", SAVE["dash"], 3),
        ]

        self.buttons["upgrades"] = []

        for i, (label, key, value, maximum) in enumerate(options):

            rect = pygame.Rect(
                300,
                120 + i * 105,
                500, 78
            )

            panel(surface, rect)

            draw_text(
                surface,
                label,
                rect.x + 20,
                rect.y + 12,
                FONT
            )

            draw_text(
                surface,
                f"LEVEL {value}/{maximum}",
                rect.x + 20,
                rect.y + 47,
                SMALL, CYAN
            )

            cost = self.get_upgrade_cost(key)

            if value >= maximum:
                cost_text = "MAX LEVEL"
                cost_color = GREEN

            else:
                cost_text = f"COST: {cost} COINS"

                cost_color = (
                    GOLD if SAVE["coins"] >= cost
                    else RED
                )

            draw_text(
                surface,
                cost_text,
                rect.x + 220,
                rect.y + 47,
                SMALL, cost_color
            )

            button_rect = pygame.Rect(
                rect.right - 115,
                rect.y + 17,
                95, 43
            )

            self.buttons["upgrades"].append(
                (button_rect, key)
            )

            button(
                surface,
                button_rect,
                "MAXED" if value >= maximum else "BUY",
                mouse,
                disabled=value >= maximum
            )

        # Rank
        rank = SAVE["rank"]

        rank_name, rank_color = RANKS[rank]

        rank_rect = pygame.Rect(
            300, 440, 500, 85
        )

        panel(
            surface,
            rank_rect,
            (35, 30, 55),
            rank_color
        )

        draw_text(
            surface,
            "CURRENT RANK: " + rank_name,
            320, 452, FONT, rank_color
        )

        if rank < len(RANKS) - 1:

            next_name = RANKS[rank + 1][0]
            cost = self.get_upgrade_cost("rank")

            draw_text(
                surface,
                f"NEXT: {next_name}",
                320, 489, SMALL, WHITE
            )

            draw_text(
                surface,
                f"COST: {cost} COINS",
                490, 489, SMALL,
                GOLD if SAVE["coins"] >= cost else RED
            )

            rank_label = "RANK UP"

        else:
            rank_label = "MAX RANK"

        rank_button = pygame.Rect(
            680, 457, 100, 48
        )

        self.buttons["rank"] = rank_button

        button(
            surface,
            rank_button,
            rank_label,
            mouse,
            disabled=rank >= len(RANKS) - 1
        )

        self.buttons["upgrades_back"] = pygame.Rect(
            40, 620, 150, 40
        )

        button(
            surface,
            self.buttons["upgrades_back"],
            "BACK",
            mouse
        )

    # --------------------------------------------------------
    # WORLDS
    # --------------------------------------------------------

    def draw_worlds(self, surface):

        surface.fill((16, 22, 42))

        draw_text(
            surface,
            "CHOOSE YOUR WORLD",
            WIDTH // 2,
            45, BIG, WHITE, True
        )

        mouse = pygame.mouse.get_pos()

        self.buttons["worlds"] = []

        for i, (name, bg, accent) in enumerate(WORLDS):

            row = i // 2
            col = i % 2

            rect = pygame.Rect(
                160 + col * 410,
                120 + row * 100,
                360, 76
            )

            unlocked = (
                SAVE["best_level"] >= i * 10 + 1
            )

            panel(
                surface,
                rect,
                bg,
                accent
            )

            draw_text(
                surface,
                name,
                rect.x + 18,
                rect.y + 25,
                SMALL
            )

            draw_text(
                surface,
                "UNLOCKED" if unlocked else "LOCKED",
                rect.right - 105,
                rect.y + 27,
                SMALL,
                GREEN if unlocked else RED
            )

            self.buttons["worlds"].append(
                (rect, i, unlocked)
            )

        self.buttons["worlds_back"] = pygame.Rect(
            40, 620, 150, 40
        )

        button(
            surface,
            self.buttons["worlds_back"],
            "BACK", mouse
        )

    # --------------------------------------------------------
    # PROFILE
    # --------------------------------------------------------

    def draw_profile(self, surface):

        surface.fill((16, 22, 42))

        draw_text(
            surface,
            "PLAYER PROFILE",
            WIDTH // 2,
            45, BIG, WHITE, True
        )

        stats = [
            ("BEST LEVEL", SAVE["best_level"]),
            ("TOTAL COINS", SAVE["total_coins"]),
            ("TOTAL GEMS", SAVE["total_gems"]),
            ("BOSSES DEFEATED", SAVE["bosses_defeated"]),
            ("DEATHS", SAVE["deaths"]),
            ("LEVELS COMPLETED", SAVE["levels_completed"]),
            ("DAILY STREAK", SAVE["daily_streak"]),
            ("RANK", RANKS[SAVE["rank"]][0]),
            ("OWNED SKINS", len(SAVE["owned_skins"])),
            ("OWNED HATS", len(SAVE["owned_hats"])),
            ("OWNED PETS", len(SAVE["owned_pets"])),
            ("OWNED TRAILS", len(SAVE["owned_trails"])),
        ]

        for i, (label, value) in enumerate(stats):

            x = 110 + (i % 2) * 450
            y = 100 + (i // 2) * 82

            rect = pygame.Rect(
                x, y, 390, 65
            )

            panel(surface, rect)

            draw_text(
                surface,
                label,
                x + 18, y + 9,
                SMALL, MUTED
            )

            draw_text(
                surface,
                value,
                x + 18, y + 34,
                FONT, GOLD
            )

        self.buttons["profile_back"] = pygame.Rect(
            40, 620, 150, 40
        )

        button(
            surface,
            self.buttons["profile_back"],
            "BACK",
            pygame.mouse.get_pos()
        )

    # --------------------------------------------------------
    # MISSIONS
    # --------------------------------------------------------

    def draw_missions(self, surface):

        surface.fill((16, 22, 42))

        draw_text(
            surface,
            "DAILY MISSIONS",
            WIDTH // 2,
            45, BIG, WHITE, True
        )

        self.reset_daily_missions()

        descriptions = [
            "COLLECT 20 COINS",
            "COLLECT 5 GEMS",
            "COMPLETE 1 LEVEL",
        ]

        goals = [20, 5, 1]

        rewards = [
            "80 COINS",
            "4 GEMS",
            "120 COINS",
        ]

        self.buttons["missions"] = []

        mouse = pygame.mouse.get_pos()

        for i in range(3):

            rect = pygame.Rect(
                230,
                135 + i * 130,
                640, 95
            )

            panel(surface, rect)

            draw_text(
                surface,
                descriptions[i],
                rect.x + 20,
                rect.y + 13,
                FONT
            )

            value = min(
                goals[i],
                SAVE["missions"][i]
            )

            draw_text(
                surface,
                f"PROGRESS: {value}/{goals[i]}",
                rect.x + 20,
                rect.y + 48,
                SMALL, CYAN
            )

            draw_text(
                surface,
                "REWARD: " + rewards[i],
                rect.x + 280,
                rect.y + 48,
                SMALL, GOLD
            )

            button_rect = pygame.Rect(
                rect.right - 145,
                rect.y + 25,
                120, 43
            )

            self.buttons["missions"].append(
                (button_rect, i)
            )

            claimed = SAVE["mission_claimed"][i]
            complete = SAVE["missions"][i] >= goals[i]

            label = (
                "CLAIM" if complete and not claimed
                else "CLAIMED" if claimed
                else "LOCKED"
            )

            button(
                surface,
                button_rect,
                label,
                mouse,
                disabled=not complete or claimed
            )

        self.buttons["daily"] = pygame.Rect(
            405, 545, 290, 48
        )

        daily_claimed = (
            SAVE["daily_date"] == date.today().isoformat()
        )

        button(
            surface,
            self.buttons["daily"],
            "DAILY GIFT CLAIMED"
            if daily_claimed else "CLAIM DAILY GIFT",
            mouse,
            disabled=daily_claimed
        )

        self.buttons["missions_back"] = pygame.Rect(
            40, 620, 150, 40
        )

        button(
            surface,
            self.buttons["missions_back"],
            "BACK", mouse
        )

    # --------------------------------------------------------
    # SETTINGS
    # --------------------------------------------------------

    def draw_settings(self, surface):

        surface.fill((16, 22, 42))

        draw_text(
            surface,
            "SETTINGS",
            WIDTH // 2,
            60, BIG, WHITE, True
        )

        mouse = pygame.mouse.get_pos()

        self.buttons["settings"] = [
            (
                "SOUND: " + ("ON" if SAVE["sound"] else "OFF"),
                pygame.Rect(360, 205, 380, 55),
                "sound"
            ),
            (
                "PARTICLES: " + ("ON" if SAVE["particles"] else "OFF"),
                pygame.Rect(360, 280, 380, 55),
                "particles"
            ),
            (
                "BACK",
                pygame.Rect(360, 385, 380, 55),
                "back"
            ),
        ]

        for label, rect, action in self.buttons["settings"]:
            button(surface, rect, label, mouse)

    # --------------------------------------------------------
    # COMPLETE
    # --------------------------------------------------------

    def draw_complete(self, surface):

        surface.fill((18, 26, 49))

        draw_text(
            surface,
            "LEVEL COMPLETE!",
            WIDTH // 2,
            220, BIG, GOLD, True
        )

        draw_text(
            surface,
            "YOU DID IT!",
            WIDTH // 2,
            280, FONT, WHITE, True
        )

        mouse = pygame.mouse.get_pos()

        self.buttons["complete"] = [
            (
                "NEXT LEVEL",
                pygame.Rect(410, 370, 280, 50),
                "next"
            ),
            (
                "MAIN MENU",
                pygame.Rect(410, 435, 280, 50),
                "menu"
            ),
        ]

        for label, rect, action in self.buttons["complete"]:
            button(surface, rect, label, mouse)

    # --------------------------------------------------------
    # DRAW DISPATCHER
    # --------------------------------------------------------

    def draw(self, surface):

        self.buttons = {}

        if self.state == "menu":
            self.draw_menu(surface)

        elif self.state == "game":
            self.draw_game(surface)

        elif self.state == "shop":
            self.draw_shop(surface)

        elif self.state == "upgrades":
            self.draw_upgrades(surface)

        elif self.state == "worlds":
            self.draw_worlds(surface)

        elif self.state == "profile":
            self.draw_profile(surface)

        elif self.state == "missions":
            self.draw_missions(surface)

        elif self.state == "settings":
            self.draw_settings(surface)

        elif self.state == "complete":
            self.draw_complete(surface)

    # --------------------------------------------------------
    # CLICK HANDLER
    # --------------------------------------------------------

    def click(self, pos):

        mouse = pos

        if self.state == "menu":

            for label, rect, action in self.buttons.get("menu", []):

                if not rect.collidepoint(mouse):
                    continue

                if action == "play":
                    self.start_level(SAVE["level"])

                elif action == "shop":
                    self.state = "shop"

                elif action == "upgrades":
                    self.state = "upgrades"

                elif action == "worlds":
                    self.state = "worlds"

                elif action == "settings":
                    self.state = "settings"

                elif action == "profile":
                    self.state = "profile"

                elif action == "missions":
                    self.state = "missions"

                return

        elif self.state == "game" and self.paused:

            for label, rect, action in self.buttons.get("pause", []):

                if not rect.collidepoint(mouse):
                    continue

                if action == "resume":
                    self.paused = False

                elif action == "restart":
                    self.start_level(self.level_number)

                elif action == "menu":
                    self.paused = False
                    self.state = "menu"

                return

        elif self.state == "shop":

            for rect, category in self.buttons.get(
                "shop_categories", []
            ):

                if rect.collidepoint(mouse):

                    self.shop_category = category
                    self.shop_index = 0
                    self.shop_scroll = 0

                    return

            for rect, item_id in self.buttons.get(
                "shop_items", []
            ):

                if rect.collidepoint(mouse):

                    self.shop_index = list(
                        CATALOGS[self.shop_category]
                    ).index(item_id)

                    self.buy_or_equip(item_id)
                    return

            back = self.buttons.get("shop_back")

            if back and back.collidepoint(mouse):
                self.state = "menu"

        elif self.state == "upgrades":

            for rect, key in self.buttons.get("upgrades", []):

                if rect.collidepoint(mouse):
                    self.buy_upgrade(key)
                    return

            rank_button = self.buttons.get("rank")

            if rank_button and rank_button.collidepoint(mouse):
                self.buy_upgrade("rank")
                return

            back = self.buttons.get("upgrades_back")

            if back and back.collidepoint(mouse):
                self.state = "menu"

        elif self.state == "worlds":

            for rect, index, unlocked in self.buttons.get(
                "worlds", []
            ):

                if rect.collidepoint(mouse):

                    if unlocked:
                        self.start_level(index * 10 + 1)
                    else:
                        self.notify("WORLD LOCKED")

                    return

            back = self.buttons.get("worlds_back")

            if back and back.collidepoint(mouse):
                self.state = "menu"

        elif self.state == "profile":

            back = self.buttons.get("profile_back")

            if back and back.collidepoint(mouse):
                self.state = "menu"

        elif self.state == "missions":

            for rect, index in self.buttons.get("missions", []):

                if rect.collidepoint(mouse):
                    self.claim_mission(index)
                    return

            daily = self.buttons.get("daily")

            if daily and daily.collidepoint(mouse):
                self.claim_daily_reward()
                return

            back = self.buttons.get("missions_back")

            if back and back.collidepoint(mouse):
                self.state = "menu"

        elif self.state == "settings":

            for label, rect, action in self.buttons.get("settings", []):

                if not rect.collidepoint(mouse):
                    continue

                if action == "sound":
                    SAVE["sound"] = not SAVE["sound"]

                    if SAVE["sound"]:
                        start_background_music()
                    else:
                        stop_background_music()

                elif action == "particles":
                    SAVE["particles"] = not SAVE["particles"]

        elif action == "back":
                    self.state = "menu"

                    save_game()
                    return

        elif self.state == "complete":

                    for label, rect, action in self.buttons.get("complete", []):

                        if not rect.collidepoint(mouse):
                            continue

                        if action == "next":
                            self.start_level(
                                min(100, self.level_number + 1)
                            )

                        elif action == "menu":
                            self.state = "menu"

                        return

    # --------------------------------------------------------
    # KEYBOARD
    # --------------------------------------------------------

    def key(self, key):

        if self.state == "game":

            if key == pygame.K_ESCAPE:
                self.paused = not self.paused
                return

            if self.paused:
                return

            if key in (
                pygame.K_SPACE,
                pygame.K_UP,
                pygame.K_w
            ):
                self.player.jump()

            elif key in (
                pygame.K_LSHIFT,
                pygame.K_RSHIFT
            ):
                self.player.dash()

        elif self.state == "shop":

            if key == pygame.K_ESCAPE:
                self.state = "menu"

            elif key in (
                pygame.K_UP,
                pygame.K_DOWN
            ):

                count = len(
                    CATALOGS[self.shop_category]
                )

                max_scroll = max(
                    0,
                    count * 63 - 425
                )

                if key == pygame.K_UP:
                    self.shop_scroll = max(
                        0,
                        self.shop_scroll - 45
                    )

                else:
                    self.shop_scroll = min(
                        max_scroll,
                        self.shop_scroll + 45
                    )

        elif key == pygame.K_ESCAPE:
            self.state = "menu"


# ============================================================
# MAIN LOOP
# ============================================================

def main():

    game = Game()

    game.reset_daily_missions()

    start_background_music()
    running = True

    while running:

        clock.tick(FPS)

        keys = pygame.key.get_pressed()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                save_game()
                running = False

            elif event.type == pygame.KEYDOWN:

                game.key(event.key)

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:
                    game.click(event.pos)

                elif game.state == "shop":

                    count = len(
                        CATALOGS[game.shop_category]
                    )

                    max_scroll = max(
                        0,
                        count * 63 - 425
                    )

                    if event.button == 4:

                        game.shop_scroll = max(
                            0,
                            game.shop_scroll - 45
                        )

                    elif event.button == 5:

                        game.shop_scroll = min(
                            max_scroll,
                            game.shop_scroll + 45
                        )

        if game.state == "game":

            game.update_game(keys)

        else:

            game.tick += 1
            update_particles()

        game.draw(screen)

        if game.state != "game":

            for p in particles:
                p.draw(screen)

        pygame.display.flip()

    save_game()
    pygame.quit()


if __name__ == "__main__":

    try:
        main()

    except Exception:

        save_game()
        pygame.quit()
        raise
