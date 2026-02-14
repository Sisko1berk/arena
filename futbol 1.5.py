import pygame
import math
import random

# --- CONFIGURATION ---
WIDTH, HEIGHT = 600, 900  # Vertical "Phone" Aspect Ratio
FPS = 60
ARENA_RADIUS = 280
MARBLE_RADIUS = 35
BALL_RADIUS = 20
SPEED_LIMIT = 15

# Colors
GRASS_GREEN = (30, 160, 30)
LINE_WHITE = (255, 255, 255)
UI_BG = (20, 20, 20)
TEXT_COLOR = (255, 255, 255)

# --- SETUP ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Marble Football Sim")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 50, bold=True)

# Helper to load images or make placeholders
def load_circular_image(filename, color, radius):
    try:
        img = pygame.image.load(filename).convert_alpha()
        img = pygame.transform.scale(img, (radius*2, radius*2))
        return img
    except FileNotFoundError:
        # Fallback if image isn't found
        surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (radius, radius), radius)
        return surf

# --- PHYSICS CLASS ---
class Marble:
    def __init__(self, x, y, radius, img_name, color, is_ball=False):
        self.x = x
        self.y = y
        self.radius = radius
        self.img = load_circular_image(img_name, color, radius)
        self.vx = random.choice([-8, 8])
        self.vy = random.choice([-8, 8])
        self.is_ball = is_ball
        self.mass = 1 if is_ball else 3  # Teams are heavier than the ball

    def move(self):
        self.x += self.vx
        self.y += self.vy
        
        # Friction (Air resistance)
        self.vx *= 0.995
        self.vy *= 0.995

    def draw(self, surface):
        rect = self.img.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(self.img, rect)

    def check_wall_collision(self, center_x, center_y, arena_radius):
        dx = self.x - center_x
        dy = self.y - center_y
        dist = math.hypot(dx, dy)

        if dist + self.radius > arena_radius:
            # Physics: Push back inside
            angle = math.atan2(dy, dx)
            overlap = (dist + self.radius) - arena_radius
            self.x -= math.cos(angle) * overlap
            self.y -= math.sin(angle) * overlap

            # Physics: Reflect Velocity (Bounce)
            # Normal Vector (n)
            nx, ny = math.cos(angle), math.sin(angle)
            # Dot Product
            dot = self.vx * nx + self.vy * ny
            # Reflection
            self.vx -= 2 * dot * nx
            self.vy -= 2 * dot * ny
            
            # Add "Bounciness" energy loss
            self.vx *= 0.9
            self.vy *= 0.9

# --- MAIN LOOP ---
def main():
    # Center of the field
    cx, cy = WIDTH // 2, HEIGHT // 2 + 50
    
    # Create Objects
    team1 = Marble(cx - 100, cy, MARBLE_RADIUS, "team1.png", (200, 50, 50))
    team2 = Marble(cx + 100, cy, MARBLE_RADIUS, "team2.png", (50, 50, 200))
    ball = Marble(cx, cy - 150, BALL_RADIUS, "ball.png", (255, 255, 255), is_ball=True)
    
    objects = [team1, team2, ball]
    
    score1, score2 = 0, 0
    running = True

    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2. Physics Logic
        for obj in objects:
            obj.move()
            obj.check_wall_collision(cx, cy, ARENA_RADIUS)

        # Marble-to-Marble Collisions
        for i in range(len(objects)):
            for j in range(i + 1, len(objects)):
                o1 = objects[i]
                o2 = objects[j]
                
                dx = o2.x - o1.x
                dy = o2.y - o1.y
                dist = math.hypot(dx, dy)
                
                if dist < o1.radius + o2.radius:
                    # Simple Elastic Collision Response
                    angle = math.atan2(dy, dx)
                    
                    # Prevent sticking (Push apart)
                    overlap = (o1.radius + o2.radius - dist) / 2
                    o1.x -= math.cos(angle) * overlap
                    o1.y -= math.sin(angle) * overlap
                    o2.x += math.cos(angle) * overlap
                    o2.y += math.sin(angle) * overlap

                    # Exchange Velocities (Simplified for "Marble" feel)
                    o1.vx, o2.vx = o2.vx, o1.vx
                    o1.vy, o2.vy = o2.vy, o1.vy

        # Goal Detection (Bottom of circle)
        if ball.y > cy + ARENA_RADIUS - 40:
             if abs(ball.x - cx) < 80: # If inside goal width
                 # Goal Scored! 
                 # In these videos, usually the team closest to ball gets point
                 # For simplicity, we'll just alternate or random here
                 if ball.x < cx: score1 += 1
                 else: score2 += 1
                 
                 # Reset Ball
                 ball.x, ball.y = cx, cy
                 ball.vx, ball.vy = 0, 0

        # 3. Drawing
        screen.fill(UI_BG) # Dark Background for "Video" look

        # Draw Scoreboard
        pygame.draw.rect(screen, (40, 40, 40), (0, 0, WIDTH, 100))
        text = font.render(f"{score1} - {score2}", True, TEXT_COLOR)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 25))

        # Draw Arena
        pygame.draw.circle(screen, GRASS_GREEN, (cx, cy), ARENA_RADIUS)
        pygame.draw.circle(screen, LINE_WHITE, (cx, cy), ARENA_RADIUS, 5)
        pygame.draw.circle(screen, LINE_WHITE, (cx, cy), 50, 2) # Center circle
        
        # Draw Goal Box
        pygame.draw.rect(screen, LINE_WHITE, (cx - 60, cy + ARENA_RADIUS - 10, 120, 20))

        # Draw Players
        for obj in objects:
            obj.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()