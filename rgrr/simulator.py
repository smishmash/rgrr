import random
import numpy as np
from typing import Optional, Sequence

from rgrr.model import Model
from rgrr.plotting import plot_resources_histogram
from rgrr.operations import SimulatorOperation

class FenwickTree:

    """A Fenwick Tree (or Binary Indexed Tree) for efficient prefix sum calculations."""
    def __init__(self, size: int):
        self.tree = np.zeros(size + 1, dtype=np.int64)

    def add(self, i: int, delta: int):
        """Add delta to element i."""
        i += 1  # 1-based index
        while i < len(self.tree):
            self.tree[i] += delta
            i += i & (-i)

    def prefix_sum(self, i: int) -> int:
        """Compute prefix sum up to element i."""
        i += 1  # 1-based index
        s = 0
        while i > 0:
            s += self.tree[i]
            i -= i & (-i)
        return s

    def find_kth(self, k: int) -> int:
        """Find the smallest index i such that prefix_sum(i) >= k."""
        i = 0
        p = 1 << (self.tree.size.bit_length() - 1)
        while p > 0:
            if i + p < len(self.tree) and self.tree[i + p] < k:
                k -= self.tree[i + p]
                i += p
            p >>= 1
        return i




class Simulator:
    """Runs a simulation of resource distribution among nodes."""

    def __init__(self,
                 model: Model,
                 seed: Optional[int],
                 operations: Sequence[SimulatorOperation]):
        self.model = model
        self.operations = operations
        self.total_tax_collected = 0
        self.total_expenditure_incurred = 0
        if seed is not None:
            random.seed(seed)
        # Initialize Fenwick Tree for preferential attachment
        self.fenwick_tree = FenwickTree(len(self.model.Nodes))
        for i, node in enumerate(self.model.Nodes):
            self.fenwick_tree.add(i, node.resources)

    def add_resources_to_node(self, node_id: int, amount: int):
        """Add a specific amount of resources to a specific node."""
        assert 0 <= node_id < len(self.model.Nodes)
        self.model.Nodes[node_id].resources += amount
        self.model.Nodes[node_id].resources_added += amount
        self.model.total_resources += amount
        self.fenwick_tree.add(node_id, amount)

    def get_resource_distribution(self):
        """Get a list of resource counts for each node."""
        return [node.resources for node in self.model.Nodes]

    def run(self):
        """Run the simulation."""
        # Reset resources_added for all nodes at the beginning of each run
        for node in self.model.Nodes:
            node.resources_added = 0

        for operation in self.operations:
            operation.execute(self)
        print(f"Final total resources: {self.model.total_resources}")


    def get_status(self):
        """Return the final status of the simulation as a dictionary."""
        distribution = self.get_resource_distribution()
        status = {
            "min_resources": min(distribution),
            "max_resources": max(distribution),
            "average_resources": sum(distribution) / len(distribution)
        }

        if self.total_tax_collected > 0:
            status["total_tax_collected"] = self.total_tax_collected
            status["post_tax_min_resources"] = min(distribution)
            status["post_tax_max_resources"] = max(distribution)
            status["post_tax_average_resources"] = sum(distribution) / len(distribution)
        if self.total_expenditure_incurred > 0:
            status["total_expenditure_incurred"] = self.total_expenditure_incurred
        return status


class MultiStepSimulator:
    def __init__(self, model: Model, epochs: int, seed: Optional[int], operations: Sequence[SimulatorOperation]):
        self.model = model
        self.epochs = epochs
        self.operations = operations
        self.seed = seed

    def run(self, plot_histogram: bool = False):
        """Run the simulation for a specified number of epochs."""
        for epoch in range(self.epochs):
            print(f"--- Epoch {epoch + 1}/{self.epochs} ---")
            simulator = Simulator(self.model, self.seed, self.operations)
            simulator.run()
            status = simulator.get_status()
            print(f"\nResource distribution summary:")
            print(f"  Min resources: {status['min_resources']}")
            print(f"  Max resources: {status['max_resources']}")
            print(f"  Average resources: {status['average_resources']:.2f}")

            if "total_tax_collected" in status:
                print(f"\nTotal tax collected: {status['total_tax_collected']}")
                print(f"\nResource distribution after tax:")
                print(f"  Min resources: {status['post_tax_min_resources']}")
                print(f"  Max resources: {status['post_tax_max_resources']}")
                print(f"  Average resources: {status['post_tax_average_resources']:.2f}")
            if "total_expenditure_incurred" in status:
                print(f"\nTotal expenditure incurred: {status['total_expenditure_incurred']}")
            if plot_histogram:
                plot_resources_histogram(simulator.get_resource_distribution(), f"Epoch {epoch + 1} Distribution")
        if plot_histogram:
            input("Waiting for <enter>... ")
