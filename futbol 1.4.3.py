import pygame
import math
import random
import os

# --- CONFIGURATION ---
WIDTH, HEIGHT = 600, 800
FPS = 97
FRAMES_PER_SIM_MINUTE = 30

ARENA_RADIUS = 260
BALL_RADIUS = 40
GOAL_WIDTH_RADIANS = 0.40
POST_RADIUS = 8
GOAL_DEPTH = 50

SPEED = 5.5
MIN_SPEED = 4.0

# PHYSICS CONSTANTS
GRAVITY = 0.001
BOUNCE_DAMPING = 0.9995
FRICTION = 0.99999
ELASTICITY = 0.95
POST_ELASTICITY = 1.1

# COLORS
GRASS_1 = (50, 160, 50)
GRASS_2 = (40, 140, 40)
WHITE = (245, 245, 245)
BLACK = (10, 10, 10)
NET_COLOR = (200, 200, 200)
GOLD = (255, 215, 0)
MENU_BG = (30, 30, 40)
SELECTED_COLOR = (50, 255, 50)
SCROLLBAR_BG = (50, 50, 60)
SCROLLBAR_HANDLE = (150, 150, 150)

# --- SES AYARLARI ---
STADIUM_FILE = "stadium.mp3"
GS_GOAL_FILE = "gs.mp3"
GOAL1_FILE = "goal1.mp3" # Bayern
GOAL2_FILE = "goal2.mp3" # Milan
GOAL3_FILE = "goal3.mp3" # Random havuzu

STADIUM_VOLUME = 0.3
GOAL_MUSIC_VOLUME = 0.6

