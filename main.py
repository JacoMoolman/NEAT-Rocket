# main.py

import neat
import os
import pickle
import pygame
from MoonLanderGame import MoonLanderGame

# Set the number of generations
NUM_GENERATIONS = 50000
MAX_STEPS = 10000
SAVEGENOMEINTERVAL=1

def run_neat(config_file):
    print("Starting run_neat function")
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)
    print("NEAT config loaded")

    # Check if a checkpoint exists and restore from it
    checkpoint_prefix = 'neat-checkpoint-'
    checkpoint_files = [f for f in os.listdir('.') if f.startswith(checkpoint_prefix)]
    if checkpoint_files:
        # Get the latest checkpoint file
        latest_checkpoint = max(checkpoint_files, key=os.path.getctime)
        print(f"Restoring from checkpoint {latest_checkpoint}")
        p = neat.Checkpointer.restore_checkpoint(latest_checkpoint)
    else:
        p = neat.Population(config)
        print("Population created")

    game = MoonLanderGame(show_individual_fitness=True)
    print("Game instance created")

    best_fitnesses = []
    avg_fitnesses = []

    # Add reporters to track progress
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Add the Checkpointer to save checkpoints every N generations
    # Adjust generation_interval as needed
    p.add_reporter(neat.Checkpointer(generation_interval=SAVEGENOMEINTERVAL, filename_prefix='neat-checkpoint-'))

    fitness_threshold = config.fitness_threshold  # Get the fitness threshold from the config

    # Flag to indicate if the fitness threshold is reached
    fitness_threshold_reached = False

    def eval_genomes(genomes, config):
        nonlocal fitness_threshold_reached  # Declare as nonlocal to modify the outer scope variable
        fitnesses = []  # Reset fitnesses list for each generation
        for genome_id, genome in genomes:
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            fitness = evaluate_genome(net, game)
            genome.fitness = fitness
            fitnesses.append(fitness)
            game.update_fitness_display(len(fitnesses), fitness)

            # Save the genome if it meets or exceeds the fitness threshold
            if fitness >= fitness_threshold:
                with open('best_genome.pkl', 'wb') as f:
                    pickle.dump(genome, f)
                # Set the flag to True
                fitness_threshold_reached = True

        best_fitness = max(fitnesses)
        avg_fitness = sum(fitnesses) / len(fitnesses)
        best_fitnesses.append(best_fitness)
        avg_fitnesses.append(avg_fitness)

    # Run NEAT's evolution process
    winner = p.run(eval_genomes, NUM_GENERATIONS)

    # Check if fitness threshold was reached
    if fitness_threshold_reached:
        print("Fitness threshold reached, evolution stopped.")

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
        rotate_left = output[0] > 0.0
        rotate_right = output[1] > 0.0
        thrust = output[2] > 0.0

        action = (rotate_left, rotate_right, thrust)

        # Take a step in the game
        state, reward, done, _ = game.step(action)

    game.close()

def evaluate_genome(net, game):
    state = game.reset()
    done = False
    steps = 0
    max_steps = MAX_STEPS  # Limit the number of steps per genome

    while not done and steps < max_steps:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 0

        output = net.activate(state)
        rotate_left = output[0] > 0.0
        rotate_right = output[1] > 0.0
        thrust = output[2] > 0.0
        action = (rotate_left, rotate_right, thrust)

        state, reward, done, _ = game.step(action)
        steps += 1

    return game.current_fitness  # Return the current fitness from the game

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run_neat(config_path)
