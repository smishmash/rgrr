from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask import Flask, Response, request
import json
import numpy as np
import rgrr.simulation_store as sr
from rgrr.model import Model
from rgrr.simulator import MultiStepSimulator
from rgrr.operations import (
    RandomResourceDistribution,
    PreferentialResourceDistribution,
    UniformResourceDistribution,
    IncomeTaxCollectionOperation,
    RequiredExpenditureOperation,
)

app = Flask(__name__)

spec = APISpec(
    title="RGRR API",
    version="1.0.0",
    openapi_version="3.0.2",
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)


# Flask json encoder isn't customizable
class NumpyEncoder(json.JSONEncoder):
    """Special json encoder for numpy types"""

    def default(self, o):
        if isinstance(o, np.integer):
            return int(o)
        elif isinstance(o, np.floating):
            return float(o)
        elif isinstance(o, np.ndarray):
            return o.tolist()
        return json.JSONEncoder.default(self, o)


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
    simulation = sr.get_simulation(id)
    if not simulation:
        return jsonify({"error": f"Simulation {id} not found."}), 404
    distributions = simulation.distributions
    if distributions:
        return jsonify(distributions)
    else:
        return jsonify({"error": f"Simulation {id} has not run."}), 400


@app.route('/simulations/<string:id>/histograms', methods=['GET'])
def get_histogram(id):
    simulation = sr.get_simulation(id)
    if not simulation:
        return jsonify({"error": f"Simulation {id} not found."}), 404
    distributions = simulation.distributions
    if not distributions:
        return jsonify({"error": f"Simulation {id} has not run."}), 400
    hist_min = min(min(d) for d in distributions)
    hist_max = max(max(d) for d in distributions)
    bin_count = 20              # Make this dynamic?
    result = []
    bin_edges = [] # Initialize bin_edges
    # bin edges will be the same for each histogram
    for d in distributions:
        counts, bin_edges = np.histogram(d, bins=bin_count, range=(hist_min, hist_max), density=True)
        result.append(list(counts))
    return jsonify({
        'bin_edges': list(bin_edges),
        'epoch_distributions': result
        })


@app.route('/simulations', methods=['POST'])
def create_simulation():
    """Create a new simulation
    ---
    post:
      summary: Create a new simulation
      description: Create a new simulation with specified parameters
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                nodes:
                  type: integer
                  description: Number of nodes in the simulation
                epochs:
                  type: integer
                  description: Number of epochs to run
                resources_per_node:
                  type: integer
                  description: Initial resources per node
                seed:
                  type: integer
                  description: Random seed for reproducibility
                operations:
                  type: array
                  items:
                    type: object
                    properties:
                      type:
                        type: string
                        description: Type of operation (random, preferential, uniform, tax, expenditure)
                      resources_added:
                        type: integer
                        description: Resources to add (for distribution operations)
                      tax_rate:
                        type: number
                        description: Tax rate (for tax operation)
                      expenditure:
                        type: integer
                        description: Expenditure amount (for expenditure operation)
                  description: List of operations to perform
              required:
                - nodes
                - epochs
                - resources_per_node
                - operations
      responses:
        '201':
          description: Simulation created successfully
        '400':
          description: Invalid request parameters
    """
    try:
        data = request.get_json()

        # Validate required parameters
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        nodes = data.get('nodes')
        epochs = data.get('epochs')
        resources_per_node = data.get('resources_per_node')
        seed = data.get('seed')
        operations_data = data.get('operations', [])

        if None in (nodes, epochs, resources_per_node, operations_data):
            return jsonify({"error": "Missing required parameters: nodes, epochs, resources_per_node, operations"}), 400

        # Parse operations
        operations = []
        for op_data in operations_data:
            op_type = op_data.get('type')
            if op_type == 'random':
                operation = RandomResourceDistribution(op_data.get('resources_added', 0))
            elif op_type == 'preferential':
                operation = PreferentialResourceDistribution(op_data.get('resources_added', 0))
            elif op_type == 'uniform':
                operation = UniformResourceDistribution(op_data.get('resources_added', 0))
            elif op_type == 'tax':
                operation = IncomeTaxCollectionOperation(op_data.get('tax_rate', 0.0))
            elif op_type == 'expenditure':
                operation = RequiredExpenditureOperation(op_data.get('expenditure', 0))
            else:
                # This case should ideally not happen if create_simulation validated correctly
                return jsonify({"error": f"Unknown operation type: {op_type}"}), 400
            operations.append(operation)

        # Create simulation
        model = Model(nodes, resources_per_node)
        simulator = MultiStepSimulator(model=model, epochs=epochs, seed=seed, operations=operations)

        # Store the simulation configuration for later execution
        import uuid
        simulation_id = str(uuid.uuid4())
        sr.store_simulation(simulation_id, simulator)

        return jsonify({
            "id": simulation_id,
            "status": "created"
        }), 201

    except Exception as e:
        return jsonify({"error": f"Failed to create simulation: {str(e)}"}), 500


