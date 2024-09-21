# MoonLanderGame.py

import pygame
import math
import random

class MoonLanderGame:
    def __init__(self, render=False):
        # Initialize Pygame only if rendering is enabled
        self.render = render
        if self.render:
            pygame.init()
            self.screen = pygame.display.set_mode((800, 600))
            pygame.display.set_caption("Moon Lander")
            self.clock = pygame.time.Clock()
            self.font = pygame.font.Font(None, 36)
        else:
            pygame.font.init()
            self.font = pygame.font.Font(None, 36)

        # Game settings
        self.WIDTH = 800
        self.HEIGHT = 600
        self.MAX_LANDING_ANGLE = 40  # Maximum angle (in degrees) for safe landing
        self.MAX_LANDING_SPEED = 5   # Maximum speed for safe landing

        # Load and resize the rocket image
        self.rocket_img = pygame.image.load("Rocket.png")
        self.rocket_img = pygame.transform.scale(self.rocket_img, (self.rocket_img.get_width() // 2, self.rocket_img.get_height() // 2))
        self.rocket_rect = self.rocket_img.get_rect()

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

        # Game state variables
        self.reset()

    def reset(self):
        self.position = self.generate_rocket_position()
        self.velocity = pygame.math.Vector2(0, 0)
        self.angle = 0
        self.game_over = False
        self.landed = False
        self.current_time = 0  # Reset the timer
        self.platform_rect = self.generate_platform_position()
        return self.get_state()

    def generate_platform_position(self):
        x = random.randint(self.BOX_LEFT, self.BOX_RIGHT - self.PLATFORM_WIDTH)
        y = random.randint(self.BOX_TOP, self.BOX_BOTTOM - self.PLATFORM_HEIGHT)
        return pygame.Rect(x, y, self.PLATFORM_WIDTH, self.PLATFORM_HEIGHT)

    def generate_rocket_position(self):
        x = random.randint(self.ROCKET_START_LEFT, self.ROCKET_START_RIGHT)
        y = random.randint(self.ROCKET_START_TOP, self.ROCKET_START_BOTTOM)
        return pygame.math.Vector2(x, y)

    def step(self, action):
        """
        Performs one game step.
        Action is a tuple: (rotate_direction, thrust)
        rotate_direction: -1 for left, 1 for right, 0 for no rotation
        thrust: 0 for no thrust, 1 for thrust
        """
        if self.game_over:
            return self.get_state(), 0, True, {}

        rotate_direction, thrust = action

        # Rotate the rocket
        self.angle += rotate_direction * self.ROTATION_SPEED

        # Apply thrust in the direction the rocket is facing
        if thrust > 0:
            thrust_vector = pygame.math.Vector2(0, -self.THRUST).rotate(-self.angle)
            self.velocity += thrust_vector

        # Apply gravity
        self.velocity.y += self.GRAVITY

        # Limit speed
        if self.velocity.length() > self.MAX_SPEED:
            self.velocity.scale_to_length(self.MAX_SPEED)

        # Update position
        self.position += self.velocity

        # Keep the rocket within the screen bounds
        self.position.x = max(0, min(self.position.x, self.WIDTH))
        self.position.y = max(0, min(self.position.y, self.HEIGHT))

        # Update rocket position and rotation
        self.rocket_rect.center = self.position
        rotated_rocket = pygame.transform.rotate(self.rocket_img, self.angle)
        rotated_rect = rotated_rocket.get_rect(center=self.rocket_rect.center)

        # Check for landing or crash
        done = False
        reward = -1  # Default step penalty

        if rotated_rect.colliderect(self.platform_rect):
            if abs(self.angle) < self.MAX_LANDING_ANGLE and self.velocity.length() < self.MAX_LANDING_SPEED:
                self.landed = True
                reward = 100  # Reward for successful landing
                done = True
            else:
                self.landed = False
                reward = -100  # Penalty for crashing
                done = True
        elif rotated_rect.bottom >= self.HEIGHT:
            self.game_over = True
            self.landed = False
            reward = -100  # Penalty for crashing
            done = True

        self.current_time += 1  # Increment time

        if self.render:
            self.render_game(rotated_rocket, rotated_rect, thrust)

        return self.get_state(), reward, done, {}

    def get_state(self):
        """
        Returns the current state as a list:
        [rocket_x, rocket_y, velocity_x, velocity_y, angle, distance_x, distance_y]
        """
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

    def render_game(self, rotated_rocket, rotated_rect, thrust):
        self.screen.fill((20, 20, 40))
        pygame.draw.rect(self.screen, (200, 200, 200), self.platform_rect)
        # Draw the flames if thrust is applied
        if thrust > 0:
            rotated_flames = pygame.transform.rotate(self.flames_img, self.angle)
            flames_offset = pygame.math.Vector2(0, rotated_rect.height * 0.75).rotate(-self.angle)
            flames_pos = rotated_rect.center + flames_offset
            flames_rect = rotated_flames.get_rect(center=flames_pos)
            self.screen.blit(rotated_flames, flames_rect)
        # Draw the rotated rocket
        self.screen.blit(rotated_rocket, rotated_rect)
        # Update the display
        pygame.display.flip()
        self.clock.tick(60)  # Limit to 60 FPS

    def close(self):
        if self.render:
            pygame.quit()
