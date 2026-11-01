import random
import gurobipy as gp
from gurobipy import GRB
from robot_navigation_bfs import compute_admissible_positions



def generate_obstacle_grid(M, N, P, seed=0):
    random.seed(seed)

    # 1) Génération des poids aléatoires w_ij
    poids= [[random.randint(0, 1000) for _ in range(N)] for _ in range(M)]

    # 2) Paramètres
    L_max = 2 * P // M
    C_max = 2 * P // N

    # 3) Modèle Gurobi
    model = gp.Model("obstacle_placement")
    model.Params.LogToConsole = 0  # silence terminal

    # Variables binaires x_ij
    x = model.addVars(M, N, vtype=GRB.BINARY)

    # Objectif
    model.setObjective(
        gp.quicksum(poids[i][j] * x[i, j] for i in range(M) for j in range(N)),
        GRB.MINIMIZE,
    )

    # Total d'obstacles
    model.addConstr(gp.quicksum(x[i, j] for i in range(M) for j in range(N)) == P)

    # Bornes par ligne
    for i in range(M):
        model.addConstr(gp.quicksum(x[i, j] for j in range(N)) <= L_max)

    # Bornes par colonne
    for j in range(N):
        model.addConstr(gp.quicksum(x[i, j] for i in range(M)) <= C_max)

    # Interdiction du motif 1 0 1 sur lignes
    for i in range(M):
        for j in range(N - 2):
            model.addConstr(x[i, j] + x[i, j + 2] - x[i, j + 1] <= 1)

    # Interdiction du motif 1 0 1 sur colonnes
    for j in range(N):
        for i in range(M - 2):
            model.addConstr(x[i, j] + x[i + 2, j] - x[i + 1, j] <= 1)

    # Résolution
    model.optimize()

    if model.status != GRB.OPTIMAL:
        print("Aucune solution optimale trouvée.")
        return None, None

    # Extraction grille
    grille = [[0 for _ in range(N)] for _ in range(M)]
    for i in range(M):
        for j in range(N):
            if x[i, j].X > 0.5:
                grille[i][j] = 1

    return grille


def pick_admissible_positions(grid):
    """
    Calcule les positions admissibles (intersections) et
    choisit (D1,D2) et (F1,F2) parmi elles.
    """
    admissible = compute_admissible_positions(grid)
    M_pos = len(admissible)
    N_pos = len(admissible[0]) if M_pos > 0 else 0

    candidates = [(i, j)
                  for i in range(M_pos)
                  for j in range(N_pos)
                  if admissible[i][j]]

    if len(candidates) < 2:
        raise ValueError("Pas assez de positions admissibles pour départ/arrivée.")

    D1, D2 = random.choice(candidates)
    F1, F2 = random.choice(candidates)
    while (F1, F2) == (D1, D2):
        F1, F2 = random.choice(candidates)

    return D1, D2, F1, F2



def write_instance_file(filename, M, N, grid):
    """
    Génère un fichier d'instance compatible avec robot_navigation_bfs2.py.
    Les positions départ/arrivée sont choisies parmi les intersections admissibles
    (zones 2×2 libres), afin de garantir que le BFS puisse les utiliser.
    """

    # Choix de positions admissibles : évite les erreurs du BFS
    D1, D2, F1, F2 = pick_admissible_positions(grid)

    # Orientation initiale aléatoire
    orientation = random.choice(["N", "E", "S", "O"])

    with open(filename, "w") as f:
        # Dimensions
        f.write(f"{M} {N}\n")

        # Matrice des obstacles
        for row in grid:
            f.write(" ".join(map(str, row)) + "\n")

        # +1 car le BFS convertit ensuite en indices internes (coordonnées 1-based)
        f.write(f"{D1+1} {D2+1} {F1+1} {F2+1} {orientation}\n")

        # Fin d'instance
        f.write("0 0\n")



def main():
    print("Génération PL via Gurobi")
    M = int(input("Donner M (lignes) : "))
    N = int(input("Donner N (colonnes) : "))
    P = int(input("Donner P (obstacles) : "))

    grille = generate_obstacle_grid(M, N, P, seed=42)

    if grille is None:
        return

    print("\nGrille générée :\n")
    for r in grille:
        print(" ".join(str(x) for x in r))

    # Création du fichier instance_PL.txt
    write_instance_file("instance_PL.txt", M, N, grille)


if __name__ == "__main__":
    main()
