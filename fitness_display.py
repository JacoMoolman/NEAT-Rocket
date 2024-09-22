import pygame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np

class FitnessDisplay:
    def __init__(self, width, height, max_points=1000, show_individual=True):
        self.width = width
        self.height = height
        self.max_points = max_points
        self.show_individual = show_individual
        self.game_numbers = []
        self.fitnesses = []
        self.avg_fitnesses = []
        self.fig, self.ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
        self.canvas = FigureCanvasAgg(self.fig)

        plt.rcParams.update({'font.size': 8})
        self.ax.tick_params(axis='both', which='major', labelsize=6)

    def update(self, game_number, fitness):
        self.game_numbers.append(game_number)
        self.fitnesses.append(fitness)
        self.avg_fitnesses.append(np.mean(self.fitnesses))

        self.ax.clear()
        if self.show_individual:
            self.ax.plot(self.game_numbers, self.fitnesses, label='Individual Fitness', alpha=0.5)
        self.ax.plot(self.game_numbers, self.avg_fitnesses, label='Average Fitness', color='r')
        
        self.ax.set_xlabel('Game Number', fontsize=8)
        self.ax.set_ylabel('Fitness', fontsize=8)
        self.ax.set_title('Fitness per Game', fontsize=10)
        self.ax.legend(fontsize=6)

        # Set x-axis limits for scrolling effect
        if len(self.game_numbers) > self.max_points:
            self.ax.set_xlim(self.game_numbers[-self.max_points], self.game_numbers[-1])
        else:
            self.ax.set_xlim(0, max(self.max_points, self.game_numbers[-1]))

        # Adjust y-axis limits
        all_fitnesses = self.fitnesses + self.avg_fitnesses
        min_fitness = min(all_fitnesses)
        max_fitness = max(all_fitnesses)
        y_range = max_fitness - min_fitness
        self.ax.set_ylim(min_fitness - 0.1 * y_range, max_fitness + 0.1 * y_range)

        self.canvas.draw()
        renderer = self.canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        size = self.canvas.get_width_height()
        return pygame.image.fromstring(raw_data, size, "RGB")

    def close(self):
        plt.close(self.fig)