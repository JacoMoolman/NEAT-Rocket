import pygame
import math
import random

class MoonLanderGame:
    def __init__(self, net):
        self.net = net
        self.initialize_game()

    def initialize_game(self):
        # Initialize Pygame
        pygame.init()

        # Set up the display
        self.WIDTH = 800
        self.HEIGHT = 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Moon Lander")
        self.clock = pygame.time.Clock()

        # Clock tick rate
        self.CLOCK_SPEED = 400

        # Maximum run time (in game seconds)
        self.MAX_RUN_TIME = 400

        # Load and resize the rocket image
        self.rocket_img = pygame.image.load("Rocket.png")
        self.rocket_img = pygame.transform.scale(self.rocket_img, (self.rocket_img.get_width() // 2, self.rocket_img.get_height() // 2))
        self.rocket_rect = self.rocket_img.get_rect()

        # Load and resize the flames image
        self.flames_img = pygame.image.load("Flames.png")
        self.flames_img = pygame.transform.scale(self.flames_img, (self.rocket_img.get_width(), self.rocket_img.get_height()))
        self.flames_rect = self.flames_img.get_rect()

        # Load and resize the moon image
        self.moon_img = pygame.image.load("Moonimage.png")
        self.target_radius = 20
        self.moon_img = pygame.transform.scale(self.moon_img, (self.target_radius * 2, self.target_radius * 2))
        self.moon_rect = self.moon_img.get_rect()

        # Physics constants
        self.GRAVITY = 0.1
        self.THRUST = 0.2
        self.ROTATION_SPEED = 3
        self.MAX_SPEED = 5

        # Initialize font
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)

        # Generate random stars
        self.stars = []
        for _ in range(100):
            x = random.randint(0, self.WIDTH)
            y = random.randint(0, self.HEIGHT)
            size = random.randint(1, 3)
            self.stars.append((x, y, size))

        self.reset_game()

    def reset_game(self):
        # Reset game state
        self.position = pygame.math.Vector2(self.WIDTH // 2, self.HEIGHT // 4)
        self.velocity = pygame.math.Vector2(0, 0)
        self.angle = 0
        self.running = True
        self.score = 0
        self.thrust = False
        self.target_pos = None

        self.rocket_rect.center = self.position

        self.generate_target_position()

        # Calculate the initial distance between the rocket and the moon
        self.initial_distance = self.position.distance_to(self.target_pos)

        # Reset timer
        self.timer = 0

        # Reset zero speed time and penalty flag
        self.zero_speed_time = 0
        self.penalty_applied = False

    def generate_target_position(self):
        while True:
            x = random.randint(self.target_radius, self.WIDTH - self.target_radius)
            y = random.randint(self.target_radius, self.HEIGHT - self.target_radius)
            self.target_pos = pygame.math.Vector2(x, y)
            self.moon_rect.center = self.target_pos
            if self.target_pos.distance_to(self.position) > 100:
                break

    def run_genome(self, genome):
        # Initialize game state
        self.position = pygame.math.Vector2(self.WIDTH // 2, self.HEIGHT // 4)
        self.velocity = pygame.math.Vector2(0, 0)
        self.angle = 0
        self.running = True
        self.score = 0
        self.thrust = False
        self.target_pos = None

        self.rocket_rect.center = self.position

        self.generate_target_position()

        # Calculate the initial distance between the rocket and the moon
        self.initial_distance = self.position.distance_to(self.target_pos)

        # Reset timer
        self.timer = 0

        # Reset zero speed time and penalty flag
        self.zero_speed_time = 0
        self.penalty_applied = False

        while self.timer < self.MAX_RUN_TIME:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            # Get input values for the neural network
            inputs = [
                self.position.x / self.WIDTH,
                self.position.y / self.HEIGHT,
                self.angle / 360,
                self.velocity.x / self.MAX_SPEED,
                self.velocity.y / self.MAX_SPEED,
                self.position.distance_to(self.target_pos) / math.sqrt(self.WIDTH**2 + self.HEIGHT**2)
            ]

            # Get the output from the neural network
            outputs = self.net.activate(inputs)

            # Interpret the output and take actions
            if outputs[0] > 0.5:
                self.angle += self.ROTATION_SPEED
            if outputs[1] > 0.5:
                self.angle -= self.ROTATION_SPEED
            self.thrust = outputs[2] > 0.5

            # Apply thrust in the direction the rocket is facing
            if self.thrust:
                thrust_vector = pygame.math.Vector2(0, -self.THRUST).rotate(-self.angle)
                self.velocity += thrust_vector

            # Apply gravity
            self.velocity.y += self.GRAVITY

            # Limit speed
            if self.velocity.length() > self.MAX_SPEED:
                self.velocity.scale_to_length(self.MAX_SPEED)

            # Check if the rocket collides with the screen bounds
            if self.position.x <= 0 or self.position.x >= self.WIDTH or self.position.y <= 0 or self.position.y >= self.HEIGHT:
                self.velocity = pygame.math.Vector2(0, 0)  # Set velocity to zero if the rocket hits the wall

            # Update position
            self.position += self.velocity

            # Update rocket rect position
            self.rocket_rect.center = self.position

            # Update timer based on clock speed
            elapsed_time = self.clock.get_time()
            self.timer += elapsed_time * (60 / self.CLOCK_SPEED)

            # Check if the rocket's speed is zero
            if self.velocity.length() == 0:
                self.zero_speed_time += elapsed_time
            else:
                self.zero_speed_time = 0

            # Check if the zero speed time exceeds 5 seconds
            if self.zero_speed_time >= 500 and not self.penalty_applied:
                self.score -= 100  # Apply penalty for not moving
                self.penalty_applied = True
                self.running = False  # End the game

            # Check if the rocket collides with the moon
            if self.rocket_rect.colliderect(self.moon_rect):
                self.score += 100  # Add a reward of 100 for hitting the moon
                self.generate_target_position()
                self.initial_distance = self.position.distance_to(self.target_pos)  # Update initial distance

            # Keep the rocket within the screen bounds
            self.position.x = max(0, min(self.position.x, self.WIDTH))
            self.position.y = max(0, min(self.position.y, self.HEIGHT))

            self.draw()

            # Tick the clock
            self.clock.tick(self.CLOCK_SPEED)

        # Calculate fitness based on distance to target
        current_distance = self.position.distance_to(self.target_pos)
        distance_fitness = (self.initial_distance - current_distance) / self.initial_distance

        fitness = distance_fitness + self.score  # Include the score in the fitness calculation

        # Display fitness score for the current genome
        print(f"Genome {genome.key}: {fitness:.2f}")

        return fitness

    def draw(self):
        # Fill the screen with black color
        self.screen.fill((0, 0, 0))

        # Draw the stars
        for star in self.stars:
            x, y, size = star
            pygame.draw.circle(self.screen, (255, 255, 255), (x, y), size)

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
        self.screen.blit(speed_surface, (10, 40))

        # Render timer text
        timer_text = self.font.render(f"Time: {int(self.timer / 60):02d}.{int(self.timer % 60):02d}", True, (255, 255, 255))
        self.screen.blit(timer_text, (10, 10))

        # Display score
        score_text = f"Score: {self.score}"
        score_surface = self.font.render(score_text, True, (255, 255, 255))
        self.screen.blit(score_surface, (10, 70))

        # Display current fitness
        current_fitness = (self.initial_distance - self.position.distance_to(self.target_pos)) / self.initial_distance + self.score
        fitness_text = f"Fitness: {current_fitness:.2f}"
        fitness_surface = self.font.render(fitness_text, True, (255, 255, 255))
        self.screen.blit(fitness_surface, (10, 100))

        # Display distance to target
        distance_to_target = self.position.distance_to(self.target_pos)
        distance_text = f"Distance to Target: {distance_to_target:.2f}"
        distance_surface = self.font.render(distance_text, True, (255, 255, 255))
        self.screen.blit(distance_surface, (10, 130))

        # Draw the moon image
        self.screen.blit(self.moon_img, self.moon_rect)

        # Update the display
        pygame.display.flip()
