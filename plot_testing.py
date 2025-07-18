import matplotlib.pyplot as plt
import numpy as np

# === Configuration ===
inches = 8;
mm = inches * 25.4;
R=mm/2;

num_points = 250
base_radius = R
amplitude = 5
frequency = 50
randomness = 10

# === Generate polar coordinates ===
theta = np.linspace(0, 2 * np.pi, num_points)
r = base_radius + amplitude * np.sin(frequency * theta) + np.random.uniform(-randomness, randomness, size=num_points)

x = r * np.cos(theta)
y = r * np.sin(theta)

# === Plot ===
plt.figure(figsize=(6,6))
plt.plot(x, y, color='royalblue')

# Add grid to background
plt.grid(True,
         which='both',         # 'major', 'minor', or 'both'
         linestyle='--',       # Line style
         linewidth=0.5,
         color='gray',
         alpha=0.6)
plt.gca().set_axisbelow(True)  # Push grid behind the lines

# Formatting
plt.gca().set_aspect('equal')
plt.title("Wavy Circle with Grid")
plt.xlabel("X")
plt.ylabel("Y")
plt.show()
