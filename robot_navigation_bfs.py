
import sys
""" Pourquoi BFS ? 
    Cout uniforme = 1
    Cherche un temps minimal --> minimiser le nombre d'action et donc le nombre d'arcs
    Garantit un optimum
    Il peut s'arreter dès qu'un des sommet d'arrivée est atteint, reduction des calculs
"""


def compute_admissible_positions(obj) :
    """ 
    Avec une matrice d'obstacles obs[M][N] avec M le nombre de lignes et N le nombre 
    de colonnes, calcule les postitions possible pour le centre du robots. 
    Une position (i,j) est possible ssi les 4 cases autour sont libre. 
    retourne une matrice booléenne possble [M-1][N-1]
    """
    M = len(obj)
    N = 0  
    if M > 0 : 
        N = len(obj[0])
    

    possible = [[False for _ in range(N-1)] for _ in range (M-1)]

    for i in range (M-1):
        for j in range(N-1):
            if (obj[i][j] == 0 and
            obj[i+1][j] == 0 and
            obj[i][j+1] == 0 and
            obj[i+1][j+1] == 0): 
                possible[i][j] = True
    return possible

    #Fonction de rotations gauche/droite 
def turn_left(orientation) :
    return (orientation + 3) % 4 # -1 mod 4

def turn_right(orientation) : 
    return (orientation + 1) % 4 

def bfs_shortest_commands(obs, start_pos, start_orientation, end_pos) :
    """
    Calcule la liste de commande minimale permettant de passer de (start_pos,
    start_orientation) à end_pos (orientation finale libre).
    obs = matrice M*N : 1 si obstacle, 0 si libre
    start_pos, end_pos : position(i,j) des intesections (0 <= i <= M-2, 0 <= j <= N-2)
    start_orientation : 0=Nord(N); 1=Est(E); 2=Sud(S) et 3=Ouest(O)
    Retourne la liste de commande ou None si il y en a pas
    """
    possible = compute_admissible_positions(obs)
    M_pos = len(possible)
    N_pos = len(possible[0]) if M_pos > 0 else 0

    #Initialisation 
    si,sj = start_pos
    ei,ej = end_pos
    if not(0 <= si < M_pos and 0 <= sj < N_pos) : 
        raise ValueError("Position de départ en dehors des positions possible")
    if not (0 <= ei < M_pos and 0 <= ej < N_pos) :
        raise ValueError("Position d'arrivée en dehors des positions possible")
    if not possible[si][sj] : 
        raise ValueError("Position de départ non possible : Obstacles trop proches")
    if not possible[ei][ej] :
        raise ValueError("Position d'arrivée non possible : Obstacles trop proches")

    dir_vecteur = {
        0: (-1,0), # Nord
        1: (0,1),  # Est
        2: (1,0),  # Sud
        3: (0,-1), # Ouest
    }

    #Parcout en largeur BFS
    start_etat = (si,sj,start_orientation)
    queue = [start_etat] #File FIFO
    head = 0 
    visited = set([start_etat]) #Ensemble des etats visités
    parent = {start_etat: None} #Pour reconstruire le chemin; état précedent
    action_taken = {start_etat: None} #Action prise pour arriver à cet état
    found_end = None
    
    while head < len(queue) : 
        i, j, orientation = queue[head]
        head += 1
        
        #Vérifier si on est arrivé
        if (i,j) == (ei,ej) :
            found_end = (i,j,orientation)
            break
        #Générer les états successeurs
        #1. Tourner à gauche
        new_orientation = turn_left(orientation)
        new_etat = (i,j,new_orientation)
        if new_etat not in visited :
            visited.add(new_etat)
            parent[new_etat] = (i,j,orientation)
            action_taken[new_etat] = "G"
            queue.append(new_etat)
            
        #2. Tourner à droite
        new_orientation = turn_right(orientation)
        new_etat = (i,j,new_orientation)
        if new_etat not in visited :
            visited.add(new_etat)
            parent[new_etat] = (i,j,orientation)
            action_taken[new_etat] = "D"
            queue.append(new_etat)
        #3. Avancer
        di, dj = dir_vecteur[orientation]
        for step in [1,2,3] : #Peut avancer de 1,2 ou 3 cases 
            ci, cj = i, j 
            ok = True
            for _ in range(step) :
                ci += di
                cj += dj
                if not (0 <= ci < M_pos and 0 <= cj < N_pos) :
                    ok = False
                    break
                if not possible[ci][cj] :
                    ok = False
                    break
            if not ok :
                break #Ne peut pas avancer plus loin
            
            new_etat = (ci, cj, orientation)
            if new_etat not in visited :
                visited.add(new_etat)
                parent[new_etat] = (i,j,orientation)
                action_taken[new_etat] = f"a{step}"
                queue.append(new_etat)
        
    if found_end is None :
        return None #Aucune solution trouvée
    
    #Reconstruire le chemin
    commands = []
    etat = found_end
    while parent[etat] is not None :
        command = action_taken[etat]
        if command is None :
            break
        commands.append(command)
        etat = parent[etat]
    
    commands.reverse()
    return commands


def solve_all_instances(filename):
    """
    Lit un fichier contenant plusieurs instances au format :

        M N
        <M lignes de matrice>
        D1 D2 F1 F2 O
        0 0

    répété I fois.

    Pour chaque instance, affiche :
      - "Aucune solution trouvée." puis "-1" si aucun chemin
      - sinon :
            Suite de commandes optimale : [...]
            Temps minimal (secondes)    : k
            k cmd1 cmd2 ... cmdk
    """
    with open(filename, "r") as f:
        while True:
            # Lire la ligne "M N"
            header = f.readline()
            if not header:
                break  # fin de fichier
            header = header.strip()
            if not header:
                continue

            parts = header.split()
            if len(parts) != 2:
                break

            M, N = map(int, parts)

            # Lire la matrice MxN
            obs = []
            for _ in range(M):
                line = f.readline()
                if not line:
                    return
                row = list(map(int, line.split()))
                obs.append(row)

            # Lire la ligne "D1 D2 F1 F2 O"
            line = f.readline()
            if not line:
                return
            line = line.strip()
            parts = line.split()
            if len(parts) != 5:
                return

            D1 = int(parts[0])
            D2 = int(parts[1])
            F1 = int(parts[2])
            F2 = int(parts[3])
            O_char = parts[4]

            # Lire la ligne "0 0" de fin d'instance
            end_line = f.readline()
            if not end_line:
                return
            # on pourrait vérifier : end_line.strip() == "0 0"

            orient_map = {"N": 0, "E": 1, "S": 2, "O": 3}
            if O_char not in orient_map:
                print("Aucune solution trouvée.")
                print("-1")
                continue
            start_orient = orient_map[O_char]

            # Conversion coordonnées de cases -> indices internes (intersections)
            
            start_pos = (D1 - 1, D2 - 1)
            goal_pos  = (F1 - 1 , F2 - 1)

            try:
                cmds = bfs_shortest_commands(obs, start_pos, start_orient, goal_pos)
            except Exception:
                print("Aucune solution trouvée.")
                print("-1")
                continue
            
            # Affichage des résultats
            if cmds is None:
                print("Aucune solution trouvée. -1 ")
            else:
                # Ligne projet standard
                print(len(cmds), *cmds)


def main():
    if len(sys.argv) != 2:
        solve_all_instances("exemple_sujet.txt")
        sys.exit(1)

    filename = sys.argv[1]
    solve_all_instances(filename)


if __name__ == "__main__":
    main()