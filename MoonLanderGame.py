# MoonLanderGame.py

import pygame
import math
import random

class MoonLanderGame:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Set up the display
        self.WIDTH = 800
        self.HEIGHT = 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Moon Lander")

        # Game settings
        self.MAX_LANDING_ANGLE = 40  # Maximum angle (in degrees) for safe landing
        self.MAX_LANDING_SPEED = 5   # Maximum speed for safe landing

        # Load and resize the rocket image
        self.rocket_img = pygame.image.load("Rocket.png")
        self.rocket_img = pygame.transform.scale(self.rocket_img, (self.rocket_img.get_width() // 2, self.rocket_img.get_height() // 2))
        self.rocket_rect = self.rocket_img.get_rect()
        self.rocket_rect.center = (self.WIDTH // 2, self.HEIGHT // 4)  # Position the rocket at the top quarter of the screen

        # Load and resize the flames image
        self.flames_img = pygame.image.load("Flames.png")
        self.flames_img = pygame.transform.scale(self.flames_img, (self.rocket_img.get_width(), self.rocket_img.get_height()))
        self.flames_rect = self.flames_img.get_rect()

        # Platform properties
        self.PLATFORM_WIDTH = 100
        self.PLATFORM_HEIGHT = 10

        # Calculate the box where the platform can appear (20% smaller than the window)
        self.MARGIN = 0.1  # 10% margin on each side
        self.BOX_LEFT = int(self.WIDTH * self.MARGIN)
        self.BOX_RIGHT = int(self.WIDTH * (1 - self.MARGIN))
        self.BOX_TOP = int(self.HEIGHT * self.MARGIN)
        self.BOX_BOTTOM = int(self.HEIGHT * (1 - self.MARGIN))

        # Calculate the box where the rocket can start (top 20% of the screen)
        self.ROCKET_START_MARGIN = 0.2  # 20% of the screen height
        self.ROCKET_START_TOP = 0
        self.ROCKET_START_BOTTOM = int(self.HEIGHT * self.ROCKET_START_MARGIN)
        self.ROCKET_START_LEFT = int(self.WIDTH * 0.1)  # 10% from the left edge
        self.ROCKET_START_RIGHT = int(self.WIDTH * 0.9)  # 10% from the right edge

        # Physics constants
        self.GRAVITY = 0.1
        self.THRUST = 0.2
        self.ROTATION_SPEED = 3
        self.MAX_SPEED = 5

        # Initialize font
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)

        # Initialize clock
        self.clock = pygame.time.Clock()

        # Game state
        self.reset()

    def generate_platform_position(self):
        x = random.randint(self.BOX_LEFT, self.BOX_RIGHT - self.PLATFORM_WIDTH)
        y = random.randint(self.BOX_TOP, self.BOX_BOTTOM - self.PLATFORM_HEIGHT)
        return pygame.Rect(x, y, self.PLATFORM_WIDTH, self.PLATFORM_HEIGHT)

    def generate_rocket_position(self):
        x = random.randint(self.ROCKET_START_LEFT, self.ROCKET_START_RIGHT)
        y = random.randint(self.ROCKET_START_TOP, self.ROCKET_START_BOTTOM)
        return pygame.math.Vector2(x, y)

    def reset(self):
        self.position = self.generate_rocket_position()
        self.velocity = pygame.math.Vector2(0, 0)
        self.angle = 0
        self.game_over = False
        self.landed = False
        self.current_time = 0  # Reset the timer
        self.platform_rect = self.generate_platform_position()
        self.running = True
        self.score = 0
        return self.get_state()

    def get_state(self):
        # Return the current state of the game
        # You can include position, velocity, angle, and distance to platform
        distance = self.platform_rect.center - self.position
        state = [
            self.position.x / self.WIDTH,
            self.position.y / self.HEIGHT,
            self.velocity.x / self.MAX_SPEED,
            self.velocity.y / self.MAX_SPEED,
            self.angle / 360,
            distance.x / self.WIDTH,
            distance.y / self.HEIGHT
        ]
        return state

    def step(self, action):
        # action is a tuple: (rotate_left, rotate_right, thrust)
        # rotate_left and rotate_right are booleans
        # thrust is a boolean

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.game_over = True

        if not self.game_over:
            # Rotate the rocket
            if action[0]:
                self.angle += self.ROTATION_SPEED
            if action[1]:
                self.angle -= self.ROTATION_SPEED

            # Apply thrust in the direction the rocket is facing
            if action[2]:
                thrust_vector = pygame.math.Vector2(0, -self.THRUST).rotate(-self.angle)
                self.velocity += thrust_vector

            # Apply gravity
            self.velocity.y += self.GRAVITY

            # Limit speed
            if self.velocity.length() > self.MAX_SPEED:
                self.velocity.scale_to_length(self.MAX_SPEED)

            # Update position
            self.position += self.velocity

            # Check if the rocket touches any wall
            if (self.position.x <= 0 or self.position.x >= self.WIDTH or
                self.position.y <= 0 or self.position.y >= self.HEIGHT):
                self.landed = False
                self.game_over = True
            else:
                # Keep the rocket within the screen bounds (for rendering purposes)
                self.position.x = max(0, min(self.position.x, self.WIDTH))
                self.position.y = max(0, min(self.position.y, self.HEIGHT))

            # Update rocket position and rotation
            self.rocket_rect.center = self.position
            rotated_rocket = pygame.transform.rotate(self.rocket_img, self.angle)
            rotated_rect = rotated_rocket.get_rect(center=self.rocket_rect.center)

            # Rotate and position the flames
            rotated_flames = pygame.transform.rotate(self.flames_img, self.angle)
            flames_offset = pygame.math.Vector2(0, rotated_rect.height * 0.75).rotate(-self.angle)  # Increased offset
            flames_pos = rotated_rect.center + flames_offset

            # Check for landing or crash
            if rotated_rect.colliderect(self.platform_rect):
                if abs(self.angle) < self.MAX_LANDING_ANGLE and self.velocity.length() < self.MAX_LANDING_SPEED:
                    self.landed = True
                    self.score += 1000  # Reward for landing
                    self.game_over = True
                else:
                    self.landed = False
                    self.game_over = True
            elif rotated_rect.bottom >= self.HEIGHT:
                self.landed = False
                self.game_over = True

        # Fill the screen with a dark color (space-like)
        self.screen.fill((20, 20, 40))

        # Draw the platform
        pygame.draw.rect(self.screen, (200, 200, 200), self.platform_rect)

        # Draw the flames if thrust is applied
        if action[2]:
            rotated_flames = pygame.transform.rotate(self.flames_img, self.angle)
            flames_offset = pygame.math.Vector2(0, rotated_rect.height * 0.75).rotate(-self.angle)  # Increased offset
            flames_pos = rotated_rect.center + flames_offset
            flames_rect = rotated_flames.get_rect(center=flames_pos)
            self.screen.blit(rotated_flames, flames_rect)

        # Draw the rotated rocket
        self.screen.blit(rotated_rocket, rotated_rect)

        # Display speed
        speed = self.velocity.length()
        velocity_text = f"Speed: {speed:.2f}"
        speed_surface = self.font.render(velocity_text, True, (255, 255, 255))
        self.screen.blit(speed_surface, (10, 10))

        # Display current time
        time_text = f"Time: {self.current_time / 1000:.2f}"
        time_surface = self.font.render(time_text, True, (255, 255, 255))
        self.screen.blit(time_surface, (10, 50))

        # Update the game over message
        if self.game_over and not self.landed:
            text = self.font.render("Crashed!", True, (255, 0, 0))
            text_rect = text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
            self.screen.blit(text, text_rect)
        elif self.game_over and self.landed:
            text = self.font.render("Landed Successfully!", True, (0, 255, 0))
            text_rect = text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
            self.screen.blit(text, text_rect)

        # Update the display
        pygame.display.flip()

        # Tick the clock
        self.clock.tick(600)

        # Update time
        self.current_time += self.clock.get_time()

        # Calculate reward
        reward = 0
        if self.landed:
            reward = 1000  # Reward for landing
        elif self.game_over:
            reward = -100  # Penalty for crashing
        else:
            # Reward for getting closer to the platform
            distance = self.platform_rect.center - self.position
            reward = -distance.length() / 1000  # Normalize

        # Get new state
        state = self.get_state()

        return state, reward, self.game_over, {}

    def close(self):
        pygame.quit()
