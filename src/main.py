from io_utils import parse_vrp_file
from evaluate import (
    distance_depot_to_client,
    distance_between_clients,
    total_demand,
    lower_bound_vehicles
)

def main_test_open_file():
    instance = parse_vrp_file("data/data101.vrp")

    print("Nom :", instance.name)
    print("Type :", instance.problem_type)
    print("Nombre de clients :", instance.nb_clients)
    print("Capacité max :", instance.max_quantity)
    print("Dépôt :", instance.depot)
    print("Client 1 :", instance.clients[1])
    print("Client 100 :", instance.clients[100])

def main_test_borne_inf():
    instance = parse_vrp_file("data/data101.vrp")

    print("Nom :", instance.name)
    print("Type :", instance.problem_type)
    print("Nombre de clients :", instance.nb_clients)
    print("Capacité max :", instance.max_quantity)
    print("Dépôt :", instance.depot)
    print("Client 1 :", instance.clients[1])
    print("Client 100 :", instance.clients[100])

    print("\n--- Tests utiles pour la question 2 ---")
    print("Distance dépôt -> client 1 :", distance_depot_to_client(instance, 1))
    print("Distance client 1 -> client 2 :", distance_between_clients(instance, 1, 2))
    print("Demande totale :", total_demand(instance))
    print("Borne inférieure véhicules :", lower_bound_vehicles(instance))

if __name__ == "__main__":
    #main_test_open_file()
    main_test_borne_inf()