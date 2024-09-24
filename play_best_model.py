import neat
import pickle
import pygame
from MoonLanderGame import MoonLanderGame

def play_best_genome(genome_path, config_path):
    # Load configuration
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    # Load the best genome
    with open(genome_path, 'rb') as f:
        genome = pickle.load(f)

    # Create the neural network from the genome
    net = neat.nn.FeedForwardNetwork.create(genome, config)

    # Create a game instance
    game = MoonLanderGame(show_individual_fitness=False)

    # Play the game
    state = game.reset()
    done = False

    while not done and game.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        # Get action from the neural network
        output = net.activate(state)

        # Convert network output to actions
        rotate_left = output[0] > 0.0
        rotate_right = output[1] > 0.0
        thrust = output[2] > 0.0

        action = (rotate_left, rotate_right, thrust)

        # Take a step in the game
        state, reward, done, _ = game.step(action)

    # Close the game
    game.close()

if __name__ == '__main__':
    genome_path = 'best_genome.pkl'
    config_path = 'config-feedforward.txt'
    play_best_genome(genome_path, config_path)