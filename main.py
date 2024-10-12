import neat
import pickle
from GetMoonGame import MoonLanderGame
from functools import partial

def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        game = MoonLanderGame(net, genomes)  # Pass the genomes to the MoonLanderGame class
        genome.fitness = game.run_genome(genome)

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(eval_genomes, 500)

    with open('winner.pkl', 'wb') as f:
        pickle.dump(winner, f)

    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == '__main__':
    config_path = 'config-feedforward.txt'
    run(config_path)
