import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pareto

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
