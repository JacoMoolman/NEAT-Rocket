import pygame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from collections import deque
import numpy as np

class FitnessDisplay:
    def __init__(self, width, height, max_points=1000, show_individual=True):
        self.width = width
        self.height = height
        self.max_points = max_points
        self.show_individual = show_individual
        self.game_numbers = deque(maxlen=max_points)
        self.fitnesses = deque(maxlen=max_points)
        self.avg_fitnesses = deque(maxlen=max_points)
        self.fig, self.ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
        self.canvas = FigureCanvasAgg(self.fig)

        plt.rcParams.update({'font.size': 8})
        self.ax.tick_params(axis='both', which='major', labelsize=6)

    def update(self, game_number, fitness):
        self.game_numbers.append(game_number)
        self.fitnesses.append(fitness)
        
        # Calculate the average fitness up to this point
        self.avg_fitnesses.append(np.mean(self.fitnesses))

        self.ax.clear()
        if self.show_individual:
            self.ax.plot(self.game_numbers, self.fitnesses, label='Individual Fitness', alpha=0.5)
        self.ax.plot(self.game_numbers, self.avg_fitnesses, label='Average Fitness', color='r')
        self.ax.set_xlabel('Game Number', fontsize=8)
        self.ax.set_ylabel('Fitness', fontsize=8)
        self.ax.set_title('Fitness per Game', fontsize=10)
        self.ax.legend(fontsize=6)

        # Set x-axis limits to show only the last max_points
        if len(self.game_numbers) > 1:
            self.ax.set_xlim(self.game_numbers[0], self.game_numbers[-1])

        # Adjust y-axis limits dynamically
        min_fitness = min(min(self.fitnesses), min(self.avg_fitnesses))
        max_fitness = max(max(self.fitnesses), max(self.avg_fitnesses))
        y_range = max_fitness - min_fitness
        if y_range == 0:
            y_range = 1  # Prevent division by zero
        self.ax.set_ylim(min_fitness - 0.1 * y_range, max_fitness + 0.1 * y_range)

        self.canvas.draw()
        renderer = self.canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        size = self.canvas.get_width_height()
        return pygame.image.fromstring(raw_data, size, "RGB")

    def close(self):
        plt.close(self.fig)
