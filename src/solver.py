from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from construction import (
    build_solution_with_k_vehicles,
    find_first_feasible_vehicle_count,
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
    sa_iterations=3000,
    sa_temperature=150.0,
    sa_cooling_rate=0.997,
    sa_neighbor_attempts=100,
    tabu_iterations=60,
    tabu_tenure=20,
    tabu_max_neighbors=200,
    repetitions=5,
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
    method="both",
):
    found_k, _ = find_first_feasible_vehicle_count(
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
        # Pour le VRPTW, les tentatives aléatoires n'aboutissent jamais (contraintes
        # trop restrictives) : on limite à 3 pour éviter ~167 s de calcul inutile par run.
        # Le safety net déterministe de generate_random_solution prend le relais.
        _max_attempts = 3 if check_time_windows else 100
        initial_routes = generate_random_solution(
            instance,
            k=found_k,
            max_attempts=_max_attempts,
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

        sa_entry = None
        if method in ("sa", "both"):
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
            sa_entry = {
                "best_distance": sa_result.best_distance,
                "iterations": sa_result.iterations,
                "runtime_seconds": sa_result.runtime_seconds,
                "generated_neighbors": sa_result.generated_neighbors,
                "failed_neighbor_generations": sa_result.failed_neighbor_generations,
                "accepted_moves": sa_result.accepted_moves,
            }

        tabu_entry = None
        if method in ("tabu", "both"):
            tabu_result = tabu_search(
                instance,
                initial_routes=initial_routes,
                seed=seed,
                check_time_windows=check_time_windows,
                max_iterations=preset.tabu_iterations,
                tabu_tenure=preset.tabu_tenure,
                max_neighbors=preset.tabu_max_neighbors,
            )
            tabu_entry = {
                "best_distance": tabu_result.best_distance,
                "iterations": tabu_result.iterations,
                "runtime_seconds": tabu_result.runtime_seconds,
                "accepted_moves": tabu_result.accepted_moves,
                "explored_neighbors": tabu_result.explored_neighbors,
            }

        runs.append(
            {
                "seed": seed,
                "initial_distance": initial_eval["distance"],
                "initial_feasible": initial_eval["feasible"],
                "simulated_annealing": sa_entry,
                "tabu_search": tabu_entry,
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

    sa_runs = [r for r in successful_runs if r["simulated_annealing"] is not None]
    tabu_runs = [r for r in successful_runs if r["tabu_search"] is not None]

    return {
        "instance": experiment_result["instance"],
        "vehicles": experiment_result["vehicles"],
        "runs": len(successful_runs),
        "initial_distance": summarize_metric(
            [run["initial_distance"] for run in successful_runs]
        ),
        "simulated_annealing": {
            "best_distance": summarize_metric(
                [r["simulated_annealing"]["best_distance"] for r in sa_runs]
            ),
            "runtime_seconds": summarize_metric(
                [r["simulated_annealing"]["runtime_seconds"] for r in sa_runs]
            ),
            "generated_neighbors": summarize_metric(
                [r["simulated_annealing"]["generated_neighbors"] for r in sa_runs]
            ),
            "accepted_moves": summarize_metric(
                [r["simulated_annealing"]["accepted_moves"] for r in sa_runs]
            ),
        } if sa_runs else None,
        "tabu_search": {
            "best_distance": summarize_metric(
                [r["tabu_search"]["best_distance"] for r in tabu_runs]
            ),
            "runtime_seconds": summarize_metric(
                [r["tabu_search"]["runtime_seconds"] for r in tabu_runs]
            ),
            "explored_neighbors": summarize_metric(
                [r["tabu_search"]["explored_neighbors"] for r in tabu_runs]
            ),
            "accepted_moves": summarize_metric(
                [r["tabu_search"]["accepted_moves"] for r in tabu_runs]
            ),
        } if tabu_runs else None,
    }


def run_experiment_suite(
    instances,
    preset_name="quick",
    limit=None,
    seed_base=1000,
    check_time_windows=False,
    output_path=None,
    method="both",
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
            method=method,
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
    lines.append(f"\n=== Résultats par run ({preset.name}) ===")
    lines.append(
        f"{'Nom':15} {'R':>3} {'k':>4} {'Initial':>12} {'SA':>12} {'Tabou':>12} {'SA t(s)':>10} {'Tabou t(s)':>12}"
    )

    for item in suite_result["results"]:
        raw = item["raw"]
        instance_name = raw["instance"]
        k = raw["vehicles"]

        if not raw["runs"]:
            lines.append(
                f"{instance_name:15} {'-':>3} {'-':>4} {'échec':>12} {'-':>12} {'-':>12} {'-':>10} {'-':>12}"
            )
            continue

        for run_index, run in enumerate(raw["runs"], start=1):
            if not run["initial_feasible"]:
                k_s = str(k) if k is not None else "-"
                lines.append(
                    f"{instance_name:15} {run_index:3d} {k_s:>4} {'échec':>12} {'-':>12} {'-':>12} {'-':>10} {'-':>12}"
                )
                continue

            initial = run["initial_distance"]
            sa = run["simulated_annealing"]
            tabu = run["tabu_search"]

            sa_dist_s = f"{sa['best_distance']:12.2f}" if sa else f"{'—':>12}"
            sa_time_s = f"{sa['runtime_seconds']:10.2f}" if sa else f"{'—':>10}"
            tabu_dist_s = f"{tabu['best_distance']:12.2f}" if tabu else f"{'—':>12}"
            tabu_time_s = f"{tabu['runtime_seconds']:12.2f}" if tabu else f"{'—':>12}"

            lines.append(
                f"{instance_name:15} {run_index:3d} {k:4d} {initial:12.2f} "
                f"{sa_dist_s} {tabu_dist_s} {sa_time_s} {tabu_time_s}"
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
            if run["simulated_annealing"] is not None:
                lines.append(
                    "    recuit simulé : "
                    f"{run['simulated_annealing']['best_distance']:.2f} "
                    f"en {run['simulated_annealing']['runtime_seconds']:.2f}s "
                    f"({run['simulated_annealing']['generated_neighbors']} voisins générés)"
                )
            if run["tabu_search"] is not None:
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
    lines.append(f"\n=== Voisins générés/explorés par run ({preset.name}) ===")
    lines.append(
        f"{'Nom':15} {'R':>3} {'k':>4} {'SA gen':>10} {'SA acc':>10} {'Tabou exp':>12} {'Tabou acc':>12}"
    )

    for item in suite_result["results"]:
        raw = item["raw"]
        instance_name = raw["instance"]
        k = raw["vehicles"]

        for run_index, run in enumerate(raw["runs"], start=1):
            if not run["initial_feasible"]:
                continue

            sa = run["simulated_annealing"]
            tabu = run["tabu_search"]

            sa_gen_s = f"{sa['generated_neighbors']:10d}" if sa else f"{'—':>10}"
            sa_acc_s = f"{sa['accepted_moves']:10d}" if sa else f"{'—':>10}"
            tabu_exp_s = f"{tabu['explored_neighbors']:12d}" if tabu else f"{'—':>12}"
            tabu_acc_s = f"{tabu['accepted_moves']:12d}" if tabu else f"{'—':>12}"

            lines.append(
                f"{instance_name:15} {run_index:3d} {k:4d} "
                f"{sa_gen_s} {sa_acc_s} {tabu_exp_s} {tabu_acc_s}"
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

        sa_sum = summary["simulated_annealing"]
        tabu_sum = summary["tabu_search"]
        summary_parts = [f"initial_avg={summary['initial_distance']['avg']:.2f}"]
        if sa_sum:
            summary_parts += [
                f"sa_avg={sa_sum['best_distance']['avg']:.2f}",
                f"sa_time={sa_sum['runtime_seconds']['avg']:.2f}",
                f"sa_generated={sa_sum['generated_neighbors']['avg']:.2f}",
            ]
        if tabu_sum:
            summary_parts += [
                f"tabu_avg={tabu_sum['best_distance']['avg']:.2f}",
                f"tabu_time={tabu_sum['runtime_seconds']['avg']:.2f}",
                f"tabu_explored={tabu_sum['explored_neighbors']['avg']:.2f}",
            ]
        handle.write("summary " + " ".join(summary_parts) + "\n")

        for run_index, run in enumerate(raw["runs"], start=1):
            if not run["initial_feasible"]:
                handle.write(f"run={run_index} seed={run['seed']} status=failed\n")
                continue

            run_parts = [
                f"run={run_index}",
                f"seed={run['seed']}",
                f"initial={run['initial_distance']:.2f}",
            ]
            if run["simulated_annealing"] is not None:
                sa = run["simulated_annealing"]
                run_parts += [
                    f"sa={sa['best_distance']:.2f}",
                    f"sa_time={sa['runtime_seconds']:.2f}",
                    f"sa_generated={sa['generated_neighbors']}",
                ]
            if run["tabu_search"] is not None:
                tb = run["tabu_search"]
                run_parts += [
                    f"tabu={tb['best_distance']:.2f}",
                    f"tabu_time={tb['runtime_seconds']:.2f}",
                    f"tabu_explored={tb['explored_neighbors']}",
                ]
            handle.write(" ".join(run_parts) + "\n")
