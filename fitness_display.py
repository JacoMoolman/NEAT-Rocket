# fitness_display.py

import pygame

class FitnessDisplay:
    def __init__(self, width, height, max_points=200, show_individual=True):
        self.width = width
        self.height = height
        self.max_points = max_points
        self.show_individual = show_individual

        # Initialize a Surface to draw on
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill((0, 0, 0))  # Fill with black

        # Initialize font
        pygame.font.init()
        self.font = pygame.font.Font(None, 20)

        # Initialize lists to store fitness data
        self.fitnesses = []
        self.avg_fitnesses = []

    def update(self, game_number, fitness):
        # Append the fitness to the list
        self.fitnesses.append(fitness)

        # Limit the size of the fitnesses list
        if len(self.fitnesses) > self.max_points:
            self.fitnesses.pop(0)

        # Calculate average fitness
        avg_fitness = sum(self.fitnesses) / len(self.fitnesses)
        self.avg_fitnesses.append(avg_fitness)

        # Limit the size of avg_fitnesses list
        if len(self.avg_fitnesses) > self.max_points:
            self.avg_fitnesses.pop(0)

        # Clear the surface
        self.surface.fill((0, 0, 0))

        # Compute scaling factors
        max_fitness = max(self.fitnesses) if self.fitnesses else 1
        min_fitness = min(self.fitnesses) if self.fitnesses else 0
        if max_fitness == min_fitness:
            max_fitness += 1  # Avoid division by zero
        fitness_range = max_fitness - min_fitness

        x_scale = (self.width - 40) / (len(self.fitnesses) - 1 if len(self.fitnesses) > 1 else 1)
        y_scale = (self.height - 40) / fitness_range

        # Draw axes
        pygame.draw.line(self.surface, (255, 255, 255), (20, 20), (20, self.height - 20))  # Y axis
        pygame.draw.line(self.surface, (255, 255, 255), (20, self.height - 20), (self.width - 20, self.height - 20))  # X axis

        # Draw individual fitnesses
        if self.show_individual and len(self.fitnesses) > 1:
            for i in range(1, len(self.fitnesses)):
                x1 = 20 + (i - 1) * x_scale
                y1 = self.height - 20 - (self.fitnesses[i - 1] - min_fitness) * y_scale
                x2 = 20 + i * x_scale
                y2 = self.height - 20 - (self.fitnesses[i] - min_fitness) * y_scale
                pygame.draw.line(self.surface, (0, 255, 0), (x1, y1), (x2, y2), 2)

        # Draw average fitness
        if len(self.avg_fitnesses) > 1:
            for i in range(1, len(self.avg_fitnesses)):
                x1 = 20 + (i - 1) * x_scale
                y1 = self.height - 20 - (self.avg_fitnesses[i - 1] - min_fitness) * y_scale
                x2 = 20 + i * x_scale
                y2 = self.height - 20 - (self.avg_fitnesses[i] - min_fitness) * y_scale
                pygame.draw.line(self.surface, (255, 0, 0), (x1, y1), (x2, y2), 2)

        # Draw current fitness
        fitness_text = self.font.render(f"Fitness: {fitness:.2f}", True, (255, 255, 255))
        self.surface.blit(fitness_text, (20, 0))

        # Draw average fitness
        avg_fitness_text = self.font.render(f"Avg Fitness: {avg_fitness:.2f}", True, (255, 255, 255))
        self.surface.blit(avg_fitness_text, (20, 20))

        return self.surface

    def close(self):
        pass  # No resources to close
