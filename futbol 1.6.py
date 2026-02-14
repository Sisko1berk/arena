import pygame
import math
import random

# --- CONFIGURATION ---
WIDTH, HEIGHT = 600, 900
FPS = 60
ARENA_RADIUS = 280
MARBLE_RADIUS = 30

# Colors
GRASS_GREEN = (30, 160, 30)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
BLUE = (50, 50, 255)
BG_COLOR = (20, 20, 20)

# --- SETUP ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Step 2: Physics & Wall Bouncing")
clock = pygame.time.Clock()

# --- THE PHYSICS CLASS ---
class Marble:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.radius = MARBLE_RADIUS
        self.color = color
        
        # 1. Give it random speed (Velocity)
        # We pick a random number between -8 and 8 for both directions
        self.vx = random.choice([-8, -6, 6, 8])
        self.vy = random.choice([-8, -6, 6, 8])

    def move(self):
        # 2. Update Position
        self.x += self.vx
        self.y += self.vy

    def check_wall_collision(self, center_x, center_y, arena_radius):
        # Calculate distance from the center of the arena
        dx = self.x - center_x
        dy = self.y - center_y
        dist = math.hypot(dx, dy)

        # Check if we hit the wall
        # (Distance from center + our radius) > Arena Radius
        if dist + self.radius > arena_radius:
            
            # --- THE MATH PART ---
            
            # A. Calculate the Angle of the wall at the point of impact
            angle = math.atan2(dy, dx)
            
            # B. Push the marble back inside (so it doesn't get stuck)
            overlap = (dist + self.radius) - arena_radius
            self.x -= math.cos(angle) * overlap
            self.y -= math.sin(angle) * overlap

            # C. Reflect the Velocity (Bounce)
            # We need the "Normal Vector" (nx, ny) which points from wall to center
            nx = math.cos(angle)
            ny = math.sin(angle)
            
            # Dot Product formula allows us to calculate reflection
            dot_product = self.vx * nx + self.vy * ny
            
            # Apply reflection
            self.vx -= 2 * dot_product * nx
            self.vy -= 2 * dot_product * ny
            
            # Optional: Lose a tiny bit of energy (Friction)
            self.vx *= 0.95
            self.vy *= 0.95

    def draw(self, surface):
        # Draw the main circle
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        # Draw a white outline so it looks like a token
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius, 3)

# --- MAIN GAME LOOP ---
def main():
    # Define the center of our circular arena
    cx, cy = WIDTH // 2, HEIGHT // 2
    
    # Create two marbles
    marble1 = Marble(cx - 100, cy, RED)
    marble2 = Marble(cx + 100, cy, BLUE)
    
    running = True
    while running:
        # 1. Handle Events (Close button)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2. Physics Logic
        marble1.move()
        marble1.check_wall_collision(cx, cy, ARENA_RADIUS)
        
        marble2.move()
        marble2.check_wall_collision(cx, cy, ARENA_RADIUS)

        # 3. Drawing
        screen.fill(BG_COLOR) # Clear screen
        
        # Draw Arena
        pygame.draw.circle(screen, GRASS_GREEN, (cx, cy), ARENA_RADIUS)
        pygame.draw.circle(screen, WHITE, (cx, cy), ARENA_RADIUS, 5) # Outline
        
        # Draw Marbles
        marble1.draw(screen)
        marble2.draw(screen)

        pygame.display.flip() # Show the frame
        clock.tick(FPS) # Limit speed to 60 FPS

    pygame.quit()

if __name__ == "__main__":
    main()