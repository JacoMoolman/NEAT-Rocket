# main.py

import neat
import os
import pickle
import multiprocessing
from MoonLanderGame import MoonLanderGame

# Set the number of generations
NUM_GENERATIONS = 50

def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        # Create a neural network for the genome
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        # Create a game instance
        game = MoonLanderGame()

        # Initialize fitness
        fitness = 0

        # Reset the game to get the initial state
        state = game.reset()
        done = False

        while not done:
            # Get action from the neural network
            output = net.activate(state)

            # Convert network output to actions
            rotate_left = output[0] > 0.5
            rotate_right = output[1] > 0.5
            thrust = output[2] > 0.5

            action = (rotate_left, rotate_right, thrust)

            # Take a step in the game
            state, reward, done, _ = game.step(action)

            # Update fitness
            fitness += reward

            # Optionally, break if the game runs too long
            if game.current_time > 20000:  # 20 seconds max per game
                break

        # Assign fitness to the genome
        genome.fitness = fitness

        # Close the game
        game.close()

def run_neat():
    # Load the config file
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    # Create the population
    p = neat.Population(config)

    # Add reporters for fancy stats
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run NEAT
    winner = p.run(eval_genomes, NUM_GENERATIONS)

    # Save the winner
    with open('best_genome.pkl', 'wb') as f:
        pickle.dump(winner, f)

    # Visualize the winner
    visualize_winner(winner, config)

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

if __name__ == '__main__':
    run_neat()
