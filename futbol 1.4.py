import pygame
import math
import random

# --- CONFIGURATION (YOUR VALUES KEPT EXACTLY AS REQUESTED) ---
WIDTH, HEIGHT = 600, 800
FPS = 60
FRAMES_PER_SIM_MINUTE = 30  # 0.5 seconds = 1 in-game minute

ARENA_RADIUS = 260
BALL_RADIUS = 40
GOAL_WIDTH_RADIANS = 0.30 
SPEED = 5.5  

# PHYSICS CONSTANTS
GRAVITY = 0.00           
BOUNCE_DAMPING = 0.9995    
FRICTION = 0.9999         
ELASTICITY = 0.999999999999        

# COLORS
GRASS_1 = (50, 160, 50)
GRASS_2 = (40, 140, 40)
WHITE = (245, 245, 245)
BLACK = (10, 10, 10)
NET_COLOR = (200, 200, 200)
GOLD = (255, 215, 0) # Added for GOLLL text

# TEAM COLORS
TRABZON_COLORS = [(128, 0, 0), (0, 191, 255)] 
FENER_COLORS = [(255, 255, 0), (0, 0, 128)]

# --- SETUP ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Futbol Simulasyonu")

# FONTS
font_score = pygame.font.SysFont("Arial", 50, bold=True)
font_timer = pygame.font.SysFont("Arial", 30, bold=True)
font_event = pygame.font.SysFont("Arial", 60, bold=True)
font_team = pygame.font.SysFont("Arial", 24, bold=True)
font_goal_list = pygame.font.SysFont("Arial", 16, bold=True)
font_goll_msg = pygame.font.SysFont("Arial", 90, bold=True)

clock = pygame.time.Clock()

# --- HELPER FUNCTIONS ---

