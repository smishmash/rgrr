import random
from typing import Optional
import numpy as np

from .model import Model
from .plotting import plot_resources_histogram

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
                 method: str,
                 resources_added: int,
                 target_node: Optional[int] = None,
                 tax_rate: float = 0.0,
                 required_expenditure: int = 0,
                 seed: Optional[int] = None):
        self.model = model
        self.method = method
        self.tax_rate = tax_rate
        self.required_expenditure = required_expenditure
        self.total_tax_collected = 0
        self.total_expenditure_incurred = 0
        self.resources_added = resources_added
        self.target_node = target_node
        if self.method == 'specific' and self.target_node is None:
            raise ValueError("Target node must be specified for 'specific' method.")
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

    def add_resources_evenly(self, total_resources: int):
        """Distribute resources evenly among all nodes."""
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

        # Redistribute the collected tax evenly
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
        print(f"\nAdding {self.resources_added} additional resources using '{self.method}' method...")

        if self.method == 'random':
            self.add_resources_randomly(self.resources_added)
        elif self.method == 'preferential':
            self.add_resources_preferentially(self.resources_added)
        elif self.method == 'even':
            self.add_resources_evenly(self.resources_added)
        elif self.method == 'specific':
            self.add_resources_to_node(self.target_node, self.resources_added)
        else:
            raise Exception(f"Unrecognized method {self.method}.")
        if self.tax_rate > 0:
            self.apply_tax(self.tax_rate)
        if self.required_expenditure > 0:
            self.apply_required_expenditure(self.required_expenditure)
        print(f"Final total resources: {self.model.total_resources}")


    def get_status(self):
        """Return the final status of the simulation as a dictionary."""
        distribution = self.get_resource_distribution()
        status = {
            "min_resources": min(distribution),
            "max_resources": max(distribution),
            "average_resources": sum(distribution) / len(distribution)
        }

        if self.tax_rate > 0:
            status["tax_rate"] = self.tax_rate
            status["total_tax_collected"] = self.total_tax_collected
            status["post_tax_min_resources"] = min(distribution)
            status["post_tax_max_resources"] = max(distribution)
            status["post_tax_average_resources"] = sum(distribution) / len(distribution)
        if self.required_expenditure > 0:
            status["required_expenditure"] = self.required_expenditure
            status["total_expenditure_incurred"] = self.total_expenditure_incurred
        return status


class MultiStepSimulator:
    def __init__(self, simulator: Simulator, epochs: int):
        self.simulator = simulator
        self.epochs = epochs

    def run(self, plot_histogram: bool = False):
        """Run the simulation for a specified number of epochs."""
        for epoch in range(self.epochs):
            print(f"--- Epoch {epoch + 1}/{self.epochs} ---")
            self.simulator.run()
            status = self.simulator.get_status()
            print(f"\nResource distribution summary:")
            print(f"  Min resources: {status['min_resources']}")
            print(f"  Max resources: {status['max_resources']}")
            print(f"  Average resources: {status['average_resources']:.2f}")

            if self.simulator.tax_rate > 0:
                print(f"\nApplied income tax at a rate of {status['tax_rate']}")
                print(f"  Total tax collected: {status['total_tax_collected']}")
                print(f"\nResource distribution after tax:")
                print(f"  Min resources: {status['post_tax_min_resources']}")
                print(f"  Max resources: {status['post_tax_max_resources']}")
                print(f"  Average resources: {status['post_tax_average_resources']:.2f}")
            if self.simulator.required_expenditure > 0:
                print(f"\nApplied required expenditure of {status['required_expenditure']}")
                print(f"  Total expenditure incurred: {status['total_expenditure_incurred']}")
            if plot_histogram:
                plot_resources_histogram(self.simulator.get_resource_distribution(), f"Epoch {epoch + 1} Distribution")
        if plot_histogram:
            input("Waiting for <enter>... ")
