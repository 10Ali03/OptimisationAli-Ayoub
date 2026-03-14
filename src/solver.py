from dataclasses import dataclass

from construction import find_minimum_vehicles, generate_random_solution
from evaluate import evaluate_solution
from meta.simulated_annealing import simulated_annealing
from meta.tabu_search import tabu_search


@dataclass(frozen=True)
class ExperimentPreset:
    name: str
    sa_iterations: int
    sa_temperature: float
    sa_cooling_rate: float
    sa_neighbor_attempts: int
    tabu_iterations: int
    tabu_tenure: int
    tabu_max_neighbors: int
    repetitions: int


QUICK_PRESET = ExperimentPreset(
    name="quick",
    sa_iterations=300,
    sa_temperature=100.0,
    sa_cooling_rate=0.98,
    sa_neighbor_attempts=50,
    tabu_iterations=5,
    tabu_tenure=5,
    tabu_max_neighbors=40,
    repetitions=1,
)

LONG_PRESET = ExperimentPreset(
    name="long",
    sa_iterations=1200,
    sa_temperature=120.0,
    sa_cooling_rate=0.995,
    sa_neighbor_attempts=100,
    tabu_iterations=10,
    tabu_tenure=8,
    tabu_max_neighbors=60,
    repetitions=2,
)


def available_presets():
    return {
        QUICK_PRESET.name: QUICK_PRESET,
        LONG_PRESET.name: LONG_PRESET,
    }


def get_preset(name="quick"):
    presets = available_presets()
    if name not in presets:
        raise ValueError(f"Preset inconnu : {name}")
    return presets[name]


def select_instances(instances, names=None, limit=None):
    selected = instances

    if names:
        wanted = set(names)
        selected = [instance for instance in instances if instance.name in wanted]

    if limit is not None:
        selected = selected[:limit]

    return selected


def run_metaheuristics_on_instance(
    instance,
    preset,
    seed_base=0,
    check_time_windows=False,
):
    found_k, _ = find_minimum_vehicles(instance)
    if found_k is None:
        return {
            "instance": instance.name,
            "vehicles": None,
            "runs": [],
        }

    runs = []
    for repetition in range(preset.repetitions):
        seed = seed_base + repetition
        initial_routes = generate_random_solution(
            instance,
            k=found_k,
            max_attempts=100,
            seed=seed,
            check_time_windows=check_time_windows,
        )
        if initial_routes is None:
            runs.append(
                {
                    "seed": seed,
                    "initial_distance": None,
                    "initial_feasible": False,
                    "simulated_annealing": None,
                    "tabu_search": None,
                }
            )
            continue

        initial_eval = evaluate_solution(
            instance,
            initial_routes,
            check_time_windows=check_time_windows,
        )
        sa_result = simulated_annealing(
            instance,
            initial_routes=initial_routes,
            seed=seed,
            check_time_windows=check_time_windows,
            max_iterations=preset.sa_iterations,
            initial_temperature=preset.sa_temperature,
            cooling_rate=preset.sa_cooling_rate,
            neighbor_attempts=preset.sa_neighbor_attempts,
        )
        tabu_result = tabu_search(
            instance,
            initial_routes=initial_routes,
            seed=seed,
            check_time_windows=check_time_windows,
            max_iterations=preset.tabu_iterations,
            tabu_tenure=preset.tabu_tenure,
            max_neighbors=preset.tabu_max_neighbors,
        )

        runs.append(
            {
                "seed": seed,
                "initial_distance": initial_eval["distance"],
                "initial_feasible": initial_eval["feasible"],
                "simulated_annealing": {
                    "best_distance": sa_result.best_distance,
                    "iterations": sa_result.iterations,
                    "runtime_seconds": sa_result.runtime_seconds,
                    "accepted_moves": sa_result.accepted_moves,
                },
                "tabu_search": {
                    "best_distance": tabu_result.best_distance,
                    "iterations": tabu_result.iterations,
                    "runtime_seconds": tabu_result.runtime_seconds,
                    "accepted_moves": tabu_result.accepted_moves,
                    "explored_neighbors": tabu_result.explored_neighbors,
                },
            }
        )

    return {
        "instance": instance.name,
        "vehicles": found_k,
        "runs": runs,
    }


def summarize_metric(values):
    if not values:
        return None
    return {
        "min": min(values),
        "max": max(values),
        "avg": sum(values) / len(values),
    }


