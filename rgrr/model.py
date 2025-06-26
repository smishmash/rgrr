import random
from typing import Optional
import numpy as np

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

class Node:
    def __init__(self, id: int, resources: int = 0):
        self.id = id
        self.resources = resources
        self.resources_added = 0

class Model:
    def __init__(self, size: int, resources_per_node: int = 0):
        self.Nodes = [Node(i, resources_per_node) for i in range(size)]
        self.total_resources = size * resources_per_node

class Simulator:
    def __init__(self, model: Model, seed: Optional[int] = None):
        self.model = model
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
    
    def print_status(self):
        """Print current status of all nodes."""
        print(f"Total nodes: {len(self.model.Nodes)}")
        print(f"Total resources: {self.model.total_resources}")
        print("Node resources:")
        for node in self.model.Nodes:
            print(f"  Node {node.id}: {node.resources} resources ({node.resources_added} added)")
