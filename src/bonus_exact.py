from dataclasses import dataclass

from ortools.linear_solver import pywraplp

try:
    from evaluate import (
        distance_between_clients,
        distance_depot_to_client,
        lower_bound_vehicles,
    )
except ModuleNotFoundError:
    from src.evaluate import (
        distance_between_clients,
        distance_depot_to_client,
        lower_bound_vehicles,
    )


@dataclass
class ExactRunResult:
    num_clients: int
    num_vehicles: int
    status: str
    objective: float | None
    runtime_seconds: float


def build_subinstance(instance, num_clients):
    client_ids = sorted(instance.clients.keys())[:num_clients]

    class SubInstance:
        pass

    sub = SubInstance()
    sub.name = f"{instance.name}_first_{num_clients}"
    sub.comment = instance.comment
    sub.problem_type = instance.problem_type
    sub.coordinates_type = instance.coordinates_type
    sub.nb_depots = instance.nb_depots
    sub.nb_clients = num_clients
    sub.max_quantity = instance.max_quantity
    sub.depot = instance.depot
    sub.clients = {i + 1: instance.clients[cid] for i, cid in enumerate(client_ids)}
    return sub


def solve_cvrp_mip(instance, time_limit_seconds=30):
    solver = pywraplp.Solver.CreateSolver("SCIP")
    if solver is None:
        raise RuntimeError("Solveur SCIP indisponible dans OR-Tools.")

    solver.SetTimeLimit(int(time_limit_seconds * 1000))

    n = instance.nb_clients
    k = lower_bound_vehicles(instance)
    nodes = list(range(n + 1))
    clients = list(range(1, n + 1))

    def dist(i, j):
        if i == 0 and j == 0:
            return 0.0
        if i == 0:
            return distance_depot_to_client(instance, j)
        if j == 0:
            return distance_depot_to_client(instance, i)
        return distance_between_clients(instance, i, j)

    x = {}
    for i in nodes:
        for j in nodes:
            if i != j:
                x[i, j] = solver.BoolVar(f"x_{i}_{j}")

    u = {i: solver.NumVar(0, instance.max_quantity, f"u_{i}") for i in clients}

    for j in clients:
        solver.Add(sum(x[i, j] for i in nodes if i != j) == 1)
        solver.Add(sum(x[j, i] for i in nodes if i != j) == 1)

    solver.Add(sum(x[0, j] for j in clients) == k)
    solver.Add(sum(x[j, 0] for j in clients) == k)

    demands = {i: instance.clients[i].demand for i in clients}
    for i in clients:
        solver.Add(u[i] >= demands[i])
        solver.Add(u[i] <= instance.max_quantity)

    for i in clients:
        for j in clients:
            if i != j:
                solver.Add(
                    u[i] - u[j] + instance.max_quantity * x[i, j]
                    <= instance.max_quantity - demands[j]
                )

    objective = solver.Objective()
    for i in nodes:
        for j in nodes:
            if i != j:
                objective.SetCoefficient(x[i, j], dist(i, j))
    objective.SetMinimization()

    status = solver.Solve()
    status_map = {
        pywraplp.Solver.OPTIMAL: "OPTIMAL",
        pywraplp.Solver.FEASIBLE: "FEASIBLE",
        pywraplp.Solver.INFEASIBLE: "INFEASIBLE",
        pywraplp.Solver.UNBOUNDED: "UNBOUNDED",
        pywraplp.Solver.ABNORMAL: "ABNORMAL",
        pywraplp.Solver.NOT_SOLVED: "NOT_SOLVED",
    }

    return ExactRunResult(
        num_clients=n,
        num_vehicles=k,
        status=status_map.get(status, str(status)),
        objective=objective.Value() if status in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE) else None,
        runtime_seconds=solver.wall_time() / 1000.0,
    )


def run_bonus_scaling(instance, sizes, time_limit_seconds=30):
    results = []
    for size in sizes:
        subinstance = build_subinstance(instance, size)
        results.append(solve_cvrp_mip(subinstance, time_limit_seconds=time_limit_seconds))
    return results
