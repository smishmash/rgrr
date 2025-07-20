import os
import pytest
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from rgrr.operations import (
    ResourceDistributionOperation,
    IncomeTaxCollectionOperation,
    RequiredExpenditureOperation,
    RandomResourceDistribution,
    PreferentialResourceDistribution,
    UniformResourceDistribution,
)

# Mocks for Simulator, Model, and Node
class MockNode:
    def __init__(self, id, resources=0, resources_added=0):
        self.id = id
        self.resources = resources
        self.resources_added = resources_added

class MockModel:
    def __init__(self, num_nodes, initial_resources=0):
        self.Nodes = [MockNode(i, initial_resources) for i in range(num_nodes)]
        self.total_resources = num_nodes * initial_resources

class MockSimulator:
    def __init__(self, num_nodes, initial_resources=0):
        self.model = MockModel(num_nodes, initial_resources)
        self.total_tax_collected = 0
        self.total_expenditure_incurred = 0
        # Mock Fenwick Tree
        self.fenwick_tree = MagicMock()
        self.fenwick_tree.find_kth.return_value = 0  # Default mock behavior

    def add_resources_to_node(self, node_id, amount):
        node = self.model.Nodes[node_id]
        node.resources += amount
        if amount > 0:
            node.resources_added += amount
        self.model.total_resources += amount

@pytest.fixture
def simulator():
    return MockSimulator(num_nodes=3, initial_resources=10)

# Tests for ResourceDistributionOperation
def test_resource_distribution_factory():
    op_random = ResourceDistributionOperation.create('random', 10)
    assert isinstance(op_random, RandomResourceDistribution)

    op_preferential = ResourceDistributionOperation.create('preferential', 10)
    assert isinstance(op_preferential, PreferentialResourceDistribution)

    op_uniform = ResourceDistributionOperation.create('uniform', 10)
    assert isinstance(op_uniform, UniformResourceDistribution)

    with pytest.raises(ValueError):
        ResourceDistributionOperation.create('invalid_method', 10)

def test_random_distribution(simulator):
    op = RandomResourceDistribution(10)
    with patch('random.randint', return_value=0):
        op.execute(simulator)
        assert simulator.model.Nodes[0].resources == 20
        assert simulator.model.total_resources == 40

def test_preferential_distribution(simulator):
    op = PreferentialResourceDistribution(10)
    simulator.model.total_resources = 30
    simulator.fenwick_tree.find_kth.return_value = 1
    op.execute(simulator)
    assert simulator.model.Nodes[1].resources == 20
    assert simulator.model.total_resources == 40

def test_uniform_distribution(simulator):
    op = UniformResourceDistribution(10)
    op.execute(simulator)
    assert simulator.model.Nodes[0].resources == 14
    assert simulator.model.Nodes[1].resources == 13
    assert simulator.model.Nodes[2].resources == 13
    assert simulator.model.total_resources == 40

# Tests for IncomeTaxCollectionOperation
def test_income_tax_collection(simulator):
    # Add some resources to be taxed
    simulator.add_resources_to_node(0, 10)
    simulator.add_resources_to_node(1, 20)
    
    op = IncomeTaxCollectionOperation(tax_rate=0.1)
    op.execute(simulator)
    
    # Tax on node 0: 10 * 0.1 = 1
    # Tax on node 1: 20 * 0.1 = 2
    assert simulator.model.Nodes[0].resources == 19 # 10 initial + 10 added - 1 tax
    assert simulator.model.Nodes[1].resources == 28 # 10 initial + 20 added - 2 tax
    assert simulator.total_tax_collected == 3

def test_income_tax_with_zero_rate(simulator):
    op = IncomeTaxCollectionOperation(tax_rate=0.0)
    op.execute(simulator)
    assert simulator.total_tax_collected == 0
    assert simulator.model.Nodes[0].resources == 10

def test_income_tax_invalid_rate():
    with pytest.raises(ValueError):
        op = IncomeTaxCollectionOperation(tax_rate=1.5)
        op.execute(MagicMock())

# Tests for RequiredExpenditureOperation
def test_required_expenditure(simulator):
    op = RequiredExpenditureOperation(expenditure=5)
    op.execute(simulator)
    
    # Each node started with 10, expenditure is 5
    assert simulator.model.Nodes[0].resources == 5
    assert simulator.model.Nodes[1].resources == 5
    assert simulator.model.Nodes[2].resources == 5
    assert simulator.total_expenditure_incurred == 15

def test_required_expenditure_exceeds_resources(simulator):
    op = RequiredExpenditureOperation(expenditure=15)
    op.execute(simulator)
    
    # Nodes only have 10, so only 10 can be deducted
    assert simulator.model.Nodes[0].resources == 0
    assert simulator.model.Nodes[1].resources == 0
    assert simulator.model.Nodes[2].resources == 0
    assert simulator.total_expenditure_incurred == 30

def test_required_expenditure_with_zero_expenditure(simulator):
    op = RequiredExpenditureOperation(expenditure=0)
    op.execute(simulator)
    assert simulator.model.Nodes[0].resources == 10
    assert simulator.total_expenditure_incurred == 0
