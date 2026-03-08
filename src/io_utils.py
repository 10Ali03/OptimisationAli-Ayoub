from dataclasses import dataclass
from pathlib import Path


@dataclass
class Depot:
    id_name: str
    x: float
    y: float
    ready_time: float
    due_time: float


@dataclass
class Client:
    id_name: str
    x: float
    y: float
    ready_time: float
    due_time: float
    demand: int
    service: float


@dataclass
class VRPTWInstance:
    name: str
    comment: str
    problem_type: str
    coordinates_type: str
    nb_depots: int
    nb_clients: int
    max_quantity: int
    depot: Depot
    clients: dict   # clé = int (1..n), valeur = Client


def parse_vrp_file(filepath: str) -> VRPTWInstance:
    """
    Lit un fichier .vrp et retourne une instance structurée.
    """
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {filepath}")

    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]

    # On enlève uniquement les lignes totalement vides
    lines = [line for line in lines if line != ""]

    # Métadonnées
    name = ""
    comment = ""
    problem_type = ""
    coordinates_type = ""
    nb_depots = 0
    nb_clients = 0
    max_quantity = 0

    depot = None
    clients = {}

    current_section = None  # None / DEPOTS / CLIENTS

    for line in lines:
        # -----------------------------
        # Sections
        # -----------------------------
        if line.startswith("DATA_DEPOTS"):
            current_section = "DEPOTS"
            continue

        if line.startswith("DATA_CLIENTS"):
            current_section = "CLIENTS"
            continue

        # -----------------------------
        # Métadonnées
        # -----------------------------
        if ":" in line and current_section is None:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            if key == "NAME":
                name = value
            elif key == "COMMENT":
                comment = value
            elif key == "TYPE":
                problem_type = value
            elif key == "COORDINATES":
                coordinates_type = value
            elif key == "NB_DEPOTS":
                nb_depots = int(value)
            elif key == "NB_CLIENTS":
                nb_clients = int(value)
            elif key == "MAX_QUANTITY":
                max_quantity = int(value)

            continue

        # -----------------------------
        # Lecture dépôt
        # -----------------------------
        if current_section == "DEPOTS":
            parts = line.split()

            if len(parts) != 5:
                raise ValueError(f"Ligne dépôt invalide : {line}")

            depot = Depot(
                id_name=parts[0],
                x=float(parts[1]),
                y=float(parts[2]),
                ready_time=float(parts[3]),
                due_time=float(parts[4]),
            )

            # Comme on n'a qu'un dépôt dans tes fichiers
            current_section = None
            continue

        # -----------------------------
        # Lecture clients
        # -----------------------------
        if current_section == "CLIENTS":
            parts = line.split()

            if len(parts) != 7:
                raise ValueError(f"Ligne client invalide : {line}")

            client_id_name = parts[0]

            if not client_id_name.startswith("c"):
                raise ValueError(f"Identifiant client invalide : {client_id_name}")

            client_id = int(client_id_name[1:])

            clients[client_id] = Client(
                id_name=client_id_name,
                x=float(parts[1]),
                y=float(parts[2]),
                ready_time=float(parts[3]),
                due_time=float(parts[4]),
                demand=int(parts[5]),
                service=float(parts[6]),
            )

    # -----------------------------
    # Vérifications finales
    # -----------------------------
    if depot is None:
        raise ValueError("Aucun dépôt trouvé dans le fichier.")

    if len(clients) != nb_clients:
        raise ValueError(
            f"Nombre de clients incohérent : attendu {nb_clients}, lu {len(clients)}"
        )

    return VRPTWInstance(
        name=name,
        comment=comment,
        problem_type=problem_type,
        coordinates_type=coordinates_type,
        nb_depots=nb_depots,
        nb_clients=nb_clients,
        max_quantity=max_quantity,
        depot=depot,
        clients=clients,
    )