import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pareto
from matplotlib.widgets import RadioButtons

class EpochPlotter:
    def __init__(self):
        self.distributions = {}
        self.fig, self.ax = plt.subplots()
        self.current_epoch = 0
        self.radio = None
        self.xlim = None
        self.ylim = None

    def add_distribution(self, epoch: int, distribution):
        self.distributions[epoch] = distribution

    def plot_epoch(self, epoch):
        self.current_epoch = epoch
        self.ax.clear()
        distribution = self.distributions[epoch]

        self.ax.hist(distribution, bins=20, density=True, alpha=0.7, edgecolor='black', label='Resource Distribution')

        shape, loc, scale = pareto.fit(distribution, floc=0)
        estimated_alpha = shape
        self.ax.set_title(f'Epoch {epoch} with Theoretical Pareto Distribution (alpha={estimated_alpha:.2f})', fontsize=10)

        x = np.linspace(min(distribution), max(distribution), 100)
        x_positive = x[x > 0]
        pareto_pdf = pareto.pdf(x_positive, b=estimated_alpha, loc=loc, scale=scale)
        self.ax.plot(x_positive, pareto_pdf, color='r', linestyle='--', label=f'Theoretical Pareto (alpha={estimated_alpha:.2f})')

        self.ax.set_xlabel('Resources')
        self.ax.set_ylabel('Probability Density')
        self.ax.grid(axis='y', alpha=0.75)
        self.ax.legend()
        if self.xlim:
            self.ax.set_xlim(self.xlim)
        if self.ylim:
            self.ax.set_ylim(self.ylim)
        plt.draw()

    def key_press(self, event):
        if event.key == 'right':
            epochs = sorted(self.distributions.keys())
            current_index = epochs.index(self.current_epoch)
            if current_index < len(epochs) - 1:
                self.plot_epoch(epochs[current_index + 1])
                if self.radio:
                    self.radio.set_active(current_index + 1)
        elif event.key == 'left':
            epochs = sorted(self.distributions.keys())
            current_index = epochs.index(self.current_epoch)
            if current_index > 0:
                self.plot_epoch(epochs[current_index - 1])
                if self.radio:
                    self.radio.set_active(current_index - 1)

    def show(self):
        epochs = sorted(self.distributions.keys())
        if not epochs:
            return

        # Determine global x and y ranges
        global_min_x, global_max_x = float('inf'), float('-inf')
        global_max_y = float('-inf')

        for dist in self.distributions.values():
            global_min_x = min(global_min_x, min(dist))
            global_max_x = max(global_max_x, max(dist))
            hist, _ = np.histogram(dist, bins=20, density=True)
            global_max_y = max(global_max_y, hist.max())

        # self.xlim = (global_min_x, global_max_x)
        # self.ylim = (0, global_max_y * 1.1)  # Add a little padding

        plt.subplots_adjust(left=0.3)
        radio_ax = plt.axes((0.05, 0.4, 0.15, 0.5), facecolor='lightgoldenrodyellow')
        epoch_labels = [f'Epoch {e}' for e in epochs]
        self.radio = RadioButtons(radio_ax, epoch_labels)

        def on_radio_clicked(label):
            epoch = int(label.split(' ')[1])
            self.plot_epoch(epoch)

        self.radio.on_clicked(on_radio_clicked)
        self.fig.canvas.mpl_connect('key_press_event', self.key_press)

        self.plot_epoch(epochs[0])
        plt.show()

def plot_resources_histogram(distribution, title: str = "Resource Distribution"):
    """Plot a histogram of the final resource distribution."""
    plt.figure()
    plt.hist(distribution, bins=20, density=True, alpha=0.7, edgecolor='black', label='Resource Distribution')
    plt.suptitle(title)

    shape, loc, scale = pareto.fit(distribution, floc=0)
    estimated_alpha = shape
    plt.title(f'with Theoretical Pareto Distribution (alpha={estimated_alpha:.2f})', fontsize=10)

    x = np.linspace(min(distribution), max(distribution), 100)
    x_positive = x[x > 0]
    pareto_pdf = pareto.pdf(x_positive, b=estimated_alpha, loc=loc, scale=scale)
    plt.plot(x_positive, pareto_pdf, color='r', linestyle='--', label=f'Theoretical Pareto (alpha={estimated_alpha:.2f})')

    plt.xlabel('Resources')
    plt.ylabel('Probability Density')
    plt.grid(axis='y', alpha=0.75)
    plt.legend()
    plt.show(block=False)
