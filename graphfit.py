import matplotlib.pyplot as plt

# Step 1: Read data from the file
file_path = 'fitness_values.txt'
with open(file_path, 'r') as file:
    data = [float(line.strip().split(':')[1]) for line in file]

# Step 2: Plot the data without markers
plt.figure(figsize=(10, 6))
plt.plot(data, linestyle='-', linewidth=1, color='b', alpha=0.7, label='fit data')  # Remove markers, adjust line width and transparency
plt.title('Data from fit.txt')
plt.xlabel('Index')
plt.ylabel('Value (Log Scale)')
plt.yscale('log')  # Set the y-axis to a logarithmic scale
plt.grid(True)
plt.legend()

# Step 3: Show the plot
plt.show()
