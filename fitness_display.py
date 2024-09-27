# fitness_display.py

import pygame

class FitnessDisplay:
    def __init__(self, width, height, max_points=10000, show_individual=True):
        self.width = width
        self.height = height
        self.max_points = max_points
        self.show_individual = show_individual

        # Initialize a Surface to draw on
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill((255, 255, 255))  # Fill with white

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

        # Only draw the graph if show_individual is True
        if self.show_individual:
            self.draw_graph(fitness, avg_fitness)

        return self.surface

    def draw_graph(self, fitness, avg_fitness):
        # Clear the surface
        self.surface.fill((255, 255, 255))

        # Compute scaling factors
        max_fitness = max(self.fitnesses) if self.fitnesses else 1
        min_fitness = min(self.fitnesses) if self.fitnesses else 0
        if max_fitness == min_fitness:
            max_fitness += 1  # Avoid division by zero
        fitness_range = max_fitness - min_fitness

        x_scale = (self.width - 40) / (len(self.fitnesses) - 1 if len(self.fitnesses) > 1 else 1)
        y_scale = (self.height - 40) / fitness_range

        # Draw axes
        pygame.draw.line(self.surface, (0, 0, 0), (20, 20), (20, self.height - 20))  # Y axis
        pygame.draw.line(self.surface, (0, 0, 0), (20, self.height - 20), (self.width - 20, self.height - 20))  # X axis

        # Draw individual fitnesses
        if self.show_individual and len(self.fitnesses) > 1:
            points = [(20 + i * x_scale, self.height - 20 - (f - min_fitness) * y_scale) for i, f in enumerate(self.fitnesses)]
            pygame.draw.lines(self.surface, (0, 0, 255), False, points, 1)

        # Draw average fitness
        if len(self.avg_fitnesses) > 1:
            avg_points = [(20 + i * x_scale, self.height - 20 - (f - min_fitness) * y_scale) for i, f in enumerate(self.avg_fitnesses)]
            pygame.draw.lines(self.surface, (255, 0, 0), False, avg_points, 2)

        # Draw current fitness
        fitness_text = self.font.render(f"Fitness: {fitness:.2f}", True, (0, 0, 0))
        self.surface.blit(fitness_text, (20, 0))

        # Draw average fitness
        avg_fitness_text = self.font.render(f"Avg Fitness: {avg_fitness:.2f}", True, (0, 0, 0))
        self.surface.blit(avg_fitness_text, (20, 20))

        return self.surface

    def close(self):
        pass  # No resources to close
