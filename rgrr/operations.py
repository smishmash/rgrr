from __future__ import annotations
import random
import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from rgrr.simulator import Simulator

class SimulatorOperation(ABC):
    """Abstract base class for all simulator operations."""

    @abstractmethod
    def execute(self, simulator: Simulator):
        pass

class ResourceDistributionOperation(SimulatorOperation, ABC):
    """Abstract base class for resource distribution operations."""

    def __init__(self, resources_added: int):
        self.resources_added = resources_added

    @staticmethod
    def create(method: str, resources_added: int) -> 'ResourceDistributionOperation':
        if method == 'random':
            return RandomResourceDistribution(resources_added)
        elif method == 'preferential':
            return PreferentialResourceDistribution(resources_added)
        elif method == 'uniform':
            return UniformResourceDistribution(resources_added)
        else:
            raise ValueError(f"Unrecognized distribution method: {method}")

    @property
    @abstractmethod
    def method(self) -> str:
        """The method of resource distribution."""
        pass

    def execute(self, simulator: Simulator):
        logging.debug(f"\nAdding {self.resources_added} additional resources using '{self.method}' method...")
        self._distribute(simulator, self.resources_added)

    @abstractmethod
    def _distribute(self, simulator: Simulator, total_resources: int):
        pass


class RandomResourceDistribution(ResourceDistributionOperation):
    """Distributes resources randomly among all nodes."""

    @property
    def method(self) -> str:
        return 'random'

    def _distribute(self, simulator: Simulator, total_resources: int):
        for _ in range(total_resources):
            random_node_id = random.randint(0, len(simulator.model.Nodes) - 1)
            simulator.add_resources_to_node(random_node_id, 1)


class PreferentialResourceDistribution(ResourceDistributionOperation):
    """Adds resources preferentially based on current resource count (rich get richer)."""

    @property
    def method(self) -> str:
        return 'preferential'

    def _distribute(self, simulator: Simulator, total_resources: int):
        for _ in range(total_resources):
            total_weight = simulator.model.total_resources
            if total_weight == 0:
                # If there are no resources, distribute randomly
                random_node_id = random.randint(0, len(simulator.model.Nodes) - 1)
                simulator.add_resources_to_node(random_node_id, 1)
                continue

            # Select node based on weighted probability using Fenwick Tree
            rand_val = random.randint(1, total_weight)
            node_id = simulator.fenwick_tree.find_kth(rand_val)

            # Add resource to the selected node
            simulator.add_resources_to_node(node_id, 1)


class UniformResourceDistribution(ResourceDistributionOperation):
    """Distributes resources uniformly among all nodes."""

    @property
    def method(self) -> str:
        return 'uniform'

    def _distribute(self, simulator: Simulator, total_resources: int):
        if not simulator.model.Nodes:
            return
        resources_per_node = total_resources // len(simulator.model.Nodes)
        remainder = total_resources % len(simulator.model.Nodes)
        for i in range(len(simulator.model.Nodes)):
            amount = resources_per_node + (1 if i < remainder else 0)
            simulator.add_resources_to_node(i, amount)

class IncomeTaxCollectionOperation(SimulatorOperation):
    """Applies tax to resources added and collects it."""

    def __init__(self, tax_rate: float):
        self.tax_rate = tax_rate

    def execute(self, simulator: Simulator):
        """Apply a tax to the resources added to each node and collect it."""
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
        simulator.total_tax_collected += total_tax

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
