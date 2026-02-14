import pygame
import sys

# --- Configuration ---
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
BALL_RADIUS = 25           # Updated to your preference
GRAVITY = 0.5
BOUNCE_FACTOR = 0.95       # Updated to your preference
FPS = 60

# Cage Settings (The size of the "room" inside the window)
CAGE_WIDTH, CAGE_HEIGHT = 500, 400
# Calculate top-left corner to center the cage on screen
CAGE_X = (WINDOW_WIDTH - CAGE_WIDTH) // 2
CAGE_Y = (WINDOW_HEIGHT - CAGE_HEIGHT) // 2
CAGE_THICKNESS = 5

# Colors (R, G, B)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
BLACK = (20, 20, 20)      # Dark grey background
GREY  = (100, 100, 100)   # Color of the cage walls

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Red Ball in a Cage")
    clock = pygame.time.Clock()

    # Define the Cage Rectangle (x, y, width, height)
    cage_rect = pygame.Rect(CAGE_X, CAGE_Y, CAGE_WIDTH, CAGE_HEIGHT)

    # --- Ball Initial State ---
    # Spawn in the EXACT center of the cage
    ball_x = cage_rect.centerx
    ball_y = cage_rect.centery
    
    # Initial velocity
    vel_x = 5
    vel_y = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- Physics Logic ---
        vel_y += GRAVITY
        
        ball_x += vel_x
        ball_y += vel_y

        # --- CAGE Collision Detection ---
        # We now check against cage_rect.bottom, cage_rect.top, etc.
        
        # 1. Floor (Bottom of cage)
        if ball_y + BALL_RADIUS > cage_rect.bottom:
            ball_y = cage_rect.bottom - BALL_RADIUS
            vel_y = -vel_y * BOUNCE_FACTOR

        # 2. Ceiling (Top of cage)
        if ball_y - BALL_RADIUS < cage_rect.top:
            ball_y = cage_rect.top + BALL_RADIUS
            vel_y = -vel_y * BOUNCE_FACTOR

        # 3. Right Wall
        if ball_x + BALL_RADIUS > cage_rect.right:
            ball_x = cage_rect.right - BALL_RADIUS
            vel_x = -vel_x * BOUNCE_FACTOR

        # 4. Left Wall
        if ball_x - BALL_RADIUS < cage_rect.left:
            ball_x = cage_rect.left + BALL_RADIUS
            vel_x = -vel_x * BOUNCE_FACTOR

        # --- Drawing ---
        screen.fill(BLACK) 
        
        # Draw the Cage
        pygame.draw.rect(screen, GREY, cage_rect, CAGE_THICKNESS)
        
        # Draw the Ball
        pygame.draw.circle(screen, RED, (int(ball_x), int(ball_y)), BALL_RADIUS)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()