# MoonLanderGame.py

import pygame
import math
import random
from fitness_display import FitnessDisplay

class MoonLanderGame:
    def __init__(self, show_individual_fitness=True):
        # Initialize Pygame
        pygame.init()

        # Set up the display
        self.WIDTH = 800
        self.HEIGHT = 600
        self.screen = None
        self.clock = None

        # Game settings
        self.MAX_LANDING_ANGLE = 300  # Maximum angle (in degrees) for safe landing
        self.MAX_LANDING_SPEED = 10   # Maximum speed for safe landing

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

        # Game state
        self.reset()

        self.CLOCK_SPEED = 600  # New attribute to store the clock speed
        self.TIME_SCALE = self.CLOCK_SPEED / 60  # Scale factor for time

        # Fitness display
        self.fitness_display = FitnessDisplay(200, 150, max_points=1000, show_individual=show_individual_fitness)
        self.fitness_surface = None

    def initialize_display(self):
        if self.screen is None:
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
            pygame.display.set_caption("Moon Lander")
            self.clock = pygame.time.Clock()

    def generate_platform_position(self):
        x = random.randint(self.BOX_LEFT, self.BOX_RIGHT - self.PLATFORM_WIDTH)
        y = random.randint(self.BOX_TOP, self.BOX_BOTTOM - self.PLATFORM_HEIGHT)
        return pygame.Rect(x, y, self.PLATFORM_WIDTH, self.PLATFORM_HEIGHT)

    def generate_rocket_position(self):
        x = random.randint(self.ROCKET_START_LEFT, self.ROCKET_START_RIGHT)
        y = random.randint(self.ROCKET_START_TOP, self.ROCKET_START_BOTTOM)
        return pygame.math.Vector2(x, y)

    def reset(self):
        self.initialize_display()
        self.position = self.generate_rocket_position()
        self.velocity = pygame.math.Vector2(0, 0)
        self.angle = 0
        self.game_over = False
        self.landed = False
        self.current_time = 0  # Reset the timer
        self.platform_rect = self.generate_platform_position()
        self.running = True
        self.score = 0
        self.thrust = False  # Reset thrust when resetting the game
        self.rocket_rect.center = self.position
        return self.get_state()

    def reset_rocket(self):
        self.position = self.generate_rocket_position()
        self.velocity = pygame.math.Vector2(0, 0)
        self.angle = 0
        self.thrust = False
        self.landed = False
        self.rocket_rect.center = self.position

    def get_state(self):
        # Return the current state of the game
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
            self.thrust = action[2]  # Update the thrust attribute
            if self.thrust:
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

            # Initialize reward
            reward = 0

            # Check for landing or crash
            if rotated_rect.colliderect(self.platform_rect):
                if abs(self.angle) < self.MAX_LANDING_ANGLE and self.velocity.length() < self.MAX_LANDING_SPEED:
                    self.landed = True
                    self.score += 100  # Increase the score
                    reward = 1000  # Reward for landing
                    self.reset_rocket()
                else:
                    self.landed = False
                    self.game_over = True
                    reward = -100  # Penalty for crashing
            elif rotated_rect.bottom >= self.HEIGHT:
                self.landed = False
                self.game_over = True
                reward = -100  # Penalty for crashing

            if not self.game_over and not self.landed:
                # Reward for getting closer to the platform
                distance = self.platform_rect.center - self.position
                reward = -distance.length() / 1000  # Normalize

        self.draw()

        # Tick the clock
        self.clock.tick(self.CLOCK_SPEED)

        # Update time (scaled to match the increased clock speed)
        self.current_time += self.clock.get_time() * self.TIME_SCALE

        # Get new state
        state = self.get_state()

        return state, reward, self.game_over, {}

    def draw(self):
        # Fill the screen with a dark color (space-like)
        self.screen.fill((20, 20, 40))

        # Draw the platform
        pygame.draw.rect(self.screen, (200, 200, 200), self.platform_rect)

        # Draw the flames if thrust is applied
        if self.thrust:
            rotated_flames = pygame.transform.rotate(self.flames_img, self.angle)
            flames_offset = pygame.math.Vector2(0, self.rocket_rect.height * 0.75).rotate(-self.angle)
            flames_pos = self.rocket_rect.center + flames_offset
            flames_rect = rotated_flames.get_rect(center=flames_pos)
            self.screen.blit(rotated_flames, flames_rect)

        # Draw the rotated rocket
        rotated_rocket = pygame.transform.rotate(self.rocket_img, self.angle)
        rotated_rect = rotated_rocket.get_rect(center=self.rocket_rect.center)
        self.screen.blit(rotated_rocket, rotated_rect)

        # Display speed
        speed = self.velocity.length()
        velocity_text = f"Speed: {speed:.2f}"
        speed_surface = self.font.render(velocity_text, True, (255, 255, 255))
        self.screen.blit(speed_surface, (10, 10))

        # Display current time (adjusted for the increased speed)
        time_text = f"Time: {self.current_time / 1000:.2f}"
        time_surface = self.font.render(time_text, True, (255, 255, 255))
        self.screen.blit(time_surface, (10, 50))

        # Display the score
        score_text = f"Score: {self.score}"
        score_surface = self.font.render(score_text, True, (255, 255, 255))
        self.screen.blit(score_surface, (10, 90))

        # Update the game over message
        if self.game_over:
            text = self.font.render("Crashed!", True, (255, 0, 0))
            text_rect = text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
            self.screen.blit(text, text_rect)

        # Display the fitness graph
        if self.fitness_surface:
            self.screen.blit(self.fitness_surface, (self.WIDTH - 220, 20))

        # Update the display
        pygame.display.flip()

    def update_fitness_display(self, game_number, fitness):
        self.fitness_surface = self.fitness_display.update(game_number, fitness)

    def close(self):
        # Close the fitness display and Pygame
        self.fitness_display.close()
        if self.screen is not None:
            pygame.quit()
            self.screen = None
            self.clock = None
