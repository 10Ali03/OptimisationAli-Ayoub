import random

from evaluate import (
    distance_between_clients,
    distance_depot_to_client,
    is_route_feasible,
    lower_bound_vehicles,
    route_load,
    solution_distance,
)


def choose_seeds(instance, k, unserved):
    """
    Choisit les k clients les plus éloignés du dépôt comme graines.
    """
    ordered = sorted(
        unserved,
        key=lambda cid: distance_depot_to_client(instance, cid),
        reverse=True
    )
    return ordered[:k]


def choose_time_window_seeds(instance, k, unserved):
    """
    Choisit comme graines les clients les plus urgents au sens de leur due_time.
    """
    ordered = sorted(
        unserved,
        key=lambda cid: (instance.clients[cid].due_time, instance.clients[cid].ready_time),
    )
    return ordered[:k]


def insertion_cost(instance, route, client_id, position):
    candidate_route = route[:position] + [client_id] + route[position:]
    return solution_distance(instance, [candidate_route]) - solution_distance(instance, [route])


def feasible_insertion_positions(
    instance,
    route,
    client_id,
    check_time_windows=False,
):
    positions = []

    for position in range(len(route) + 1):
        candidate_route = route[:position] + [client_id] + route[position:]
        if is_route_feasible(
            instance,
            candidate_route,
            check_time_windows=check_time_windows,
        ):
            positions.append(position)

    return positions


def best_feasible_insertion(instance, routes, unserved, check_time_windows=False):
    best_move = None
    best_cost = float("inf")

    for client_id in unserved:
        for route_index, route in enumerate(routes):
            for position in feasible_insertion_positions(
                instance,
                route,
                client_id,
                check_time_windows=check_time_windows,
            ):
                cost = insertion_cost(instance, route, client_id, position)
                if cost < best_cost:
                    best_cost = cost
                    best_move = (client_id, route_index, position)

    return best_move


def random_feasible_insertion(instance, routes, unserved, rng, check_time_windows=False):
    clients = list(unserved)
    rng.shuffle(clients)
    route_indices = list(range(len(routes)))
    rng.shuffle(route_indices)

    for client_id in clients:
        candidate_moves = []
        for route_index in route_indices:
            positions = feasible_insertion_positions(
                instance,
                routes[route_index],
                client_id,
                check_time_windows=check_time_windows,
            )
            for position in positions:
                candidate_moves.append((client_id, route_index, position))

        if candidate_moves:
            return rng.choice(candidate_moves)

    return None


def randomized_best_feasible_insertion(
    instance,
    routes,
    unserved,
    rng,
    check_time_windows=False,
    candidate_pool_size=8,
):
    candidate_moves = []

    for client_id in unserved:
        client = instance.clients[client_id]
        for route_index, route in enumerate(routes):
            positions = feasible_insertion_positions(
                instance,
                route,
                client_id,
                check_time_windows=check_time_windows,
            )
            for position in positions:
                cost = insertion_cost(instance, route, client_id, position)
                candidate_moves.append(
                    (
                        cost,
                        client.due_time,
                        len(route),
                        client_id,
                        route_index,
                        position,
                    )
                )

    if not candidate_moves:
        return None

    candidate_moves.sort()
    restricted = candidate_moves[:candidate_pool_size]
    _, _, _, client_id, route_index, position = rng.choice(restricted)
    return client_id, route_index, position


def nearest_feasible_client(instance, route, unserved, check_time_windows=False):
    """
    Retourne le client admissible le plus proche du dernier sommet de la route
    (ou du dépôt si la route est vide).
    """
    best_client = None
    best_distance = float("inf")

    if not route:
        for cid in unserved:
            candidate_route = route + [cid]
            if is_route_feasible(
                instance,
                candidate_route,
                check_time_windows=check_time_windows,
            ):
                d = distance_depot_to_client(instance, cid)
                if d < best_distance:
                    best_distance = d
                    best_client = cid
    else:
        last_client = route[-1]
        for cid in unserved:
            candidate_route = route + [cid]
            if is_route_feasible(
                instance,
                candidate_route,
                check_time_windows=check_time_windows,
            ):
                d = distance_between_clients(instance, last_client, cid)
                if d < best_distance:
                    best_distance = d
                    best_client = cid

    return best_client


def admissible_clients(instance, route, unserved, check_time_windows=False):
    """
    Retourne les clients pouvant être ajoutés en fin de tournée sans violer
    les contraintes activées.
    """
    feasible_clients = []

    for client_id in unserved:
        candidate_route = route + [client_id]
        if is_route_feasible(
            instance,
            candidate_route,
            check_time_windows=check_time_windows,
        ):
            feasible_clients.append(client_id)

    return feasible_clients


