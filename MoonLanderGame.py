# MoonLanderGame.py

import pygame
import math
import random
import os
from fitness_display import FitnessDisplay

class MoonLanderGame:
    def __init__(self, show_individual_fitness=True, show_display=True, pop_size=0, minimize_window=False, show_graph=True):
        self.show_display = show_display
        self.minimize_window = minimize_window
        self.show_graph = show_graph
        if not self.show_display:
            # Set SDL to use the dummy NULL video driver, so it doesn't need a windowing system.
            os.environ["SDL_VIDEODRIVER"] = "dummy"
        # Initialize Pygame
        pygame.init()
        pygame.mixer.init()
        # Load the beep sound
        self.beep_sound = pygame.mixer.Sound("beep.mp3")

        # Set up the display
        self.WIDTH = 800
        self.HEIGHT = 600
        self.screen = None
        self.clock = None

        # Game settings
        self.MAX_LANDING_ANGLE = 30  # Maximum angle (in degrees) for safe landing
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
        self.PLATFORM_Y = self.HEIGHT - self.PLATFORM_HEIGHT // 2  # Fixed Y position for the platform
        self.PLATFORM_X = (self.WIDTH - self.PLATFORM_WIDTH) // 2  # Fixed X position in the middle

        # Set the Y coordinate for rocket spawn
        self.ROCKET_START_Y = 50

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

        self.CLOCK_SPEED = 400  # Adjusted clock speed to normal
        self.TIME_SCALE = self.CLOCK_SPEED / 60  # Scale factor for time

        # Fitness display
        self.fitness_display = FitnessDisplay(200, 150, max_points=5000, show_individual=show_individual_fitness and show_graph)

        self.fitness_surface = None

        self.game_number = 0  # Initialize game number here
        self.population_number = 0
        self.current_generation = 0

        self.low_speed_start_time = None
        self.LOW_SPEED_THRESHOLD = 0.9
        self.MAX_LOW_SPEED_DURATION = 5000  # 5 seconds in milliseconds

        self.current_fitness = 0

        self.last_x_position = self.position.x  # Initialize last_x_position
        self.x_position_start_time = None  # Initialize x_position_start_time

        # Initialize display if show_display is True
        if self.show_display:
            self.initialize_display()

        self.pop_size = pop_size

        self.generation = 0  # Initialize generation number

        self.MAX_GAME_TIME = 60 * 1000  # 60 seconds in milliseconds

    def initialize_display(self):
        if self.screen is None:
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
            pygame.display.set_caption("Moon Lander")
            self.clock = pygame.time.Clock()
            
            if self.minimize_window:
                pygame.display.iconify()  # This minimizes the window

    def generate_platform_position(self):
        return pygame.Rect(self.PLATFORM_X, self.PLATFORM_Y, self.PLATFORM_WIDTH, self.PLATFORM_HEIGHT)

    def generate_rocket_position(self):
        x = random.randint(0, self.WIDTH)  # Random X position
        y = self.HEIGHT // 2  # Middle of the screen vertically
        return pygame.math.Vector2(x, y)

    def reset(self):
        self.platform_rect = self.generate_platform_position()
        self.position = self.generate_rocket_position()
        self.velocity = pygame.math.Vector2(0, 0)
        self.angle = 0
        self.game_over = False
        self.landed = False
        self.current_time = 0  # Reset the timer
        self.running = True
        self.score = 0
        self.thrust = False  # Reset thrust when resetting the game
        self.rocket_rect.center = self.position
        self.previous_distance = None  # Initialize previous_distance
        self.current_fitness = 0
        return self.get_state()

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
        if self.show_display:
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

            # Keep angle within [-180, 180] degrees
            if self.angle > 180:
                self.angle -= 360
            elif self.angle < -180:
                self.angle += 360

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

            # Constrain the rocket within the screen bounds
            self.position.x = max(0, min(self.position.x, self.WIDTH))
            self.position.y = max(0, min(self.position.y, self.HEIGHT))

            # Check for low speed condition
            current_speed = self.velocity.length()
            if 0 < current_speed < self.LOW_SPEED_THRESHOLD:
                if self.low_speed_start_time is None:
                    self.low_speed_start_time = self.current_time
                elif self.current_time - self.low_speed_start_time > self.MAX_LOW_SPEED_DURATION:
                    self.landed = False
                    self.game_over = True
                    reward = -100  # Penalty for crashing
            else:
                self.low_speed_start_time = None

            # Check for no X movement condition
            if self.position.x == self.last_x_position:
                if self.x_position_start_time is None:
                    self.x_position_start_time = self.current_time
                elif self.current_time - self.x_position_start_time > self.MAX_LOW_SPEED_DURATION:
                    self.landed = False
                    self.game_over = True
                    reward = -100  # Penalty for no X movement
            else:
                self.x_position_start_time = None

            self.last_x_position = self.position.x  # Update the last X position

            # Remove the check for touching walls
            # Keep the rocket within the screen bounds (for rendering purposes)
            self.position.x = max(0, self.position.x)
            self.position.y = max(0, self.position.y)
            reward = 1  # Initialize reward

            # Update rocket position and rotation
            self.rocket_rect.center = self.position
            rotated_rocket = pygame.transform.rotate(self.rocket_img, self.angle)
            rotated_rect = rotated_rocket.get_rect(center=self.rocket_rect.center)

            # Rotate and position the flames
            rotated_flames = pygame.transform.rotate(self.flames_img, self.angle)
            flames_offset = pygame.math.Vector2(0, rotated_rect.height * 0.75).rotate(-self.angle)  # Increased offset
            flames_pos = rotated_rect.center + flames_offset

            # Calculate distance to platform center on X-axis
            platform_center_x = self.platform_rect.centerx
            current_distance_x = abs(self.position.x - platform_center_x)

            # Compute reward based on change in X-axis distance
            if self.previous_distance is not None:
                delta_distance_x = self.previous_distance - current_distance_x
                reward = delta_distance_x * 1  # Scale reward for more impact
            else:
                reward = 0

            self.previous_distance = current_distance_x  # Update previous distance

            # Check for landing or crash
            if rotated_rect.colliderect(self.platform_rect):
                if abs(self.angle) < self.MAX_LANDING_ANGLE and self.velocity.length() < self.MAX_LANDING_SPEED:
                    self.landed = True
                    self.score += 1  # Increase the score
                    reward += 1000  # Reward for landing
                    if self.show_display:
                        self.beep_sound.play()  # Play the beep sound
                    self.reset()
                else:
                    self.landed = False
                    self.game_over = True
                    reward = -100  # Penalty for crashing
            elif self.position.y + rotated_rect.height / 2 >= self.HEIGHT:
                self.landed = False
                self.game_over = True
                reward = -100  # Penalty for crashing at the bottom of the screen

            # Check if the game has exceeded the time limit
            if self.current_time > self.MAX_GAME_TIME:
                self.game_over = True
                reward = -50  # Penalty for timeout

        if self.show_display:
            self.draw()

        # Tick the clock
        if self.show_display:
            self.clock.tick(self.CLOCK_SPEED)
            # Update time (scaled to match the increased clock speed)
            self.current_time += self.clock.get_time() * self.TIME_SCALE
        else:
            # When not showing display, manage time manually
            self.current_time += (1000 / self.CLOCK_SPEED) * self.TIME_SCALE

        # Get new state
        state = self.get_state()

        self.current_fitness += reward

        return state, reward, self.game_over, {}

    def draw(self):
        if not self.show_display:
            return
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

        # Display the current fitness
        fitness_text = f"Current Fitness: {self.current_fitness:.2f}"
        fitness_surface = self.font.render(fitness_text, True, (255, 255, 255))
        self.screen.blit(fitness_surface, (10, 90))

        # Display the generation number and population number
        generation_text = f"Gen {self.generation-1}, Member #: {self.population_number}"
        generation_surface = self.font.render(generation_text, True, (255, 255, 255))
        self.screen.blit(generation_surface, (10, 130))

        # Display the fitness graph
        if self.fitness_surface and self.show_graph:
            self.screen.blit(self.fitness_surface, (self.WIDTH - 220, 20))

        # Update the display
        pygame.display.flip()

    def update_fitness_display(self, game_number, fitness):
        if self.show_display and self.show_graph:
            self.fitness_surface = self.fitness_display.update(game_number, fitness)
        
        # Update the population number
        self.population_number = game_number % self.pop_size

    def update_generation(self, generation):
        self.generation = generation + 1  # Add 1 to start from 1 instead of 0

    def close(self):
        # Close the fitness display and Pygame
        if self.show_display:
            self.fitness_display.close()
            if self.screen is not None:
                pygame.quit()
                self.screen = None
                self.clock = None
        else:
            pygame.quit()