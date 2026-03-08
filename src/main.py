from pathlib import Path

from io_utils import parse_vrp_file
from evaluate import total_demand, lower_bound_vehicles
from construction import find_minimum_vehicles


def load_all_instances(data_folder="data"):
    data_path = Path(data_folder)

    if not data_path.exists():
        raise FileNotFoundError(f"Dossier introuvable : {data_folder}")

    instances = []

    for file_path in sorted(data_path.glob("*.vrp")):
        instance = parse_vrp_file(file_path)
        instances.append(instance)

    return instances


def print_instances_summary(instances):
    print("\n=== Résumé des instances ===")
    print(f"{'Nom':15} {'Clients':>8} {'Capacité':>10} {'DemandeTot':>12} {'LB':>6}")

    for inst in instances:
        demand = total_demand(inst)
        lb = lower_bound_vehicles(inst)

        print(f"{inst.name:15} {inst.nb_clients:8d} {inst.max_quantity:10d} {demand:12d} {lb:6d}")


def print_vehicle_search(instances):
    print("\n=== Recherche du nombre de véhicules ===")
    print(f"{'Nom':15} {'LB':>6} {'Trouvé':>8} {'Distance':>12}")

    for inst in instances:
        lb = lower_bound_vehicles(inst)
        found_k, routes = find_minimum_vehicles(inst)

        if found_k is None:
            found_str = "échec"
            dist_str = "-"
        else:
            found_str = str(found_k)
            from construction import solution_distance
            dist_str = f"{solution_distance(inst, routes):.2f}"

        print(f"{inst.name:15} {lb:6d} {found_str:>8} {dist_str:>12}")


def main():
    instances = load_all_instances("data")
    print_instances_summary(instances)
    print_vehicle_search(instances)


if __name__ == "__main__":
    main()