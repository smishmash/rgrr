#!/usr/bin/env python3

import argparse
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pareto

from .rgrr.model import Model
from .rgrr.simulator import Simulator


def main():
    # Set up command line argument parser
    parser = argparse.ArgumentParser(
        description='Simulate preferential attachment network growth and resource distribution',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        '-n', '--nodes',
        type=int,
        default=100,
        help='Number of nodes'
    )

    parser.add_argument(
        '-r', '--resources',
        type=int,
        default=100,
        help='Initial number of resources per node'
    )

    parser.add_argument(
        '-a', '--add-resources',
        type=int,
        default=0,
        help='Additional resources to add during simulation'
    )

    parser.add_argument(
        '-m', '--method',
        type=str,
        choices=['random', 'preferential', 'even', 'specific'],
        default='random',
        help='Method for adding resources: random, preferential (rich get richer), even, or specific node'
    )

    parser.add_argument(
        '--target-node',
        type=int,
        default=0,
        help='Target node ID when using specific method'
    )

    parser.add_argument(
        '-s', '--seed',
        type=int,
        default=None,
        help='Random seed for reproducibility'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output file path for the network visualization (e.g., network.png)'
    )

    parser.add_argument(
        '--income-tax-rate',
        type=float,
        default=0.0,
        help='Income tax rate to apply at the end of the simulation'
    )

    parser.add_argument(
        '--plot-histogram',
        action='store_true',
        help='Plot a histogram of resource counts after simulation'
    )

    # Parse arguments
    args = parser.parse_args()

    # Create the simulation model with initial resources
    m = Model(args.nodes, args.resources)

    # Create simulator
    simulator = Simulator(m, args.method, args.income_tax_rate, args.seed)

    print(f"Created model with {args.nodes} nodes, each starting with {args.resources} resources")
    print(f"Initial total resources: {m.total_resources}")

    # Add additional resources if specified
    if args.add_resources == 0:
        args.add_resources = m.total_resources

    # Run the simulation
    simulator.run(args.add_resources, args.target_node)

    # Show the final status
    simulator.show_status()

    # Get the final distribution for plotting
    distribution = simulator.get_resource_distribution()

    # Plot histogram and theoretical Pareto distribution if requested
    if args.plot_histogram:
        # Create the histogram
        counts, bins, _ = plt.hist(distribution, bins=20, density=True, alpha=0.7, edgecolor='black', label='Resource Distribution')

        estimated_alpha = None
        # Use distribution directly as it's always positive as per user feedback
        # Fit the Pareto distribution. floc=0 fixes the location parameter at 0.
        # The fit returns shape, loc, and scale. We are interested in the shape parameter.
        shape, loc, scale = pareto.fit(distribution, floc=0)
        estimated_alpha = shape
        plt.title(f'Distribution of Resources per Node with Theoretical Pareto Distribution (alpha={estimated_alpha:.2f})')

        # Plot the theoretical Pareto distribution
        # Use the range of the histogram for the theoretical curve
        x = np.linspace(min(distribution), max(distribution), 100)

        # Ensure x values are positive for Pareto distribution
        x_positive = x[x > 0]
        pareto_pdf = pareto.pdf(x_positive, b=estimated_alpha, loc=loc, scale=scale)
        plt.plot(x_positive, pareto_pdf, color='r', linestyle='--', label=f'Theoretical Pareto (alpha={estimated_alpha:.2f})')

        plt.xlabel('Resources')
        plt.ylabel('Probability Density')
        plt.grid(axis='y', alpha=0.75)
        plt.legend()
        plt.show()


if __name__ == "__main__":
    main()