@app.route('/simulations/<string:id>/run', methods=['POST'])
def run_simulation(id):
    """Run a previously created simulation
    ---
    post:
      summary: Run a simulation
      description: Run a simulation identified by its ID
      parameters:
        - in: path
          name: id
          schema:
            type: string
          required: true
          description: Simulation ID to run
      responses:
        '200':
          description: Simulation run successfully
        '404':
          description: Simulation ID not found
        '500':
          description: Failed to run simulation
    """
    try:
        simulator = sr.get_simulation(id)
        simulator.run()
        return jsonify({
            "id": id,
            "status": "completed"
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed to run simulation {id}: {str(e)}"}), 500


@app.route('/simulations', methods=['GET'])
def list_simulations():
    """
    ---
    get:
      summary: Get a list of all simulation IDs
      responses:
        200:
          description: A list of simulation IDs
          content:
            application/json:
              schema:
                type: array
                items:
                  type: string
    """
    simulation_ids = sr.list_simulation_ids()
    return jsonify(simulation_ids)


@app.route("/simulations/<string:id>", methods=["GET"])
def get_simulation_details(id):
    """Get simulation details
    ---
    get:
      summary: Get simulation details
      description: Get detailed information about a specific simulation
      parameters:
      - in: path
        name: id
        schema:
          type: string
        required: true
        description: Simulation ID
      responses:
        '200':
          description: Simulation details
        '404':
          description: Simulation not found
    """
    simulation = sr.get_simulation(id)
    if not simulation:
        return jsonify({"error": f"Simulation {id} not found."}), 404

    operations_data = []
    for op in simulation.operations:
        op_type_str = ""
        if isinstance(op, RandomResourceDistribution):
            op_type_str = "random"
        elif isinstance(op, PreferentialResourceDistribution):
            op_type_str = "preferential"
        elif isinstance(op, UniformResourceDistribution):
            op_type_str = "uniform"
        elif isinstance(op, IncomeTaxCollectionOperation):
            op_type_str = "tax"
        elif isinstance(op, RequiredExpenditureOperation):
            op_type_str = "expenditure"

        op_dict = {
            "type": op_type_str,
            "resources_added": 0,
            "tax_rate": 0.0,
            "expenditure": 0,
        }

        if isinstance(
            op,
            (
                RandomResourceDistribution,
                PreferentialResourceDistribution,
                UniformResourceDistribution,
            ),
        ):
            op_dict["resources_added"] = op.resources_added
            del op_dict["tax_rate"]
            del op_dict["expenditure"]
        elif isinstance(op, IncomeTaxCollectionOperation):
            op_dict["tax_rate"] = op.tax_rate
            del op_dict["resources_added"]
            del op_dict["expenditure"]
        elif isinstance(op, RequiredExpenditureOperation):
            op_dict["expenditure"] = op.expenditure
            del op_dict["resources_added"]
            del op_dict["tax_rate"]
        operations_data.append(op_dict)

    details = {
        "id": id,
        "nodes": simulation.model.Nodes.__len__(),
        "epochs": simulation.epochs,
        "resources_per_node": simulation.model.Nodes[0].resources
        if simulation.model.Nodes
        else 0,
        "seed": simulation.seed,
        "operations": operations_data,
    }
    return jsonify(details)


with app.test_request_context():
    spec.path(view=get_distribution)
    spec.path(view=get_histogram)
    spec.path(view=create_simulation)
    spec.path(view=run_simulation)
    spec.path(view=list_simulations)
    spec.path(view=get_simulation_details)


@app.route('/swagger.json')
def swagger_json():
    return jsonify(spec.to_dict())