def build_random_solution_with_k_vehicles(
    instance,
    k,
    rng=None,
    check_time_windows=False,
):
    """
    Construit aléatoirement une solution avec exactement k tournées.
    Retourne None si la construction échoue.
    """
    if k <= 0:
        return None

    rng = rng or random.Random()
    unserved = set(instance.clients.keys())
    routes = [[] for _ in range(k)]

    if check_time_windows:
        seed_route_indices = list(range(k))
        rng.shuffle(seed_route_indices)
        seed_candidates = choose_time_window_seeds(instance, min(k, len(unserved)), list(unserved))

        for route_index, client_id in zip(seed_route_indices, seed_candidates):
            candidate_route = [client_id]
            if not is_route_feasible(
                instance,
                candidate_route,
                check_time_windows=True,
            ):
                continue
            routes[route_index].append(client_id)
            unserved.remove(client_id)

        while unserved:
            move = randomized_best_feasible_insertion(
                instance,
                routes,
                unserved,
                rng,
                check_time_windows=True,
            )
            if move is None:
                move = best_feasible_insertion(
                    instance,
                    routes,
                    unserved,
                    check_time_windows=True,
                )
            if move is None:
                return None

            client_id, route_index, position = move
            routes[route_index].insert(position, client_id)
            unserved.remove(client_id)

        return [route for route in routes if route]

    route_indices = list(range(k))
    rng.shuffle(route_indices)

    for route_index in route_indices:
        if not unserved:
            break

        candidates = admissible_clients(
            instance,
            routes[route_index],
            unserved,
            check_time_windows=check_time_windows,
        )

        if not candidates:
            return None

        client_id = rng.choice(candidates)
        routes[route_index].append(client_id)
        unserved.remove(client_id)

    progress = True
    while unserved and progress:
        progress = False
        route_indices = list(range(k))
        rng.shuffle(route_indices)

        for route_index in route_indices:
            candidates = admissible_clients(
                instance,
                routes[route_index],
                unserved,
                check_time_windows=check_time_windows,
            )

            if not candidates:
                continue

            client_id = rng.choice(candidates)
            routes[route_index].append(client_id)
            unserved.remove(client_id)
            progress = True

            if not unserved:
                break

    if unserved:
        return None

    return routes


def build_solution_with_k_vehicles(instance, k, check_time_windows=False):
    """
    Tente de construire une solution avec exactement k véhicules.
    Retourne une liste de routes si succès, sinon None.
    """
    unserved = set(instance.clients.keys())
    routes = [[] for _ in range(k)]

    if check_time_windows:
        while unserved:
            move = best_feasible_insertion(
                instance,
                routes,
                unserved,
                check_time_windows=True,
            )
            if move is None:
                return None

            client_id, route_index, position = move
            routes[route_index].insert(position, client_id)
            unserved.remove(client_id)

        return [route for route in routes if route]

    # Initialisation par graines
    seeds = choose_seeds(instance, k, list(unserved))

    for i, cid in enumerate(seeds):
        candidate_route = routes[i] + [cid]
        if not is_route_feasible(
            instance,
            candidate_route,
            check_time_windows=check_time_windows,
        ):
            return None
        routes[i].append(cid)
        unserved.remove(cid)

    # Compléter les routes
    progress = True
    while unserved and progress:
        progress = False

        for i in range(k):
            cid = nearest_feasible_client(
                instance,
                routes[i],
                unserved,
                check_time_windows=check_time_windows,
            )

            if cid is not None:
                routes[i].append(cid)
                unserved.remove(cid)
                progress = True

    if unserved:
        return None

    return routes


def find_first_feasible_vehicle_count(instance, max_extra=10, check_time_windows=False):
    """
    Cherche le premier nombre de véhicules pour lequel notre construction
    heuristique trouve une solution faisable à partir de la borne inférieure.
    """
    lb = lower_bound_vehicles(instance)

    for k in range(lb, lb + max_extra + 1):
        routes = build_solution_with_k_vehicles(
            instance,
            k,
            check_time_windows=check_time_windows,
        )
        if routes is not None:
            return k, routes

    return None, None


def find_minimum_vehicles(instance, max_extra=10, check_time_windows=False):
    """
    Alias historique conservé pour compatibilité.

    Attention : cette fonction ne prouve pas toujours la minimalité. En CVRP,
    si elle trouve une solution avec k = LB, la borne capacitaire certifie ce k.
    En VRPTW, le résultat doit être lu comme le premier k trouvé faisable par
    notre heuristique de construction.
    """
    return find_first_feasible_vehicle_count(
        instance,
        max_extra=max_extra,
        check_time_windows=check_time_windows,
    )


def generate_random_solution(
    instance,
    k=None,
    max_attempts=100,
    seed=None,
    check_time_windows=False,
):
    """
    Génère une solution aléatoire faisable.
    Si k est omis, on démarre à la borne inférieure capacité.
    """
    rng = random.Random(seed)
    target_k = lower_bound_vehicles(instance) if k is None else k

    for _ in range(max_attempts):
        routes = build_random_solution_with_k_vehicles(
            instance,
            target_k,
            rng=rng,
            check_time_windows=check_time_windows,
        )
        if routes is not None:
            return routes

    if check_time_windows:
        # Safety net: keep the API robust on hard VRPTW instances.
        return build_solution_with_k_vehicles(
            instance,
            target_k,
            check_time_windows=True,
        )

    return None
