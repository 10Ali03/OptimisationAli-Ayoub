import argparse
from pathlib import Path

from io_utils import parse_vrp_file
from evaluate import evaluate_solution, lower_bound_vehicles, solution_distance, total_demand
from construction import find_minimum_vehicles, generate_random_solution
from solver import (
    format_experiment_details,
    format_experiment_table,
    run_experiment_suite,
    select_instances,
)


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
            dist_str = f"{solution_distance(inst, routes):.2f}"

        print(f"{inst.name:15} {lb:6d} {found_str:>8} {dist_str:>12}")


def print_vehicle_search_with_time_windows(instances, limit=5):
    print("\n=== Recherche du nombre de véhicules avec fenêtres de temps ===")
    print(f"{'Nom':15} {'LB':>6} {'Trouvé':>8} {'Distance':>12}")

    for inst in instances[:limit]:
        lb = lower_bound_vehicles(inst)
        found_k, routes = find_minimum_vehicles(
            inst,
            max_extra=25,
            check_time_windows=True,
        )

        if found_k is None:
            found_str = "échec"
            dist_str = "-"
        else:
            found_str = str(found_k)
            dist_str = f"{solution_distance(inst, routes):.2f}"

        print(f"{inst.name:15} {lb:6d} {found_str:>8} {dist_str:>12}")


def print_random_initial_solutions(instances, seed=42):
    print("\n=== Génération aléatoire de solutions initiales ===")
    print(f"{'Nom':15} {'k':>4} {'Faisable':>10} {'Distance':>12}")

    for index, inst in enumerate(instances):
        found_k, _ = find_minimum_vehicles(inst)

        if found_k is None:
            print(f"{inst.name:15} {'-':>4} {'échec':>10} {'-':>12}")
            continue

        routes = generate_random_solution(
            inst,
            k=found_k,
            max_attempts=100,
            seed=seed + index,
            check_time_windows=False,
        )

        if routes is None:
            feasible_str = "échec"
            dist_str = "-"
        else:
            feasible = evaluate_solution(inst, routes, check_time_windows=False)["feasible"]
            feasible_str = "oui" if feasible else "non"
            dist_str = f"{solution_distance(inst, routes):.2f}"

        print(f"{inst.name:15} {found_k:4d} {feasible_str:>10} {dist_str:>12}")


def print_metaheuristics_comparison(instances, preset_name="quick", limit=1):
    suite_result = run_experiment_suite(
        instances,
        preset_name=preset_name,
        limit=limit,
    )
    print(format_experiment_table(suite_result))


def parse_args():
    parser = argparse.ArgumentParser(description="VRPTW / CVRP experimentation runner")
    parser.add_argument(
        "--mode",
        choices=("overview", "experiment"),
        default="overview",
        help="overview pour le résumé habituel, experiment pour lancer une campagne dédiée",
    )
    parser.add_argument(
        "--preset",
        choices=("quick", "long"),
        default="quick",
        help="preset expérimental à utiliser",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="nombre maximal d'instances à traiter",
    )
    parser.add_argument(
        "--instances",
        nargs="*",
        default=None,
        help="noms exacts des fichiers d'instance, par ex. data101.vrp",
    )
    parser.add_argument(
        "--details",
        action="store_true",
        help="affiche aussi le détail run par run en mode experiment",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    instances = load_all_instances("data")
    selected_instances = select_instances(
        instances,
        names=args.instances,
        limit=args.limit,
    )

    if args.mode == "experiment":
        suite_result = run_experiment_suite(
            selected_instances,
            preset_name=args.preset,
            limit=None,
        )
        print(format_experiment_table(suite_result))
        if args.details:
            print(format_experiment_details(suite_result))
        return

    print_instances_summary(instances)
    print_vehicle_search(instances)
    print_vehicle_search_with_time_windows(instances)
    print_random_initial_solutions(instances)
    print_metaheuristics_comparison(instances, preset_name="quick", limit=1)


if __name__ == "__main__":
    main()