# --- TAKIM VERİTABANI ---
TEAMS = {
    # --- TRENDYOL SÜPER LİG ---
    "GALATASARAY":    {"colors": [(169, 4, 50), (253, 185, 18)], "short": "GS"},
    "FENERBAHÇE":     {"colors": [(255, 255, 0), (0, 0, 128)],   "short": "FB"},
    "BEŞİKTAŞ":       {"colors": [(255, 255, 255), (10, 10, 10)],"short": "BJK"},
    "TRABZONSPOR":    {"colors": [(128, 0, 0), (0, 191, 255)],   "short": "TS"},
    "BAŞAKŞEHİR":     {"colors": [(255, 102, 0), (0, 0, 102)],   "short": "IBFK"},
    "KASIMPAŞA":      {"colors": [(255, 255, 255), (0, 0, 128)], "short": "KAS"},
    "SİVASSPOR":      {"colors": [(255, 0, 0), (255, 255, 255)], "short": "SVS"},
    "ALANYASPOR":     {"colors": [(255, 165, 0), (0, 128, 0)],   "short": "ALN"},
    "RİZESPOR":       {"colors": [(0, 128, 0), (0, 0, 255)],     "short": "RİZ"},
    "ANTALYASPOR":    {"colors": [(255, 0, 0), (255, 255, 255)], "short": "ANT"},
    "GAZİANTEP FK":   {"colors": [(200, 16, 46), (10, 10, 10)],  "short": "GFK"},
    "KONYASPOR":      {"colors": [(0, 128, 0), (255, 255, 255)], "short": "KON"},
    "KAYSERİSPOR":    {"colors": [(255, 204, 0), (255, 0, 0)],   "short": "KAY"},
    "BODRUM FK":      {"colors": [(0, 128, 0), (255, 255, 255)], "short": "BOD"},
    "EYÜPSPOR":       {"colors": [(230, 230, 250), (255, 215, 0)],"short": "EYP"},
    "GÖZTEPE":        {"colors": [(255, 215, 0), (255, 0, 0)],   "short": "GÖZ"},
    "SAMSUNSPOR":     {"colors": [(255, 0, 0), (255, 255, 255)], "short": "SAM"},
    "HATAYSPOR":      {"colors": [(128, 0, 0), (255, 255, 255)], "short": "HAT"},
    "ADANA DEMİR":    {"colors": [(0, 0, 255), (173, 216, 230)], "short": "ADS"},
    # --- AVRUPA ---
    "MAN CITY":       {"colors": [(108, 171, 221), (255, 255, 255)],"short": "MC"},
    "LIVERPOOL":      {"colors": [(200, 16, 46), (255, 255, 255)],  "short": "LIV"},
    "ARSENAL":        {"colors": [(239, 1, 7), (255, 255, 255)],    "short": "ARS"},
    "ASTON VILLA":    {"colors": [(103, 14, 54), (149, 191, 229)],  "short": "AVL"},
    "TOTTENHAM":      {"colors": [(255, 255, 255), (19, 34, 87)],   "short": "TOT"},
    "MAN UTD":        {"colors": [(218, 41, 28), (255, 255, 255)],  "short": "MUN"},
    "CHELSEA":        {"colors": [(3, 70, 148), (255, 255, 255)],   "short": "CHE"},
    "REAL MADRID":    {"colors": [(255, 255, 255), (255, 215, 0)],"short": "RMA"},
    "BARCELONA":      {"colors": [(0, 77, 152), (165, 0, 68)],    "short": "BAR"},
    "ATLETICO":       {"colors": [(203, 53, 36), (255, 255, 255)],"short": "ATM"},
    "GIRONA":         {"colors": [(200, 16, 46), (255, 255, 255)],"short": "GIR"},
    "B. MUNIH":       {"colors": [(220, 5, 45), (255, 255, 255)], "short": "BAY"},
    "DORTMUND":       {"colors": [(253, 225, 0), (10, 10, 10)],   "short": "BVB"},
    "LEVERKUSEN":     {"colors": [(10, 10, 10), (227, 34, 25)],   "short": "B04"},
    "RB LEIPZIG":     {"colors": [(255, 255, 255), (221, 5, 43)], "short": "RBL"},
    "INTER":          {"colors": [(0, 102, 187), (10, 10, 10)],   "short": "INT"},
    "MILAN":          {"colors": [(251, 9, 11), (10, 10, 10)],    "short": "MIL"},
    "JUVENTUS":       {"colors": [(255, 255, 255), (10, 10, 10)], "short": "JUV"},
    "ATALANTA":       {"colors": [(30, 113, 184), (10, 10, 10)],  "short": "ATA"},
    "ROMA":           {"colors": [(134, 38, 51), (240, 188, 66)], "short": "ROM"},
    "LAZIO":          {"colors": [(135, 206, 235), (255, 255, 255)],"short": "LAZ"},
    "PSG":            {"colors": [(0, 65, 112), (218, 41, 28)],   "short": "PSG"},
    "LILLE":          {"colors": [(238, 36, 54), (0, 51, 102)],   "short": "LIL"},
    "MONACO":         {"colors": [(255, 0, 0), (255, 255, 255)],  "short": "ASM"},
    "BENFICA":        {"colors": [(232, 48, 48), (255, 255, 255)],"short": "SLB"},
    "SPORTING":       {"colors": [(0, 128, 0), (255, 255, 255)],  "short": "SCP"},
    "PORTO":          {"colors": [(0, 0, 255), (255, 255, 255)],  "short": "POR"},
    "AJAX":           {"colors": [(255, 255, 255), (210, 18, 46)],"short": "AJX"},
    "PSV":            {"colors": [(255, 0, 0), (255, 255, 255)],  "short": "PSV"},
    "FEYENOORD":      {"colors": [(255, 255, 255), (255, 0, 0)],  "short": "FEY"},
}

TEAM_NAMES = list(TEAMS.keys())

# --- SETUP ---
pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(8)

screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Futbol Simulasyonu")


# --- SES YÜKLEME ---
# 1. Arkaplan
stadium_music_loaded = False
if os.path.exists(STADIUM_FILE):
    try:
        pygame.mixer.music.load(STADIUM_FILE)
        pygame.mixer.music.set_volume(STADIUM_VOLUME)
        stadium_music_loaded = True
    except Exception:
        pass

# 2. Gol Müzikleri
goal_sounds = {}

def load_sound(path):
    if os.path.exists(path):
        try:
            snd = pygame.mixer.Sound(path)
            snd.set_volume(GOAL_MUSIC_VOLUME)
            return snd
        except: return None
    return None

goal_sounds["GS"] = load_sound(GS_GOAL_FILE)
goal_sounds["GOAL1"] = load_sound(GOAL1_FILE)
goal_sounds["GOAL2"] = load_sound(GOAL2_FILE)
goal_sounds["GOAL3"] = load_sound(GOAL3_FILE)

