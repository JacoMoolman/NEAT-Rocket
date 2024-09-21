import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moon Lander")

# Game settings
MAX_LANDING_ANGLE = 40  # Maximum angle (in degrees) for safe landing
MAX_LANDING_SPEED = 5   # Maximum speed for safe landing

# Load and resize the rocket image
rocket_img = pygame.image.load("Rocket.png")
rocket_img = pygame.transform.scale(rocket_img, (rocket_img.get_width() // 2, rocket_img.get_height() // 2))
rocket_rect = rocket_img.get_rect()
rocket_rect.center = (WIDTH // 2, HEIGHT // 4)  # Position the rocket at the top quarter of the screen

# Load and resize the flames image
flames_img = pygame.image.load("Flames.png")
flames_img = pygame.transform.scale(flames_img, (rocket_img.get_width(), rocket_img.get_height()))
flames_rect = flames_img.get_rect()

# Platform properties
PLATFORM_WIDTH = 100
PLATFORM_HEIGHT = 10

# Calculate the box where the platform can appear (20% smaller than the window)
MARGIN = 0.1  # 10% margin on each side
BOX_LEFT = int(WIDTH * MARGIN)
BOX_RIGHT = int(WIDTH * (1 - MARGIN))
BOX_TOP = int(HEIGHT * MARGIN)
BOX_BOTTOM = int(HEIGHT * (1 - MARGIN))

# Calculate the box where the rocket can start (top 20% of the screen)
ROCKET_START_MARGIN = 0.2  # 20% of the screen height
ROCKET_START_TOP = 0
ROCKET_START_BOTTOM = int(HEIGHT * ROCKET_START_MARGIN)
ROCKET_START_LEFT = int(WIDTH * 0.1)  # 10% from the left edge
ROCKET_START_RIGHT = int(WIDTH * 0.9)  # 10% from the right edge

# Function to generate a random platform position
def generate_platform_position():
    x = random.randint(BOX_LEFT, BOX_RIGHT - PLATFORM_WIDTH)
    y = random.randint(BOX_TOP, BOX_BOTTOM - PLATFORM_HEIGHT)
    return pygame.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)

# Function to generate a random rocket start position
def generate_rocket_position():
    x = random.randint(ROCKET_START_LEFT, ROCKET_START_RIGHT)
    y = random.randint(ROCKET_START_TOP, ROCKET_START_BOTTOM)
    return pygame.math.Vector2(x, y)

# Function to reset the game
def reset_game():
    global position, velocity, angle, game_over, landed, current_time
    position = generate_rocket_position()
    velocity = pygame.math.Vector2(0, 0)
    angle = 0
    game_over = False
    landed = False
    current_time = 0  # Reset the timer
    return generate_platform_position()

# Generate initial platform and rocket positions
platform_rect = reset_game()

# Physics constants
GRAVITY = 0.1
THRUST = 0.2
ROTATION_SPEED = 3
MAX_SPEED = 5

# Rocket properties
position = pygame.math.Vector2(rocket_rect.center)
velocity = pygame.math.Vector2(0, 0)
angle = 0

# Game state
game_over = False
landed = False

# Initialize font
pygame.font.init()
font = pygame.font.Font(None, 36)

# Game loop
running = True
clock = pygame.time.Clock()
while running:
    dt = clock.tick(60)  # This will now return milliseconds

    if not game_over:
        current_time += dt  # Add the elapsed milliseconds to the timer

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
        # Get pressed keys
        keys = pygame.key.get_pressed()
        
        # Rotate the rocket
        if keys[pygame.K_LEFT]:
            angle += ROTATION_SPEED
        if keys[pygame.K_RIGHT]:
            angle -= ROTATION_SPEED
        
        # Apply thrust in the direction the rocket is facing
        if keys[pygame.K_UP]:
            thrust_vector = pygame.math.Vector2(0, -THRUST).rotate(-angle)
            velocity += thrust_vector

        # Apply gravity
        velocity.y += GRAVITY

        # Update position
        position += velocity

        # Limit speed
        if velocity.length() > MAX_SPEED:
            velocity.scale_to_length(MAX_SPEED)

        # Keep the rocket within the screen bounds
        position.x = max(0, min(position.x, WIDTH))
        position.y = max(0, min(position.y, HEIGHT))

        # Update rocket position and rotation
        rocket_rect.center = position
        rotated_rocket = pygame.transform.rotate(rocket_img, angle)
        rotated_rect = rotated_rocket.get_rect(center=rocket_rect.center)

        # Rotate and position the flames
        rotated_flames = pygame.transform.rotate(flames_img, angle)
        flames_offset = pygame.math.Vector2(0, rotated_rect.height * 0.75).rotate(-angle)  # Increased offset
        flames_pos = rotated_rect.center + flames_offset

        # Check for landing or crash
        if rotated_rect.colliderect(platform_rect):
            if abs(angle) < MAX_LANDING_ANGLE and velocity.length() < MAX_LANDING_SPEED:
                landed = True
                platform_rect = reset_game()  # Reset for next round
            else:
                landed = False
                game_over = True
        elif rotated_rect.bottom >= HEIGHT:
            game_over = True
            landed = False

    # Fill the screen with a dark color (space-like)
    screen.fill((20, 20, 40))

    # Draw the platform
    pygame.draw.rect(screen, (200, 200, 200), platform_rect)

    # Draw the flames if thrust is applied
    if keys[pygame.K_UP]:
        rotated_flames = pygame.transform.rotate(flames_img, angle)
        flames_offset = pygame.math.Vector2(0, rotated_rect.height * 0.75).rotate(-angle)  # Increased offset
        flames_pos = rotated_rect.center + flames_offset
        flames_rect = rotated_flames.get_rect(center=flames_pos)
        screen.blit(rotated_flames, flames_rect)

    # Draw the rotated rocket
    screen.blit(rotated_rocket, rotated_rect)

    # Display speed
    speed = velocity.length()
    velocity_text = f"Speed: {speed:.2f}"
    speed_surface = font.render(velocity_text, True, (255, 255, 255))
    screen.blit(speed_surface, (10, 10))

    # Display current time
    time_text = f"Time: {current_time / 1000:.2f}"
    time_surface = font.render(time_text, True, (255, 255, 255))
    screen.blit(time_surface, (10, 50))

    # Update the game over message
    if game_over and not landed:
        text = font.render("Crashed!", True, (255, 0, 0))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)

    # Update the display
    pygame.display.flip()

    # If game over and not landed (crashed), wait a bit before closing
    if game_over and not landed:
        pygame.time.wait(2000)  # Wait for 2 seconds
        running = False

# Quit the game
pygame.quit()
