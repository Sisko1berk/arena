import pygame
import math
import random

# --- CONFIGURATION ---
WIDTH, HEIGHT = 600, 800  # Slightly wider for better view
FPS = 60
FRAMES_PER_SIM_MINUTE = 30  # 0.5 seconds (30 frames) = 1 in-game minute

ARENA_RADIUS = 260
BALL_RADIUS = 30
GOAL_WIDTH_RADIANS = 0.35 # Width of goal in radians
SPEED = 4.5 # Reduced speed as requested

# Colors
GRASS_1 = (50, 160, 50)
GRASS_2 = (40, 140, 40) # Darker stripe
WHITE = (240, 240, 240)
BLACK = (20, 20, 20)
NET_COLOR = (200, 200, 200)
# Team Colors
TRABZON_COLORS = [(128, 0, 0), (0, 191, 255)] # Claret & Blue
FENER_COLORS = [(255, 255, 0), (0, 0, 128)]   # Yellow & Navy

# --- SETUP ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Champions League Simulation")
font_score = pygame.font.SysFont("Arial", 50, bold=True)
font_timer = pygame.font.SysFont("Arial", 35, bold=True)
font_event = pygame.font.SysFont("Arial", 60, bold=True)
clock = pygame.time.Clock()

# --- HELPER FUNCTIONS ---

