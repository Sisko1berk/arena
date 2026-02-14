import pygame
import math
import random

# --- CONFIGURATION ---
WIDTH, HEIGHT = 500, 800
FPS = 60
ARENA_RADIUS = 220
BALL_RADIUS = 30
GOAL_WIDTH = 80  # How wide the goal opening is (in degrees or pixels)
SPEED = 7

# Colors
GREEN_FIELD = (34, 139, 34)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE_RING = (0, 0, 255)
# Team Colors
TRABZON_COLORS = [(128, 0, 0), (0, 191, 255)] # Claret & Blue
FENER_COLORS = [(255, 255, 0), (0, 0, 128)]   # Yellow & Navy

# --- SETUP ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Football Simulation")
font = pygame.font.SysFont("Arial", 40, bold=True)
timer_font = pygame.font.SysFont("Arial", 30, bold=True)
clock = pygame.time.Clock()

def load_image_or_color(filename, color, radius, text):
    """
    Helper to create a surface for the ball. 
    If you have images 'ts.png' and 'fb.png', you can modify this to load them.
    """
    surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    pygame.draw.circle(surf, color[0], (radius, radius), radius)
    pygame.draw.circle(surf, color[1], (radius, radius), radius - 5)
    
    # Draw text initials
    text_surf = pygame.font.SysFont("Arial", 20, bold=True).render(text, True, WHITE)
    rect = text_surf.get_rect(center=(radius, radius))
    surf.blit(text_surf, rect)
    return surf

class Ball:
    def __init__(self, x, y, name, color_scheme, initials):
        self.x = x
        self.y = y
        self.vx = random.choice([-SPEED, SPEED])
        self.vy = random.choice([-SPEED, SPEED])
        self.radius = BALL_RADIUS
        self.image = load_image_or_color(None, color_scheme, self.radius, initials)
        self.name = name

    def move(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, surface):
        rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(self.image, rect)

    def collide_circle_wall(self, cx, cy, radius):
        """Reflect velocity vector across the normal of the collision point on the circle"""
        dx = self.x - cx
        dy = self.y - cy
        dist = math.hypot(dx, dy)

        if dist + self.radius >= radius:
            # Normal Vector
            nx = dx / dist
            ny = dy / dist

            # Reflection formula: V_new = V_old - 2 * (V_old . Normal) * Normal
            dot_product = self.vx * nx + self.vy * ny
            self.vx = self.vx - 2 * dot_product * nx
            self.vy = self.vy - 2 * dot_product * ny

            # Push ball back inside to prevent sticking
            overlap = (dist + self.radius) - radius
            self.x -= nx * overlap
            self.y -= ny * overlap
            
            return True # Hit wall
        return False

def check_ball_collision(b1, b2):
    dx = b2.x - b1.x
    dy = b2.y - b1.y
    dist = math.hypot(dx, dy)

    if dist < b1.radius + b2.radius:
        # Simple elastic collision response
        # Calculate normal
        nx = dx / dist
        ny = dy / dist
        
        # Relative velocity
        dvx = b1.vx - b2.vx
        dvy = b1.vy - b2.vy
        
        # Impact speed
        speed_normal = dvx * nx + dvy * ny
        
        # If moving away, don't simulate
        if speed_normal < 0:
            return

        # Impulse (assuming equal mass)
        impulse = speed_normal
        
        b1.vx -= impulse * nx
        b1.vy -= impulse * ny
        b2.vx += impulse * nx
        b2.vy += impulse * ny
        
        # Separate circles to prevent sticking
        overlap = (b1.radius + b2.radius) - dist
        b1.x -= nx * overlap / 2
        b1.y -= ny * overlap / 2
        b2.x += nx * overlap / 2
        b2.y += ny * overlap / 2

