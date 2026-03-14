from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from construction import (
    build_solution_with_k_vehicles,
    find_minimum_vehicles,
    generate_random_solution,
)
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
    found_k, _ = find_minimum_vehicles(
        instance,
        max_extra=25 if check_time_windows else 10,
        check_time_windows=check_time_windows,
    )
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
        if initial_routes is None and check_time_windows:
            initial_routes = build_solution_with_k_vehicles(
                instance,
                found_k,
                check_time_windows=True,
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
                    "generated_neighbors": sa_result.generated_neighbors,
                    "failed_neighbor_generations": sa_result.failed_neighbor_generations,
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
            "generated_neighbors": summarize_metric(
                [run["simulated_annealing"]["generated_neighbors"] for run in successful_runs]
            ),
            "accepted_moves": summarize_metric(
                [run["simulated_annealing"]["accepted_moves"] for run in successful_runs]
            ),
        },
        "tabu_search": {
            "best_distance": summarize_metric(
                [run["tabu_search"]["best_distance"] for run in successful_runs]
            ),
            "runtime_seconds": summarize_metric(
                [run["tabu_search"]["runtime_seconds"] for run in successful_runs]
            ),
            "explored_neighbors": summarize_metric(
                [run["tabu_search"]["explored_neighbors"] for run in successful_runs]
            ),
            "accepted_moves": summarize_metric(
                [run["tabu_search"]["accepted_moves"] for run in successful_runs]
            ),
        },
    }


def run_experiment_suite(
    instances,
    preset_name="quick",
    limit=None,
    seed_base=1000,
    check_time_windows=False,
    output_path=None,
):
    preset = get_preset(preset_name)
    selected_instances = instances if limit is None else instances[:limit]
    output_file = Path(output_path) if output_path else None

    if output_file is not None:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open("a", encoding="utf-8") as handle:
            handle.write(
                f"\n# Run started {datetime.now().isoformat(timespec='seconds')}\n"
            )
            handle.write(
                f"preset={preset.name} time_windows={check_time_windows} instances={len(selected_instances)}\n"
            )

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
        if output_file is not None:
            append_experiment_result(output_file, preset, results[-1], check_time_windows)

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
                f"en {run['simulated_annealing']['runtime_seconds']:.2f}s "
                f"({run['simulated_annealing']['generated_neighbors']} voisins générés)"
            )
            lines.append(
                "    recherche tabou : "
                f"{run['tabu_search']['best_distance']:.2f} "
                f"en {run['tabu_search']['runtime_seconds']:.2f}s "
                f"({run['tabu_search']['explored_neighbors']} voisins explorés)"
            )

    return "\n".join(lines)


def format_generation_table(suite_result):
    lines = []
    preset = suite_result["preset"]
    lines.append(f"\n=== Voisins générés/explorés ({preset.name}) ===")
    lines.append(
        f"{'Nom':15} {'k':>4} {'SA gen(avg)':>12} {'SA acc(avg)':>12} {'Tabou exp(avg)':>15} {'Tabou acc(avg)':>15}"
    )

    for item in suite_result["results"]:
        summary = item["summary"]
        if summary["runs"] == 0:
            lines.append(
                f"{summary['instance']:15} {'-':>4} {'-':>12} {'-':>12} {'-':>15} {'-':>15}"
            )
            continue

        sa_gen = summary["simulated_annealing"]["generated_neighbors"]["avg"]
        sa_acc = summary["simulated_annealing"]["accepted_moves"]["avg"]
        tabu_exp = summary["tabu_search"]["explored_neighbors"]["avg"]
        tabu_acc = summary["tabu_search"]["accepted_moves"]["avg"]

        lines.append(
            f"{summary['instance']:15} "
            f"{summary['vehicles']:4d} "
            f"{sa_gen:12.2f} "
            f"{sa_acc:12.2f} "
            f"{tabu_exp:15.2f} "
            f"{tabu_acc:15.2f}"
        )

    return "\n".join(lines)


def append_experiment_result(output_file, preset, result_item, check_time_windows):
    summary = result_item["summary"]
    raw = result_item["raw"]

    with output_file.open("a", encoding="utf-8") as handle:
        handle.write(
            f"\n## {summary['instance']} | preset={preset.name} | time_windows={check_time_windows}\n"
        )
        handle.write(f"vehicles={summary['vehicles']} successful_runs={summary['runs']}\n")

        if summary["runs"] == 0:
            handle.write("status=failed\n")
            return

        handle.write(
            "summary "
            f"initial_avg={summary['initial_distance']['avg']:.2f} "
            f"sa_avg={summary['simulated_annealing']['best_distance']['avg']:.2f} "
            f"tabu_avg={summary['tabu_search']['best_distance']['avg']:.2f} "
            f"sa_time={summary['simulated_annealing']['runtime_seconds']['avg']:.2f} "
            f"tabu_time={summary['tabu_search']['runtime_seconds']['avg']:.2f} "
            f"sa_generated={summary['simulated_annealing']['generated_neighbors']['avg']:.2f} "
            f"tabu_explored={summary['tabu_search']['explored_neighbors']['avg']:.2f}\n"
        )

        for run_index, run in enumerate(raw["runs"], start=1):
            if not run["initial_feasible"]:
                handle.write(f"run={run_index} seed={run['seed']} status=failed\n")
                continue

            handle.write(
                f"run={run_index} seed={run['seed']} "
                f"initial={run['initial_distance']:.2f} "
                f"sa={run['simulated_annealing']['best_distance']:.2f} "
                f"sa_time={run['simulated_annealing']['runtime_seconds']:.2f} "
                f"sa_generated={run['simulated_annealing']['generated_neighbors']} "
                f"tabu={run['tabu_search']['best_distance']:.2f} "
                f"tabu_time={run['tabu_search']['runtime_seconds']:.2f} "
                f"tabu_explored={run['tabu_search']['explored_neighbors']}\n"
            )
