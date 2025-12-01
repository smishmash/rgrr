from flask import Flask, request
import numpy.testing as npt
import os
import sys
import unittest
from unittest.mock import patch, Mock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from rgrr.server import app
import rgrr.simulation_store as sr


class TestServerEndpoints(unittest.TestCase):
    def setUp(self):
        self.test_app = app.test_client()
        sr.simulations.clear()

    def tearDown(self):
        sr.simulations.clear()


    @patch('rgrr.simulation_store.get_simulation')
    def test_get_distribution_existing_simulation(self, mock_get_simulation):
        sim_mock = Mock()
        sim_mock.distributions = [[10, 20, 30], [15, 25, 35]]
        mock_get_simulation.return_value = sim_mock
        response = self.test_app.get('/simulations/123/distributions')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data, [[10, 20, 30], [15, 25, 35]])


    @patch('rgrr.simulation_store.get_simulation')
    def test_get_distribution_non_existing_simulation(self, mock_get_simulation):
        mock_get_simulation.return_value = None
        response = self.test_app.get('/simulations/123/distributions')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['error'], 'Simulation 123 not found.')


    @patch('rgrr.simulation_store.get_simulation')
    def test_get_histogram_existing_simulation(self, mock_get_simulation):
        sim_mock = Mock()
        sim_mock.distributions = [[10, 20, 30], [15, 25, 35]]
        mock_get_simulation.return_value = sim_mock
        response = self.test_app.get('/simulations/123/histograms')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.keys(), {'bin_edges', 'epoch_distributions'})
        exp_bin_edges = [10.0, 11.25, 12.5, 13.75, 15.0, 16.25, 17.5, 18.75, 20.0, 21.25, 22.5, 23.75, 25.0, 26.25, 27.5, 28.75, 30.0, 31.25, 32.5, 33.75, 35.0]
        npt.assert_almost_equal(data['bin_edges'], exp_bin_edges)
        exp_epoch_dists = [
                [0.26666666666666666, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.26666666666666666, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.26666666666666666, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.26666666666666666, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.26666666666666666, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.26666666666666666]
            ]
        npt.assert_almost_equal(data['epoch_distributions'], exp_epoch_dists)


    @patch('rgrr.simulation_store.get_simulation')
    def test_get_histogram_non_existing_simulation(self, mock_get_simulation):
        mock_get_simulation.return_value = None
        response = self.test_app.get('/simulations/123/histograms')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['error'], 'Simulation 123 not found.')


    def test_swagger_json(self):
        response = self.test_app.get('/swagger.json')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('openapi', data)
        self.assertEqual(data['openapi'], '3.0.2')

    def test_create_run_and_fetch_simulation(self):
        # 1. Create a simulation
        simulation_config = {
            "nodes": 10,
            "epochs": 5,
            "resources_per_node": 1,
            "operations": [{"type": "random", "resources_added": 5}]
        }
        create_response = self.test_app.post('/simulations', json=simulation_config)
        self.assertEqual(create_response.status_code, 201)
        create_data = create_response.get_json()
        simulation_id = create_data['id']
        self.assertIsNotNone(simulation_id)
        self.assertEqual(create_data['status'], 'created')

        # 2. Run the simulation
        run_response = self.test_app.post(f'/simulations/{simulation_id}/run')
        self.assertEqual(run_response.status_code, 200)
        run_data = run_response.get_json()
        self.assertEqual(run_data['id'], simulation_id)
        self.assertEqual(run_data['status'], 'completed')

        # 3. Fetch simulation distribution
        dist_response = self.test_app.get(f'/simulations/{simulation_id}/distributions')
        self.assertEqual(dist_response.status_code, 200)
        dist_data = dist_response.get_json()
        self.assertIsInstance(dist_data, list)
        self.assertGreater(len(dist_data), 0)

        # 4. Fetch simulation histogram
        hist_response = self.test_app.get(f'/simulations/{simulation_id}/histograms')
        self.assertEqual(hist_response.status_code, 200)
        hist_data = hist_response.get_json()
        self.assertIn('bin_edges', hist_data)
        self.assertIn('epoch_distributions', hist_data)
        self.assertIsInstance(hist_data['bin_edges'], list)
        self.assertIsInstance(hist_data['epoch_distributions'], list)
        self.assertGreater(len(hist_data['epoch_distributions']), 0)

    def test_list_simulations_empty(self):
        """
        Test that GET /simulations returns an empty list when no simulations exist.
        """
        response = self.test_app.get('/simulations')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_list_simulations_with_data(self):
        """
        Test that GET /simulations returns a list of simulation IDs when simulations exist.
        """
        # Create a first simulation
        response1 = self.test_app.post('/simulations', json={
            "nodes": 10,
            "epochs": 1,
            "resources_per_node": 10,
            "operations": [{"type": "random", "resources_added": 100}]
        })
        self.assertEqual(response1.status_code, 201)
        sim_id1 = response1.get_json()['id']

        # Create a second simulation
        response2 = self.test_app.post('/simulations', json={
            "nodes": 5,
            "epochs": 2,
            "resources_per_node": 5,
            "operations": [{"type": "uniform", "resources_added": 50}]
        })
        self.assertEqual(response2.status_code, 201)
        sim_id2 = response2.get_json()['id']

        list_response = self.test_app.get('/simulations')
        self.assertEqual(list_response.status_code, 200)
        retrieved_ids = list_response.get_json()
        self.assertIsInstance(retrieved_ids, list)
        self.assertIn(sim_id1, retrieved_ids)
        self.assertIn(sim_id2, retrieved_ids)
        self.assertEqual(len(retrieved_ids), 2)

    def test_get_simulation_details(self):
        """Test that GET /simulations/<id> returns correct simulation details."""
        # 1. Create a simulation with various operations
        simulation_config = {
            "nodes": 20,
            "epochs": 10,
            "resources_per_node": 5,
            "seed": 123,
            "operations": [
                {"type": "random", "resources_added": 10},
                {"type": "preferential", "resources_added": 20},
                {"type": "uniform", "resources_added": 30},
                {"type": "tax", "tax_rate": 0.1},
                {"type": "expenditure", "expenditure": 2},
            ],
        }
        create_response = self.test_app.post("/simulations", json=simulation_config)
        self.assertEqual(create_response.status_code, 201)
        simulation_id = create_response.get_json()["id"]

        # 2. Fetch simulation details
        details_response = self.test_app.get(f"/simulations/{simulation_id}")
        self.assertEqual(details_response.status_code, 200)
        details_data = details_response.get_json()

        # 3. Assert the returned details are correct
        self.assertEqual(details_data["id"], simulation_id)
        self.assertEqual(details_data["nodes"], simulation_config["nodes"])
        self.assertEqual(details_data["epochs"], simulation_config["epochs"])
        self.assertEqual(
            details_data["resources_per_node"], simulation_config["resources_per_node"]
        )
        self.assertEqual(details_data["seed"], simulation_config["seed"])

        # Assert operations
        self.assertEqual(
            len(details_data["operations"]), len(simulation_config["operations"])
        )
        for i, op_data in enumerate(details_data["operations"]):
            expected_op = simulation_config["operations"][i]
            self.assertEqual(op_data["type"], expected_op["type"])
            if "resources_added" in expected_op:
                self.assertEqual(
                    op_data["resources_added"], expected_op["resources_added"]
                )
            if "tax_rate" in expected_op:
                self.assertEqual(op_data["tax_rate"], expected_op["tax_rate"])
            if "expenditure" in expected_op:
                self.assertEqual(op_data["expenditure"], expected_op["expenditure"])


    def test_details_of_missing_simulation_return_error(self):
        # Test for non-existent simulation
        non_existent_id = "non-existent-id"
        not_found_response = self.test_app.get(f"/simulations/{non_existent_id}")
        self.assertEqual(not_found_response.status_code, 404)
        self.assertEqual(
            not_found_response.get_json()["error"],
            f"Simulation {non_existent_id} not found.",
        )

    def test_create_and_fetch_simulation_json_match(self):
        """Test that the JSON used to create a simulation matches the fetched details."""
        initial_config = {
            "nodes": 15,
            "epochs": 7,
            "resources_per_node": 3,
            "seed": 456,
            "operations": [
                {"type": "random", "resources_added": 10},
                {"type": "tax", "tax_rate": 0.05},
                {"type": "expenditure", "expenditure": 1},
            ],
        }

        # Create the simulation
        create_response = self.test_app.post("/simulations", json=initial_config)
        self.assertEqual(create_response.status_code, 201)
        simulation_id = create_response.get_json()["id"]

        # Fetch the simulation details
        details_response = self.test_app.get(f"/simulations/{simulation_id}")
        self.assertEqual(details_response.status_code, 200)
        fetched_details = details_response.get_json()

        # Prepare expected details for comparison
        expected_details = {
            "id": simulation_id,
            "nodes": initial_config["nodes"],
            "epochs": initial_config["epochs"],
            "resources_per_node": initial_config["resources_per_node"],
            "seed": initial_config["seed"],
            "operations": [],
        }

        for op in initial_config["operations"]:
            op_copy = op.copy()
            if op_copy["type"] == "random":
                op_copy["type"] = "random"
            elif op_copy["type"] == "tax":
                op_copy["type"] = "tax"
            elif op_copy["type"] == "expenditure":
                op_copy["type"] = "expenditure"
            expected_details["operations"].append(op_copy)

        # Compare fetched details with expected details
        self.assertDictEqual(fetched_details, expected_details)
