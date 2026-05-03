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

CVRP_SA    = [1266.78, 1292.26, 1634.58, 1611.01, 1250.95, 1245.11, 1311.63, 1327.29, 1197.26, 1151.47]
CVRP_TABU  = [1339.08, 1309.82, 1686.47, 1720.14, 1312.29, 1305.22, 1301.29, 1335.45, 1163.18, 1115.68]
CVRP_INIT  = [3655.35, 3537.80, 4718.01, 4675.37, 3519.79, 3542.86, 4613.08, 4366.31, 3580.75, 3379.92]

VRPTW_SA   = [1706.28, 1584.73, 1740.38, 1593.91, 1238.83, 1105.87, 1544.00, 1443.74, 1378.63, 1331.76]
VRPTW_TABU = [1683.01, 1488.40, 1713.19, 1532.88, 1190.92, 1060.79, 1445.97, 1360.69, 1268.26, 1156.67]

CVRP_TIME_SA   = [1.26, 1.11, 2.07, 2.06, 1.19, 1.13, 0.66, 0.65, 0.62, 0.55]
CVRP_TIME_TABU = [5.05, 4.57, 8.33, 8.41, 4.84, 4.55, 2.68, 2.66, 2.36, 2.29]
VRPTW_TIME_SA   = [56.81, 17.78, 31.90, 20.07, 13.34, 16.25, 12.31, 10.53,  9.35,  5.18]
VRPTW_TIME_TABU = [336.61, 88.36, 214.38, 127.15, 49.77, 68.33, 54.46, 44.16, 44.81, 21.02]

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
