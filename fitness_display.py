import pygame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from collections import deque
import numpy as np

class FitnessDisplay:
    def __init__(self, width, height, max_points=1000):
        self.width = width
        self.height = height
        self.max_points = max_points
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
        self.ax.plot(list(self.game_numbers), list(self.fitnesses), label='Individual Fitness', alpha=0.5)
        self.ax.plot(list(self.game_numbers), list(self.avg_fitnesses), label='Average Fitness', color='r')
        self.ax.set_xlabel('Game Number', fontsize=8)
        self.ax.set_ylabel('Fitness', fontsize=8)
        self.ax.set_title('Fitness per Game', fontsize=10)
        self.ax.legend(fontsize=6)

        self.canvas.draw()
        renderer = self.canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        size = self.canvas.get_width_height()
        return pygame.image.fromstring(raw_data, size, "RGB")

    def close(self):
        plt.close(self.fig)