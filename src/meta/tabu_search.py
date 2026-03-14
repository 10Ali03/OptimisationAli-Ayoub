import time
from collections import deque
from dataclasses import dataclass

from construction import build_solution_with_k_vehicles, generate_random_solution
from evaluate import evaluate_solution, lower_bound_vehicles
from neighbors import generate_neighbors


@dataclass
class TabuSearchResult:
    best_routes: list[list[int]]
    best_distance: float
    initial_distance: float
    iterations: int
    explored_neighbors: int
    accepted_moves: int
    runtime_seconds: float


def routes_signature(routes):
    return tuple(tuple(route) for route in routes)


def tabu_search(
    instance,
    initial_routes=None,
    k=None,
    seed=None,
    check_time_windows=False,
    operators=("relocate", "swap", "2opt"),
    max_iterations=200,
    tabu_tenure=25,
    max_neighbors=500,
):
    start_time = time.perf_counter()

    if initial_routes is None:
        initial_routes = generate_random_solution(
            instance,
            k=k,
            seed=seed,
            check_time_windows=check_time_windows,
        )
        if initial_routes is None and check_time_windows:
            target_k = lower_bound_vehicles(instance) if k is None else k
            initial_routes = build_solution_with_k_vehicles(
                instance,
                target_k,
                check_time_windows=True,
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

    tabu_queue = deque([routes_signature(current_routes)], maxlen=tabu_tenure)
    tabu_set = {routes_signature(current_routes)}

    explored_neighbors = 0
    accepted_moves = 0
    iterations_done = 0

    for iteration in range(max_iterations):
        neighbors = generate_neighbors(
            instance,
            current_routes,
            operators=operators,
            check_time_windows=check_time_windows,
        )
        if max_neighbors is not None:
            neighbors = neighbors[:max_neighbors]

        if not neighbors:
            iterations_done = iteration + 1
            break

        best_candidate = None
        best_candidate_distance = None

        for candidate in neighbors:
            explored_neighbors += 1
            candidate_distance = evaluate_solution(
                instance,
                candidate,
                check_time_windows=check_time_windows,
            )["distance"]
            signature = routes_signature(candidate)
            is_tabu = signature in tabu_set
            aspiration = candidate_distance < best_distance

            if is_tabu and not aspiration:
                continue

            if (
                best_candidate is None
                or candidate_distance < best_candidate_distance
            ):
                best_candidate = candidate
                best_candidate_distance = candidate_distance

        if best_candidate is None:
            iterations_done = iteration + 1
            break

        current_routes = [list(route) for route in best_candidate]
        current_distance = best_candidate_distance
        accepted_moves += 1

        signature = routes_signature(current_routes)
        if len(tabu_queue) == tabu_queue.maxlen:
            removed = tabu_queue.popleft()
            tabu_set.discard(removed)
        tabu_queue.append(signature)
        tabu_set.add(signature)

        if current_distance < best_distance:
            best_routes = [list(route) for route in current_routes]
            best_distance = current_distance

        iterations_done = iteration + 1

    runtime_seconds = time.perf_counter() - start_time
    return TabuSearchResult(
        best_routes=best_routes,
        best_distance=best_distance,
        initial_distance=evaluate_solution(
            instance,
            initial_routes,
            check_time_windows=check_time_windows,
        )["distance"],
        iterations=iterations_done,
        explored_neighbors=explored_neighbors,
        accepted_moves=accepted_moves,
        runtime_seconds=runtime_seconds,
    )
