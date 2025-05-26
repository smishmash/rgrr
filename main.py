#!/usr/bin/env python3

import argparse
import rgrr.model as model


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
        '--show-status',
        action='store_true',
        help='Show detailed status of all nodes'
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
    
    # Show status if requested
    if args.show_status:
        print("\n" + "="*50)
        simulator.print_status()
    else:
        # Show summary
        distribution = simulator.get_resource_distribution()
        print(f"\nResource distribution summary:")
        print(f"  Min resources: {min(distribution)}")
        print(f"  Max resources: {max(distribution)}")
        print(f"  Average resources: {sum(distribution) / len(distribution):.2f}")


if __name__ == "__main__":
    main()
