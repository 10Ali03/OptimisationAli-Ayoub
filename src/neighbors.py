import random

from evaluate import evaluate_solution


def clone_routes(routes):
    return [list(route) for route in routes]


def cleanup_empty_routes(routes):
    return [route for route in routes if route]


def feasible_solution(instance, routes, check_time_windows=False):
    return evaluate_solution(
        instance,
        routes,
        check_time_windows=check_time_windows,
    )["feasible"]


def relocate_neighbors(instance, routes, check_time_windows=False):
    neighbors = []

    for source_index, source_route in enumerate(routes):
        for client_pos, client_id in enumerate(source_route):
            for target_index in range(len(routes)):
                for insert_pos in range(len(routes[target_index]) + 1):
                    if source_index == target_index and (
                        insert_pos == client_pos or insert_pos == client_pos + 1
                    ):
                        continue

                    candidate = clone_routes(routes)
                    moved_client = candidate[source_index].pop(client_pos)

                    adjusted_insert_pos = insert_pos
                    if source_index == target_index and insert_pos > client_pos:
                        adjusted_insert_pos -= 1

                    candidate[target_index].insert(adjusted_insert_pos, moved_client)
                    candidate = cleanup_empty_routes(candidate)

                    if feasible_solution(
                        instance,
                        candidate,
                        check_time_windows=check_time_windows,
                    ):
                        neighbors.append(candidate)

    return neighbors


def swap_neighbors(instance, routes, check_time_windows=False):
    neighbors = []

    for route_i, first_route in enumerate(routes):
        for pos_i, _ in enumerate(first_route):
            for route_j in range(route_i, len(routes)):
                second_route = routes[route_j]
                start_pos_j = pos_i + 1 if route_i == route_j else 0

                for pos_j in range(start_pos_j, len(second_route)):
                    candidate = clone_routes(routes)
                    candidate[route_i][pos_i], candidate[route_j][pos_j] = (
                        candidate[route_j][pos_j],
                        candidate[route_i][pos_i],
                    )

                    if feasible_solution(
                        instance,
                        candidate,
                        check_time_windows=check_time_windows,
                    ):
                        neighbors.append(candidate)

    return neighbors


def two_opt_neighbors(instance, routes, check_time_windows=False):
    neighbors = []

    for route_index, route in enumerate(routes):
        if len(route) < 3:
            continue

        for start in range(len(route) - 1):
            for end in range(start + 1, len(route)):
                candidate = clone_routes(routes)
                candidate[route_index] = (
                    candidate[route_index][:start]
                    + list(reversed(candidate[route_index][start : end + 1]))
                    + candidate[route_index][end + 1 :]
                )

                if feasible_solution(
                    instance,
                    candidate,
                    check_time_windows=check_time_windows,
                ):
                    neighbors.append(candidate)

    return neighbors


def unique_neighbors(neighbors):
    seen = set()
    unique = []

    for candidate in neighbors:
        key = tuple(tuple(route) for route in candidate)
        if key in seen:
            continue
        seen.add(key)
        unique.append(candidate)

    return unique


def random_relocate_neighbor(
    instance,
    routes,
    rng=None,
    check_time_windows=False,
    max_attempts=100,
):
    rng = rng or random.Random()

    non_empty_route_indices = [index for index, route in enumerate(routes) if route]
    if not non_empty_route_indices:
        return None

    for _ in range(max_attempts):
        source_index = rng.choice(non_empty_route_indices)
        source_route = routes[source_index]
        client_pos = rng.randrange(len(source_route))
        target_index = rng.randrange(len(routes))
        insert_pos = rng.randrange(len(routes[target_index]) + 1)

        if source_index == target_index and (
            insert_pos == client_pos or insert_pos == client_pos + 1
        ):
            continue

        candidate = clone_routes(routes)
        moved_client = candidate[source_index].pop(client_pos)

        adjusted_insert_pos = insert_pos
        if source_index == target_index and insert_pos > client_pos:
            adjusted_insert_pos -= 1

        candidate[target_index].insert(adjusted_insert_pos, moved_client)
        candidate = cleanup_empty_routes(candidate)

        if feasible_solution(instance, candidate, check_time_windows=check_time_windows):
            return candidate

    return None


