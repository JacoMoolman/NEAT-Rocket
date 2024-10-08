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
            os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init()
        pygame.mixer.init()
        self.beep_sound = pygame.mixer.Sound("beep.mp3")

        self.WIDTH = 800
        self.HEIGHT = 600
        self.screen = None
        self.clock = None

        self.MAX_LANDING_ANGLE = 30
        self.MAX_LANDING_SPEED = 10

        self.rocket_img = pygame.image.load("Rocket.png")
        self.rocket_img = pygame.transform.scale(self.rocket_img, (self.rocket_img.get_width() // 2, self.rocket_img.get_height() // 2))
        self.rocket_rect = self.rocket_img.get_rect()
        self.rocket_rect.center = (self.WIDTH // 2, self.HEIGHT // 4)

        self.flames_img = pygame.image.load("Flames.png")
        self.flames_img = pygame.transform.scale(self.flames_img, (self.rocket_img.get_width(), self.rocket_img.get_height()))
        self.flames_rect = self.flames_img.get_rect()

        self.PLATFORM_WIDTH = 100
        self.PLATFORM_HEIGHT = 10
        self.PLATFORM_Y = self.HEIGHT - self.PLATFORM_HEIGHT // 2
        self.PLATFORM_X = (self.WIDTH - self.PLATFORM_WIDTH) // 2

        self.ROCKET_START_Y = 50

        self.GRAVITY = 0.1
        self.THRUST = 0.2
        self.ROTATION_SPEED = 3
        self.MAX_SPEED = 5

        pygame.font.init()
        self.font = pygame.font.Font(None, 36)

        self.reset()

        self.CLOCK_SPEED = 50
        self.TIME_SCALE = self.CLOCK_SPEED / 60

        self.fitness_display = FitnessDisplay(200, 150, max_points=5000, show_individual=show_individual_fitness and show_graph)

        self.fitness_surface = None

        self.game_number = 0
        self.population_number = 0
        self.current_generation = 0

        self.low_speed_start_time = None
        self.LOW_SPEED_THRESHOLD = 0.9
        self.MAX_LOW_SPEED_DURATION = 5000

        self.current_fitness = 0

        self.last_x_position = self.position.x
        self.x_position_start_time = None

        if self.show_display:
            self.initialize_display()

        self.pop_size = pop_size

        self.generation = 0

        self.MAX_GAME_TIME = 60 * 1000

        self.rotate_left = False
        self.rotate_right = False
        self.thrust = False

    def initialize_display(self):
        if self.screen is None:
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
            pygame.display.set_caption("Moon Lander")
            self.clock = pygame.time.Clock()
            
            if self.minimize_window:
                pygame.display.iconify()

    def generate_platform_position(self):
        return pygame.Rect(self.PLATFORM_X, self.PLATFORM_Y, self.PLATFORM_WIDTH, self.PLATFORM_HEIGHT)

    def generate_rocket_position(self):
        platform_center_x = self.PLATFORM_X + self.PLATFORM_WIDTH / 2
        min_distance = self.WIDTH / 4

        while True:
            x = random.randint(0, self.WIDTH)
            if abs(x - platform_center_x) >= min_distance:
                break

        y = self.ROCKET_START_Y
        return pygame.math.Vector2(x, y)

    def reset(self):
        self.platform_rect = self.generate_platform_position()
        self.position = self.generate_rocket_position()
        self.velocity = pygame.math.Vector2(0, 0)
        self.angle = 0
        self.game_over = False
        self.landed = False
        self.current_time = 0
        self.running = True
        self.score = 0
        self.thrust = False
        self.rocket_rect.center = self.position
        self.previous_distance = None
        self.current_fitness = 0
        self.previous_distance_x = None
        self.previous_distance_y = None
        return self.get_state()

    def get_state(self):
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

    def step(self):
        if self.show_display:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.game_over = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.rotate_left = True
                    elif event.key == pygame.K_RIGHT:
                        self.rotate_right = True
                    elif event.key == pygame.K_UP:
                        self.thrust = True
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.rotate_left = False
                    elif event.key == pygame.K_RIGHT:
                        self.rotate_right = False
                    elif event.key == pygame.K_UP:
                        self.thrust = False

        if not self.game_over:
            if self.rotate_left:
                self.angle += self.ROTATION_SPEED
            if self.rotate_right:
                self.angle -= self.ROTATION_SPEED

            if self.angle > 180:
                self.angle -= 360
            elif self.angle < -180:
                self.angle += 360

            if self.thrust:
                thrust_vector = pygame.math.Vector2(0, -self.THRUST).rotate(-self.angle)
                self.velocity += thrust_vector

            self.velocity.y += self.GRAVITY

            if self.velocity.length() > self.MAX_SPEED:
                self.velocity.scale_to_length(self.MAX_SPEED)

            self.position += self.velocity

            self.position.x = max(0, min(self.position.x, self.WIDTH))
            self.position.y = max(0, min(self.position.y, self.HEIGHT))

            current_speed = self.velocity.length()
            if 0 < current_speed < self.LOW_SPEED_THRESHOLD:
                if self.low_speed_start_time is None:
                    self.low_speed_start_time = self.current_time
                elif self.current_time - self.low_speed_start_time > self.MAX_LOW_SPEED_DURATION:
                    self.landed = False
                    self.game_over = True
                    reward = -100
            else:
                self.low_speed_start_time = None

            if self.position.x == self.last_x_position:
                if self.x_position_start_time is None:
                    self.x_position_start_time = self.current_time
                elif self.current_time - self.x_position_start_time > self.MAX_LOW_SPEED_DURATION:
                    self.landed = False
                    self.game_over = True
                    reward = -100
            else:
                self.x_position_start_time = None

            self.last_x_position = self.position.x

            self.position.x = max(0, self.position.x)
            self.position.y = max(0, self.position.y)
            reward = 1

            self.rocket_rect.center = self.position
            rotated_rocket = pygame.transform.rotate(self.rocket_img, self.angle)
            rotated_rect = rotated_rocket.get_rect(center=self.rocket_rect.center)

            rotated_flames = pygame.transform.rotate(self.flames_img, self.angle)
            flames_offset = pygame.math.Vector2(0, rotated_rect.height * 0.75).rotate(-self.angle)
            flames_pos = rotated_rect.center + flames_offset

            platform_center_x = self.platform_rect.centerx
            platform_center_y = self.platform_rect.centery
            current_distance_x = abs(self.position.x - platform_center_x)
            current_distance_y = abs(self.position.y - platform_center_y)

            if self.previous_distance_x is not None and self.previous_distance_y is not None:
                delta_distance_x = self.previous_distance_x - current_distance_x
                delta_distance_y = self.previous_distance_y - current_distance_y
                
                reward = delta_distance_x * 2 + delta_distance_y * 1
                
                if abs(delta_distance_x) < 0.1 and abs(delta_distance_y) > 0.1:
                    reward -= 1
            else:
                reward = 0

            self.previous_distance_x = current_distance_x
            self.previous_distance_y = current_distance_y

            upright_reward = math.cos(math.radians(self.angle)) * 0.2
            reward += upright_reward

            distance_penalty = -(current_distance_x + current_distance_y) * 0.01
            reward += distance_penalty

            if rotated_rect.colliderect(self.platform_rect):
                if abs(self.angle) < self.MAX_LANDING_ANGLE and self.velocity.length() < self.MAX_LANDING_SPEED:
                    self.landed = True
                    self.score += 1
                    reward += 1000
                    if self.show_display:
                        self.beep_sound.play()
                    self.reset()
                else:
                    self.landed = False
                    self.game_over = True
                    reward = -1000
                    reward += 200
            elif self.position.y + rotated_rect.height / 2 >= self.HEIGHT:
                self.landed = False
                self.game_over = True
                reward = -1000

            if self.current_time > self.MAX_GAME_TIME:
                self.game_over = True
                reward = -50

        if self.show_display:
            self.draw()

        if self.show_display:
            self.clock.tick(self.CLOCK_SPEED)
            self.current_time += self.clock.get_time() * self.TIME_SCALE
        else:
            self.current_time += (1000 / self.CLOCK_SPEED) * self.TIME_SCALE

        state = self.get_state()

        self.current_fitness += reward

        self.update_fitness_display(self.game_number, self.current_fitness)

        return self.game_over

    def draw(self):
        if not self.show_display:
            return
        self.screen.fill((20, 20, 40))

        pygame.draw.rect(self.screen, (200, 200, 200), self.platform_rect)

        if self.thrust:
            rotated_flames = pygame.transform.rotate(self.flames_img, self.angle)
            flames_offset = pygame.math.Vector2(0, self.rocket_rect.height * 0.75).rotate(-self.angle)
            flames_pos = self.rocket_rect.center + flames_offset
            flames_rect = rotated_flames.get_rect(center=flames_pos)
            self.screen.blit(rotated_flames, flames_rect)

        rotated_rocket = pygame.transform.rotate(self.rocket_img, self.angle)
        rotated_rect = rotated_rocket.get_rect(center=self.rocket_rect.center)
        self.screen.blit(rotated_rocket, rotated_rect)

        speed = self.velocity.length()
        velocity_text = f"Speed: {speed:.2f}"
        speed_surface = self.font.render(velocity_text, True, (255, 255, 255))
        self.screen.blit(speed_surface, (10, 10))

        time_text = f"Time: {self.current_time / 1000:.2f}"
        time_surface = self.font.render(time_text, True, (255, 255, 255))
        self.screen.blit(time_surface, (10, 50))

        fitness_text = f"Current Fitness: {self.current_fitness:.2f}"
        fitness_surface = self.font.render(fitness_text, True, (255, 255, 255))
        self.screen.blit(fitness_surface, (10, 90))

        generation_text = f"Gen {self.generation-1}, Member #: {self.population_number}"
        generation_surface = self.font.render(generation_text, True, (255, 255, 255))
        self.screen.blit(generation_surface, (10, 130))

        if self.fitness_surface and self.show_graph:
            self.screen.blit(self.fitness_surface, (self.WIDTH - 220, 20))

        pygame.display.flip()

    def update_fitness_display(self, game_number, fitness):
        if self.show_display and self.show_graph:
            self.fitness_surface = self.fitness_display.update(game_number, fitness)
        
        if self.pop_size > 0:
            self.population_number = game_number % self.pop_size
        else:
            self.population_number = game_number

    def update_generation(self, generation):
        self.generation = generation + 1

    def close(self):
        if self.show_display:
            self.fitness_display.close()
            if self.screen is not None:
                pygame.quit()
                self.screen = None
                self.clock = None
        else:
            pygame.quit()

    def run(self):
        self.reset()
        while self.running:
            self.step()
        self.close()

if __name__ == "__main__":
    game = MoonLanderGame(show_individual_fitness=False, show_display=True, pop_size=0, minimize_window=False, show_graph=True)
    game.run()