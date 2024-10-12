import pickle
import neat
import GetMoonGame

# Load the NEAT config
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     'config-feedforward.txt')

# Create the population
p = neat.Population(config)

# Load the winner genome
with open('winner.pkl', 'rb') as f:
    winner = pickle.load(f)

# Create a neural network from the winner genome
winner_net = neat.nn.FeedForwardNetwork.create(winner, config)

# Create the game with display enabled
game = GetMoonGame.MoonLanderGame(net=winner_net)

# Run the game using the winner neural network
fitness = game.run_genome(winner)

print(f"Winner fitness: {fitness}")

# Close the game
game.close()