def random_swap_neighbor(
    instance,
    routes,
    rng=None,
    check_time_windows=False,
    max_attempts=100,
):
    rng = rng or random.Random()

    indexed_clients = [
        (route_index, pos)
        for route_index, route in enumerate(routes)
        for pos in range(len(route))
    ]
    if len(indexed_clients) < 2:
        return None

    for _ in range(max_attempts):
        (route_i, pos_i), (route_j, pos_j) = rng.sample(indexed_clients, 2)
        candidate = clone_routes(routes)
        candidate[route_i][pos_i], candidate[route_j][pos_j] = (
            candidate[route_j][pos_j],
            candidate[route_i][pos_i],
        )

        if feasible_solution(instance, candidate, check_time_windows=check_time_windows):
            return candidate

    return None


def random_two_opt_neighbor(
    instance,
    routes,
    rng=None,
    check_time_windows=False,
    max_attempts=100,
):
    rng = rng or random.Random()

    eligible_routes = [
        route_index for route_index, route in enumerate(routes) if len(route) >= 3
    ]
    if not eligible_routes:
        return None

    for _ in range(max_attempts):
        route_index = rng.choice(eligible_routes)
        route = routes[route_index]
        start, end = sorted(rng.sample(range(len(route)), 2))
        if start == end:
            continue

        candidate = clone_routes(routes)
        candidate[route_index] = (
            candidate[route_index][:start]
            + list(reversed(candidate[route_index][start : end + 1]))
            + candidate[route_index][end + 1 :]
        )

        if feasible_solution(instance, candidate, check_time_windows=check_time_windows):
            return candidate

    return None


def random_neighbor(
    instance,
    routes,
    operators=None,
    rng=None,
    check_time_windows=False,
    max_attempts_per_operator=100,
):
    rng = rng or random.Random()
    operators = list(operators or ("relocate", "swap", "2opt"))
    rng.shuffle(operators)

    for operator in operators:
        if operator == "relocate":
            candidate = random_relocate_neighbor(
                instance,
                routes,
                rng=rng,
                check_time_windows=check_time_windows,
                max_attempts=max_attempts_per_operator,
            )
        elif operator == "swap":
            candidate = random_swap_neighbor(
                instance,
                routes,
                rng=rng,
                check_time_windows=check_time_windows,
                max_attempts=max_attempts_per_operator,
            )
        elif operator == "2opt":
            candidate = random_two_opt_neighbor(
                instance,
                routes,
                rng=rng,
                check_time_windows=check_time_windows,
                max_attempts=max_attempts_per_operator,
            )
        else:
            raise ValueError(f"Opérateur inconnu : {operator}")

        if candidate is not None:
            return candidate

    return None


def generate_neighbors(
    instance,
    routes,
    operators=None,
    check_time_windows=False,
):
    operators = operators or ("relocate", "swap", "2opt")
    neighbors = []

    for operator in operators:
        if operator == "relocate":
            neighbors.extend(
                relocate_neighbors(
                    instance,
                    routes,
                    check_time_windows=check_time_windows,
                )
            )
        elif operator == "swap":
            neighbors.extend(
                swap_neighbors(
                    instance,
                    routes,
                    check_time_windows=check_time_windows,
                )
            )
        elif operator == "2opt":
            neighbors.extend(
                two_opt_neighbors(
                    instance,
                    routes,
                    check_time_windows=check_time_windows,
                )
            )
        else:
            raise ValueError(f"Opérateur inconnu : {operator}")

    return unique_neighbors(neighbors)


def generate_sampled_neighbors(
    instance,
    routes,
    operators=None,
    rng=None,
    check_time_windows=False,
    max_neighbors=100,
    max_attempts=None,
):
    rng = rng or random.Random()
    if max_neighbors is None:
        return generate_neighbors(
            instance,
            routes,
            operators=operators,
            check_time_windows=check_time_windows,
        )

    max_attempts = max_attempts or max_neighbors * 10
    sampled = []
    seen = set()

    for _ in range(max_attempts):
        candidate = random_neighbor(
            instance,
            routes,
            operators=operators,
            rng=rng,
            check_time_windows=check_time_windows,
        )
        if candidate is None:
            continue

        key = tuple(tuple(route) for route in candidate)
        if key in seen:
            continue

        seen.add(key)
        sampled.append(candidate)
        if len(sampled) >= max_neighbors:
            break

    return sampled


def best_neighbor(
    instance,
    routes,
    operators=None,
    check_time_windows=False,
):
    neighbors = generate_neighbors(
        instance,
        routes,
        operators=operators,
        check_time_windows=check_time_windows,
    )

    if not neighbors:
        return None, None

    best_routes = min(
        neighbors,
        key=lambda candidate: evaluate_solution(
            instance,
            candidate,
            check_time_windows=check_time_windows,
        )["distance"],
    )

    best_distance = evaluate_solution(
        instance,
        best_routes,
        check_time_windows=check_time_windows,
    )["distance"]
    return best_routes, best_distance
