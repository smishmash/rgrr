from flask import Flask, request
import numpy.testing as npt
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from rgrr.server import app
from rgrr.simulation_results import get_simulation_results

class TestServerEndpoints(unittest.TestCase):
    def setUp(self):
        self.test_app = app.test_client()
        self.test_app.testing = True


    @patch('rgrr.simulation_results.get_simulation_results', MagicMock(return_value = [[10, 20, 30], [15, 25, 35]]))
    def test_get_distribution_existing_simulation(self):
        response = self.test_app.get('/simulations/123/distributions')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data, [[10, 20, 30], [15, 25, 35]])


    @patch('rgrr.simulation_results.get_simulation_results')
    @unittest.skip('ID not implemented.')
    def test_get_distribution_non_existing_simulation(self, mock_get_simulation_results):
        get_simulation_results.return_value = []
        response = self.test_app.get('/simulations/123/distributions')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['error'], 'Simulation 123 not found.')


    @patch('rgrr.simulation_results.get_simulation_results', MagicMock(return_value = [[10, 20, 30], [15, 25, 35]]))
    def test_get_histogram_existing_simulation(self):
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


    @patch('rgrr.simulation_results.get_simulation_results')
    @unittest.skip('ID not implemented.')
    def test_get_histogram_non_existing_simulation(self, mock_get_simulation_results):
        get_simulation_results.return_value = []
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