def summarize_experiment(experiment_result):
    successful_runs = [
        run for run in experiment_result["runs"] if run["initial_feasible"]
    ]
    if not successful_runs:
        return {
            "instance": experiment_result["instance"],
            "vehicles": experiment_result["vehicles"],
            "runs": 0,
            "initial_distance": None,
            "simulated_annealing": None,
            "tabu_search": None,
        }

    return {
        "instance": experiment_result["instance"],
        "vehicles": experiment_result["vehicles"],
        "runs": len(successful_runs),
        "initial_distance": summarize_metric(
            [run["initial_distance"] for run in successful_runs]
        ),
        "simulated_annealing": {
            "best_distance": summarize_metric(
                [run["simulated_annealing"]["best_distance"] for run in successful_runs]
            ),
            "runtime_seconds": summarize_metric(
                [run["simulated_annealing"]["runtime_seconds"] for run in successful_runs]
            ),
        },
        "tabu_search": {
            "best_distance": summarize_metric(
                [run["tabu_search"]["best_distance"] for run in successful_runs]
            ),
            "runtime_seconds": summarize_metric(
                [run["tabu_search"]["runtime_seconds"] for run in successful_runs]
            ),
        },
    }


def run_experiment_suite(
    instances,
    preset_name="quick",
    limit=None,
    seed_base=1000,
    check_time_windows=False,
):
    preset = get_preset(preset_name)
    selected_instances = instances if limit is None else instances[:limit]

    results = []
    for index, instance in enumerate(selected_instances):
        result = run_metaheuristics_on_instance(
            instance,
            preset,
            seed_base=seed_base + index * preset.repetitions,
            check_time_windows=check_time_windows,
        )
        results.append(
            {
                "raw": result,
                "summary": summarize_experiment(result),
            }
        )

    return {
        "preset": preset,
        "results": results,
    }


def format_experiment_table(suite_result):
    lines = []
    preset = suite_result["preset"]
    lines.append(f"\n=== Comparaison métaheuristiques ({preset.name}) ===")
    lines.append(
        f"{'Nom':15} {'k':>4} {'Init(avg)':>12} {'SA(avg)':>12} {'Tabou(avg)':>12} {'SA t(s)':>10} {'Tabou t(s)':>12}"
    )

    for item in suite_result["results"]:
        summary = item["summary"]
        if summary["runs"] == 0:
            lines.append(
                f"{summary['instance']:15} {'-':>4} {'échec':>12} {'-':>12} {'-':>12} {'-':>10} {'-':>12}"
            )
            continue

        initial_avg = summary["initial_distance"]["avg"]
        sa_avg = summary["simulated_annealing"]["best_distance"]["avg"]
        tabu_avg = summary["tabu_search"]["best_distance"]["avg"]
        sa_time = summary["simulated_annealing"]["runtime_seconds"]["avg"]
        tabu_time = summary["tabu_search"]["runtime_seconds"]["avg"]

        lines.append(
            f"{summary['instance']:15} "
            f"{summary['vehicles']:4d} "
            f"{initial_avg:12.2f} "
            f"{sa_avg:12.2f} "
            f"{tabu_avg:12.2f} "
            f"{sa_time:10.2f} "
            f"{tabu_time:12.2f}"
        )

    return "\n".join(lines)


def format_experiment_details(suite_result):
    lines = []
    preset = suite_result["preset"]
    lines.append(f"\n=== Détail des expériences ({preset.name}) ===")

    for item in suite_result["results"]:
        summary = item["summary"]
        raw = item["raw"]
        lines.append(f"\nInstance : {summary['instance']}")
        lines.append(f"Véhicules : {summary['vehicles']}")
        lines.append(f"Répétitions faisables : {summary['runs']}")

        for run_index, run in enumerate(raw["runs"], start=1):
            lines.append(f"  Run {run_index} | seed={run['seed']}")
            if not run["initial_feasible"]:
                lines.append("    solution initiale : échec")
                continue

            lines.append(f"    initiale : {run['initial_distance']:.2f}")
            lines.append(
                "    recuit simulé : "
                f"{run['simulated_annealing']['best_distance']:.2f} "
                f"en {run['simulated_annealing']['runtime_seconds']:.2f}s"
            )
            lines.append(
                "    recherche tabou : "
                f"{run['tabu_search']['best_distance']:.2f} "
                f"en {run['tabu_search']['runtime_seconds']:.2f}s"
            )

    return "\n".join(lines)
