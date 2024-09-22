# main.py

import neat
import os
import pickle
import pygame
from MoonLanderGame import MoonLanderGame

# Set the number of generations
NUM_GENERATIONS = 5000

def run_neat(config_file):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    p = neat.Population(config)
    game = MoonLanderGame(show_individual_fitness=False)

    best_fitnesses = []
    avg_fitnesses = []
    fitnesses = []  # New list to store all fitnesses

    def eval_genomes(genomes, config):
        for genome_id, genome in genomes:
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            fitness = evaluate_genome(net, game)
            genome.fitness = fitness
            fitnesses.append(fitness)  # Add each fitness to the list
            game.update_fitness_display(len(fitnesses), fitness)  # Update display for each game

        best_fitness = max(fitnesses)
        avg_fitness = sum(fitnesses) / len(fitnesses)
        best_fitnesses.append(best_fitness)
        avg_fitnesses.append(avg_fitness)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(eval_genomes, NUM_GENERATIONS)

    # Save the winner
    with open('best_genome.pkl', 'wb') as f:
        pickle.dump(winner, f)

    # Visualize the winner
    visualize_winner(winner, config)

    # Close the game
    game.close()

def visualize_winner(winner, config):
    # Create a neural network from the winner
    net = neat.nn.FeedForwardNetwork.create(winner, config)

    # Create a game instance
    game = MoonLanderGame()

    # Reset the game
    state = game.reset()
    done = False

    while not done and game.running:
        # Get action from the neural network
        output = net.activate(state)

        # Convert network output to actions
        rotate_left = output[0] > 0.5
        rotate_right = output[1] > 0.5
        thrust = output[2] > 0.5

        action = (rotate_left, rotate_right, thrust)

        # Take a step in the game
        state, reward, done, _ = game.step(action)

    game.close()

def evaluate_genome(net, game):
    state = game.reset()
    done = False
    fitness = 0

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 0

        output = net.activate(state)
        rotate_left = output[0] > 0.5
        rotate_right = output[1] > 0.5
        thrust = output[2] > 0.5
        action = (rotate_left, rotate_right, thrust)

        state, reward, done, _ = game.step(action)
        fitness += reward

        if game.current_time > 60000:  # Equivalent to 60 seconds of real time
            break

    return fitness

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run_neat(config_path)
