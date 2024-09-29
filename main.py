# main.py

import neat
import os
import pickle
import glob
from multiprocessing import Process, Queue, cpu_count
from MoonLanderGame import MoonLanderGame
import time

SHOW_GRAPH = False
current_generation = 0  # Initialize the current generation variable

def evaluate_genomes_with_display(genomes_chunk, config, queue, generation):
    # Initialize Pygame in this process
    game = MoonLanderGame(show_individual_fitness=True, show_display=True, pop_size=config.pop_size, minimize_window=True, show_graph=SHOW_GRAPH)
    game.update_generation(generation)
    game.generation = generation  # Set the generation number
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
            game.update_fitness_display(genome_id, fitness)  # Update fitness display in each step
        # Send fitness back to main process
        queue.put((genome_id, fitness))
        game.reset()  # Reset the game for the next genome
    game.close()
    queue.put('DONE')  # Signal that this process is done

def evaluate_genomes_no_display(genomes_chunk, config, queue, generation):
    for genome_id, genome in genomes_chunk:
        game = MoonLanderGame(show_individual_fitness=False, show_display=False, pop_size=config.pop_size)
        game.update_generation(generation)  # This line is correct
        game.generation = generation  # Set the generation number
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
    global current_generation
    current_generation += 1

    N = min(7, len(genomes))  
    num_cores = min(7, len(genomes))  
    total_processes = num_cores

    # Divide genomes into chunks
    genomes_per_process = max(1, len(genomes) // total_processes)
    chunks = [genomes[i:i + genomes_per_process] for i in range(0, len(genomes), genomes_per_process)]

    processes = []
    queues = []

    # Start processes with display
    for i in range(N):
        queue = Queue()
        p = Process(target=evaluate_genomes_with_display, args=(chunks[i], config, queue, current_generation))
        p.start()
        queues.append(queue)
        processes.append(p)

    # Start processes without display
    for i in range(N, len(chunks)):
        queue = Queue()
        p = Process(target=evaluate_genomes_no_display, args=(chunks[i], config, queue, current_generation))
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

# Move the BestGenomeSaver class outside the run function
# Custom reporter to save the best genome
class BestGenomeSaver(neat.reporting.BaseReporter):
    def post_evaluate(self, config, population, species, best_genome):
        with open('best_genome.pkl', 'wb') as f:
            pickle.dump(best_genome, f)
        print(f"Best genome saved with fitness: {best_genome.fitness}")

def run(config_file):
    global current_generation
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
        current_generation = latest_checkpoint_number
    else:
        p = neat.Population(config)
        current_generation = 0

    # Add reporters
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    
    # Save checkpoints every 5 generations
    p.add_reporter(neat.Checkpointer(5, filename_prefix=checkpoint_prefix))

    # Add the BestGenomeSaver reporter
    p.add_reporter(BestGenomeSaver())

    winner = p.run(eval_genomes, 3000)

    # Save the winner
    with open('winner.pkl', 'wb') as f:
        pickle.dump(winner, f)
    print(f"Winner genome saved with fitness: {winner.fitness}")

if __name__ == '__main__':
    # Determine path to configuration file.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
