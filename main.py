# main.py

import neat
import os
import pickle
import glob
from multiprocessing import Process, Queue, cpu_count
from MoonLanderGame import MoonLanderGame
import time

def evaluate_genomes_with_display(genomes_chunk, config, queue):
    # Initialize Pygame in this process
    game = MoonLanderGame(show_individual_fitness=False, show_display=True, pop_size=config.pop_size)
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
    queue.put('DONE')  # Signal that this process is done

def evaluate_genomes_no_display(genomes_chunk, config, queue):
    for genome_id, genome in genomes_chunk:
        game = MoonLanderGame(show_individual_fitness=False, show_display=False, pop_size=config.pop_size)
        net = neat.nn.FeedForwardNetwork.create(genome, config)  # Add this line
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
    queue.put('DONE')  # Signal that this process is done

def eval_genomes(genomes, config):
    N = 5  # Number of processes with display

    # Divide genomes into chunks
    num_cores = 7  # Number of cores to use
    total_processes = num_cores
    genomes_per_process = len(genomes) // total_processes
    chunks = [genomes[i * genomes_per_process:(i + 1) * genomes_per_process] for i in range(total_processes)]
    # Add any remaining genomes to the last chunk
    if len(genomes) % total_processes != 0:
        chunks[-1].extend(genomes[total_processes * genomes_per_process:])

    processes = []
    queues = []

    # Start processes with display
    for i in range(N):
        queue = Queue()
        p = Process(target=evaluate_genomes_with_display, args=(chunks[i], config, queue))
        p.start()
        queues.append(queue)
        processes.append(p)

    # Start processes without display
    for i in range(N, total_processes):
        queue = Queue()
        p = Process(target=evaluate_genomes_no_display, args=(chunks[i], config, queue))
        p.start()
        queues.append(queue)
        processes.append(p)

    # Collect results
    finished_processes = 0
    while finished_processes < total_processes:
        for queue in queues:
            while not queue.empty():
                result = queue.get()
                if result == 'DONE':
                    finished_processes += 1
                else:
                    genome_id, fitness = result
                    # Assign fitness to the genome
                    for gid, genome in genomes:
                        if gid == genome_id:
                            genome.fitness = fitness
                            break
        time.sleep(0.1)  # Avoid busy waiting

    # Wait for all processes to finish
    for p in processes:
        p.join()

    # Ensure all genomes have fitness assigned
    for genome_id, genome in genomes:
        if genome.fitness is None:
            genome.fitness = -1000  # Assign a default low fitness

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
