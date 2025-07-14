from __future__ import annotations
import random
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from rgrr.simulator import Simulator

class SimulatorOperation(ABC):
    """Abstract base class for all simulator operations."""

    @abstractmethod
    def execute(self, simulator: Simulator):
        pass

class ResourceDistributionOperation(SimulatorOperation):
    """Distributes resources based on a specified method."""

    def __init__(self, method: str, resources_added: int, target_node: Optional[int] = None):
        self.method = method
        self.resources_added = resources_added
        self.target_node = target_node
        if self.method == 'specific' and self.target_node is None:
            raise ValueError("Target node must be specified for 'specific' method.")

    def _add_resources_randomly(self, simulator: Simulator, total_resources: int):
        """Distribute resources randomly among all nodes."""
        for _ in range(total_resources):
            random_node_id = random.randint(0, len(simulator.model.Nodes) - 1)
            simulator.add_resources_to_node(random_node_id, 1)

    def _add_resources_preferentially(self, simulator: Simulator, total_resources: int):
        """Add resources preferentially based on current resource count (rich get richer)."""
        for _ in range(total_resources):
            total_weight = simulator.model.total_resources
            if total_weight == 0:
                # If there are no resources, distribute randomly
                self._add_resources_randomly(simulator, 1)
                continue

            # Select node based on weighted probability using Fenwick Tree
            rand_val = random.randint(1, total_weight)
            node_id = simulator.fenwick_tree.find_kth(rand_val)

            # Add resource to the selected node
            simulator.add_resources_to_node(node_id, 1)

    def _add_resources_uniformly(self, simulator: Simulator, total_resources: int):
        """Distribute resources uniformly among all nodes."""
        if not simulator.model.Nodes:
            return
        resources_per_node = total_resources // len(simulator.model.Nodes)
        remainder = total_resources % len(simulator.model.Nodes)
        for i in range(len(simulator.model.Nodes)):
            amount = resources_per_node + (1 if i < remainder else 0)
            simulator.add_resources_to_node(i, amount)

    def execute(self, simulator: Simulator):
        print(f"\nAdding {self.resources_added} additional resources using '{self.method}' method...")
        if self.method == 'random':
            self._add_resources_randomly(simulator, self.resources_added)
        elif self.method == 'preferential':
            self._add_resources_preferentially(simulator, self.resources_added)
        elif self.method == 'uniform':
            self._add_resources_uniformly(simulator, self.resources_added)
        else:
            raise Exception(f"Unrecognized method {self.method}.")

class IncomeTaxCollectionOperation(SimulatorOperation):
    """Applies tax to resources added and collects it."""

    def __init__(self, tax_rate: float):
        self.tax_rate = tax_rate

    def execute(self, simulator: Simulator):
        """Apply a tax to the resources added to each node and redistribute the collected tax."""
        if not (0 <= self.tax_rate <= 1):
            raise ValueError("Tax rate must be between 0 and 1.")
        if self.tax_rate == 0:
            return

        total_tax = 0
        for node in simulator.model.Nodes:
            tax_amount = int(node.resources_added * self.tax_rate)
            if tax_amount > 0:
                simulator.add_resources_to_node(node.id, -tax_amount)
                total_tax += tax_amount
        simulator.total_tax_collected = total_tax

        # Redistribute the collected tax uniformly
        if not simulator.model.Nodes:
            return
        resources_per_node = total_tax // len(simulator.model.Nodes)
        remainder = total_tax % len(simulator.model.Nodes)
        for i in range(len(simulator.model.Nodes)):
            amount = resources_per_node + (1 if i < remainder else 0)
            simulator.add_resources_to_node(i, amount)

class RequiredExpenditureOperation(SimulatorOperation):
    """Applies a required expenditure, reducing resources from each node."""

    def __init__(self, expenditure: int):
        self.expenditure = expenditure

    def execute(self, simulator: Simulator):
        """Apply a required expenditure, reducing resources from each node."""
        if self.expenditure == 0:
            return

        total_expenditure_incurred = 0
        for node in simulator.model.Nodes:
            amount_to_deduct = min(node.resources, self.expenditure) # Deduct up to 'expenditure' or node's current resources
            simulator.add_resources_to_node(node.id, -amount_to_deduct)
            total_expenditure_incurred += amount_to_deduct
        simulator.total_expenditure_incurred = total_expenditure_incurred
