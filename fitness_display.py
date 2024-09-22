import pygame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg

class FitnessDisplay:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.generations = []
        self.best_fitnesses = []
        self.avg_fitnesses = []
        self.fig, self.ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
        self.canvas = FigureCanvasAgg(self.fig)

        # Set smaller font sizes
        plt.rcParams.update({'font.size': 8})  # Default font size
        self.ax.tick_params(axis='both', which='major', labelsize=6)  # Tick label font size

    def update(self, generation, best_fitness, avg_fitness):
        self.generations.append(generation)
        self.best_fitnesses.append(best_fitness)
        self.avg_fitnesses.append(avg_fitness)

        self.ax.clear()
        self.ax.plot(self.generations, self.best_fitnesses, label='Best Fitness')
        self.ax.plot(self.generations, self.avg_fitnesses, label='Average Fitness')
        self.ax.set_xlabel('Generation', fontsize=8)
        self.ax.set_ylabel('Fitness', fontsize=8)
        self.ax.set_title('Fitness over Generations', fontsize=10)
        self.ax.legend(fontsize=6)

        self.canvas.draw()
        renderer = self.canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        size = self.canvas.get_width_height()
        return pygame.image.fromstring(raw_data, size, "RGB")

    def close(self):
        plt.close(self.fig)