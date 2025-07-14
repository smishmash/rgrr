import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from rgrr.model import Model
from rgrr.simulator import Simulator, MultiStepSimulator

class TestSimulator(unittest.TestCase):

    def setUp(self):
        # Common setup for tests
        self.initial_nodes = 5
        self.initial_resources_per_node = 10
        self.m = Model(self.initial_nodes, self.initial_resources_per_node)

    def test_initial_total_resources(self):
        # Test that Model initializes total_resources correctly
        self.assertEqual(self.m.total_resources, self.initial_nodes * self.initial_resources_per_node)

    def test_run_specific(self):
        resources_to_add = 5
        target_node_id = 0
        simulator = Simulator(self.m, 'specific', resources_to_add, target_node_id, seed=42)
        initial_total = self.m.total_resources
        simulator.run()
        self.assertEqual(self.m.Nodes[target_node_id].resources, self.initial_resources_per_node + resources_to_add)
        self.assertEqual(self.m.total_resources, initial_total + resources_to_add)

    def test_run_random(self):
        resources_to_add = 100
        initial_total = self.m.total_resources
        simulator = Simulator(self.m, 'random', resources_to_add, tax_rate=0.0, seed=42)
        simulator.run()
        self.assertEqual(self.m.total_resources, initial_total + resources_to_add)

    def test_run_preferential(self):
        resources_to_add = 100
        simulator = Simulator(self.m, 'preferential', resources_to_add, tax_rate=0.0, seed=42)
        initial_total = self.m.total_resources
        simulator.run()
        self.assertEqual(self.m.total_resources, initial_total + resources_to_add)

    def test_run_evenly(self):
        resources_to_add = 100
        simulator = Simulator(self.m, 'even', resources_to_add, tax_rate=0.0, seed=42)
        initial_total = self.m.total_resources
        simulator.run()
        self.assertEqual(self.m.total_resources, initial_total + resources_to_add)
        # Check for even distribution (within 1 resource difference)
        distribution = simulator.get_resource_distribution()
        min_res = min(distribution)
        max_res = max(distribution)
        self.assertTrue(max_res - min_res <= 1)

    def test_apply_tax(self):
        tax_rate = 0.1
        resources_to_add = 100
        simulator = Simulator(self.m, 'random', resources_to_add, tax_rate=tax_rate, seed=42)
        initial_resources = simulator.get_resource_distribution()
        simulator.run()
        final_resources = simulator.get_resource_distribution()

        # Check that tax was applied correctly
        for i in range(len(self.m.Nodes)):
            resources_added = self.m.Nodes[i].resources_added
            tax_amount = int(resources_added * tax_rate)
            # The change in resources should be the resources added, minus the tax, plus the redistributed tax
            redistributed_tax = simulator.total_tax_collected // len(self.m.Nodes)
            remainder = simulator.total_tax_collected % len(self.m.Nodes)
            if i < remainder:
                redistributed_tax += 1

            self.assertEqual(final_resources[i] - initial_resources[i], resources_added - tax_amount + redistributed_tax)

        # Because taxes collected are rounded down
        self.assertEqual(simulator.total_tax_collected, 8)
        self.assertEqual(self.m.total_resources, sum(initial_resources) + 100)

    def test_apply_required_expenditure(self):
        expenditure_per_node = 5
        resources_to_add = 0 # No resources added for this test
        simulator = Simulator(self.m, 'random', resources_to_add, required_expenditure=expenditure_per_node, seed=42)
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
        simulator = Simulator(self.m, 'random', resources_to_add, seed=42)
        multi_step_simulator = MultiStepSimulator(simulator, epochs)

        initial_total_resources = self.m.total_resources
        multi_step_simulator.run()

        expected_total_resources = initial_total_resources + (epochs * resources_to_add)
        self.assertEqual(self.m.total_resources, expected_total_resources)

if __name__ == '__main__':
    unittest.main()
