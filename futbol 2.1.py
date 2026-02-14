import pygame
import math
import random

# --- CONFIGURATION & PARAMETERS ---
WIDTH, HEIGHT = 540, 960  # Portrait mode
FPS = 60

# Colors
GREEN_FIELD = (34, 139, 34)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
YELLOW = (255, 215, 0)

# Physics Parameters
FRICTION = 0.995        # Slows down objects slightly every frame (1.0 = no friction)
ELASTICITY = 0.8        # Bounciness of collisions
PLAYER_SPEED = 0.2      # How fast players accelerate
MAX_SPEED = 12          # Speed limit to prevent glitching

# Dimensions
CENTER = (WIDTH // 2, HEIGHT // 2)
ARENA_RADIUS = 250
GOAL_WIDTH = 100
BALL_RADIUS = 15
PLAYER_RADIUS = 30

# --- PHYSICS ENGINE ---
class PhysicsObject:
    def __init__(self, x, y, radius, mass, color, label=""):
        self.x = x
        self.y = y
        self.vx = random.choice([-5, 5])
        self.vy = random.choice([-5, 5])
        self.radius = radius
        self.mass = mass
        self.color = color
        self.label = label

    def move(self):
        # Update position
        self.x += self.vx
        self.y += self.vy

        # Friction
        self.vx *= FRICTION
        self.vy *= FRICTION

    def draw(self, screen):
        # Draw circle
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        # Draw border
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 2)
        # Draw Text/Logo Placeholder
        if self.label:
            font = pygame.font.SysFont("Arial", 12, bold=True)
            text = font.render(self.label, True, BLACK)
            text_rect = text.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(text, text_rect)

    def check_wall_collision(self):
        # Distance from center of arena
        dx = self.x - CENTER[0]
        dy = self.y - CENTER[1]
        dist = math.hypot(dx, dy)

        # Check if touching the circular wall
        if dist + self.radius > ARENA_RADIUS:
            # 1. Calculate the Normal Vector (direction from wall to center)
            angle = math.atan2(dy, dx)
            
            # 2. Push object back inside to prevent sticking
            overlap = (dist + self.radius) - ARENA_RADIUS
            self.x -= math.cos(angle) * overlap
            self.y -= math.sin(angle) * overlap

            # 3. Reflect Velocity Vector (Bounce)
            # Formula: v_new = v - 2 * (v . n) * n
            nx = math.cos(angle)
            ny = math.sin(angle)
            
            dot_product = self.vx * nx + self.vy * ny
            
            self.vx -= 2 * dot_product * nx
            self.vy -= 2 * dot_product * ny
            
            # Apply energy loss (wall bounciness)
            self.vx *= ELASTICITY
            self.vy *= ELASTICITY