def draw_striped_pitch(surface, cx, cy, radius):
    # 1. Base Green
    pygame.draw.circle(surface, GRASS_1, (cx, cy), radius)
    
    # 2. Draw stripes using a mask
    stripe_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    for i in range(0, radius*2, 60):
        pygame.draw.rect(stripe_surf, GRASS_2, (0, i, radius*2, 30))
    
    # Create circular mask
    mask_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    pygame.draw.circle(mask_surf, (255, 255, 255, 255), (radius, radius), radius)
    
    # Apply mask
    stripe_surf.blit(mask_surf, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
    surface.blit(stripe_surf, (cx - radius, cy - radius))
    
    # Field Markings
    pygame.draw.circle(surface, WHITE, (cx, cy), radius, 5) 
    pygame.draw.circle(surface, WHITE, (cx, cy), 50, 2)     
    pygame.draw.line(surface, WHITE, (cx - radius + 20, cy), (cx + radius - 20, cy), 2) 

def draw_rotating_net(surface, cx, cy, radius, angle, width_rad):
    start_angle = angle - width_rad / 2
    end_angle = angle + width_rad / 2
    
    ix1 = cx + math.cos(start_angle) * radius
    iy1 = cy + math.sin(start_angle) * radius
    ix2 = cx + math.cos(end_angle) * radius
    iy2 = cy + math.sin(end_angle) * radius
    
    depth = 40
    ox1 = cx + math.cos(start_angle) * (radius + depth)
    oy1 = cy + math.sin(start_angle) * (radius + depth)
    ox2 = cx + math.cos(end_angle) * (radius + depth)
    oy2 = cy + math.sin(end_angle) * (radius + depth)
    
    points = [(ix1, iy1), (ox1, oy1), (ox2, oy2), (ix2, iy2)]
    pygame.draw.polygon(surface, WHITE, points, 3) 
    
    for t in range(1, 4):
        r = radius + (depth * t / 4)
        px1 = cx + math.cos(start_angle) * r
        py1 = cy + math.sin(start_angle) * r
        px2 = cx + math.cos(end_angle) * r
        py2 = cy + math.sin(end_angle) * r
        pygame.draw.line(surface, NET_COLOR, (px1, py1), (px2, py2), 1)

def get_random_spawn(cx, cy, r_limit):
    """Returns a random (x, y) inside the arena"""
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

    def move(self):
        # 1. ADD GRAVITY
        self.vy += GRAVITY
        
        # 2. ADD FRICTION
        self.vx *= FRICTION
        self.vy *= FRICTION
        
        self.x += self.vx
        self.y += self.vy

    def draw(self, surface):
        pygame.draw.circle(surface, self.color[0], (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, self.color[1], (int(self.x), int(self.y)), self.radius - 6)
        txt = pygame.font.SysFont("Arial", 16, bold=True).render(self.text, True, WHITE)
        rect = txt.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(txt, rect)

    def collide_wall(self, cx, cy, radius):
        dx = self.x - cx
        dy = self.y - cy
        dist = math.hypot(dx, dy)
        
        if dist + self.radius >= radius:
            nx, ny = dx / dist, dy / dist
            
            # --- THE FIX: Only bounce if moving towards the wall ---
            # Dot product of Velocity and Normal (Center -> Ball)
            dot = self.vx * nx + self.vy * ny
            
            if dot > 0: # Ball is moving OUTWARDS (towards wall)
                # Reflect velocity
                self.vx = (self.vx - 2 * dot * nx) * BOUNCE_DAMPING
                self.vy = (self.vy - 2 * dot * ny) * BOUNCE_DAMPING
            
            # HARD FIX: Push ball out of wall so it doesn't stick
            overlap = (dist + self.radius) - radius
            self.x -= nx * overlap
            self.y -= ny * overlap
            return True
        return False

def resolve_collisions(b1, b2):
    """
    Advanced collision resolution to prevent sticking.
    """
    dx = b2.x - b1.x
    dy = b2.y - b1.y
    dist = math.hypot(dx, dy)
    
    if dist < b1.radius + b2.radius:
        if dist == 0: dist = 0.1
            
        nx, ny = dx/dist, dy/dist
        
        # 1. SEPARATE THEM (This fixes the sticking!)
        overlap = (b1.radius + b2.radius) - dist
        b1.x -= nx * overlap * 0.5
        b1.y -= ny * overlap * 0.5
        b2.x += nx * overlap * 0.5
        b2.y += ny * overlap * 0.5
        
        # 2. BOUNCE THEM
        dvx, dvy = b1.vx - b2.vx, b1.vy - b2.vy
        vel_normal = dvx*nx + dvy*ny
        
        if vel_normal > 0: return # Already moving apart
        
        # Impulse
        j = -(1 + ELASTICITY) * vel_normal / 2
        b1.vx += j * nx
        b1.vy += j * ny
        b2.vx -= j * nx
        b2.vy -= j * ny

# --- GAME VARIABLES ---
center_x, center_y = WIDTH // 2, HEIGHT // 2
score1, score2 = 0, 0

# Random spawn for initial balls
sx1, sy1 = get_random_spawn(center_x, center_y, ARENA_RADIUS)
sx2, sy2 = get_random_spawn(center_x, center_y, ARENA_RADIUS)

ball1 = Ball(sx1, sy1, TRABZON_COLORS, "TS")
ball2 = Ball(sx2, sy2, FENER_COLORS, "FB")

# Goal
goal_angle = 1 * math.pi / 2 
goal_rotating = False
goal_rot_speed = 0.015
goll_timer = 0  # Timer for "GOLLL!" text

# Scoreboard Data
goal_events_1 = [] # Stores times for Team 1
goal_events_2 = [] # Stores times for Team 2

# Time Management
state = "FIRST_HALF" 
frame_counter = 0
added_time_1 = random.randint(1, 3)
added_time_2 = random.randint(2, 8)
display_added_time = False

# Crowd
crowd = []
for _ in range(100):
    crowd.append((random.randint(0, WIDTH), random.randint(0, HEIGHT), random.choice([TRABZON_COLORS[0], FENER_COLORS[1], (50,50,50)])))

running = True
while running:
    # --- INPUT ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

    # --- LOGIC ---
    if state in ["FIRST_HALF", "SECOND_HALF"]:
        frame_counter += 1
        total_mins_played = frame_counter // FRAMES_PER_SIM_MINUTE
        
        # First Half
        if state == "FIRST_HALF":
            sim_minute = total_mins_played
            if sim_minute >= 45:
                display_added_time = True
                if sim_minute >= 45 + added_time_1:
                    state = "Devre arası"
                    pygame.time.delay(500)
            else:
                display_added_time = False
        
        # Second Half
        elif state == "SECOND_HALF":
            sim_minute = 45 + total_mins_played 
            if sim_minute >= 90:
                display_added_time = True
                if sim_minute >= 90 + added_time_2:
                    state = "FULLTIME"
            else:
                display_added_time = False

        # Physics
        if goal_rotating:
            goal_angle = (goal_angle + goal_rot_speed) % (2 * math.pi)

        if goll_timer > 0:
            goll_timer -= 1

        for b in [ball1, ball2]:
            b.move()

        # --- SOLVER LOOP (Fixes Sticking) ---
        # Runs collision logic 8 times per frame to ensure balls don't get pinned
        for _ in range(8):
            ball1.collide_wall(center_x, center_y, ARENA_RADIUS)
            ball2.collide_wall(center_x, center_y, ARENA_RADIUS)
            resolve_collisions(ball1, ball2)

        # Goal Detection
        for b in [ball1, ball2]:
            dist = math.hypot(b.x - center_x, b.y - center_y)
            if dist > ARENA_RADIUS - b.radius - 10:
                ball_ang = math.atan2(b.y - center_y, b.x - center_x)
                
                goal_n = goal_angle % (2*math.pi)
                ball_n = ball_ang % (2*math.pi)
                
                diff = abs(ball_n - goal_n)
                while diff > math.pi: diff = abs(diff - 2*math.pi)
                
                if diff < GOAL_WIDTH_RADIANS / 2:
                    # GOAL!
                    goll_timer = 90 # 1.5 seconds @ 60fps
                    
                    # Format time string
                    time_mark = f"{sim_minute}'"
                    if display_added_time: time_mark = f"{sim_minute}+'"

                    if b == ball1: 
                        score1 += 1
                        goal_events_1.append(time_mark)
                        # Respawn SCORER only
                        ball1.x, ball1.y = center_x, center_y
                    else: 
                        score2 += 1
                        goal_events_2.append(time_mark)
                        # Respawn SCORER only
                        ball2.x, ball2.y = center_x, center_y
                    
                    if score1 + score2 >= 1: goal_rotating = True
                    
                    # RESET TEMPO (Both get random fast velocity)
                    ball1.vx = random.choice([-SPEED, SPEED]) * random.uniform(0.8, 1.2)
                    ball1.vy = random.choice([-SPEED, SPEED]) * random.uniform(0.8, 1.2)
                    ball2.vx = random.choice([-SPEED, SPEED]) * random.uniform(0.8, 1.2)
                    ball2.vy = random.choice([-SPEED, SPEED]) * random.uniform(0.8, 1.2)
                    
                    pygame.time.delay(300)

    # --- STATE TRANSITIONS ---
    if state == "HALFTIME":
        pygame.time.delay(2000)
        state = "SECOND_HALF"
        frame_counter = 0 
        display_added_time = False
        
        # Reset positions for 2nd half kickoff (Random)
        rx1, ry1 = get_random_spawn(center_x, center_y, ARENA_RADIUS)
        rx2, ry2 = get_random_spawn(center_x, center_y, ARENA_RADIUS)
        ball1.x, ball1.y = rx1, ry1
        ball2.x, ball2.y = rx2, ry2

    # --- DRAWING ---
    screen.fill(BLACK)
    for dot in crowd:
        pygame.draw.circle(screen, dot[2], (dot[0], dot[1]), 2)

    draw_striped_pitch(screen, center_x, center_y, ARENA_RADIUS)
    draw_rotating_net(screen, center_x, center_y, ARENA_RADIUS, goal_angle, GOAL_WIDTH_RADIANS)

    ball1.draw(screen)
    ball2.draw(screen)

    # --- NEW SCOREBOARD UI ---
    
    # 1. Scoreboard Background
    panel_w, panel_h = 380, 80
    panel_x = WIDTH // 2 - panel_w // 2
    pygame.draw.rect(screen, (30, 30, 30), (panel_x, 20, panel_w, panel_h), border_radius=10)
    pygame.draw.rect(screen, WHITE, (panel_x, 20, panel_w, panel_h), 2, border_radius=10)

    # 2. Team Names
    ts_surf = font_team.render("TRABZON", True, TRABZON_COLORS[1])
    fb_surf = font_team.render("FENER", True, FENER_COLORS[0])
    screen.blit(ts_surf, (panel_x + 20, 30))
    screen.blit(fb_surf, (panel_x + panel_w - fb_surf.get_width() - 20, 30))

    # 3. Main Score
    score_surf = font_score.render(f"{score1} - {score2}", True, WHITE)
    screen.blit(score_surf, (WIDTH//2 - score_surf.get_width()//2, 25))

    # 4. Timer (Below Score)
    time_str = ""
    col = WHITE
    if state == "FIRST_HALF":
        base = 45 if display_added_time else 0
        if display_added_time:
            time_str = f"45+{sim_minute - 45}'"
            col = (255, 50, 50)
        else:
            time_str = f"{sim_minute}'"
    elif state == "HALFTIME":
        time_str = "HT"
        col = (255, 215, 0)
    elif state == "SECOND_HALF":
        if display_added_time:
            time_str = f"90+{sim_minute - 90}'"
            col = (255, 50, 50)
        else:
            time_str = f"{sim_minute}'"
    elif state == "FULLTIME":
        time_str = "FT"
        col = (255, 215, 0)

    timer_surf = font_timer.render(time_str, True, col)
    screen.blit(timer_surf, (WIDTH//2 - timer_surf.get_width()//2, 70))

    # 5. Goal Lists (The Timeline)
    # Left Side (Trabzon)
    y_off = 110
    for t_str in goal_events_1[-5:]: # Show last 5
        t_surf = font_goal_list.render(t_str, True, WHITE)
        screen.blit(t_surf, (panel_x + 30, y_off))
        y_off += 20
        
    # Right Side (Fener)
    y_off = 110
    for t_str in goal_events_2[-5:]:
        t_surf = font_goal_list.render(t_str, True, WHITE)
        # Right align
        screen.blit(t_surf, (panel_x + panel_w - 50, y_off))
        y_off += 20

    # 6. GOLLL! Animation
    if goll_timer > 0:
        goll_surf = font_goll_msg.render("GOLLL!", True, GOLD)
        outline_surf = font_goll_msg.render("GOLLL!", True, BLACK)
        
        # Center of screen
        gx, gy = WIDTH//2 - goll_surf.get_width()//2, HEIGHT//2 - 50
        screen.blit(outline_surf, (gx+4, gy+4))
        screen.blit(goll_surf, (gx, gy))

    # Halftime / Fulltime Overlays
    if state == "HALFTIME":
        overlay = font_event.render("HALF TIME", True, WHITE)
        screen.blit(overlay, (WIDTH//2 - overlay.get_width()//2, HEIGHT//2 + 50))
    elif state == "FULLTIME":
        overlay = font_event.render("FULL TIME", True, WHITE)
        screen.blit(overlay, (WIDTH//2 - overlay.get_width()//2, HEIGHT//2 + 50))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()