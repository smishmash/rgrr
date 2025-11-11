from typing import List
from rgrr.simulator import MultiStepSimulator

simulations = {}

def store_simulation(id: str, simulator: MultiStepSimulator):
    global simulations
    simulations[id] = simulator

def get_simulation(id: str) -> MultiStepSimulator:
    global simulations
    return simulations.get(id)


def list_simulation_ids() -> List[str]:
    """
    Returns a list of all simulation IDs currently stored.
    """
    return list(simulations.keys())
