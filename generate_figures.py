import sys
import math
import random
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from io_utils import parse_vrp_file
from construction import build_solution_with_k_vehicles, generate_random_solution, find_minimum_vehicles
from evaluate import evaluate_solution
from neighbors import random_neighbor, generate_sampled_neighbors

# ---------------------------------------------------------------------------
# Données des campagnes longues (improved_long_cvrp.log / vrptw.log)
# ---------------------------------------------------------------------------

INSTANCES = ["data101", "data102", "data1101", "data1102", "data111",
             "data112", "data1201", "data1202", "data201", "data202"]

CVRP_SA    = [1488.99, 1572.25, 1971.79, 1988.77, 1531.17, 1484.82, 1531.84, 1594.21, 1276.75, 1313.29]
CVRP_TABU  = [1776.59, 1846.33, 2301.35, 2344.61, 1806.32, 1831.06, 1870.48, 1892.68, 1614.32, 1525.08]
CVRP_INIT  = [3649.06, 3647.26, 4635.30, 4783.86, 3498.39, 3629.29, 4441.38, 4483.64, 3432.02, 3451.40]

VRPTW_SA   = [1744.18, 1624.00, 1800.45, 1692.94, 1321.15, 1167.36, 1704.66, 1604.65, 1513.91, 1514.41]
VRPTW_TABU = [1746.76, 1536.16, 1790.35, 1652.58, 1310.27, 1182.16, 1506.00, 1499.79, 1310.55, 1238.85]

CVRP_TIME_SA   = [0.51, 0.56, 0.76, 0.74, 0.54, 0.70, 0.54, 0.62, 0.45, 0.52]
CVRP_TIME_TABU = [1.19, 1.33, 1.77, 1.94, 1.44, 1.62, 1.29, 1.43, 1.11, 1.21]
VRPTW_TIME_SA   = [38.22, 6.23, 9.42, 8.23, 4.13, 4.27, 4.13, 3.67, 3.71, 1.92]
VRPTW_TIME_TABU = [163.55, 28.60, 58.78, 31.51, 13.85, 15.17, 16.49, 11.09, 11.54, 5.04]

# ---------------------------------------------------------------------------
# 1. Comparaison distances
# ---------------------------------------------------------------------------

