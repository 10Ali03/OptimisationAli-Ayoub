import argparse
from pathlib import Path

from io_utils import parse_vrp_file
from evaluate import evaluate_solution, lower_bound_vehicles, solution_distance, total_demand
from construction import find_minimum_vehicles, generate_random_solution
from solver import (
    format_experiment_details,
    format_generation_table,
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
    print(format_generation_table(suite_result))


def run_bonus_mode(instances, sizes, time_limit_seconds):
    try:
        from bonus_exact import run_bonus_scaling
    except ImportError:
        print("Erreur : le module 'ortools' est requis pour le mode bonus.")
        print("Installez-le avec : pip install ortools")
        return

    if not instances:
        raise ValueError("Aucune instance sélectionnée pour le bonus exact.")

    instance = instances[0]
    results = run_bonus_scaling(
        instance,
        sizes=sizes,
        time_limit_seconds=time_limit_seconds,
    )

    print("\n=== Bonus exact OR-Tools ===")
    print(f"Instance source : {instance.name}")
    print(f"{'Clients':>8} {'k':>4} {'Statut':>12} {'Objectif':>12} {'Temps(s)':>10}")
    for result in results:
        objective = "-" if result.objective is None else f"{result.objective:.2f}"
        print(
            f"{result.num_clients:8d} "
            f"{result.num_vehicles:4d} "
            f"{result.status:>12} "
            f"{objective:>12} "
            f"{result.runtime_seconds:10.2f}"
        )


def parse_args():
    parser = argparse.ArgumentParser(description="VRPTW / CVRP experimentation runner")
    parser.add_argument(
        "--mode",
        choices=("overview", "experiment", "bonus"),
        default="overview",
        help="overview pour le résumé habituel, experiment pour lancer une campagne dédiée, bonus pour l'étude exacte OR-Tools",
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
    parser.add_argument(
        "--time-windows",
        action="store_true",
        help="active la version avec fenêtres de temps en mode experiment",
    )
    parser.add_argument(
        "--output-file",
        default="experiment_results.log",
        help="fichier texte où enregistrer les resultats des campagnes experimentales",
    )
    parser.add_argument(
        "--sizes",
        nargs="*",
        type=int,
        default=[5, 10, 15, 20],
        help="tailles de sous-instances à tester en mode bonus",
    )
    parser.add_argument(
        "--time-limit",
        type=float,
        default=10.0,
        help="limite de temps par sous-instance en secondes pour le mode bonus",
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
            check_time_windows=args.time_windows,
            output_path=args.output_file,
        )
        print(format_experiment_table(suite_result))
        print(format_generation_table(suite_result))
        if args.details:
            print(format_experiment_details(suite_result))
        return

    if args.mode == "bonus":
        run_bonus_mode(selected_instances, sizes=args.sizes, time_limit_seconds=args.time_limit)
        return

    print_instances_summary(instances)
    print_vehicle_search(instances)
    print_vehicle_search_with_time_windows(instances)
    print_random_initial_solutions(instances)
    print_metaheuristics_comparison(instances, preset_name="quick", limit=1)


if __name__ == "__main__":
    main()
