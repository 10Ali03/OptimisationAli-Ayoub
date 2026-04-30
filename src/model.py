from dataclasses import dataclass


@dataclass
class Depot:
    id_name: str
    x: float
    y: float
    ready_time: float
    due_time: float


@dataclass
class Client:
    id_name: str
    x: float
    y: float
    ready_time: float
    due_time: float
    demand: int
    service: float


@dataclass
class VRPTWInstance:
    name: str
    comment: str
    problem_type: str
    coordinates_type: str
    nb_depots: int
    nb_clients: int
    max_quantity: int
    depot: Depot
    clients: dict   # clé = int (1..n), valeur = Client
