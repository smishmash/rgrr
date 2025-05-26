import unittest
import preferential.model as model

class TestSimulator(unittest.TestCase):

    def setUp(self):
        # Common setup for tests
        self.initial_nodes = 5
        self.initial_resources_per_node = 10
        self.m = model.Model(self.initial_nodes, self.initial_resources_per_node)
        self.simulator = model.Simulator(self.m)

    def test_initial_total_resources(self):
        # Test that Model initializes total_resources correctly
        self.assertEqual(self.m.total_resources, self.initial_nodes * self.initial_resources_per_node)

    def test_add_resources_to_node(self):
        amount_to_add = 5
        target_node_id = 0
        initial_total = self.m.total_resources
        
        success = self.simulator.add_resources_to_node(target_node_id, amount_to_add)
        self.assertTrue(success)
        self.assertEqual(self.m.Nodes[target_node_id].resources, self.initial_resources_per_node + amount_to_add)
        self.assertEqual(self.m.total_resources, initial_total + amount_to_add)

        # Test adding to a non-existent node
        success = self.simulator.add_resources_to_node(999, amount_to_add)
        self.assertFalse(success)
        self.assertEqual(self.m.total_resources, initial_total + amount_to_add) # Total resources should not change

    def test_add_resources_randomly(self):
        resources_to_add = 100
        initial_total = self.m.total_resources
        
        self.simulator.add_resources_randomly(resources_to_add)
        self.assertEqual(self.m.total_resources, initial_total + resources_to_add)
        # Further assertions could check if resources are distributed (non-zero for some nodes)
        # but exact distribution is random, so checking total is sufficient for this test.

    def test_add_resources_preferentially(self):
        resources_to_add = 100
        initial_total = self.m.total_resources
        
        self.simulator.add_resources_preferentially(resources_to_add)
        self.assertEqual(self.m.total_resources, initial_total + resources_to_add)
        # Similar to random, exact distribution is hard to test, but total should be correct.

    def test_add_resources_evenly(self):
        resources_to_add = 100
        initial_total = self.m.total_resources
        
        self.simulator.add_resources_evenly(resources_to_add)
        self.assertEqual(self.m.total_resources, initial_total + resources_to_add)
        
        # Check for even distribution (within 1 resource difference)
        distribution = self.simulator.get_resource_distribution()
        min_res = min(distribution)
        max_res = max(distribution)
        self.assertTrue(max_res - min_res <= 1)

if __name__ == '__main__':
    unittest.main()
