import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import rgrr.model as model

class TestSimulator(unittest.TestCase):

    def setUp(self):
        # Common setup for tests
        self.initial_nodes = 5
        self.initial_resources_per_node = 10
        self.m = model.Model(self.initial_nodes, self.initial_resources_per_node)

    def test_initial_total_resources(self):
        # Test that Model initializes total_resources correctly
        self.assertEqual(self.m.total_resources, self.initial_nodes * self.initial_resources_per_node)

    def test_run_specific(self):
        simulator = model.Simulator(self.m, method='specific', seed=42)
        amount_to_add = 5
        target_node_id = 0
        initial_total = self.m.total_resources
        simulator.run(amount_to_add, target_node_id)
        self.assertEqual(self.m.Nodes[target_node_id].resources, self.initial_resources_per_node + amount_to_add)
        self.assertEqual(self.m.total_resources, initial_total + amount_to_add)

    def test_run_random(self):
        simulator = model.Simulator(self.m, method='random', tax_rate=0.0, seed=42)
        resources_to_add = 100
        initial_total = self.m.total_resources
        simulator.run(resources_to_add)
        self.assertEqual(self.m.total_resources, initial_total + resources_to_add)

    def test_run_preferential(self):
        simulator = model.Simulator(self.m, method='preferential', tax_rate=0.0, seed=42)
        resources_to_add = 100
        initial_total = self.m.total_resources
        simulator.run(resources_to_add)
        self.assertEqual(self.m.total_resources, initial_total + resources_to_add)

    def test_run_evenly(self):
        simulator = model.Simulator(self.m, method='even', tax_rate=0.0, seed=42)
        resources_to_add = 100
        initial_total = self.m.total_resources        
        simulator.run(resources_to_add)
        self.assertEqual(self.m.total_resources, initial_total + resources_to_add)
        # Check for even distribution (within 1 resource difference)
        distribution = simulator.get_resource_distribution()
        min_res = min(distribution)
        max_res = max(distribution)
        self.assertTrue(max_res - min_res <= 1)

    def test_apply_tax(self):
        tax_rate = 0.1
        simulator = model.Simulator(self.m, method='random', tax_rate=tax_rate, seed=42)
        
        # Get initial state
        initial_resources = simulator.get_resource_distribution()
        
        # Run the simulation
        simulator.run(100)
        
        # Get final state
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

if __name__ == '__main__':
    unittest.main()
