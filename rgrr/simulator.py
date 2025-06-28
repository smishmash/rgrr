import random
from typing import Optional
import numpy as np
from .model import Model

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
    def __init__(self, model: Model, method: str, tax_rate: float = 0.0, seed: Optional[int] = None):
        self.model = model
        self.method = method
        self.tax_rate = tax_rate
        self.total_tax_collected = 0
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

    def run(self, add_resources: int, target_node: Optional[int] = None):
        """Run the simulation."""
        print(f"\nAdding {add_resources} additional resources using '{self.method}' method...")

        if self.method == 'random':
            self.add_resources_randomly(add_resources)
        elif self.method == 'preferential':
            self.add_resources_preferentially(add_resources)
        elif self.method == 'even':
            self.add_resources_evenly(add_resources)
        elif self.method == 'specific':
            if target_node is None:
                raise ValueError("Target node must be specified for 'specific' method.")
            self.add_resources_to_node(target_node, add_resources)
        else:
            raise Exception(f"Unrecognized method {self.method}.")
        if self.tax_rate > 0:
            self.apply_tax(self.tax_rate)
        print(f"Final total resources: {self.model.total_resources}")


    def show_status(self):
        """Show the final status of the simulation."""
        distribution = self.get_resource_distribution()
        print(f"\nResource distribution summary:")
        print(f"  Min resources: {min(distribution)}")
        print(f"  Max resources: {max(distribution)}")
        print(f"  Average resources: {sum(distribution) / len(distribution):.2f}")

        if self.tax_rate > 0:
            print(f"\nApplied income tax at a rate of {self.tax_rate}")
            print(f"  Total tax collected: {self.total_tax_collected}")
            distribution = self.get_resource_distribution()
            print(f"\nResource distribution after tax:")
            print(f"  Min resources: {min(distribution)}")
            print(f"  Max resources: {max(distribution)}")
            print(f"  Average resources: {sum(distribution) / len(distribution):.2f}")
