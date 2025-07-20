from flask import Flask, jsonify
from .simulation_results import get_simulation_results

app = Flask(__name__)

@app.route('/simulations/<string:id>/distribution', methods=['GET'])
def get_distribution(id):
    distributions = get_simulation_results(id)
    if distributions:
        return jsonify(distributions)
    else:
        return jsonify({"error": "Simulation has not been run yet."}), 404
