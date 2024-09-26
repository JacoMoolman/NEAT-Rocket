# main.py

import neat
import os
import pickle
import glob
from multiprocessing import Process, Queue
from MoonLanderGame import MoonLanderGame

def evaluate_genomes_with_display(genomes_chunk, config, queue):
    # Initialize Pygame in this process
    game = MoonLanderGame(show_individual_fitness=False, show_display=True)
    for genome_id, genome in genomes_chunk:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        game.update_fitness_display(genome_id, 0)
        fitness = 0.0
        state = game.get_state()
        while not game.game_over:
            action = net.activate(state)
            rotate_left = action[0] > 0.5
            rotate_right = action[1] > 0.5
            thrust = action[2] > 0.5
            state, reward, done, _ = game.step((rotate_left, rotate_right, thrust))
            fitness += reward
        # Send fitness back to main process
        queue.put((genome_id, fitness))
        game.reset()  # Reset the game for the next genome
    game.close()

def evaluate_genomes_no_display(genomes_chunk, config, queue):
    for genome_id, genome in genomes_chunk:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        game = MoonLanderGame(show_individual_fitness=False, show_display=False)
        fitness = 0.0
        state = game.get_state()
        while not game.game_over:
            action = net.activate(state)
            rotate_left = action[0] > 0.5
            rotate_right = action[1] > 0.5
            thrust = action[2] > 0.5
            state, reward, done, _ = game.step((rotate_left, rotate_right, thrust))
            fitness += reward
        # Send fitness back to main process
        queue.put((genome_id, fitness))
        game.close()

def eval_genomes(genomes, config):
    N = 5  # Number of processes with display

    # Divide genomes into N chunks for display processes
    genomes_with_display = [[] for _ in range(N)]
    genomes_without_display = []
    for idx, (genome_id, genome) in enumerate(genomes):
        if idx % (N + 1) < N:
            genomes_with_display[idx % N].append((genome_id, genome))
        else:
            genomes_without_display.append((genome_id, genome))

    # Start N processes with display
    queues = []
    processes = []
    for i in range(N):
        queue = Queue()
        p = Process(target=evaluate_genomes_with_display, args=(genomes_with_display[i], config, queue))
        p.start()
        queues.append(queue)
        processes.append(p)

    # Evaluate the rest in parallel
    num_cores = 7  # Number of cores to use
    num_processes_no_display = num_cores - N
    queues_no_display = []
    processes_no_display = []
    if num_processes_no_display > 0 and len(genomes_without_display) > 0:
        # Split genomes_without_display into chunks
        from math import ceil
        chunk_size = ceil(len(genomes_without_display) / num_processes_no_display)
        for i in range(num_processes_no_display):
            chunk = genomes_without_display[i * chunk_size:(i + 1) * chunk_size]
            if chunk:
                queue = Queue()
                p = Process(target=evaluate_genomes_no_display, args=(chunk, config, queue))
                p.start()
                queues_no_display.append(queue)
                processes_no_display.append(p)

    # Collect results from display processes
    for queue in queues:
        while True:
            try:
                genome_id, fitness = queue.get(timeout=1)
                # Assign fitness to the genome
                for gid, genome in genomes:
                    if gid == genome_id:
                        genome.fitness = fitness
                        break
            except:
                break

    # Collect results from no-display processes
    for queue in queues_no_display:
        while True:
            try:
                genome_id, fitness = queue.get(timeout=1)
                # Assign fitness to the genome
                for gid, genome in genomes:
                    if gid == genome_id:
                        genome.fitness = fitness
                        break
            except:
                break

    # Wait for all processes to finish
    for p in processes:
        p.join()
    for p in processes_no_display:
        p.join()

def run(config_file):
    # Load the config file
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_file,
    )

    # Find the latest checkpoint
    checkpoint_prefix = 'neat-checkpoint-'
    checkpoints = glob.glob(f'{checkpoint_prefix}*')
    if checkpoints:
        # Extract the generation numbers
        checkpoint_numbers = [int(ckpt.split('-')[-1]) for ckpt in checkpoints]
        latest_checkpoint_number = max(checkpoint_numbers)
        latest_checkpoint = f'{checkpoint_prefix}{latest_checkpoint_number}'
        print(f'Loading checkpoint {latest_checkpoint}')
        p = neat.Checkpointer.restore_checkpoint(latest_checkpoint)
    else:
        p = neat.Population(config)

    # Add reporters
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # Save checkpoints every 10 generations
    p.add_reporter(neat.Checkpointer(10))

    # Run for up to 300 generations
    winner = p.run(eval_genomes, 300)

    # Save the winner
    with open('winner.pkl', 'wb') as f:
        pickle.dump(winner, f)

if __name__ == '__main__':
    # Determine path to configuration file.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
