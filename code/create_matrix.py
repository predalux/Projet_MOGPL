import sys
import random
from robot_navigation_bfs import compute_admissible_positions



def generate_matrix(M, N, num_obstacles):
    """Génère une matrice MxN contenant environ obstacle_ratio de 1."""

    # Initialement tout à 0
    mat = [[0 for _ in range(N)] for _ in range(M)]

    # Tirage aléatoire de positions pour les obstacles
    all_positions = [(i, j) for i in range(M) for j in range(N)]
    obstacles = random.sample(all_positions, num_obstacles)

    for i, j in obstacles:
        mat[i][j] = 1

    return mat


def pick_valid_position(matrix,possible):
    """Choisit une position (i,j) dont la case vaut 0 dans la matrice possible."""
    M = len(possible)
    N = len(possible[0]) if M > 0 else 0

    valid_positions = [(i, j) for i in range(M) for j in range(N) if possible[i][j]]

    return random.choice(valid_positions)


def main():
    # Vérification des arguments
    if len(sys.argv) != 5:
        print("Usage : python create_matrix.py M N I Obs")
        sys.exit(1)

    M = int(sys.argv[1])
    N = int(sys.argv[2])
    I = int(sys.argv[3])
    Obs = int(sys.argv[4])
    filename = f"instance_{M}_{N}_{Obs}.txt"

    with open(filename, "w") as f:

        for _ in range(I):
            # Génération matrice
            matrix = generate_matrix(M, N, Obs)

            possible = compute_admissible_positions(matrix)

            # Choix aléatoire de départ et arrivée valides
            D1, D2 = pick_valid_position(matrix, possible)
            F1, F2 = pick_valid_position(matrix, possible)

            # Orientation aléatoire
            orientations = ["N", "E", "S", "O"]
            O = random.choice(orientations)

            possible_positions = [(i, j) for i in range(len(possible)) for j in range(len(possible[0])) if possible[i][j]]
            if len(possible_positions) > 1:
                while (F1, F2) == (D1, D2):
                    F1, F2 = pick_valid_position(matrix, possible)

            # Ligne 1 de l'instance
            f.write(f"{M} {N}\n")

            # Matrice
            for row in matrix:
                f.write(" ".join(map(str, row)) + "\n")

            # Ligne D1 D2 F1 F2 O (coordonnées de cases, donc +1)
            f.write(f"{D1 + 1} {D2 + 1} {F1 + 1} {F2 + 1} {O}\n")

            # Dernière ligne de l'instance
            f.write("0 0\n")
            
            # Espace entre les instances
            f.write("\n\n")

    print(f"Fichier '{filename}' généré avec succès avec {I} instances et {Obs} obstacles !")


if __name__ == "__main__":
    main()