def fig_comparison_distances():
    x = np.arange(len(INSTANCES))
    width = 0.15

    fig, ax = plt.subplots(figsize=(16, 6))
    ax.bar(x - 2*width, CVRP_INIT,  width, label="CVRP - initiale",        color="#c5cae9", alpha=0.85)
    ax.bar(x - 1*width, CVRP_SA,    width, label="CVRP - recuit simulé",   color="#2e7d32", alpha=0.85)
    ax.bar(x,           CVRP_TABU,  width, label="CVRP - recherche tabou", color="#e64a19", alpha=0.85)
    ax.bar(x + 1*width, VRPTW_SA,   width, label="VRPTW - recuit simulé",  color="#1a237e", alpha=0.85)
    ax.bar(x + 2*width, VRPTW_TABU, width, label="VRPTW - recherche tabou",color="#f9a825", alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels(INSTANCES, fontsize=9)
    ax.set_ylabel("Distance")
    ax.set_title("Comparaison des distances finales moyennes")
    ax.legend(fontsize=8, loc="upper right")
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.savefig("figures/comparison_distances.png", dpi=150)
    plt.close()
    print("comparison_distances.png généré")


# ---------------------------------------------------------------------------
# 2. Comparaison temps
# ---------------------------------------------------------------------------

def fig_comparison_times():
    x = np.arange(len(INSTANCES))
    width = 0.2

    fig, ax = plt.subplots(figsize=(16, 6))
    ax.bar(x - 1.5*width, CVRP_TIME_SA,    width, label="CVRP - recuit simulé",   color="#2e7d32", alpha=0.85)
    ax.bar(x - 0.5*width, CVRP_TIME_TABU,  width, label="CVRP - recherche tabou", color="#e64a19", alpha=0.85)
    ax.bar(x + 0.5*width, VRPTW_TIME_SA,   width, label="VRPTW - recuit simulé",  color="#1a237e", alpha=0.85)
    ax.bar(x + 1.5*width, VRPTW_TIME_TABU, width, label="VRPTW - recherche tabou",color="#f9a825", alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels(INSTANCES, fontsize=9)
    ax.set_ylabel("Temps (s)")
    ax.set_title("Comparaison des temps moyens d'exécution")
    ax.legend(fontsize=8)
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.savefig("figures/comparison_times.png", dpi=150)
    plt.close()
    print("comparison_times.png généré")


# ---------------------------------------------------------------------------
# Helpers : SA et Tabou avec suivi de convergence
# ---------------------------------------------------------------------------

def sa_convergence(instance, initial_routes, check_time_windows=False,
                   max_iterations=2500, initial_temperature=150.0,
                   cooling_rate=0.997, seed=42):
    rng = random.Random(seed)
    current_routes = [list(r) for r in initial_routes]
    current_distance = evaluate_solution(instance, current_routes,
                                         check_time_windows=check_time_windows)["distance"]
    best_distance = current_distance
    temperature = initial_temperature
    history = [best_distance]

    for _ in range(max_iterations):
        if temperature < 1e-3:
            break
        candidate = random_neighbor(instance, current_routes,
                                    rng=rng, check_time_windows=check_time_windows,
                                    max_attempts_per_operator=100)
        if candidate is not None:
            d = evaluate_solution(instance, candidate,
                                  check_time_windows=check_time_windows)["distance"]
            delta = d - current_distance
            if delta <= 0 or rng.random() < math.exp(-delta / temperature):
                current_routes = [list(r) for r in candidate]
                current_distance = d
                if current_distance < best_distance:
                    best_distance = current_distance
        temperature *= cooling_rate
        history.append(best_distance)

    return history


def tabu_convergence(instance, initial_routes, check_time_windows=False,
                     max_iterations=40, tabu_tenure=20, max_neighbors=150, seed=42):
    from collections import deque
    rng = random.Random(seed)
    current_routes = [list(r) for r in initial_routes]
    current_distance = evaluate_solution(instance, current_routes,
                                         check_time_windows=check_time_windows)["distance"]
    best_distance = current_distance

    tabu_q = deque([tuple(tuple(r) for r in current_routes)], maxlen=tabu_tenure)
    tabu_s = {tabu_q[0]}

    history = [best_distance]

    for _ in range(max_iterations):
        neighbors = generate_sampled_neighbors(instance, current_routes,
                                               rng=rng,
                                               check_time_windows=check_time_windows,
                                               max_neighbors=max_neighbors)
        if not neighbors:
            break

        best_c = None
        best_cd = float("inf")
        for cand in neighbors:
            cd = evaluate_solution(instance, cand,
                                   check_time_windows=check_time_windows)["distance"]
            sig = tuple(tuple(r) for r in cand)
            if sig in tabu_s and cd >= best_distance:
                continue
            if cd < best_cd:
                best_c, best_cd = cand, cd

        if best_c is None:
            break

        current_routes = [list(r) for r in best_c]
        current_distance = best_cd
        sig = tuple(tuple(r) for r in current_routes)
        if len(tabu_q) == tabu_q.maxlen:
            tabu_s.discard(tabu_q.popleft())
        tabu_q.append(sig)
        tabu_s.add(sig)

        if current_distance < best_distance:
            best_distance = current_distance

        history.append(best_distance)

    return history


# ---------------------------------------------------------------------------
# 3. Convergence data101 CVRP
# ---------------------------------------------------------------------------

def fig_convergence_cvrp():
    instance = parse_vrp_file("data/data101.vrp")
    found_k, routes = find_minimum_vehicles(instance)
    initial = generate_random_solution(instance, k=found_k, seed=42)
    if initial is None:
        initial = routes

    print("  Calcul SA CVRP data101...")
    sa_hist = sa_convergence(instance, initial, check_time_windows=False, seed=42)

    print("  Calcul Tabou CVRP data101...")
    tabu_hist = tabu_convergence(instance, initial, check_time_windows=False, seed=42)

    n_sa = len(sa_hist)
    n_tabu = len(tabu_hist)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(range(n_sa), sa_hist, color="#2e7d32", linewidth=1.5, label="Recuit simulé")

    # Tabou : étaler les n_tabu points sur l'axe [0, n_sa-1]
    if n_tabu > 1:
        tabu_x = np.linspace(0, n_sa - 1, n_tabu)
    else:
        tabu_x = [0]
    ax.plot(tabu_x, tabu_hist, color="#e64a19", linewidth=1.5, label="Recherche tabou")

    ax.set_xlabel("Itérations")
    ax.set_ylabel("Meilleure distance connue")
    ax.set_title("Convergence sur data101.vrp en CVRP (preset long)")
    ax.legend()
    ax.grid(linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.savefig("figures/convergence_data101_cvrp.png", dpi=150)
    plt.close()
    print("convergence_data101_cvrp.png généré")


# ---------------------------------------------------------------------------
# 4. Convergence data1201 VRPTW
# ---------------------------------------------------------------------------

def fig_convergence_vrptw():
    instance = parse_vrp_file("data/data1201.vrp")
    found_k, routes = find_minimum_vehicles(instance, max_extra=25, check_time_windows=True)
    initial = build_solution_with_k_vehicles(instance, found_k, check_time_windows=True)
    if initial is None:
        initial = routes

    print("  Calcul SA VRPTW data1201...")
    sa_hist = sa_convergence(instance, initial, check_time_windows=True, seed=42)

    print("  Calcul Tabou VRPTW data1201...")
    tabu_hist = tabu_convergence(instance, initial, check_time_windows=True, seed=42)

    n_sa = len(sa_hist)
    n_tabu = len(tabu_hist)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(range(n_sa), sa_hist, color="#2e7d32", linewidth=1.5, label="Recuit simulé")

    if n_tabu > 1:
        tabu_x = np.linspace(0, n_sa - 1, n_tabu)
    else:
        tabu_x = [0]
    ax.plot(tabu_x, tabu_hist, color="#e64a19", linewidth=1.5, label="Recherche tabou")

    ax.set_xlabel("Itérations")
    ax.set_ylabel("Meilleure distance connue")
    ax.set_title("Evolution de la distance sur data1201.vrp en VRPTW (preset long)")
    ax.legend()
    ax.grid(linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.savefig("figures/convergence_data1201_vrptw.png", dpi=150)
    plt.close()
    print("convergence_data1201_vrptw.png généré")


# ---------------------------------------------------------------------------
# 5. Routes data1201 comparaison CVRP vs VRPTW
# ---------------------------------------------------------------------------

def fig_routes_data1201():
    from meta.simulated_annealing import simulated_annealing
    from meta.tabu_search import tabu_search

    instance = parse_vrp_file("data/data1201.vrp")
    depot = instance.depot

    # CVRP : recuit simulé
    k_cvrp, _ = find_minimum_vehicles(instance, check_time_windows=False)
    init_cvrp = generate_random_solution(instance, k=k_cvrp, seed=0)
    sa_result = simulated_annealing(instance, initial_routes=init_cvrp, seed=0,
                                    check_time_windows=False,
                                    max_iterations=2500, initial_temperature=150.0,
                                    cooling_rate=0.997)
    routes_cvrp = sa_result.best_routes

    # VRPTW : tabou
    k_vrptw, _ = find_minimum_vehicles(instance, max_extra=25, check_time_windows=True)
    init_vrptw = build_solution_with_k_vehicles(instance, k_vrptw, check_time_windows=True)
    tabu_result = tabu_search(instance, initial_routes=init_vrptw, seed=0,
                              check_time_windows=True,
                              max_iterations=40, tabu_tenure=20, max_neighbors=150)
    routes_vrptw = tabu_result.best_routes

    colors = plt.cm.tab10.colors

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for ax, routes, title in [
        (axes[0], routes_cvrp, f"CVRP – {len(routes_cvrp)} véhicules (recuit simulé)"),
        (axes[1], routes_vrptw, f"VRPTW – {len(routes_vrptw)} véhicules (recherche tabou)"),
    ]:
        ax.scatter(depot.x, depot.y, s=120, c="black", zorder=5, marker="s")
        ax.annotate("Dépôt", (depot.x, depot.y), textcoords="offset points",
                    xytext=(5, 5), fontsize=7)

        for i, route in enumerate(routes):
            color = colors[i % len(colors)]
            xs = [depot.x] + [instance.clients[c].x for c in route] + [depot.x]
            ys = [depot.y] + [instance.clients[c].y for c in route] + [depot.y]
            ax.plot(xs, ys, color=color, linewidth=1.2, alpha=0.8)
            for c in route:
                ax.scatter(instance.clients[c].x, instance.clients[c].y,
                           s=25, c=[color], zorder=4)

        ax.set_title(title, fontsize=10)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.grid(linestyle="--", alpha=0.3)

    plt.suptitle("Visualisation des tournées — data1201.vrp", fontsize=12)
    plt.tight_layout()
    plt.savefig("figures/routes_data1201_comparison.png", dpi=150)
    plt.close()
    print("routes_data1201_comparison.png généré")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    os.makedirs("figures", exist_ok=True)

    print("=== Génération des figures ===")
    fig_comparison_distances()
    fig_comparison_times()

    print("Convergence CVRP data101...")
    fig_convergence_cvrp()

    print("Convergence VRPTW data1201...")
    fig_convergence_vrptw()

    print("Routes data1201...")
    fig_routes_data1201()

    print("=== Terminé ===")
