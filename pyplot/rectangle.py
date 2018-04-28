import matplotlib.pyplot as plt
import matplotlib.patches as patches

# create a figure and a set of subplots
fig, ax = plt.subplots(1)
fig.set_size_inches(20, 10)

ax.add_patch(patches.Rectangle((0.1, 0.1), 0.5, 0.5, linewidth=1,edgecolor='r',facecolor='none'))

fig.savefig('rectangle.pdf')
