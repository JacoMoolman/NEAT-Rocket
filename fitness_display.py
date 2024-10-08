# fitness_display.py

import pygame

class FitnessDisplay:
    def __init__(self, width, height, max_points=10000, show_individual=True):
        self.width = width
        self.height = height
        self.max_points = max_points
        self.show_individual = show_individual

        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill((255, 255, 255))

        pygame.font.init()
        self.font = pygame.font.Font(None, 20)

        self.fitnesses = []
        self.avg_fitnesses = []

    def update(self, game_number, fitness):
        self.fitnesses.append(fitness)

        if len(self.fitnesses) > self.max_points:
            self.fitnesses.pop(0)

        avg_fitness = sum(self.fitnesses) / len(self.fitnesses)
        self.avg_fitnesses.append(avg_fitness)

        if len(self.avg_fitnesses) > self.max_points:
            self.avg_fitnesses.pop(0)

        self.draw_graph(fitness, avg_fitness)

        return self.surface

    def draw_graph(self, fitness, avg_fitness):
        self.surface.fill((255, 255, 255))

        max_fitness = max(self.fitnesses) if self.fitnesses else 1
        min_fitness = min(self.fitnesses) if self.fitnesses else 0
        if max_fitness == min_fitness:
            max_fitness += 1
        fitness_range = max_fitness - min_fitness

        x_scale = (self.width - 60) / (len(self.fitnesses) - 1 if len(self.fitnesses) > 1 else 1)
        y_scale = (self.height - 60) / fitness_range

        pygame.draw.line(self.surface, (0, 0, 0), (40, 20), (40, self.height - 40))
        pygame.draw.line(self.surface, (0, 0, 0), (40, self.height - 40), (self.width - 20, self.height - 40))

        for i in range(0, len(self.fitnesses), max(1, len(self.fitnesses) // 5)):
            x = 40 + i * x_scale
            label = str(i)
            text_surface = self.font.render(label, True, (0, 0, 0))
            self.surface.blit(text_surface, (x - text_surface.get_width() // 2, self.height - 35))

        for i in range(5):
            y = self.height - 40 - i * (self.height - 60) / 4
            label = f"{min_fitness + i * fitness_range / 4:.1f}"
            text_surface = self.font.render(label, True, (0, 0, 0))
            self.surface.blit(text_surface, (5, y - text_surface.get_height() // 2))

        if self.show_individual and len(self.fitnesses) > 1:
            points = [(40 + i * x_scale, self.height - 40 - (f - min_fitness) * y_scale) for i, f in enumerate(self.fitnesses)]
            pygame.draw.lines(self.surface, (0, 0, 255), False, points, 1)

        if len(self.avg_fitnesses) > 1:
            avg_points = [(40 + i * x_scale, self.height - 40 - (f - min_fitness) * y_scale) for i, f in enumerate(self.avg_fitnesses)]
            pygame.draw.lines(self.surface, (255, 0, 0), False, avg_points, 2)

        fitness_text = self.font.render(f"Fitness: {fitness:.2f}", True, (0, 0, 0))
        self.surface.blit(fitness_text, (40, 0))

        avg_fitness_text = self.font.render(f"Avg Fitness: {avg_fitness:.2f}", True, (0, 0, 0))
        self.surface.blit(avg_fitness_text, (40, 20))

    def close(self):
        pass  # No resources to close
