from flask import Flask, jsonify
from .simulation_results import get_simulation_results
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

app = Flask(__name__)

spec = APISpec(
    title="RGRR API",
    version="1.0.0",
    openapi_version="3.0.2",
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)

@app.route('/simulations/<string:id>/distribution', methods=['GET'])
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
    distributions = get_simulation_results(id)
    if distributions:
        return jsonify(distributions)
    else:
        return jsonify({"error": "Simulation has not been run yet."}), 404

with app.test_request_context():
    spec.path(view=get_distribution)

@app.route('/swagger.json')
def swagger_json():
    return jsonify(spec.to_dict())
