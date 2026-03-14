import math
import random
import time
from dataclasses import dataclass

from construction import generate_random_solution
from evaluate import evaluate_solution
from neighbors import random_neighbor


@dataclass
class SimulatedAnnealingResult:
    best_routes: list[list[int]]
    best_distance: float
    initial_distance: float
    iterations: int
    accepted_moves: int
    improving_moves: int
    temperature_final: float
    runtime_seconds: float


def simulated_annealing(
    instance,
    initial_routes=None,
    k=None,
    seed=None,
    check_time_windows=False,
    operators=("relocate", "swap", "2opt"),
    max_iterations=2000,
    initial_temperature=100.0,
    cooling_rate=0.995,
    min_temperature=1e-3,
    neighbor_attempts=100,
):
    rng = random.Random(seed)
    start_time = time.perf_counter()

    if initial_routes is None:
        initial_routes = generate_random_solution(
            instance,
            k=k,
            seed=seed,
            check_time_windows=check_time_windows,
        )
        if initial_routes is None:
            raise ValueError("Impossible de générer une solution initiale faisable.")

    current_routes = [list(route) for route in initial_routes]
    current_distance = evaluate_solution(
        instance,
        current_routes,
        check_time_windows=check_time_windows,
    )["distance"]

    best_routes = [list(route) for route in current_routes]
    best_distance = current_distance
    temperature = initial_temperature
    accepted_moves = 0
    improving_moves = 0
    iterations_done = 0

    for iteration in range(max_iterations):
        if temperature < min_temperature:
            break

        candidate_routes = random_neighbor(
            instance,
            current_routes,
            operators=operators,
            rng=rng,
            check_time_windows=check_time_windows,
            max_attempts_per_operator=neighbor_attempts,
        )

        if candidate_routes is None:
            temperature *= cooling_rate
            iterations_done = iteration + 1
            continue

        candidate_distance = evaluate_solution(
            instance,
            candidate_routes,
            check_time_windows=check_time_windows,
        )["distance"]
        delta = candidate_distance - current_distance

        accept_move = False
        if delta <= 0:
            accept_move = True
            if delta < 0:
                improving_moves += 1
        else:
            acceptance_probability = math.exp(-delta / temperature)
            if rng.random() < acceptance_probability:
                accept_move = True

        if accept_move:
            current_routes = [list(route) for route in candidate_routes]
            current_distance = candidate_distance
            accepted_moves += 1

            if current_distance < best_distance:
                best_routes = [list(route) for route in current_routes]
                best_distance = current_distance

        temperature *= cooling_rate
        iterations_done = iteration + 1

    runtime_seconds = time.perf_counter() - start_time
    return SimulatedAnnealingResult(
        best_routes=best_routes,
        best_distance=best_distance,
        initial_distance=evaluate_solution(
            instance,
            initial_routes,
            check_time_windows=check_time_windows,
        )["distance"],
        iterations=iterations_done,
        accepted_moves=accepted_moves,
        improving_moves=improving_moves,
        temperature_final=temperature,
        runtime_seconds=runtime_seconds,
    )
