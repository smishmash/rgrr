#!/usr/bin/env python3

import argparse

from rgrr.model import Model
from rgrr.simulator import Simulator, MultiStepSimulator


def main():
    # Set up command line argument parser
    parser = argparse.ArgumentParser(
        description='Simulate preferential resource distribution',
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
        '--required-expenditure',
        type=int,
        default=0,
        help='Required expenditure to apply at the end of the simulation'
    )

    parser.add_argument(
        '--epochs',
        type=int,
        default=1,
        help='Number of epochs to run the simulation'
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
    if args.add_resources == 0:
        args.add_resources = m.total_resources
    simulator = Simulator(m, args.method, args.add_resources, args.target_node, args.income_tax_rate, args.required_expenditure, args.seed)

    print(f"Created model with {args.nodes} nodes, each starting with {args.resources} resources")
    print(f"Initial total resources: {m.total_resources}")

    # Create and run the multi-step simulation
    multi_step_simulator = MultiStepSimulator(simulator, args.epochs)
    multi_step_simulator.run(args.plot_histogram)


if __name__ == "__main__":
    main()
