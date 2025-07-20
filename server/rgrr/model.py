class Node:
    def __init__(self, id: int, resources: int = 0):
        self.id = id
        self.resources = resources
        self.resources_added = 0

class Model:
    def __init__(self, size: int, resources_per_node: int = 0):
        self.Nodes = [Node(i, resources_per_node) for i in range(size)]
        self.total_resources = size * resources_per_node
