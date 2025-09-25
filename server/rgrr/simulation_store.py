from typing import List

simulations = {}

def store_simulation(id: str, simulator: "MultiStepSimulator"):
    global simulations
    simulations[id] = simulator

def get_simulation(id: str) -> "MultiStepSimulator":
    global simulations
    return simulations.get(id)
