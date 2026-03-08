import math


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


def total_demand(instance):
    return sum(client.demand for client in instance.clients.values())


def lower_bound_vehicles(instance):
    return math.ceil(total_demand(instance) / instance.max_quantity)