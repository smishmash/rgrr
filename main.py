#!/usr/bin/env python3

import argparse

from rgrr.model import Model
import rgrr.simulator as sim
from rgrr.operations import (
    ResourceDistributionOperation,
    IncomeTaxCollectionOperation,
    RequiredExpenditureOperation
)

def main():
    # Set up command line argument parser
    parser = argparse.ArgumentParser(
        description='Simulate preferential resource distribution',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Model specification
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

    # Non-operation simulator specification
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

    # Operation specifications
    parser.add_argument(
        '--random-method',
        type=int,
        default=0,
        help='Use random method for adding resources'
    )

    parser.add_argument(
        '--preferential-method',
        type=int,
        default=0,
        help='Use preferential method for adding resources'
    )

    parser.add_argument(
        '--uniform-method',
        type=int,
        default=0,
        help='Use uniform method for adding resources'
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

    # Parse arguments
    args = parser.parse_args()

    # Create the simulation model with initial resources
    m = Model(args.nodes, args.resources)

    operations = []
    if args.random_method:
        operations.append(ResourceDistributionOperation('random', args.random_method))
    if args.preferential_method:
        operations.append(ResourceDistributionOperation('preferential', args.preferential_method))
    if args.uniform_method:
        operations.append(ResourceDistributionOperation('uniform', args.uniform_method))
    if args.income_tax_rate:
        operations.append(IncomeTaxCollectionOperation(args.income_tax_rate))
    if args.required_expenditure:
        operations.append(RequiredExpenditureOperation(args.required_expenditure))

    print(f"Created model with {args.nodes} nodes, each starting with {args.resources} resources")
    print(f"Initial total resources: {m.total_resources}")

    # Create and run the multi-step simulation
    multi_step_simulator = sim.MultiStepSimulator(m, args.epochs, args.seed, operations)
    multi_step_simulator.run(args.plot_histogram)


if __name__ == "__main__":
    main()