def draw_striped_pitch(surface, cx, cy, radius):
    # 1. Draw base grass
    pygame.draw.circle(surface, GRASS_1, (cx, cy), radius)
    
    # 2. Draw stripes (calc width based on circle geometry)
    stripe_height = 40
    for y in range(int(cy - radius), int(cy + radius), stripe_height * 2):
        # Determine the width of the stripe at this Y position using circle equation
        # x^2 + y^2 = r^2  => x = sqrt(r^2 - y_rel^2)
        y_rel_top = y - cy
        y_rel_bot = (y + stripe_height) - cy
        
        # We need to stay inside the circle. 
        # Simple approximation: Draw rect and mask, OR math.
        # Let's do a quick surface mask for perfect circle edges.
        pass 
    
    # Better approach for clean stripes: Draw a big striped rect, then blit a circle mask
    temp_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    temp_surf.fill((0,0,0,0))
    pygame.draw.circle(temp_surf, (255, 255, 255, 255), (radius, radius), radius)
    
    stripe_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    stripe_surf.fill(GRASS_1)
    for i in range(0, radius*2, 50):
        pygame.draw.rect(stripe_surf, GRASS_2, (0, i, radius*2, 25))
        
    # Apply mask
    stripe_surf.blit(temp_surf, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
    surface.blit(stripe_surf, (cx - radius, cy - radius))
    
    # Field Markings
    pygame.draw.circle(surface, WHITE, (cx, cy), radius, 5) # Outer ring
    pygame.draw.circle(surface, WHITE, (cx, cy), 50, 2)     # Center circle
    pygame.draw.line(surface, WHITE, (cx - radius + 20, cy), (cx + radius - 20, cy), 2) # Halfway line

def draw_rotating_net(surface, cx, cy, radius, angle, width_rad):
    """Draws a net that sticks out of the arena at the goal angle"""
    # Calculate corners of the goal arc
    start_angle = angle - width_rad / 2
    end_angle = angle + width_rad / 2
    
    # Inner points (on the arena edge)
    ix1 = cx + math.cos(start_angle) * radius
    iy1 = cy + math.sin(start_angle) * radius
    ix2 = cx + math.cos(end_angle) * radius
    iy2 = cy + math.sin(end_angle) * radius
    
    # Outer points (depth of net)
    depth = 40
    ox1 = cx + math.cos(start_angle) * (radius + depth)
    oy1 = cy + math.sin(start_angle) * (radius + depth)
    ox2 = cx + math.cos(end_angle) * (radius + depth)
    oy2 = cy + math.sin(end_angle) * (radius + depth)
    
    # Draw Net Polygon
    points = [(ix1, iy1), (ox1, oy1), (ox2, oy2), (ix2, iy2)]
    
    # Draw "Netting" crosshatch
    pygame.draw.polygon(surface, WHITE, points, 3) # Frame
    
    # Simple cross lines for net effect
    for t in range(1, 4):
        # Interpolate between inner/outer
        r = radius + (depth * t / 4)
        px1 = cx + math.cos(start_angle) * r
        py1 = cy + math.sin(start_angle) * r
        px2 = cx + math.cos(end_angle) * r
        py2 = cy + math.sin(end_angle) * r
        pygame.draw.line(surface, NET_COLOR, (px1, py1), (px2, py2), 1)

class Ball:
    def __init__(self, x, y, color_scheme, text):
        self.x, self.y = x, y
        self.vx = random.choice([-SPEED, SPEED])
        self.vy = random.choice([-SPEED, SPEED])
        self.radius = BALL_RADIUS
        self.color = color_scheme
        self.text = text

    def move(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, surface):
        # Draw Ball body
        pygame.draw.circle(surface, self.color[0], (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, self.color[1], (int(self.x), int(self.y)), self.radius - 6)
        # Text
        txt = pygame.font.SysFont("Arial", 16, bold=True).render(self.text, True, WHITE)
        rect = txt.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(txt, rect)

    def collide_wall(self, cx, cy, radius):
        dx = self.x - cx
        dy = self.y - cy
        dist = math.hypot(dx, dy)
        if dist + self.radius >= radius:
            nx, ny = dx / dist, dy / dist
            dot = self.vx * nx + self.vy * ny
            self.vx -= 2 * dot * nx
            self.vy -= 2 * dot * ny
            overlap = (dist + self.radius) - radius
            self.x -= nx * overlap
            self.y -= ny * overlap
            return True
        return False

def check_collision(b1, b2):
    dx, dy = b2.x - b1.x, b2.y - b1.y
    dist = math.hypot(dx, dy)
    if dist < b1.radius + b2.radius:
        nx, ny = dx/dist, dy/dist
        dvx, dvy = b1.vx - b2.vx, b1.vy - b2.vy
        impulse = dvx*nx + dvy*ny
        if impulse > 0: return # Moving away
        b1.vx -= impulse * nx
        b1.vy -= impulse * ny
        b2.vx += impulse * nx
        b2.vy += impulse * ny
        # De-penetrate
        overlap = (b1.radius + b2.radius) - dist
        b1.x -= nx * overlap * 0.5
        b1.y -= ny * overlap * 0.5
        b2.x += nx * overlap * 0.5
        b2.y += ny * overlap * 0.5

# --- GAME VARIABLES ---
center_x, center_y = WIDTH // 2, HEIGHT // 2
score1, score2 = 0, 0
ball1 = Ball(center_x - 60, center_y, TRABZON_COLORS, "TS")
ball2 = Ball(center_x + 60, center_y, FENER_COLORS, "FB")

# Goal
goal_angle = math.pi / 2
goal_rotating = False
goal_rot_speed = 0.015

# Time Management
state = "FIRST_HALF" # FIRST_HALF, HALFTIME, SECOND_HALF, FULLTIME
frame_counter = 0
added_time_1 = random.randint(1, 3)
added_time_2 = random.randint(2, 8)
display_added_time = False

# Crowd Background
crowd = []
for _ in range(100):
    crowd.append((random.randint(0, WIDTH), random.randint(0, HEIGHT), random.choice([TRABZON_COLORS[0], FENER_COLORS[1], (50,50,50)])))

running = True
while running:
    # --- INPUT ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

    # --- LOGIC ---
    
    # 1. Timer Logic
    if state in ["FIRST_HALF", "SECOND_HALF"]:
        frame_counter += 1
        
        # Calculate current minute
        total_mins_played = frame_counter // FRAMES_PER_SIM_MINUTE
        
        # First Half Check
        if state == "FIRST_HALF":
            sim_minute = total_mins_played
            if sim_minute >= 45:
                display_added_time = True
                if sim_minute >= 45 + added_time_1:
                    state = "HALFTIME"
                    pygame.time.delay(1000) # Pause briefly before showing HT screen
            else:
                display_added_time = False
        
        # Second Half Check
        elif state == "SECOND_HALF":
            sim_minute = 45 + total_mins_played # Reset counter at HT
            if sim_minute >= 90:
                display_added_time = True
                if sim_minute >= 90 + added_time_2:
                    state = "FULLTIME"
            else:
                display_added_time = False

    # 2. Physics (Only move if playing)
    if state in ["FIRST_HALF", "SECOND_HALF"]:
        if goal_rotating:
            goal_angle = (goal_angle + goal_rot_speed) % (2 * math.pi)

        for b in [ball1, ball2]:
            b.move()
            b.collide_wall(center_x, center_y, ARENA_RADIUS)

        check_collision(ball1, ball2)

        # Goal Detection
        for b in [ball1, ball2]:
            dist = math.hypot(b.x - center_x, b.y - center_y)
            if dist > ARENA_RADIUS - b.radius - 5:
                ball_ang = math.atan2(b.y - center_y, b.x - center_x)
                diff = abs(ball_ang - goal_angle)
                while diff > math.pi: diff = abs(diff - 2*math.pi)
                
                if diff < GOAL_WIDTH_RADIANS / 2:
                    # GOAL!
                    if b == ball1: score1 += 1
                    else: score2 += 1
                    
                    if score1 + score2 >= 1: goal_rotating = True
                    goal_angle = math.pi / 2 # Reset goal pos
                    
                    # Reset Balls
                    ball1.x, ball1.y = center_x - 60, center_y
                    ball2.x, ball2.y = center_x + 60, center_y
                    ball1.vx, ball1.vy = random.choice([-SPEED, SPEED]), random.choice([-SPEED, SPEED])
                    ball2.vx, ball2.vy = random.choice([-SPEED, SPEED]), random.choice([-SPEED, SPEED])
                    pygame.time.delay(500)

    # 3. State Transitions
    if state == "HALFTIME":
        # Simply wait or click to continue. Here we auto-resume after 2s
        pygame.time.delay(2000)
        state = "SECOND_HALF"
        frame_counter = 0 # Reset frame counter for 2nd half logic
        display_added_time = False

    # --- DRAWING ---
    screen.fill(BLACK)
    
    # Draw Crowd (Static background detail)
    for dot in crowd:
        pygame.draw.circle(screen, dot[2], (dot[0], dot[1]), 2)

    # Draw Pitch
    draw_striped_pitch(screen, center_x, center_y, ARENA_RADIUS)
    
    # Draw Goal Net (Behind the wall line)
    draw_rotating_net(screen, center_x, center_y, ARENA_RADIUS, goal_angle, GOAL_WIDTH_RADIANS)

    # Draw Balls
    ball1.draw(screen)
    ball2.draw(screen)

    # --- UI & OVERLAYS ---
    
    # Scoreboard
    score_surf = font_score.render(f"{score1} - {score2}", True, WHITE)
    screen.blit(score_surf, (WIDTH//2 - score_surf.get_width()//2, 40))

    # Timer String Construction
    time_str = ""
    if state == "FIRST_HALF":
        if display_added_time:
            time_str = f"45 + {sim_minute - 45}'"
            col = (255, 50, 50) # Red for stoppage
        else:
            time_str = f"{sim_minute}'"
            col = WHITE
    elif state == "HALFTIME":
        time_str = "HT"
        col = (255, 255, 0)
    elif state == "SECOND_HALF":
        if display_added_time:
            time_str = f"90 + {sim_minute - 90}'"
            col = (255, 50, 50)
        else:
            time_str = f"{sim_minute}'"
            col = WHITE
    elif state == "FULLTIME":
        time_str = "FT"
        col = (255, 255, 0)

    timer_surf = font_timer.render(time_str, True, col)
    screen.blit(timer_surf, (WIDTH//2 - timer_surf.get_width()//2, 90))

    # Big Overlay for Half/Full time
    if state == "HALFTIME":
        overlay = font_event.render("HALF TIME", True, WHITE)
        screen.blit(overlay, (WIDTH//2 - overlay.get_width()//2, HEIGHT//2 - 50))
    elif state == "FULLTIME":
        overlay = font_event.render("FULL TIME", True, WHITE)
        screen.blit(overlay, (WIDTH//2 - overlay.get_width()//2, HEIGHT//2 - 50))
        # Optional: Stop loop or restart
        # pygame.time.delay(3000); running = False 

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()