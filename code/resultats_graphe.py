import sys
import pandas as pd
import matplotlib.pyplot as plt


def lire_lignes(filename) :
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]


def detecter_format(lines) :
    """
    Retourne "taille" si on a des lignes 'N = M = ...',
    sinon "obstacles" si on a des lignes 'X obstacles :',
    sinon None.
    """
    has_nm = any("N = M =" in line for line in lines)
    if has_nm:
        return "taille"

    has_obstacles = any("obstacles" in line for line in lines)
    if has_obstacles:
        return "obstacles"

    return None


def extraire_entier_debut(tail):
    """"
    Extrait les premiers chiffres au début de la chaîne `tail`.
    Exemple : "10 donc 10 obstacles :" -> 10
              "20 obstacles :"         -> 20
    Retourne None si aucun chiffre.
    """
    num_str = ""
    for ch in tail.strip():
        if ch.isdigit():
            num_str += ch
        else:
            break
    if num_str == "":
        return None
    return int(num_str)


def extraire_entier_fin(tail) :
    """
    Extrait les premiers chiffres à partir du début de tail.
    Utilisé pour la partie après 'Temps minimal :'.
    Exemple : ' 12' -> 12, ' 12 bla' -> 12
    """
    num_str = ""
    for ch in tail.strip():
        if ch.isdigit():
            num_str += ch
        else:
            break
    if num_str == "":
        return None
    return int(num_str)


def parser_format_taille(lines):
    """
    Pour le fichier du type resultats_M_N_Obs.txt :
    """
    data = {}          # taille -> liste de temps
    current_size = None

    for line in lines:

        # Détection "N = M = 10 ..."
        if "N = M =" in line:
            tail = line.split("=")[-1]
            size = extraire_entier_debut(tail)
            if size is not None:
                current_size = size
                if current_size not in data:
                    data[current_size] = []
            else:
                current_size = None
            continue

        # Détection "Temps minimal : X"
        if "Temps minimal" in line:
            parts = line.split(":")
            if len(parts) >= 2 and current_size is not None:
                val = extraire_entier_fin(parts[-1])
                if val is not None:
                    data[current_size].append(val)
            continue

    # Construction des lignes pour le DataFrame
    rows = []
    for size, times in data.items():
        for i, t in enumerate(times, start=1):
            rows.append([size, i, t])
    return rows, "Taille", "Taille M = N", "Temps moyen par taille (N = M = Obs)"


def parser_format_obstacles(lines):
    """
    Pour le fichier du type resultats_20_20_Obs.txt :
    """
    data = {}          # nb_obstacles -> liste de temps
    current_obs = None

    for line in lines:

        # Détection "X obstacles :"
        if "obstacles" in line:
            # ex: "10 obstacles :", "30 obstacles :"
            # On prend le début de la ligne
            tokens = line.split()
            if tokens:
                # tokens[0] devrait être le nombre
                nb = extraire_entier_debut(tokens[0])
                if nb is not None:
                    current_obs = nb
                    if current_obs not in data:
                        data[current_obs] = []
            continue

        # Détection "Temps minimal : X"
        if "Temps minimal" in line:
            parts = line.split(":")
            if len(parts) >= 2 and current_obs is not None:
                val = extraire_entier_fin(parts[-1])
                if val is not None:
                    data[current_obs].append(val)
            continue

    rows = []
    for obs, times in data.items():
        for i, t in enumerate(times, start=1):
            rows.append([obs, i, t])
    return rows, "Obstacles", "Nombre d'obstacles", "Temps moyen en fonction du nombre d'obstacles (M = N = 20)"


def main():
    # Récupération du nom de fichier
    if len(sys.argv) >= 2:
        filename = sys.argv[1]
    else:
        # Tu peux mettre ici un nom par défaut si tu veux
        filename = "resultats_M_N_Obs.txt"

    lines = lire_lignes(filename)
    fmt = detecter_format(lines)

    if fmt is None:
        print("Format de fichier non reconnu (ni 'N = M =' ni 'obstacles').")
        sys.exit(1)

    if fmt == "taille":
        rows, group_col, x_label, title = parser_format_taille(lines)
    else:  # fmt == "obstacles"
        rows, group_col, x_label, title = parser_format_obstacles(lines)

    if not rows:
        print("Aucune donnée de temps trouvée dans le fichier.")
        sys.exit(0)

    # DataFrame
    df = pd.DataFrame(rows, columns=[group_col, "Instance", "Temps"])
    print("\n Tableau des Temps \n")
    print(df)

    # Moyennes
    avg = df.groupby(group_col)["Temps"].mean()
    print(f"\n Moyennes par {group_col.upper()}\n")
    print(avg)

    # Graphe
    plt.figure(figsize=(8, 5))
    plt.plot(avg.index, avg.values, marker="o")
    plt.xlabel(x_label)
    plt.ylabel("Temps moyen (secondes)")
    plt.title(title)
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    main()
