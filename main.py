# main.py

import neat
import os
import tempfile
import multiprocessing
from MoonLanderGame import MoonLanderGame

def eval_genomes(genomes, config):
    # Use multiprocessing to evaluate genomes in parallel
    jobs = []
    for genome_id, genome in genomes:
        jobs.append((genome, config))

    with multiprocessing.Pool() as pool:
        results = pool.map(run_simulation, jobs)

    # Assign fitness to genomes
    for (genome_id, genome), fitness in zip(genomes, results):
        genome.fitness = fitness

def run_simulation(args):
    genome, config = args
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    game = MoonLanderGame(render=False)
    fitness = 0
    done = False
    state = game.reset()
    while not done:
        # Get action from neural network
        output = net.activate(state)
        # Convert output to actions
        rotate_direction = 0
        if output[0] < -0.33:
            rotate_direction = -1  # Rotate left
        elif output[0] > 0.33:
            rotate_direction = 1   # Rotate right
        else:
            rotate_direction = 0   # No rotation

        thrust = 1 if output[1] > 0.5 else 0  # Thrust if output > 0.5
        action = (rotate_direction, thrust)
        # Take a step in the game
        state, reward, done, _ = game.step(action)
        fitness += reward
        # Optional: Add a maximum number of steps to prevent infinite loops
        if game.current_time > 1000:
            break
    game.close()
    return fitness

def run_neat(config_file):
    # Load configuration
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)
    # Create the population
    p = neat.Population(config)
    # Add a stdout reporter to show progress in the terminal
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # Run NEAT
    winner = p.run(eval_genomes, 50)  # Run for 50 generations
    # Save the winner
    with open('best_genome.pkl', 'wb') as f:
        import pickle
        pickle.dump(winner, f)
    # Visualize the best genome
    visualize_winner(winner, config)

def visualize_winner(winner, config):
    # Create the neural network
    net = neat.nn.FeedForwardNetwork.create(winner, config)
    # Create the game with rendering enabled
    game = MoonLanderGame(render=True)
    state = game.reset()
    done = False
    while not done:
        # Get action from neural network
        output = net.activate(state)
        # Convert output to actions
        rotate_direction = 0
        if output[0] < -0.33:
            rotate_direction = -1  # Rotate left
        elif output[0] > 0.33:
            rotate_direction = 1   # Rotate right
        else:
            rotate_direction = 0   # No rotation

        thrust = 1 if output[1] > 0.5 else 0  # Thrust if output > 0.5
        action = (rotate_direction, thrust)
        # Take a step in the game
        state, reward, done, _ = game.step(action)
    game.close()

if __name__ == '__main__':
    # Generate NEAT config and save as a temp file
    config_data = """
[NEAT]
fitness_criterion     = max
fitness_threshold     = 1000
pop_size              = 50
reset_on_extinction   = False

[DefaultGenome]
# node activation options
activation_default      = relu
activation_mutate_rate  = 0.0
activation_options      = relu

# node aggregation options
aggregation_default     = sum
aggregation_mutate_rate = 0.0
aggregation_options     = sum

# bias options
bias_init_mean          = 0.0
bias_init_stdev         = 1.0
bias_max_value          = 30.0
bias_min_value          = -30.0
bias_mutate_power       = 0.5
bias_mutate_rate        = 0.7
bias_replace_rate       = 0.1

# genome compatibility options
compatibility_disjoint_coefficient = 1.0
compatibility_weight_coefficient   = 0.5

# connection add/remove rates
conn_add_prob           = 0.5
conn_delete_prob        = 0.5

# connection options
enabled_default         = True
enabled_mutate_rate     = 0.01

# feed forward?
feed_forward            = True

# initial connection
initial_connection      = full_direct

# node add/remove rates
node_add_prob           = 0.2
node_delete_prob        = 0.2

# network parameters
num_hidden              = 0
num_inputs              = 7
num_outputs             = 2

# response options
response_init_mean          = 1.0
response_init_stdev         = 0.0
response_max_value          = 30.0
response_min_value          = -30.0
response_mutate_power       = 0.0
response_mutate_rate        = 0.0
response_replace_rate       = 0.0

# weight options
weight_init_mean        = 0.0
weight_init_stdev       = 1.0
weight_max_value        = 30
weight_min_value        = -30
weight_mutate_power     = 0.5
weight_mutate_rate      = 0.8
weight_replace_rate     = 0.1

[DefaultSpeciesSet]
compatibility_threshold = 3.0

[DefaultStagnation]
species_fitness_func    = max
max_stagnation          = 20
species_elitism         = 2

[DefaultReproduction]
elitism                 = 2
survival_threshold      = 0.2
    """
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write(config_data)
        config_path = f.name

    run_neat(config_path)

    # Remove the temporary config file
    os.remove(config_path)
