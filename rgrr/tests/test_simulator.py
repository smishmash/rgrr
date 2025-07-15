import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import rgrr.simulator as sim
from rgrr.model import Model
from rgrr.operations import (
    ResourceDistributionOperation,
    IncomeTaxCollectionOperation,
    RequiredExpenditureOperation
)

class TestSimulator(unittest.TestCase):

    def setUp(self):
        # Common setup for tests
        self.initial_nodes = 5
        self.initial_resources_per_node = 10
        self.m = Model(self.initial_nodes, self.initial_resources_per_node)

    def test_initial_total_resources(self):
        # Test that Model initializes total_resources correctly
        self.assertEqual(self.m.total_resources, self.initial_nodes * self.initial_resources_per_node)

    def test_run_random(self):
        resources_to_add = 100
        initial_total = self.m.total_resources
        operations = [ResourceDistributionOperation('random', resources_to_add)]
        simulator = sim.Simulator(self.m, 42, operations)
        simulator.run()
        self.assertEqual(self.m.total_resources, initial_total + resources_to_add)

    def test_run_preferential(self):
        resources_to_add = 100
        operations = [ResourceDistributionOperation('preferential', resources_to_add)]
        simulator = sim.Simulator(self.m, 42, operations)
        initial_total = self.m.total_resources
        simulator.run()
        self.assertEqual(self.m.total_resources, initial_total + resources_to_add)

    def test_run_uniformly(self):
        resources_to_add = 100
        operations = [ResourceDistributionOperation('uniform', resources_to_add)]
        simulator = sim.Simulator(self.m, 42, operations)
        initial_total = self.m.total_resources
        simulator.run()
        self.assertEqual(self.m.total_resources, initial_total + resources_to_add)
        # Check for uniform distribution (within 1 resource difference)
        distribution = simulator.get_resource_distribution()
        min_res = min(distribution)
        max_res = max(distribution)
        self.assertTrue(max_res - min_res <= 1)

    def test_apply_tax(self):
        tax_rate = 0.1
        resources_to_add = 100
        operations = [
            ResourceDistributionOperation('random', resources_to_add),
            IncomeTaxCollectionOperation(tax_rate)
        ]
        simulator = sim.Simulator(self.m, 42, operations)
        initial_total_resources = self.m.total_resources
        simulator.run()

        # Tax is collected but not redistributed in the same epoch.
        self.assertGreater(simulator.total_tax_collected, 0)
        self.assertEqual(self.m.total_resources, initial_total_resources + resources_to_add - simulator.total_tax_collected)

    def test_apply_required_expenditure(self):
        expenditure_per_node = 5
        operations = [
            RequiredExpenditureOperation(expenditure_per_node)
        ]
        simulator = sim.Simulator(self.m, 42, operations)
        initial_total_resources = self.m.total_resources
        initial_node_resources = [node.resources for node in self.m.Nodes]

        simulator.run()

        # Calculate expected total expenditure
        expected_total_expenditure = 0
        for res in initial_node_resources:
            expected_total_expenditure += min(res, expenditure_per_node)

        self.assertGreater(expected_total_expenditure, 0)
        self.assertEqual(simulator.total_expenditure_incurred, expected_total_expenditure)
        self.assertEqual(self.m.total_resources, initial_total_resources - expected_total_expenditure)

        for i, node in enumerate(self.m.Nodes):
            expected_resources = initial_node_resources[i] - min(initial_node_resources[i], expenditure_per_node)
            self.assertEqual(node.resources, expected_resources)


class TestMultiStepSimulator(unittest.TestCase):
    def setUp(self):
        self.initial_nodes = 5
        self.initial_resources_per_node = 10
        self.m = Model(self.initial_nodes, self.initial_resources_per_node)

    def test_run(self):
        epochs = 3
        resources_to_add = 20
        operations = [ResourceDistributionOperation('random', resources_to_add)]
        multi_step_simulator = sim.MultiStepSimulator(self.m, epochs, 42, operations, 'random')

        initial_total_resources = self.m.total_resources
        multi_step_simulator.run()

        expected_total_resources = initial_total_resources + (epochs * resources_to_add)
        self.assertEqual(self.m.total_resources, expected_total_resources)

    def test_expenditure_redistribution(self):
        epochs = 2
        resources_to_add = 20
        expenditure_per_node = 15
        operations = [
            ResourceDistributionOperation('uniform', resources_to_add),
            RequiredExpenditureOperation(expenditure_per_node)
        ]
        multi_step_simulator = sim.MultiStepSimulator(self.m, epochs, 42, operations, 'uniform')

        initial_total_resources = self.m.total_resources
        multi_step_simulator.run()

        # In epoch 1:
        # Start with 5*10 = 50 resources.
        # Add 20 resources uniformly -> 50 + 20 = 70 total. Each node has 14.
        # Incur expenditure of 15 per node. Each node has 14, so each gives 14. Total expenditure = 14 * 5 = 70.
        # Each node has 0 resources.
        # In epoch 2:
        # Redistribute 70 resources from expenditure uniformly. Each node gets 14.
        # Add 20 resources uniformly -> 70 + 20 = 90 total. Each node gets 4 more, so 18 each.
        # Incur expenditure of 15 per node. Each node gives 15. Total expenditure = 15 * 5 = 75.
        # Each node has 3 resources. Total resources = 15.
        self.assertEqual(self.m.total_resources, 15)

    def test_tax_redistribution(self):
        epochs = 2
        resources_to_add = 100
        tax_rate = 0.1
        operations = [
            ResourceDistributionOperation('random', resources_to_add),
            IncomeTaxCollectionOperation(tax_rate)
        ]
        multi_step_simulator = sim.MultiStepSimulator(self.m, epochs, 42, operations, 'random')

        initial_total_resources = self.m.total_resources
        multi_step_simulator.run()

        # In epoch 1:
        # Start with 5*10 = 50 resources.
        # Add 100 resources randomly -> 150 total.
        # Tax at 0.1 on the 100 added resources. With seed 42, total tax collected is 8.
        # End of epoch 1 total resources = 150 - 8 = 142.
        # In epoch 2:
        # Redistribute 8 resources from tax uniformly. Total resources = 142 + 8 = 150.
        # Add 100 resources randomly -> 150 + 100 = 250.
        # Tax at 0.1 on the 100 added resources. With seed 42, total tax collected is 8.
        # End of epoch 2 total resources = 250 - 8 = 242.
        self.assertEqual(self.m.total_resources, 242)

if __name__ == '__main__':
    unittest.main()
