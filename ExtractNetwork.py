import neat
import pickle
import networkx as nx
import matplotlib.pyplot as plt

# Load the winner genome from the pickle file
with open('winner copy.pkl', 'rb') as f:
    winner = pickle.load(f)

# Load the NEAT configuration file
config_path = 'config-feedforward.txt'
config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                            neat.DefaultSpeciesSet, neat.DefaultStagnation,
                            config_path)

# Define descriptive labels for input nodes
input_labels = {
    -1: "Rocket X Position",
    -2: "Rocket Y Position",
    -3: "Rocket Angle",
    -4: "Rocket Velocity X",
    -5: "Rocket Velocity Y",
    -6: "Distance to Target",
    -7: "X Distance to Target",
    -8: "Y Distance to Target",
    -9: "Angle to Target",
    -10: "Angular Velocity",
    -11: "Relative Velocity X",
    -12: "Relative Velocity Y",
    -13: "Distance to Vertical Edge",
    -14: "Distance to Horizontal Edge",
    -15: "Angle Between Rocket and Velocity",
}

# Define descriptive labels for output nodes
output_labels = {
    0: "Right Rotation",
    1: "Left Rotation",
    2: "Thrust",
}

# Create a directed graph to represent the neural network
graph = nx.DiGraph()

# Add nodes and classify them by type (input, hidden, output)
input_nodes = []
hidden_nodes = []
output_nodes = []

# Get input, output, and hidden nodes based on the config
for node_key in config.genome_config.input_keys:
    input_nodes.append(node_key)
    label = input_labels.get(node_key, f"Input {node_key}")
    graph.add_node(node_key, label=label, layer="input")

for node_key in config.genome_config.output_keys:
    output_nodes.append(node_key)
    label = output_labels.get(node_key, f"Output {node_key}")
    graph.add_node(node_key, label=label, layer="output")

for node_key, node in winner.nodes.items():
    if node_key not in input_nodes and node_key not in output_nodes:
        hidden_nodes.append(node_key)
        graph.add_node(node_key, label=f"Hidden {node_key}\nBias: {node.bias:.2f}", layer="hidden")

# Add connections to the graph
for conn_key, conn in winner.connections.items():
    if conn.enabled:
        graph.add_edge(conn_key[0], conn_key[1], weight=f"{conn.weight:.2f}")

# Assign positions to the nodes in a way that resembles a traditional neural network diagram
pos = {}

# Arrange input nodes on the left
for i, node in enumerate(input_nodes):
    pos[node] = (-1, i - len(input_nodes) / 2)

# Arrange output nodes on the right
for i, node in enumerate(output_nodes):
    pos[node] = (1, i - len(output_nodes) / 2)

# Arrange hidden nodes in the middle
for i, node in enumerate(hidden_nodes):
    pos[node] = (0, i - len(hidden_nodes) / 2)

# Draw the graph
plt.figure(figsize=(16, 10))

# Draw nodes with labels
nx.draw_networkx_nodes(graph, pos, node_color='lightblue', node_size=1500, alpha=0.9)
nx.draw_networkx_labels(graph, pos, labels=nx.get_node_attributes(graph, 'label'), font_size=8, font_weight='bold')

# Draw edges with weights
nx.draw_networkx_edges(graph, pos, edge_color='black', arrows=True)
edge_labels = nx.get_edge_attributes(graph, 'weight')
nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=8)

# Set plot title
plt.title("Neural Network Visualization-Winner")

# Display the graph
plt.axis('off')
plt.show()
