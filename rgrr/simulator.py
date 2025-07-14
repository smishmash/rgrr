import random
import numpy as np
from abc import ABC, abstractmethod
from typing import Optional

from rgrr.model import Model
from rgrr.plotting import plot_resources_histogram

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



class SimulatorOperation(ABC):
    """Abstract base class for all simulator operations."""

    @abstractmethod
    def execute(self, simulator: 'Simulator'):
        pass

class ResourceDistributionOperation(SimulatorOperation):
    """Distributes resources based on a specified method."""

    def __init__(self, method: str, resources_added: int):
        self.method = method
        self.resources_added = resources_added

    def execute(self, simulator: 'Simulator'):
        print(f"\nAdding {self.resources_added} additional resources using '{self.method}' method...")
        if self.method == 'random':
            simulator.add_resources_randomly(self.resources_added)
        elif self.method == 'preferential':
            simulator.add_resources_preferentially(self.resources_added)
        elif self.method == 'uniform':
            simulator.add_resources_uniformly(self.resources_added)
        else:
            raise Exception(f"Unrecognized method {self.method}.")

class IncomeTaxCollectionOperation(SimulatorOperation):
    """Applies tax to resources added and collects it."""

    def __init__(self, tax_rate: float):
        self.tax_rate = tax_rate

    def execute(self, simulator: 'Simulator'):
        simulator.apply_tax(self.tax_rate)

class RequiredExpenditureOperation(SimulatorOperation):
    """Applies a required expenditure, reducing resources from each node."""

    def __init__(self, expenditure: int):
        self.expenditure = expenditure

    def execute(self, simulator: 'Simulator'):
        simulator.apply_required_expenditure(self.expenditure)

class Simulator:
    """Runs a simulation of resource distribution among nodes."""

    def __init__(self,
                 model: Model,
                 seed: Optional[int],
                 operations: list[SimulatorOperation]):
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

    def add_resources_randomly(self, total_resources: int):
        """Distribute resources randomly among all nodes."""
        for _ in range(total_resources):
            random_node_id = random.randint(0, len(self.model.Nodes) - 1)
            self.add_resources_to_node(random_node_id, 1)

    def add_resources_preferentially(self, total_resources: int):
        """Add resources preferentially based on current resource count (rich get richer)."""
        for _ in range(total_resources):
            total_weight = self.model.total_resources
            if total_weight == 0:
                # If there are no resources, distribute randomly
                self.add_resources_randomly(1)
                continue

            # Select node based on weighted probability using Fenwick Tree
            rand_val = random.randint(1, total_weight)
            node_id = self.fenwick_tree.find_kth(rand_val)

            # Add resource to the selected node
            self.add_resources_to_node(node_id, 1)

    def add_resources_uniformly(self, total_resources: int):
        """Distribute resources uniformly among all nodes."""
        if not self.model.Nodes:
            return
        resources_per_node = total_resources // len(self.model.Nodes)
        remainder = total_resources % len(self.model.Nodes)
        for i in range(len(self.model.Nodes)):
            amount = resources_per_node + (1 if i < remainder else 0)
            self.add_resources_to_node(i, amount)

    def get_resource_distribution(self):
        """Get a list of resource counts for each node."""
        return [node.resources for node in self.model.Nodes]

    def apply_tax(self, tax_rate: float):
        """Apply a tax to the resources added to each node and redistribute the collected tax."""
        if not (0 <= tax_rate <= 1):
            raise ValueError("Tax rate must be between 0 and 1.")
        if tax_rate == 0:
            return

        total_tax = 0
        for node in self.model.Nodes:
            tax_amount = int(node.resources_added * tax_rate)
            if tax_amount > 0:
                self.add_resources_to_node(node.id, -tax_amount)
                total_tax += tax_amount
        self.total_tax_collected = total_tax

        # Redistribute the collected tax uniformly
        if not self.model.Nodes:
            return
        resources_per_node = total_tax // len(self.model.Nodes)
        remainder = total_tax % len(self.model.Nodes)
        for i in range(len(self.model.Nodes)):
            amount = resources_per_node + (1 if i < remainder else 0)
            self.add_resources_to_node(i, amount)

    def apply_required_expenditure(self, expenditure: int):
        """Apply a required expenditure, reducing resources from each node."""
        if expenditure == 0:
            return

        total_expenditure_incurred = 0
        for node in self.model.Nodes:
            amount_to_deduct = min(node.resources, expenditure) # Deduct up to 'expenditure' or node's current resources
            self.add_resources_to_node(node.id, -amount_to_deduct)
            total_expenditure_incurred += amount_to_deduct
        self.total_expenditure_incurred = total_expenditure_incurred

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
    def __init__(self, model: Model, epochs: int, seed: Optional[int], operations: list[SimulatorOperation]):
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
