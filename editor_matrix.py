import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from robot_navigation_bfs import bfs_shortest_commands, compute_admissible_positions

class MatrixEditor:
    def __init__(self, root, M=10, N=10):
        self.root = root
        self.root.title("Matrix Editor")

        self.M = M
        self.N = N
        self.matrix = [[0 for _ in range(N)] for _ in range(M)]

        self.robot_pos = None
        self.robot_ori = "N"
        self.goal_pos = None
        self.path = []  # Stocker le chemin optimal
        self.path_positions = []  # Positions du robot le long du chemin

        self.mode = tk.StringVar(value="obstacle")
        self.dark_mode = False  # État du mode sombre
        self.update_colors()  # Initialiser les couleurs

        # Configurer les poids pour adaptation dynamique
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        # Créer un frame principal avec deux colonnes
        self.main_frame = ttk.Frame(root)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Frame pour le canvas
        self.canvas_frame = ttk.Frame(self.main_frame)
        self.canvas_frame.grid(row=0, column=0, sticky="nsew")
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.canvas_frame, bg=self.bg_color, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        # Frame pour les contrôles (sidebar)
        self.control_frame = ttk.Frame(self.main_frame, width=150)
        self.control_frame.grid(row=0, column=1, sticky="ns", padx=10, pady=10)
        self.control_frame.grid_propagate(False)
        
        # Stocker les widgets pour la reconfiguration
        self.style = ttk.Style()
        self.update_ttk_styles()
        
        self.dark_button = ttk.Button(self.control_frame, text="Dark Mode", command=self.toggle_dark_mode)
        self.dark_button.pack(fill="x", pady=(5, 5))

        ttk.Label(self.control_frame, text="Mode d'édition :").pack(pady=(10, 5))
        ttk.Radiobutton(self.control_frame, text="Obstacle", variable=self.mode, value="obstacle").pack(anchor="w")
        ttk.Radiobutton(self.control_frame, text="Robot", variable=self.mode, value="robot").pack(anchor="w")
        ttk.Radiobutton(self.control_frame, text="Arrivée", variable=self.mode, value="goal").pack(anchor="w")

        ttk.Label(self.control_frame, text="Orientation robot").pack(pady=(10, 5))
        self.ori_var = tk.StringVar(value=self.robot_ori)
        self.ori_menu = ttk.Combobox(self.control_frame, textvariable=self.ori_var, values=["N", "E", "S", "O"], state="readonly", width=10)
        self.ori_menu.bind("<<ComboboxSelected>>", lambda e: self.set_orientation(self.ori_var.get()))
        self.ori_menu.pack(fill="x", pady=(0, 10))

        ttk.Label(self.control_frame, text="Lignes (M)").pack(pady=(10, 0))
        self.m_entry = ttk.Entry(self.control_frame, width=10)
        self.m_entry.insert(0, str(self.M))
        self.m_entry.pack(fill="x", pady=(0, 5))

        ttk.Label(self.control_frame, text="Colonnes (N)").pack(pady=(5, 0))
        self.n_entry = ttk.Entry(self.control_frame, width=10)
        self.n_entry.insert(0, str(self.N))
        self.n_entry.pack(fill="x", pady=(0, 10))

        ttk.Button(self.control_frame, text="Appliquer", command=self.change_dimensions).pack(fill="x", pady=(10, 5))
        ttk.Button(self.control_frame, text="Résoudre", command=self.solve).pack(fill="x", pady=(5, 5))
        ttk.Button(self.control_frame, text="Sauver", command=self.save).pack(fill="x", pady=(5, 5))
        ttk.Button(self.control_frame, text="Ouvrir", command=self.open_file).pack(fill="x", pady=(5, 10))

        self.canvas_width = 600
        self.canvas_height = 600
        self.draw()
        
    def change_dimensions(self):
        try:
            new_M = int(self.m_entry.get())
            new_N = int(self.n_entry.get())
            if new_M < 1 or new_N < 1:
                raise ValueError("Dimensions invalides")
            # Conserver l'ancienne matrice 
            new_matrix = [[0 for _ in range(new_N)] for _ in range(new_M)]
            min_M = min(self.M, new_M)
            min_N = min(self.N, new_N)
            for i in range(min_M):
                for j in range(min_N):
                    new_matrix[i][j] = self.matrix[i][j]
            self.M = new_M
            self.N = new_N
            self.matrix = new_matrix
            # Conserver robot et arrivée si possible
            if self.robot_pos:
                i, j = self.robot_pos
                if i < new_M and j < new_N:
                    self.robot_pos = (i, j)
                else:
                    self.robot_pos = None
            if self.goal_pos:
                i, j = self.goal_pos
                if i < new_M and j < new_N:
                    self.goal_pos = (i, j)
                else:
                    self.goal_pos = None
            self.draw()
        except Exception as e:
            messagebox.showerror("Erreur", f"Dimensions invalides : {e}")

    def on_canvas_resize(self, event):
        self.canvas_width = event.width
        self.canvas_height = event.height
        self.draw()

    def update_colors(self):
        """Met à jour les couleurs en fonction du mode"""
        if self.dark_mode:
            self.bg_color = "#2b2b2b"  # Anthracite
            self.empty_color = "#3a3a3a"  # Gris foncé pour les cases vides
            self.obstacle_color = "#ff69b4"  # Rose
            self.robot_color = "red"
            self.arrow_color = "white"
            self.goal_color = "green"
            self.path_color = "orange"
            self.path_outline = "yellow"
        else:
            self.bg_color = "#f8f8ff"  # Blanc-gris clair
            self.empty_color = "white"
            self.obstacle_color = "deepskyblue"  # Bleu clair
            self.robot_color = "red"
            self.arrow_color = "darkred"
            self.goal_color = "green"
            self.path_color = "orange"
            self.path_outline = "orange"
    
    def update_ttk_styles(self):
        """Met à jour les styles ttk en fonction du mode"""
        if self.dark_mode:
            # Styles Dark Mode
            self.style.configure("TLabel", background="#2b2b2b", foreground="white")
            self.style.configure("TButton", background="#3a3a3a", foreground="white")
            self.style.map("TButton", background=[("active", "#4a4a4a"), ("pressed", "#1a1a1a")])
            self.style.configure("TRadiobutton", background="#2b2b2b", foreground="white")
            self.style.configure("TEntry", background="#3a3a3a", foreground="white", fieldbackground="#3a3a3a", insertcolor="white")
            self.style.configure("TCombobox", background="#3a3a3a", foreground="white", fieldbackground="#3a3a3a", insertcolor="white", arrowcolor="white")
            self.style.map("TCombobox", fieldbackground=[("readonly", "#3a3a3a")], background=[("active", "#4a4a4a")])
            self.style.configure("TFrame", background="#2b2b2b")
        else:
            # Styles clair (par défaut)
            self.style.configure("TLabel", background="#f8f8ff", foreground="black")
            self.style.configure("TButton", background="white", foreground="black")
            self.style.map("TButton", background=[("active", "#e0e0e0"), ("pressed", "#d0d0d0")])
            self.style.configure("TRadiobutton", background="#f8f8ff", foreground="black")
            self.style.configure("TEntry", background="white", foreground="black", fieldbackground="white", insertcolor="black")
            self.style.configure("TCombobox", background="white", foreground="black", fieldbackground="white", insertcolor="black", arrowcolor="black")
            self.style.map("TCombobox", fieldbackground=[("readonly", "white")], background=[("active", "#f0f0f0")])
            self.style.configure("TFrame", background="#f8f8ff")

    def toggle_dark_mode(self):
        """Bascule le mode sombre"""
        self.dark_mode = not self.dark_mode
        self.update_colors()
        self.update_ttk_styles()
        self.root.config(bg=self.bg_color)
        self.canvas.config(bg=self.bg_color)
        self.draw()

    def set_orientation(self, o):
        self.robot_ori = o
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        self.canvas.config(bg=self.bg_color) 
        w = self.canvas_width / self.N
        h = self.canvas_height / self.M
        for i in range(self.M):
            for j in range(self.N):
                x0, y0 = j*w, i*h
                x1, y1 = (j+1)*w, (i+1)*h
                color = self.empty_color
                if self.matrix[i][j] == 1:
                    color = self.obstacle_color
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color)

        # Dessiner le chemin optimal avec lignes de connexion
        if self.path_positions and len(self.path_positions) > 1:
            # Dessiner les lignes reliant les points
            for i in range(len(self.path_positions) - 1):
                pos1 = self.path_positions[i]
                pos2 = self.path_positions[i + 1]
                x1, y1 = (pos1[1]+1)*w, (pos1[0]+1)*h
                x2, y2 = (pos2[1]+1)*w, (pos2[0]+1)*h
                self.canvas.create_line(x1, y1, x2, y2, fill=self.path_color, width=2, dash=(4, 4))
            # Dessiner les points du chemin
            for pos in self.path_positions:
                i, j = pos
                cx, cy = (j+1)*w, (i+1)*h  # Bas-droit de l'intersection
                r = min(w, h)/10
                self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="yellow", outline=self.path_outline, width=2)
        elif self.path_positions:
            # Si un seul point
            pos = self.path_positions[0]
            i, j = pos
            cx, cy = (j+1)*w, (i+1)*h
            r = min(w, h)/10
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="yellow", outline=self.path_outline, width=2)

        # Dessiner l'arrivée à l'intersection
        if self.goal_pos:
            i, j = self.goal_pos
            cx, cy = (j+1)*w, (i+1)*h  # Bas-droit de l'intersection
            r = min(w, h)/6
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=self.goal_color)

        # Dessiner le robot à l'intersection (bas-droit)
        if self.robot_pos:
            i, j = self.robot_pos
            cx, cy = (j+1)*w, (i+1)*h  # Bas droit de l'intersection
            r = min(w, h)/6
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=self.robot_color, outline="darkred", width=2)

            # Flèche de direction
            arrow_len = min(w, h)/3
            arrow_width = 3
            if self.robot_ori == "N":
                self.canvas.create_line(cx, cy, cx, cy-arrow_len, arrow=tk.LAST, width=arrow_width, fill=self.arrow_color)
            elif self.robot_ori == "S":
                self.canvas.create_line(cx, cy, cx, cy+arrow_len, arrow=tk.LAST, width=arrow_width, fill=self.arrow_color)
            elif self.robot_ori == "E":
                self.canvas.create_line(cx, cy, cx+arrow_len, cy, arrow=tk.LAST, width=arrow_width, fill=self.arrow_color)
            elif self.robot_ori == "O":
                self.canvas.create_line(cx, cy, cx-arrow_len, cy, arrow=tk.LAST, width=arrow_width, fill=self.arrow_color)

    def on_click(self, event):
        w = self.canvas_width / self.N
        h = self.canvas_height / self.M
        j = int(event.x // w)
        i = int(event.y // h)
        # Vérifier que les coordonnées sont valides
        if 0 <= i < self.M and 0 <= j < self.N:
            if self.mode.get() == "obstacle":
                self.matrix[i][j] = 1 - self.matrix[i][j]
            elif self.mode.get() == "robot":
                self.robot_pos = (i, j)
            elif self.mode.get() == "goal":
                self.goal_pos = (i, j)
        self.draw()

    def save(self):
        if self.robot_pos is None or self.goal_pos is None:
            messagebox.showerror("Erreur", "Robot et arrivée requis")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if not path:
            return
        with open(path, "w") as f:
            f.write(f"{self.M} {self.N}\n")
            for row in self.matrix:
                f.write(" ".join(map(str, row)) + "\n")
            D1, D2 = self.robot_pos
            F1, F2 = self.goal_pos
            f.write(f"{D1+1} {D2+1} {F1+1} {F2+1} {self.robot_ori}\n")
            f.write("0 0\n")

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not path:
            return
        with open(path, "r") as f:
            lines = f.read().splitlines()
        try:
            self.M, self.N = map(int, lines[0].split())
            self.matrix = [list(map(int, line.split())) for line in lines[1:self.M+1]]
            D1, D2, F1, F2, O = lines[self.M+1].split()
            self.robot_pos = (int(D1)-1, int(D2)-1)
            self.goal_pos = (int(F1)-1, int(F2)-1)
            self.robot_ori = O
            self.ori_var.set(self.robot_ori)
            self.path = []
            self.path_positions = []
            self.draw()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger le fichier: {e}")

    def solve(self):
        """Résout le problème avec BFS et affiche le chemin optimal"""
        if self.robot_pos is None or self.goal_pos is None:
            messagebox.showerror("Erreur", "Robot et arrivée requis")
            return
        
        try:
            # Convertir l'orientation en nombre
            orient_map = {"N": 0, "E": 1, "S": 2, "O": 3}
            start_orient = orient_map[self.robot_ori]
            
            # Appeler BFS
            commands = bfs_shortest_commands(self.matrix, self.robot_pos, start_orient, self.goal_pos)
            
            if commands is None:
                messagebox.showinfo("Résultat", "Aucune solution trouvée.")
                self.path = []
                self.path_positions = []
                self.draw()
                return
            
            # Stocker le chemin et calculer les positions
            self.path = commands
            self.path_positions = self.compute_path_positions(self.robot_pos, start_orient, commands)
            
            # Afficher les résultats
            result_text = f"Chemin optimal trouvé!\n\nCommandes ({len(commands)}): {' '.join(commands)}"
            messagebox.showinfo("Résultat", result_text)
            self.draw()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la résolution: {str(e)}")

    def compute_path_positions(self, start_pos, start_ori, commands):
        """Calcule toutes les positions du robot en suivant les commandes"""
        positions = [start_pos]
        current_pos = start_pos
        current_ori = start_ori
        
        # Vecteurs de direction: 0=Nord, 1=Est, 2=Sud, 3=Ouest
        dir_vectors = {
            0: (-1, 0),  # Nord
            1: (0, 1),   # Est
            2: (1, 0),   # Sud
            3: (0, -1)   # Ouest
        }
        
        for cmd in commands:
            if cmd == "G":  # Tourner à gauche
                current_ori = (current_ori + 3) % 4
            elif cmd == "D":  # Tourner à droite
                current_ori = (current_ori + 1) % 4
            elif cmd.startswith("a"):  # Avancer
                steps = int(cmd[1])
                di, dj = dir_vectors[current_ori]
                for _ in range(steps):
                    current_pos = (current_pos[0] + di, current_pos[1] + dj)
                    positions.append(current_pos)
        
        return positions

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Matrix Editor")
    
    style = ttk.Style()
    style.theme_use('clam') 
    
    app = MatrixEditor(root)
    root.mainloop()