import pygame
import math
import random

class MoonLanderGame:
    def __init__(self):
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
        self.CLOCK_SPEED = 60

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

        self.rocket_rect.center = self.position

        self.generate_target_position()

        # Calculate the initial distance between the rocket and the moon
        self.initial_distance = self.position.distance_to(self.target_pos)

    def generate_target_position(self):
        while True:
            x = random.randint(self.target_radius, self.WIDTH - self.target_radius)
            y = random.randint(self.target_radius, self.HEIGHT - self.target_radius)
            self.target_pos = pygame.math.Vector2(x, y)
            self.moon_rect.center = self.target_pos
            if self.target_pos.distance_to(self.position) > 100:
                break

    def run(self):
        while self.running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Key handling
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.angle += self.ROTATION_SPEED
            if keys[pygame.K_RIGHT]:
                self.angle -= self.ROTATION_SPEED
            self.thrust = keys[pygame.K_UP]

            # Apply thrust in the direction the rocket is facing
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

            # Update rocket rect position
            self.rocket_rect.center = self.position

            # Keep the rocket within the screen bounds
            self.position.x = max(0, min(self.position.x, self.WIDTH))
            self.position.y = max(0, min(self.position.y, self.HEIGHT))

            # Check if the rocket collides with the moon
            if self.rocket_rect.colliderect(self.moon_rect):
                self.score += 500  # Add a reward for hitting the moon
                self.generate_target_position()
                self.initial_distance = self.position.distance_to(self.target_pos)  # Update initial distance

            self.draw()

            # Tick the clock
            self.clock.tick(self.CLOCK_SPEED)

        pygame.quit()

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

        # Display score
        score_text = f"Score: {self.score}"
        score_surface = self.font.render(score_text, True, (255, 255, 255))
        self.screen.blit(score_surface, (10, 70))

        # Draw the moon image
        self.screen.blit(self.moon_img, self.moon_rect)

        # Update the display
        pygame.display.flip()

if __name__ == "__main__":
    game = MoonLanderGame()
    game.run()