# --- GAME CLASS ---
class FootballSim:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Physics Football Sim")
        self.clock = pygame.time.Clock()
        self.font_score = pygame.font.SysFont("Arial", 40, bold=True)
        self.font_event = pygame.font.SysFont("Arial", 60, bold=True)

        self.reset_positions()
        
        # Game State
        self.score_team1 = 0
        self.score_team2 = 0
        self.match_time = 0
        self.goal_timer = 0 # For displaying "GOAL" text

    def reset_positions(self):
        # Create Entities
        self.ball = PhysicsObject(CENTER[0], CENTER[1], BALL_RADIUS, 1, WHITE)
        
        # Team 1 (Top - Red)
        self.p1 = PhysicsObject(CENTER[0], CENTER[1] - 100, PLAYER_RADIUS, 5, RED, "TEAM A")
        
        # Team 2 (Bottom - Blue)
        self.p2 = PhysicsObject(CENTER[0], CENTER[1] + 100, PLAYER_RADIUS, 5, BLUE, "TEAM B")
        
        self.players = [self.p1, self.p2]

    def handle_collisions(self):
        # Check collision between ball and players
        for p in self.players:
            dx = self.ball.x - p.x
            dy = self.ball.y - p.y
            dist = math.hypot(dx, dy)

            if dist < self.ball.radius + p.radius:
                # 1. Resolve Overlap (move them apart)
                angle = math.atan2(dy, dx)
                overlap = (self.ball.radius + p.radius) - dist
                
                # Move ball away (it's lighter)
                self.ball.x += math.cos(angle) * overlap
                self.ball.y += math.sin(angle) * overlap

                # 2. Elastic Collision Physics (Transfer Energy)
                # Simple approximation: Swap velocities roughly based on mass
                
                # Normal vector
                nx = dx / dist
                ny = dy / dist
                
                # Relative velocity
                dvx = self.ball.vx - p.vx
                dvy = self.ball.vy - p.vy
                
                # Impact speed
                impact_speed = dvx * nx + dvy * ny
                
                if impact_speed > 0: continue # Already moving apart
                
                # Apply impulse
                impulse = 2 * impact_speed / (self.ball.mass + p.mass)
                
                self.ball.vx -= impulse * p.mass * nx
                self.ball.vy -= impulse * p.mass * ny
                p.vx += impulse * self.ball.mass * nx
                p.vy += impulse * self.ball.mass * ny

    def ai_movement(self):
        # Simple AI: Accelerate towards the ball
        for p in self.players:
            dx = self.ball.x - p.x
            dy = self.ball.y - p.y
            angle = math.atan2(dy, dx)
            
            p.vx += math.cos(angle) * PLAYER_SPEED
            p.vy += math.sin(angle) * PLAYER_SPEED
            
            # Cap max speed
            speed = math.hypot(p.vx, p.vy)
            if speed > MAX_SPEED:
                scale = MAX_SPEED / speed
                p.vx *= scale
                p.vy *= scale

    def check_goal(self):
        # Goal Top (Team B scores)
        if self.ball.y < CENTER[1] - ARENA_RADIUS + BALL_RADIUS + 5:
            if abs(self.ball.x - CENTER[0]) < GOAL_WIDTH // 2:
                self.score_team2 += 1
                self.trigger_goal()

        # Goal Bottom (Team A scores)
        elif self.ball.y > CENTER[1] + ARENA_RADIUS - BALL_RADIUS - 5:
            if abs(self.ball.x - CENTER[0]) < GOAL_WIDTH // 2:
                self.score_team1 += 1
                self.trigger_goal()

    def trigger_goal(self):
        self.goal_timer = 60 # Show text for 1 second (60 frames)
        self.reset_positions()

    def draw_field(self):
        self.screen.fill((20, 20, 20)) # Dark Background
        
        # Draw Field Circle
        pygame.draw.circle(self.screen, GREEN_FIELD, CENTER, ARENA_RADIUS)
        pygame.draw.circle(self.screen, WHITE, CENTER, ARENA_RADIUS, 5) # Boundary Line
        
        # Draw Center Line & Circle
        pygame.draw.circle(self.screen, WHITE, CENTER, 40, 3)
        pygame.draw.line(self.screen, WHITE, (CENTER[0] - ARENA_RADIUS, CENTER[1]), (CENTER[0] + ARENA_RADIUS, CENTER[1]), 2)
        
        # Draw Goals
        # Top Goal
        pygame.draw.rect(self.screen, WHITE, (CENTER[0] - GOAL_WIDTH//2, CENTER[1] - ARENA_RADIUS - 10, GOAL_WIDTH, 20))
        pygame.draw.rect(self.screen, (0,0,0,50), (CENTER[0] - GOAL_WIDTH//2, CENTER[1] - ARENA_RADIUS, GOAL_WIDTH, 40), 1) # Net simulation
        
        # Bottom Goal
        pygame.draw.rect(self.screen, WHITE, (CENTER[0] - GOAL_WIDTH//2, CENTER[1] + ARENA_RADIUS - 10, GOAL_WIDTH, 20))

    def run(self):
        running = True
        while running:
            # 1. Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # 2. Physics & Logic
            if self.goal_timer > 0:
                self.goal_timer -= 1
            else:
                self.ai_movement()
                
                # Move entities
                self.ball.move()
                self.p1.move()
                self.p2.move()
                
                # Check Collisions
                self.ball.check_wall_collision()
                self.p1.check_wall_collision()
                self.p2.check_wall_collision()
                self.handle_collisions()
                
                # Check Goals
                self.check_goal()
                
                # Update Time
                self.match_time += 1

            # 3. Drawing
            self.draw_field()
            self.ball.draw(self.screen)
            self.p1.draw(self.screen)
            self.p2.draw(self.screen)

            # Draw UI (Scoreboard)
            score_text = self.font_score.render(f"{self.score_team1} - {self.score_team2}", True, WHITE)
            self.screen.blit(score_text, (CENTER[0] - score_text.get_width() // 2, 50))
            
            time_text = self.font_score.render(f"{self.match_time // 60}'", True, YELLOW)
            self.screen.blit(time_text, (CENTER[0] - time_text.get_width() // 2, 100))

            if self.goal_timer > 0:
                goal_text = self.font_event.render("GOOOOL!", True, YELLOW)
                self.screen.blit(goal_text, (CENTER[0] - goal_text.get_width() // 2, CENTER[1] - goal_text.get_height() // 2))

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

if __name__ == "__main__":
    sim = FootballSim()
    sim.run()