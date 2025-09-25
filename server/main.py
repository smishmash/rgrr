#!/usr/bin/env python3

import argparse
import logging
from rgrr.logging_config import setup_logging

from rgrr.model import Model
import rgrr.simulator as sim
from rgrr.operations import (
    ResourceDistributionOperation,
    IncomeTaxCollectionOperation,
    RequiredExpenditureOperation
)
from rgrr.simulation_store import store_simulation, get_simulation

def run_simulation_from_args(args) -> sim.MultiStepSimulator:
    # Create the simulation model with initial resources
    m = Model(args.nodes, args.resources)

    operations = []
    expenditure_distribution_method = 'uniform' # Default
    if args.random_method:
        operations.append(ResourceDistributionOperation.create('random', args.random_method))
        expenditure_distribution_method = 'random'
    if args.preferential_method:
        operations.append(ResourceDistributionOperation.create('preferential', args.preferential_method))
        expenditure_distribution_method = 'preferential'
    if args.uniform_method:
        operations.append(ResourceDistributionOperation.create('uniform', args.uniform_method))
        expenditure_distribution_method = 'uniform'
    if args.income_tax_rate:
        operations.append(IncomeTaxCollectionOperation(args.income_tax_rate))
    if args.required_expenditure:
        operations.append(RequiredExpenditureOperation(args.required_expenditure))

    logging.debug(f"Created model with {args.nodes} nodes, each starting with {args.resources} resources")
    logging.debug(f"Initial total resources: {m.total_resources}")

    # Create and run the multi-step simulation
    multi_step_simulator = sim.MultiStepSimulator(m, args.epochs, args.seed, operations, expenditure_distribution_method)
    multi_step_simulator.run()
    return multi_step_simulator

def main():
    # Set up logging
    setup_logging()

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
        '--epochs',
        type=int,
        default=1,
        help='Number of epochs to run the simulation'
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--plot-histogram',
        action='store_true',
        help='Plot a histogram of resource counts after simulation'
    )
    group.add_argument(
        '--start-http-server',
        action='store_true',
        help='Start an HTTP server to retrieve distributions'
    )

    # Operation specifications
    dist_group = parser.add_mutually_exclusive_group()
    dist_group.add_argument(
        '--random-method',
        type=int,
        default=0,
        help='Use random method for adding resources'
    )

    dist_group.add_argument(
        '--preferential-method',
        type=int,
        default=0,
        help='Use preferential method for adding resources'
    )

    dist_group.add_argument(
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
    simulator = run_simulation_from_args(args)
    store_simulation("dummy", simulator)
    if args.plot_histogram:
        from rgrr.plotting import EpochPlotter
        plotter = EpochPlotter()
        plotter.show()

    if args.start_http_server:
        from rgrr.server import app
        from flask_swagger_ui import get_swaggerui_blueprint

        SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
        API_URL = '/swagger.json'  # Our API url (can of course be a local resource)

        # Call factory function to create our blueprint
        swaggerui_blueprint = get_swaggerui_blueprint(
            SWAGGER_URL,
            API_URL,
            config={
                'app_name': "RGRR API"
            }
        )

        app.register_blueprint(swaggerui_blueprint)
        app.run(debug=True, use_reloader=False)


if __name__ == "__main__":
    main()