# Yabanci takımlar için genel havuz
general_pool = []
if goal_sounds["GOAL1"]: general_pool.append(goal_sounds["GOAL1"])
if goal_sounds["GOAL2"]: general_pool.append(goal_sounds["GOAL2"])
if goal_sounds["GOAL3"]: general_pool.append(goal_sounds["GOAL3"])

# FONTS
font_score = pygame.font.SysFont("Arial", 50, bold=True)
font_timer = pygame.font.SysFont("Arial", 30, bold=True)
font_event = pygame.font.SysFont("Arial", 60, bold=True)
font_team = pygame.font.SysFont("Arial", 24, bold=True)
font_goal_list = pygame.font.SysFont("Arial", 16, bold=True)
font_goll_msg = pygame.font.SysFont("Arial", 90, bold=True)
font_menu_title = pygame.font.SysFont("Arial", 40, bold=True)
font_menu_item = pygame.font.SysFont("Arial", 20, bold=True)
font_ball = pygame.font.SysFont("Arial", 20, bold=True)

clock = pygame.time.Clock()

# --- HELPER FUNCTIONS ---

def draw_striped_pitch(surface, cx, cy, radius):
    pygame.draw.circle(surface, GRASS_1, (cx, cy), radius)
    stripe_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    for i in range(0, radius*2, 60):
        pygame.draw.rect(stripe_surf, GRASS_2, (0, i, radius*2, 30))
    mask_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    pygame.draw.circle(mask_surf, (255, 255, 255, 255), (radius, radius), radius)
    stripe_surf.blit(mask_surf, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
    surface.blit(stripe_surf, (cx - radius, cy - radius))
    pygame.draw.circle(surface, WHITE, (cx, cy), radius, 5)
    pygame.draw.circle(surface, WHITE, (cx, cy), 50, 2)
    pygame.draw.line(surface, WHITE, (cx - radius + 20, cy), (cx + radius - 20, cy), 2)

def calculate_goal_posts(cx, cy, radius, angle, width_rad):
    start_angle = angle - width_rad / 2
    end_angle = angle + width_rad / 2
    p1x = cx + math.cos(start_angle) * radius
    p1y = cy + math.sin(start_angle) * radius
    p2x = cx + math.cos(end_angle) * radius
    p2y = cy + math.sin(end_angle) * radius
    return (p1x, p1y), (p2x, p2y), start_angle, end_angle

def draw_real_goal(surface, cx, cy, radius, angle, width_rad):
    (p1x, p1y), (p2x, p2y), start_angle, end_angle = calculate_goal_posts(cx, cy, radius, angle, width_rad)
    depth = GOAL_DEPTH
    b1x = cx + math.cos(start_angle) * (radius + depth)
    b1y = cy + math.sin(start_angle) * (radius + depth)
    b2x = cx + math.cos(end_angle) * (radius + depth)
    b2y = cy + math.sin(end_angle) * (radius + depth)

    for i in range(1, 6):
        ratio = i / 6
        lx1 = p1x + (b1x - p1x) * ratio
        ly1 = p1y + (b1y - p1y) * ratio
        lx2 = p2x + (b2x - p2x) * ratio
        ly2 = p2y + (b2y - p2y) * ratio
        pygame.draw.line(surface, NET_COLOR, (lx1, ly1), (lx2, ly2), 1)

        lx3 = p1x + (p2x - p1x) * ratio
        ly3 = p1y + (p2y - p1y) * ratio
        lx4 = b1x + (b2x - b1x) * ratio
        ly4 = b1y + (b2y - b1y) * ratio
        pygame.draw.line(surface, NET_COLOR, (lx3, ly3), (lx4, ly4), 1)

    pygame.draw.lines(surface, WHITE, False, [(p1x, p1y), (b1x, b1y), (b2x, b2y), (p2x, p2y)], 3)
    pygame.draw.circle(surface, WHITE, (int(p1x), int(p1y)), POST_RADIUS)
    pygame.draw.circle(surface, WHITE, (int(p2x), int(p2y)), POST_RADIUS)
    pygame.draw.circle(surface, (200, 200, 200), (int(p1x), int(p1y)), POST_RADIUS-2)
    pygame.draw.circle(surface, (200, 200, 200), (int(p2x), int(p2y)), POST_RADIUS-2)

def get_random_spawn(cx, cy, r_limit):
    while True:
        rx = random.randint(cx - 150, cx + 150)
        ry = random.randint(cy - 200, cy + 50)
        dist = math.hypot(rx - cx, ry - cy)
        if dist < r_limit - BALL_RADIUS - 10:
            return rx, ry

class Ball:
    def __init__(self, x, y, color_scheme, text):
        self.x, self.y = x, y
        self.vx = random.choice([-SPEED, SPEED])
        self.vy = random.choice([-SPEED, SPEED])
        self.radius = BALL_RADIUS
        self.color = color_scheme
        self.text = text
        self.mass = 1.0

    def move(self):
        self.vy += GRAVITY
        self.vx *= FRICTION
        self.vy *= FRICTION
        current_speed = math.hypot(self.vx, self.vy)
        if current_speed < MIN_SPEED and current_speed > 0:
            scale = MIN_SPEED / current_speed
            self.vx *= scale
            self.vy *= scale
        elif current_speed == 0:
            self.vx = random.choice([-1, 1]) * MIN_SPEED
            self.vy = random.choice([-1, 1]) * MIN_SPEED
        self.x += self.vx
        self.y += self.vy

    def draw(self, surface):
        pygame.draw.circle(surface, self.color[0], (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, self.color[1], (int(self.x), int(self.y)), self.radius - 6)
        txt_black = font_ball.render(self.text, True, BLACK)
        txt_white = font_ball.render(self.text, True, WHITE)
        center_pos = (int(self.x), int(self.y))
        rect = txt_black.get_rect(center=center_pos)
        surface.blit(txt_black, (rect.x - 2, rect.y))
        surface.blit(txt_black, (rect.x + 2, rect.y))
        surface.blit(txt_black, (rect.x, rect.y - 2))
        surface.blit(txt_black, (rect.x, rect.y + 2))
        surface.blit(txt_white, rect)

    def collide_wall(self, cx, cy, radius):
        dx = self.x - cx
        dy = self.y - cy
        dist = math.hypot(dx, dy)
        if dist + self.radius >= radius:
            nx, ny = dx / dist, dy / dist
            dot = self.vx * nx + self.vy * ny
            if dot > 0:
                self.vx = (self.vx - 2 * dot * nx) * BOUNCE_DAMPING
                self.vy = (self.vy - 2 * dot * ny) * BOUNCE_DAMPING
            overlap = (dist + self.radius) - radius
            self.x -= nx * overlap
            self.y -= ny * overlap
            return True
        return False

    def collide_post(self, px, py):
        dx = self.x - px
        dy = self.y - py
        dist = math.hypot(dx, dy)
        if dist < self.radius + POST_RADIUS:
            nx, ny = dx / dist, dy / dist
            dot = self.vx * nx + self.vy * ny
            if dot < 0:
                self.vx = (self.vx - 2 * dot * nx) * POST_ELASTICITY
                self.vy = (self.vy - 2 * dot * ny) * POST_ELASTICITY
                overlap = (self.radius + POST_RADIUS) - dist
                self.x += nx * overlap
                self.y += ny * overlap
                return True
        return False

def resolve_collisions(b1, b2):
    dx = b2.x - b1.x
    dy = b2.y - b1.y
    dist = math.hypot(dx, dy)
    if dist < b1.radius + b2.radius:
        if dist == 0: dist = 0.1
        nx, ny = dx/dist, dy/dist
        overlap = (b1.radius + b2.radius) - dist
        total_mass = b1.mass + b2.mass
        m1_ratio = b2.mass / total_mass
        m2_ratio = b1.mass / total_mass
        b1.x -= nx * overlap * m1_ratio
        b1.y -= ny * overlap * m1_ratio
        b2.x += nx * overlap * m2_ratio
        b2.y += ny * overlap * m2_ratio
        rx = b2.vx - b1.vx
        ry = b2.vy - b1.vy
        vel_along_normal = rx * nx + ry * ny
        if vel_along_normal > 0: return
        j = -(1 + ELASTICITY) * vel_along_normal
        j /= (1 / b1.mass + 1 / b2.mass)
        impulse_x = j * nx
        impulse_y = j * ny
        b1.vx -= impulse_x / b1.mass
        b1.vy -= impulse_y / b1.mass
        b2.vx += impulse_x / b2.mass
        b2.vy += impulse_y / b2.mass

# --- GLOBAL GAME VARIABLES ---
center_x, center_y = WIDTH // 2, HEIGHT // 2
score1, score2 = 0, 0
goal_angle = 1 * math.pi / 2
goal_rotating = False
goal_rot_speed = 0.02
goll_timer = 0
goal_events_1 = []
goal_events_2 = []
state = "MENU"
frame_counter = 0
added_time_1 = random.randint(1, 3)
added_time_2 = random.randint(2, 8)
display_added_time = False
end_match_timer = 0 # Mac sonu bekleme suresi icin

# MENU VARIABLES
selected_home_idx = 0
selected_away_idx = 1
team1_name = ""
team2_name = ""
team1_colors = []
team2_colors = []

# Scrollbar Variables
menu_scroll_y = 0
is_dragging_scroll = False

# Placeholder objects
ball1 = None
ball2 = None
crowd = []

# SOUND CHANNELS
goal_sound_channel = None

def play_goal_music_for_team(team_short_name):
    global goal_sound_channel

    # Eger kanal doluysa once durdur (Restart / Interrupt Effect)
    if goal_sound_channel and goal_sound_channel.get_busy():
        goal_sound_channel.stop()

    # Calinacak sesi belirle
    sound_to_play = None

    # 1. Türk Takımları (Haric Tutulanlar)
    if team_short_name in ["FB", "TS", "BJK", "IBFK", "KAS", "SVS", "ALN", "RİZ", "ANT", "GFK", "KON", "KAY", "BOD", "EYP", "GÖZ", "SAM", "HAT", "ADS"]:
        return # Sessiz

    # 2. Galatasaray (Ozel)
    elif team_short_name == "GS":
        sound_to_play = goal_sounds["GS"]

    # 3. Bayern Munih (Sabit Goal1)
    elif team_short_name == "BAY":
        sound_to_play = goal_sounds["GOAL1"]

    # 4. Milan (Sabit Goal2)
    elif team_short_name == "MIL":
        sound_to_play = goal_sounds["GOAL2"]

    # 5. Diger Yabancilar (Random)
    else:
        if len(general_pool) > 0:
            sound_to_play = random.choice(general_pool)

    # Sesi cal (Eger ses dosyasi varsa)
    if sound_to_play:
        goal_sound_channel = sound_to_play.play()

def start_match():
    global ball1, ball2, crowd, team1_name, team2_name, team1_colors, team2_colors, state, score1, score2, goal_events_1, goal_events_2, frame_counter, goal_rotating, goal_sound_channel
    score1, score2 = 0, 0
    goal_events_1 = []
    goal_events_2 = []
    frame_counter = 0
    goal_rotating = False

    goal_sound_channel = None

    home_key = TEAM_NAMES[selected_home_idx]
    away_key = TEAM_NAMES[selected_away_idx]

    team1_name = TEAMS[home_key]["short"]
    team2_name = TEAMS[away_key]["short"]
    team1_colors = TEAMS[home_key]["colors"]
    team2_colors = TEAMS[away_key]["colors"]

    sx1, sy1 = get_random_spawn(center_x, center_y, ARENA_RADIUS)
    sx2, sy2 = get_random_spawn(center_x, center_y, ARENA_RADIUS)
    ball1 = Ball(sx1, sy1, team1_colors, team1_name)
    ball2 = Ball(sx2, sy2, team2_colors, team2_name)

    crowd = []
    for _ in range(120):
        rand_val = random.random()
        if rand_val < 0.45:
            col = random.choice(team1_colors)
        elif rand_val < 0.90:
            col = random.choice(team2_colors)
        else:
            col = (50, 50, 50)
        crowd.append((random.randint(0, WIDTH), random.randint(0, HEIGHT), col))

    # --- ARKA PLAN SESİNİ BAŞLAT ---
    if stadium_music_loaded:
        pygame.mixer.music.play(-1, fade_ms=500)

    state = "FIRST_HALF"

running = True


while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # --- MENU ETKILESIMI ---
        if state == "MENU":
            list_start_y = 120
            visible_h = HEIGHT - 220
            total_items_h = len(TEAM_NAMES) * 40
            max_scroll = total_items_h - visible_h
            if max_scroll < 0: max_scroll = 0
            scrollbar_w = 15
            scrollbar_x = WIDTH - 20
            scrollbar_y_start = 120
            scrollbar_h_total = visible_h
            if total_items_h > 0:
                handle_h = max(30, (visible_h / total_items_h) * scrollbar_h_total)
            else:
                handle_h = scrollbar_h_total
            if max_scroll > 0:
                scroll_ratio = abs(menu_scroll_y) / max_scroll
                handle_y = scrollbar_y_start + scroll_ratio * (scrollbar_h_total - handle_h)
            else:
                handle_y = scrollbar_y_start
            scrollbar_rect = pygame.Rect(scrollbar_x, scrollbar_y_start, scrollbar_w, scrollbar_h_total)
            handle_rect = pygame.Rect(scrollbar_x, handle_y, scrollbar_w, handle_h)

            start_btn_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT - 100, 300, 60)

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if handle_rect.collidepoint(mx, my):
                    is_dragging_scroll = True
                    mouse_offset_y = my - handle_y
                for i, name in enumerate(TEAM_NAMES):
                    item_y = 120 + i * 40 + menu_scroll_y
                    if item_y > 100 and item_y < HEIGHT - 110:
                        rect = pygame.Rect(50, item_y, 200, 30)
                        if rect.collidepoint(mx, my):
                            selected_home_idx = i
                for i, name in enumerate(TEAM_NAMES):
                    item_y = 120 + i * 40 + menu_scroll_y
                    if item_y > 100 and item_y < HEIGHT - 110:
                        rect = pygame.Rect(350, item_y, 200, 30)
                        if rect.collidepoint(mx, my):
                            selected_away_idx = i

                if start_btn_rect.collidepoint(mx, my):
                    start_match()
            elif event.type == pygame.MOUSEBUTTONUP:
                is_dragging_scroll = False
            elif event.type == pygame.MOUSEMOTION:
                if is_dragging_scroll and max_scroll > 0:
                    mx, my = pygame.mouse.get_pos()
                    new_handle_y = my - mouse_offset_y
                    if new_handle_y < scrollbar_y_start: new_handle_y = scrollbar_y_start
                    if new_handle_y > scrollbar_y_start + scrollbar_h_total - handle_h:
                        new_handle_y = scrollbar_y_start + scrollbar_h_total - handle_h
                    percent = (new_handle_y - scrollbar_y_start) / (scrollbar_h_total - handle_h)
                    menu_scroll_y = -(percent * max_scroll)
            elif event.type == pygame.MOUSEWHEEL:
                menu_scroll_y += event.y * 30
                if menu_scroll_y > 0: menu_scroll_y = 0
                if menu_scroll_y < -max_scroll: menu_scroll_y = -max_scroll

        # --- MAC SONU YENI MAC BUTONU ETKILESIMI ---
        elif state == "FULLTIME":
            if end_match_timer > 2 * FPS: # 2 Saniye gectiyse buton aktif
                # Buton konumu (Mac Baslat butonu ile ayni yer olsun)
                restart_btn_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT - 150, 300, 60)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if restart_btn_rect.collidepoint(mx, my):
                        # Menuye don
                        state = "MENU"
                        # Eger gol muzigi caliyorsa sustur
                        if goal_sound_channel: goal_sound_channel.stop()

    # --- DRAWING ---
    if state == "MENU":
        screen.fill(MENU_BG)
        title = font_menu_title.render("TAKIM SEÇİMİ", True, GOLD)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))
        home_header = font_team.render("EV SAHİBİ", True, WHITE)
        screen.blit(home_header, (80, 80))
        away_header = font_team.render("DEPLASMAN", True, WHITE)
        screen.blit(away_header, (380, 80))
        clip_rect = pygame.Rect(0, 110, WIDTH, HEIGHT - 210)
        screen.set_clip(clip_rect)
        for i, name in enumerate(TEAM_NAMES):
            item_y = 120 + i * 40 + menu_scroll_y
            if item_y < 100 or item_y > HEIGHT - 100:
                continue
            col = SELECTED_COLOR if i == selected_home_idx else WHITE
            name_surf = font_menu_item.render(name, True, col)
            screen.blit(name_surf, (50, item_y))
            col = SELECTED_COLOR if i == selected_away_idx else WHITE
            name_surf = font_menu_item.render(name, True, col)
            screen.blit(name_surf, (350, item_y))
        screen.set_clip(None)
        pygame.draw.rect(screen, SCROLLBAR_BG, scrollbar_rect)
        pygame.draw.rect(screen, SCROLLBAR_HANDLE, handle_rect, border_radius=5)

        pygame.draw.rect(screen, MENU_BG, (0, HEIGHT-110, WIDTH, 110))

        btn_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT - 100, 300, 60)
        pygame.draw.rect(screen, GRASS_1, btn_rect, border_radius=15)
        pygame.draw.rect(screen, WHITE, btn_rect, 3, border_radius=15)

        btn_txt = font_menu_title.render("MAÇI BAŞLAT", True, WHITE)
        btn_txt_rect = btn_txt.get_rect(center=btn_rect.center)
        screen.blit(btn_txt, btn_txt_rect)

    elif state in ["FIRST_HALF", "SECOND_HALF", "HALFTIME", "FULLTIME"]:
        if state in ["FIRST_HALF", "SECOND_HALF"]:
            frame_counter += 1
            total_mins_played = frame_counter // FRAMES_PER_SIM_MINUTE
            if state == "FIRST_HALF":
                sim_minute = total_mins_played
                if sim_minute >= 45:
                    display_added_time = True
                    if sim_minute >= 45 + added_time_1:
                        state = "HALFTIME"
                        pygame.time.delay(500) # Kisa bekleme
                else:
                    display_added_time = False
            elif state == "SECOND_HALF":
                sim_minute = 45 + total_mins_played
                if sim_minute >= 90:
                    display_added_time = True
                    if sim_minute >= 90 + added_time_2:
                        state = "FULLTIME"
                        end_match_timer = 0 # Sayaci sifirla
                else:
                    display_added_time = False

            if state == "FIRST_HALF" and display_added_time and sim_minute >= 45 + added_time_1:
                state = "HALFTIME"
                pygame.time.delay(500)

            if goal_rotating:
                goal_angle = (goal_angle + goal_rot_speed) % (2 * math.pi)
            if goll_timer > 0:
                goll_timer -= 1
            (p1, p2, _, _) = calculate_goal_posts(center_x, center_y, ARENA_RADIUS, goal_angle, GOAL_WIDTH_RADIANS)
            for b in [ball1, ball2]:
                b.move()
                b.collide_post(p1[0], p1[1])
                b.collide_post(p2[0], p2[1])
            for _ in range(8):
                ball1.collide_wall(center_x, center_y, ARENA_RADIUS)
                ball2.collide_wall(center_x, center_y, ARENA_RADIUS)
                resolve_collisions(ball1, ball2)
            for b in [ball1, ball2]:
                dist = math.hypot(b.x - center_x, b.y - center_y)
                if dist > ARENA_RADIUS - b.radius - 5:
                    ball_ang = math.atan2(b.y - center_y, b.x - center_x)
                    goal_n = goal_angle % (2*math.pi)
                    ball_n = ball_ang % (2*math.pi)
                    diff = abs(ball_n - goal_n)
                    while diff > math.pi: diff = abs(diff - 2*math.pi)
                    if diff < GOAL_WIDTH_RADIANS / 2:
                        goll_timer = 90
                        time_mark = f"{sim_minute}'"
                        if state == "FIRST_HALF":
                            if sim_minute > 45:
                                time_mark = f"45+{sim_minute - 45}'"
                        elif state == "SECOND_HALF":
                            if sim_minute > 90:
                                time_mark = f"90+{sim_minute - 90}'"
                        if b == ball1:
                            score1 += 1
                            goal_events_1.append(time_mark)
                            ball1.x, ball1.y = center_x, center_y
                            play_goal_music_for_team(team1_name) # <-- SES MANTIGI
                        else:
                            score2 += 1
                            goal_events_2.append(time_mark)
                            ball2.x, ball2.y = center_x, center_y
                            play_goal_music_for_team(team2_name) # <-- SES MANTIGI

                        if score1 + score2 >= 1: goal_rotating = True
                        ball1.vx = random.choice([-SPEED, SPEED]) * random.uniform(0.8, 1.2)
                        ball1.vy = random.choice([-SPEED, SPEED]) * random.uniform(0.8, 1.2)
                        ball2.vx = random.choice([-SPEED, SPEED]) * random.uniform(0.8, 1.2)
                        ball2.vy = random.choice([-SPEED, SPEED]) * random.uniform(0.8, 1.2)

        if state == "HALFTIME":
            pygame.time.delay(500) # Kisa bekleme
            state = "SECOND_HALF"
            frame_counter = 0
            display_added_time = False
            rx1, ry1 = get_random_spawn(center_x, center_y, ARENA_RADIUS)
            rx2, ry2 = get_random_spawn(center_x, center_y, ARENA_RADIUS)
            ball1.x, ball1.y = rx1, ry1
            ball2.x, ball2.y = rx2, ry2

        screen.fill(BLACK)
        for dot in crowd:
            pygame.draw.circle(screen, dot[2], (dot[0], dot[1]), 2)
        draw_striped_pitch(screen, center_x, center_y, ARENA_RADIUS)
        draw_real_goal(screen, center_x, center_y, ARENA_RADIUS, goal_angle, GOAL_WIDTH_RADIANS)
        ball1.draw(screen)
        ball2.draw(screen)
        panel_w, panel_h = 380, 80
        panel_x = WIDTH // 2 - panel_w // 2
        pygame.draw.rect(screen, (30, 30, 30), (panel_x, 20, panel_w, panel_h), border_radius=10)
        pygame.draw.rect(screen, WHITE, (panel_x, 20, panel_w, panel_h), 2, border_radius=10)
        ts_surf = font_team.render(TEAMS[TEAM_NAMES[selected_home_idx]]["short"], True, team1_colors[1])
        fb_surf = font_team.render(TEAMS[TEAM_NAMES[selected_away_idx]]["short"], True, team2_colors[0])
        screen.blit(ts_surf, (panel_x + 20, 30))
        screen.blit(fb_surf, (panel_x + panel_w - fb_surf.get_width() - 20, 30))
        score_surf = font_score.render(f"{score1} - {score2}", True, WHITE)
        screen.blit(score_surf, (WIDTH//2 - score_surf.get_width()//2, 25))
        time_str = ""
        col = WHITE
        if state == "FIRST_HALF":
            if display_added_time:
                time_str = f"45+{sim_minute - 45}'"
                col = (255, 50, 50)
            else:
                time_str = f"{sim_minute}'"
        elif state == "HALFTIME":
            time_str = "İY"
            col = (255, 215, 0)
        elif state == "SECOND_HALF":
            if display_added_time:
                time_str = f"90+{sim_minute - 90}'"
                col = (255, 50, 50)
            else:
                time_str = f"{sim_minute}'"
        elif state == "FULLTIME":
            time_str = "MS"
            col = (255, 215, 0)
        timer_surf = font_timer.render(time_str, True, col)
        screen.blit(timer_surf, (WIDTH//2 - timer_surf.get_width()//2, 70))
        y_off = 110
        for t_str in goal_events_1[-5:]:
            t_surf = font_goal_list.render(t_str, True, WHITE)
            screen.blit(t_surf, (panel_x + 30, y_off))
            y_off += 20
        y_off = 110
        for t_str in goal_events_2[-5:]:
            t_surf = font_goal_list.render(t_str, True, WHITE)
            screen.blit(t_surf, (panel_x + panel_w - 50, y_off))
            y_off += 20
        if goll_timer > 0:
            goll_surf = font_goll_msg.render("GOLLL!", True, GOLD)
            outline_surf = font_goll_msg.render("GOLLL!", True, BLACK)
            gx, gy = WIDTH//2 - goll_surf.get_width()//2, HEIGHT//2 - 50
            screen.blit(outline_surf, (gx+4, gy+4))
            screen.blit(goll_surf, (gx, gy))

        if state == "HALFTIME":
            overlay = font_event.render("İlk Yarı", True, WHITE)
            screen.blit(overlay, (WIDTH//2 - overlay.get_width()//2, HEIGHT//2 + 50))

        elif state == "FULLTIME":
            end_match_timer += 1 # Sayaci artir
            overlay = font_event.render("Maç Sonucu", True, WHITE)
            screen.blit(overlay, (WIDTH//2 - overlay.get_width()//2, HEIGHT//2 + 50))

            # --- YENI MAC BUTONU CIZIMI ---
            if end_match_timer > 2 * FPS: # 2 saniye sonra ciz
                restart_btn_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT - 150, 300, 60)
                pygame.draw.rect(screen, GRASS_1, restart_btn_rect, border_radius=15)
                pygame.draw.rect(screen, WHITE, restart_btn_rect, 3, border_radius=15)

                restart_txt = font_menu_title.render("MENÜYE DÖN", True, WHITE)
                restart_txt_rect = restart_txt.get_rect(center=restart_btn_rect.center)
                screen.blit(restart_txt, restart_txt_rect)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()