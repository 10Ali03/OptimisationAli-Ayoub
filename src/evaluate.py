import math
from dataclasses import dataclass


@dataclass
class RouteEvaluation:
    route: list[int]
    distance: float
    load: int
    arrival_times: list[float]
    service_start_times: list[float]
    waiting_times: list[float]
    departure_times: list[float]
    return_time: float
    capacity_feasible: bool
    time_feasible: bool

    @property
    def feasible(self):
        return self.capacity_feasible and self.time_feasible


def euclidean_distance(x1, y1, x2, y2):
    return math.hypot(x1 - x2, y1 - y2)


def distance_depot_to_client(instance, client_id):
    depot = instance.depot
    client = instance.clients[client_id]
    return euclidean_distance(depot.x, depot.y, client.x, client.y)


def distance_between_clients(instance, client_id_1, client_id_2):
    c1 = instance.clients[client_id_1]
    c2 = instance.clients[client_id_2]
    return euclidean_distance(c1.x, c1.y, c2.x, c2.y)


def route_load(instance, route):
    return sum(instance.clients[cid].demand for cid in route)


def route_distance(instance, route):
    if not route:
        return 0.0

    total = distance_depot_to_client(instance, route[0])

    for i in range(len(route) - 1):
        total += distance_between_clients(instance, route[i], route[i + 1])

    total += distance_depot_to_client(instance, route[-1])
    return total


def solution_distance(instance, routes):
    return sum(route_distance(instance, route) for route in routes)


def total_demand(instance):
    return sum(client.demand for client in instance.clients.values())


def lower_bound_vehicles(instance):
    return math.ceil(total_demand(instance) / instance.max_quantity)


def is_capacity_feasible(instance, route):
    return route_load(instance, route) <= instance.max_quantity


def evaluate_route(instance, route):
    if not route:
        depot_ready = instance.depot.ready_time
        depot_due = instance.depot.due_time
        return RouteEvaluation(
            route=[],
            distance=0.0,
            load=0,
            arrival_times=[],
            service_start_times=[],
            waiting_times=[],
            departure_times=[],
            return_time=depot_ready,
            capacity_feasible=True,
            time_feasible=depot_ready <= depot_due,
        )

    arrival_times = []
    service_start_times = []
    waiting_times = []
    departure_times = []

    current_time = instance.depot.ready_time
    previous_client_id = None
    time_feasible = True

    for client_id in route:
        client = instance.clients[client_id]

        if previous_client_id is None:
            travel_time = distance_depot_to_client(instance, client_id)
        else:
            travel_time = distance_between_clients(instance, previous_client_id, client_id)

        arrival_time = current_time + travel_time
        service_start = max(arrival_time, client.ready_time)
        waiting_time = max(0.0, client.ready_time - arrival_time)
        departure_time = service_start + client.service

        if service_start > client.due_time:
            time_feasible = False

        arrival_times.append(arrival_time)
        service_start_times.append(service_start)
        waiting_times.append(waiting_time)
        departure_times.append(departure_time)

        current_time = departure_time
        previous_client_id = client_id

    return_time = current_time + distance_depot_to_client(instance, route[-1])
    if return_time > instance.depot.due_time:
        time_feasible = False

    return RouteEvaluation(
        route=list(route),
        distance=route_distance(instance, route),
        load=route_load(instance, route),
        arrival_times=arrival_times,
        service_start_times=service_start_times,
        waiting_times=waiting_times,
        departure_times=departure_times,
        return_time=return_time,
        capacity_feasible=is_capacity_feasible(instance, route),
        time_feasible=time_feasible,
    )


def is_time_feasible(instance, route):
    return evaluate_route(instance, route).time_feasible


def is_route_feasible(instance, route, check_time_windows=True):
    route_eval = evaluate_route(instance, route)
    if check_time_windows:
        return route_eval.feasible
    return route_eval.capacity_feasible


def all_clients_served_exactly_once(instance, routes):
    flattened = [client_id for route in routes for client_id in route]
    expected_clients = set(instance.clients.keys())
    return len(flattened) == len(expected_clients) and set(flattened) == expected_clients


def evaluate_solution(instance, routes, check_time_windows=True):
    route_evaluations = [evaluate_route(instance, route) for route in routes]
    all_served_once = all_clients_served_exactly_once(instance, routes)
    routes_feasible = all(
        route_eval.feasible if check_time_windows else route_eval.capacity_feasible
        for route_eval in route_evaluations
    )

    return {
        "route_evaluations": route_evaluations,
        "distance": sum(route_eval.distance for route_eval in route_evaluations),
        "all_clients_served_exactly_once": all_served_once,
        "feasible": routes_feasible and all_served_once,
    }
