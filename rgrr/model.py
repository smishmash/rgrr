import random
from typing import Optional

class Node:
    def __init__(self, id: int, resources: int = 0):
        self.id = id
        self.resources = resources

class Model:
    def __init__(self, size: int, resources_per_node: int = 0):
        self.Nodes = [Node(i, resources_per_node) for i in range(size)]
        self.total_resources = size * resources_per_node

class Simulator:
    def __init__(self, model: Model, seed: Optional[int] = None):
        self.model = model
        if seed is not None:
            random.seed(seed)
    
    def add_resources_to_node(self, node_id: int, amount: int):
        """Add a specific amount of resources to a specific node."""
        assert 0 <= node_id < len(self.model.Nodes)
        self.model.Nodes[node_id].resources += amount
        self.model.total_resources += amount
    
    def add_resources_randomly(self, total_resources: int):
        """Distribute resources randomly among all nodes."""
        for _ in range(total_resources):
            random_node = random.choice(self.model.Nodes)
            random_node.resources += 1
        self.model.total_resources += total_resources
    
    def add_resources_preferentially(self, total_resources: int):
        """Add resources preferentially based on current resource count (rich get richer)."""
        for _ in range(total_resources):
            total_weight = self.model.total_resources
            assert total_weight > 0
            # Select node based on weighted probability
            rand_val = random.uniform(0, total_weight)
            # Can cumulative weight calculation be made more efficient?
            cumulative = 0
            for i, node in enumerate(self.model.Nodes):
                cumulative += node.resources
                if rand_val <= cumulative:
                    self.model.Nodes[i].resources += 1
                    self.model.total_resources += 1
                    break
    
    def add_resources_evenly(self, total_resources: int):
        """Distribute resources evenly among all nodes."""
        resources_per_node = total_resources // len(self.model.Nodes)
        remainder = total_resources % len(self.model.Nodes)
        for i, node in enumerate(self.model.Nodes):
            node.resources += resources_per_node
            if i < remainder:
                node.resources += 1
        self.model.total_resources += total_resources
    
    def get_resource_distribution(self):
        """Get a list of resource counts for each node."""
        return [node.resources for node in self.model.Nodes]
    
    def print_status(self):
        """Print current status of all nodes."""
        print(f"Total nodes: {len(self.model.Nodes)}")
        print(f"Total resources: {self.model.total_resources}")
        print("Node resources:")
        for node in self.model.Nodes:
            print(f"  Node {node.id}: {node.resources} resources")
