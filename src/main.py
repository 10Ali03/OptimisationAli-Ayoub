from io_utils import parse_vrp_file


def main_test_open_file():
    instance = parse_vrp_file("data/data101.vrp")

    print("Nom :", instance.name)
    print("Type :", instance.problem_type)
    print("Nombre de clients :", instance.nb_clients)
    print("Capacité max :", instance.max_quantity)
    print("Dépôt :", instance.depot)
    print("Client 1 :", instance.clients[1])
    print("Client 100 :", instance.clients[100])


if __name__ == "__main__":
    main_test_open_file()
