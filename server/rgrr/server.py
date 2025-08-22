from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask import Flask, Response
import json
import numpy as np
from rgrr.simulation_results import get_simulation_results
import rgrr.simulation_results as sr

app = Flask(__name__)

spec = APISpec(
    title="RGRR API",
    version="1.0.0",
    openapi_version="3.0.2",
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)


# Flask json encoder isn't customizable
class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def jsonify(value):
    return Response(json.dumps(value, cls=NumpyEncoder), mimetype='application/json')


@app.route('/simulations/<string:id>/distributions', methods=['GET'])
def get_distribution(id):
    """Get simulation distribution
    ---
    get:
      summary: Get simulation distribution
      description: Get simulation distribution
      parameters:
      - in: path
        name: id
        schema:
          type: string
        required: true
        description: Simulation ID
      responses:
        '200':
          description: Simulation distribution
        '404':
            description: Simulation not found
    """
    distributions = sr.get_simulation_results(id)
    if distributions:
        return jsonify(distributions)
    else:
        return jsonify({"error": f"Simulation {id} not found."}), 404


@app.route('/simulations/<string:id>/histograms', methods=['GET'])
def get_histogram(id):
    distributions = sr.get_simulation_results(id)
    if not distributions:
        return jsonify({"error": f"Simulation {id} not found."}), 404
    hist_min = min(min(d) for d in distributions)
    hist_max = max(max(d) for d in distributions)
    bin_count = 20              # Make this dynamic?
    result = []
    # bin edges will be the same for each histogram
    for d in distributions:
        counts, bin_edges = np.histogram(d, bins=bin_count, range=(hist_min, hist_max), density=True)
        result.append(list(counts))
    return jsonify({
        'bin_edges': list(bin_edges),
        'epoch_distributions': result
        })


with app.test_request_context():
    spec.path(view=get_distribution)

@app.route('/swagger.json')
def swagger_json():
    return jsonify(spec.to_dict())