def reset_positions():
    """Resets balls to the center with random directions"""
    b1 = Ball(WIDTH//2 - 50, HEIGHT//2, "Trabzon", TRABZON_COLORS, "TS")
    b2 = Ball(WIDTH//2 + 50, HEIGHT//2, "Fener", FENER_COLORS, "FB")
    return b1, b2

# --- GAME STATE ---
center_x, center_y = WIDTH // 2, HEIGHT // 2 + 50
team1, team2 = reset_positions()
score1, score2 = 0, 0
frame_count = 0

# Goal State
goal_angle = math.pi / 2  # Start at bottom (90 degrees or pi/2 radians)
goal_rotating = False
goal_rotation_speed = 0.02

running = True
while running:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. Logic Update
    frame_count += 1
    
    # Move Goal (Rotate if score > 0)
    if goal_rotating:
        goal_angle += goal_rotation_speed
        # Keep angle normalized 0-2pi
        goal_angle = goal_angle % (2 * math.pi)
    
    # Calculate Goal Position (for visuals and collision)
    # The goal is an arc on the perimeter
    goal_x = center_x + math.cos(goal_angle) * ARENA_RADIUS
    goal_y = center_y + math.sin(goal_angle) * ARENA_RADIUS

    # Move Balls
    team1.move()
    team2.move()

    # Wall Collisions
    team1.collide_circle_wall(center_x, center_y, ARENA_RADIUS)
    team2.collide_circle_wall(center_x, center_y, ARENA_RADIUS)

    # Ball vs Ball Collision
    check_ball_collision(team1, team2)

    # Goal Detection
    # Check if a ball is close to the goal center AND touching the edge
    for ball in [team1, team2]:
        dist_to_center = math.hypot(ball.x - center_x, ball.y - center_y)
        # Check if ball is near the wall
        if dist_to_center > ARENA_RADIUS - ball.radius - 5:
            # Check angle difference
            ball_angle = math.atan2(ball.y - center_y, ball.x - center_x)
            # Normalize angles
            diff = abs(ball_angle - goal_angle)
            while diff > math.pi: diff = abs(diff - 2*math.pi)
            
            # If within goal width (approx 15 degrees)
            if diff < 0.25: 
                # GOAL SCORED!
                if ball == team1:
                    score1 += 1
                else:
                    score2 += 1
                
                # Activate rotation after first goal (total score >= 1)
                if score1 + score2 >= 1:
                    goal_rotating = True
                    # Reset goal position to bottom on reset? 
                    # The prompt says "goals position reset", let's reset it to bottom
                    goal_angle = math.pi / 2 
                
                # Reset balls
                team1, team2 = reset_positions()
                pygame.time.delay(500) # Small pause for effect

    # 3. Drawing
    screen.fill(BLACK)

    # Draw Scoreboard
    score_text = font.render(f"{score1} - {score2}", True, WHITE)
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 50))
    
    # Draw Timer (Fake minutes)
    minutes = frame_count // 60  # Assuming 1 sec = 1 minute for fast pace
    timer_text = timer_font.render(f"{minutes}'", True, (255, 165, 0))
    screen.blit(timer_text, (WIDTH//2 - timer_text.get_width()//2, 100))

    # Draw Field
    pygame.draw.circle(screen, GREEN_FIELD, (center_x, center_y), ARENA_RADIUS)
    pygame.draw.circle(screen, BLUE_RING, (center_x, center_y), ARENA_RADIUS, 5)
    
    # Draw Center Circle Line
    pygame.draw.circle(screen, WHITE, (center_x, center_y), 50, 2)
    pygame.draw.line(screen, WHITE, (center_x - ARENA_RADIUS + 10, center_y), (center_x + ARENA_RADIUS - 10, center_y), 2)

    # Draw Goal
    # We draw a thick white line along the arc for the goal
    rect = pygame.Rect(center_x - ARENA_RADIUS, center_y - ARENA_RADIUS, ARENA_RADIUS*2, ARENA_RADIUS*2)
    start_angle = -goal_angle - 0.25  # Negative because pygame arcs go clockwise vs math counter-clockwise
    end_angle = -goal_angle + 0.25
    pygame.draw.arc(screen, WHITE, rect, start_angle, end_angle, 15)
    
    # Visual marker for goal net
    # Draw a small rectangle at the goal position to make it obvious
    pygame.draw.circle(screen, WHITE, (int(goal_x), int(goal_y)), 15)

    # Draw Balls
    team1.draw(screen)
    team2.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()