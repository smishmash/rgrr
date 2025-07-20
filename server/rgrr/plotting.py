import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons
import numpy as np
from scipy.stats import pareto

from .simulation_results import get_simulation_results

class EpochPlotter:
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.current_epoch = 0
        self.radio = None
        self.xlim = None
        self.ylim = None

    def plot_current_epoch(self):
        self.ax.clear()
        distributions = get_simulation_results("dummy")
        distribution = distributions[self.current_epoch - 1]

        self.ax.hist(distribution, bins=20, density=True, alpha=0.7, edgecolor='black', label='Resource Distribution')

        shape, loc, scale = pareto.fit(distribution, floc=0)
        estimated_alpha = shape
        self.ax.set_title(f'Epoch {self.current_epoch} with Theoretical Pareto Distribution (alpha={estimated_alpha:.2f})', fontsize=10)

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
        distributions = get_simulation_results("dummy")
        if event.key == 'right':
            if self.current_epoch < len(distributions):
                self.current_epoch += 1
                self.plot_current_epoch()
                if self.radio:
                    self.radio.set_active(self.current_epoch - 1)
        elif event.key == 'left':
            if self.current_epoch > 1:
                self.current_epoch -= 1
                self.plot_current_epoch()
                if self.radio:
                    self.radio.set_active(self.current_epoch - 1)

    def show(self):
        distributions = get_simulation_results("dummy")
        # Determine global x and y ranges
        global_min_x, global_max_x = float('inf'), float('-inf')
        global_max_y = float('-inf')
        for dist in distributions:
            global_min_x = min(global_min_x, min(dist))
            global_max_x = max(global_max_x, max(dist))
            hist, _ = np.histogram(dist, bins=20, density=True)
            global_max_y = max(global_max_y, hist.max())

        # self.xlim = (global_min_x, global_max_x)
        # self.ylim = (0, global_max_y * 1.1)  # Add a little padding

        plt.subplots_adjust(left=0.3)
        radio_ax = plt.axes((0.05, 0.4, 0.15, 0.5), facecolor='lightgoldenrodyellow')
        epoch_labels = [f'Epoch {e}' for e in range(1, len(distributions) + 1)]
        self.radio = RadioButtons(radio_ax, epoch_labels)

        def on_radio_clicked(label):
            self.current_epoch = int(label.split(' ')[1])
            self.plot_current_epoch()

        self.radio.on_clicked(on_radio_clicked)
        self.fig.canvas.mpl_connect('key_press_event', self.key_press)

        self.current_epoch = 1
        self.plot_current_epoch()
        plt.show()
