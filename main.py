#!/usr/bin/env python3

import argparse
import rgrr.model as model
import matplotlib.pyplot as plt
import numpy as np
import powerlaw


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
        '--plot-histogram',
        action='store_true',
        help='Plot a histogram of resource counts after simulation'
    )

    # Parse arguments
    args = parser.parse_args()

    # Create the simulation model with initial resources
    m = model.Model(args.nodes, args.resources)
    
    # Create simulator
    simulator = model.Simulator(m, args.seed)
    
    print(f"Created model with {args.nodes} nodes, each starting with {args.resources} resources")
    print(f"Initial total resources: {m.total_resources}")
    
    # Add additional resources if specified
    if not args.add_resources:
        args.add_resources = m.total_resources

    print(f"\nAdding {args.add_resources} additional resources using '{args.method}' method...")
    
    if args.method == 'random':
        simulator.add_resources_randomly(args.add_resources)
    elif args.method == 'preferential':
        simulator.add_resources_preferentially(args.add_resources)
    elif args.method == 'even':
        simulator.add_resources_evenly(args.add_resources)
    elif args.method == 'specific':
        success = simulator.add_resources_to_node(args.target_node, args.add_resources)
        if not success:
            print(f"Error: Node {args.target_node} does not exist. Valid range: 0-{args.nodes-1}")
            return
    else:
        print(f"Unrecognized method {args.method}.")
        
    print(f"Final total resources: {m.total_resources}")
    
    # Get resource distribution
    distribution = simulator.get_resource_distribution()

    # Show summary
    print(f"\nResource distribution summary:")
    print(f"  Min resources: {min(distribution)}")
    print(f"  Max resources: {max(distribution)}")
    print(f"  Average resources: {sum(distribution) / len(distribution):.2f}")

    # Plot histogram and theoretical power law if requested
    if args.plot_histogram:
        # Create the histogram
        counts, bins, _ = plt.hist(distribution, bins=20, density=True, alpha=0.7, edgecolor='black', label='Resource Distribution')

        estimated_alpha = None
        # Use distribution directly as it's always positive as per user feedback
        fit = powerlaw.Fit(distribution, discrete=True)
        estimated_alpha = fit.alpha
        plt.title(f'Distribution of Resources per Node with Theoretical Power Law (alpha={estimated_alpha:.2f})')

        # Plot the theoretical power law distribution
        # Use the range of the histogram for the theoretical curve
        x = np.linspace(min(distribution), max(distribution), 100)
        
        # Calculate scaling factor to roughly match the histogram's peak
        # This is a heuristic; a more rigorous approach would involve normalization
        C = 1.0 # Default scaling
        if len(bins) > 1:
            max_hist_density = np.max(counts)
            # Estimate C such that C * x_min^(-alpha) is roughly max_hist_density
            C = max_hist_density * (min(distribution) ** estimated_alpha)

        # Ensure x values are positive for power law
        x_positive = x[x > 0]
        power_law_pdf = C * (x_positive ** (-estimated_alpha))
        plt.plot(x_positive, power_law_pdf, color='r', linestyle='--', label=f'Theoretical Power Law (alpha={estimated_alpha:.2f},C={C:.4f})')

        plt.xlabel('Resources')
        plt.ylabel('Probability Density')
        plt.grid(axis='y', alpha=0.75)
        plt.legend()
        plt.show()


if __name__ == "__main__":
    main()
