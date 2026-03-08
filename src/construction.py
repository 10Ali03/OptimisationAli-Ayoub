from evaluate import distance_depot_to_client, distance_between_clients


def route_load(instance, route):
    return sum(instance.clients[cid].demand for cid in route)


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


def nearest_feasible_client(instance, route, unserved):
    """
    Retourne le client admissible le plus proche du dernier sommet de la route
    (ou du dépôt si la route est vide).
    """
    current_load = route_load(instance, route)
    best_client = None
    best_distance = float("inf")

    if not route:
        for cid in unserved:
            demand = instance.clients[cid].demand
            if current_load + demand <= instance.max_quantity:
                d = distance_depot_to_client(instance, cid)
                if d < best_distance:
                    best_distance = d
                    best_client = cid
    else:
        last_client = route[-1]
        for cid in unserved:
            demand = instance.clients[cid].demand
            if current_load + demand <= instance.max_quantity:
                d = distance_between_clients(instance, last_client, cid)
                if d < best_distance:
                    best_distance = d
                    best_client = cid

    return best_client


def build_solution_with_k_vehicles(instance, k):
    """
    Tente de construire une solution avec exactement k véhicules.
    Retourne une liste de routes si succès, sinon None.
    """
    unserved = set(instance.clients.keys())
    routes = [[] for _ in range(k)]

    # Initialisation par graines
    seeds = choose_seeds(instance, k, list(unserved))

    for i, cid in enumerate(seeds):
        routes[i].append(cid)
        unserved.remove(cid)

    # Compléter les routes
    progress = True
    while unserved and progress:
        progress = False

        for i in range(k):
            cid = nearest_feasible_client(instance, routes[i], unserved)

            if cid is not None:
                routes[i].append(cid)
                unserved.remove(cid)
                progress = True

    if unserved:
        return None

    return routes


def find_minimum_vehicles(instance, max_extra=10):
    """
    Cherche le premier nombre de véhicules faisable à partir de la borne inférieure.
    """
    from evaluate import lower_bound_vehicles

    lb = lower_bound_vehicles(instance)

    for k in range(lb, lb + max_extra + 1):
        routes = build_solution_with_k_vehicles(instance, k)
        if routes is not None:
            return k, routes

    return None, None