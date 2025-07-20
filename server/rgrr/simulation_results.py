from typing import List

simulation_results = []

def store_simulation_results(id: str, results):
    global simulation_results
    # TODO Use id
    simulation_results = results

def get_simulation_results(id: str) -> List[List[int]]:
    global simulation_results
    # TODO Use id
    return simulation_results
