import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import networkx as nx
from ant_controller import AntController
from data_service import DataService
import time

jalur_macet = [
    ("S.Rajawali", "S.Charitas", 1),
    ("S.Rajawali", "S.4 Kuto", 1),
    ('M.Salim', 'S.Charitas', 1),
    ('K.Ion', 'S.Charitas', 1),
    ('Sudirman', 'Rs.Charitas', 1)
]

class MyGui:
    def __init__(self, data_source):
        self.universitas_map = {
            "UKMS": "Universitas Katolik",
            "UIBA": "Universitas IBA",
            "UMDP": "Universitas MDP"
        }
        self.universitas_labels = list(self.universitas_map.values())
        self.universitas_values = list(self.universitas_map.keys())

        self.data_service = DataService(data_source)
        self.data = self.data_service.fetch_data(data_source)
        self.node_indices = self.data_service.get_node_indices(self.data)
        self.node_names = list(self.node_indices.keys())
        self.distances = self.data_service.get_distance(self.data, self.node_indices, [])

    def run(self):
        self.launch_gui()

    def launch_gui(self):
        self.window = tk.Tk()
        self.window.title("AntColony")

        tk.Label(self.window, text="Universitas)").pack()
        self.start_combo = ttk.Combobox(self.window, values=self.universitas_labels, state="readonly")
        self.start_combo.pack()

        tk.Label(self.window, text="Rumah Sakit").pack()
        tujuan_default = ["Rs.Charitas", "Rs.Pelabuhan"]
        self.goal_combo = ttk.Combobox(self.window, values=tujuan_default)
        self.goal_combo.set('')
        self.goal_combo.pack()

        param_frame = tk.Frame(self.window)
        param_frame.pack(pady=5)

        def add_param(label_text, default_value):
            frame = tk.Frame(param_frame)
            frame.pack(anchor='w')
            tk.Label(frame, text=label_text).pack(side=tk.LEFT)
            var = tk.StringVar(value=str(default_value))
            entry = tk.Entry(frame, textvariable=var, width=6)
            entry.pack(side=tk.LEFT)
            return var

        self.n_ants_var = add_param("Jumlah Ant (n_ants): ", 50)
        self.n_best_var = add_param("Jumlah Best (n_best): ", 10)
        self.n_iter_var = add_param("Jumlah Iterasi (n_iterations): ", 100)
        self.decay_var = add_param("Decay (0-1): ", 0.8)
        self.alpha_var = add_param("Alpha (pheromone): ", 1)
        self.beta_var = add_param("Beta (heuristic): ", 1)

        tk.Label(self.window, text="⚙️ Kepadatan:").pack()
        self.traffic_entries = {}
        for asal, tujuan, default in jalur_macet:
            frame = tk.Frame(self.window)
            frame.pack(padx=5, pady=2, anchor='w')
            tk.Label(frame, text=f"{asal} → {tujuan}: ").pack(side=tk.LEFT)
            var = tk.StringVar(value=str(default))
            self.traffic_entries[(asal, tujuan)] = var
            tk.Entry(frame, textvariable=var, width=6).pack(side=tk.LEFT)

        self.result_label = tk.Label(self.window, text="", fg="red")
        self.result_label.pack(pady=10)

        self.canvas_widget = None

        tk.Button(self.window, text="Search", command=self.show_route).pack(pady=5)

        self.window.mainloop()

    def show_route(self):
        selected_label = self.start_combo.get().strip()
        goal = self.goal_combo.get().strip()

        if not selected_label:
            self.result_label.config(text="Harap pilih Universitas!")
            return

        try:
            idx = self.universitas_labels.index(selected_label)
            start_code = self.universitas_values[idx]
        except ValueError:
            self.result_label.config(text="Universitas tidak valid!")
            return

        if start_code not in self.node_indices:
            self.result_label.config(text="Universitas tidak ditemukan.")
            return

        try:
            n_ants = int(self.n_ants_var.get())
            n_best = int(self.n_best_var.get())
            n_iter = int(self.n_iter_var.get())
            decay = float(self.decay_var.get())
            alpha = float(self.alpha_var.get())
            beta = float(self.beta_var.get())
        except Exception:
            self.result_label.config(text="Parameter tidak valid!")
            return

        traffic_settings = []
        for (asal, tujuan), var in self.traffic_entries.items():
            try:
                val = float(var.get())
                if val <= 0:
                    val = 1.0
            except Exception:
                val = 1.0
            traffic_settings.append((asal, tujuan, val))

        distances_updated = self.data_service.get_distance(self.data, self.node_indices, traffic_settings)

        ant = AntController(
            distances_updated,
            n_ants=n_ants,
            n_best=n_best,
            n_iterations=n_iter,
            decay=decay,
            alpha=alpha,
            beta=beta
        )

        start_time = time.perf_counter()

        if not goal:
            possible_goals = ["Rs.Charitas", "Rs.Pelabuhan"]
            best_route = None
            best_dist = float('inf')
            best_goal = None

            for g in possible_goals:
                if g not in self.node_indices:
                    continue
                res = ant.find_best_route(self.node_indices[start_code], self.node_indices[g])
                if res is None or res[0] is None:
                    continue
                route, dist = res
                if dist < best_dist:
                    best_route = route
                    best_dist = dist
                    best_goal = g

            if best_route is None:
                self.result_label.config(text="Rute tidak ditemukan.")
                return

            route = best_route
            dist = best_dist
            tujuan = best_goal
        else:
            if goal not in self.node_indices:
                self.result_label.config(text="Rumah Sakit tidak ditemukan.")
                return

            res = ant.find_best_route(self.node_indices[start_code], self.node_indices[goal])
            if res is None or res[0] is None:
                self.result_label.config(text="Rute Tidak ditemukan.")
                return
            route, dist = res
            tujuan = goal

        end_time = time.perf_counter()
        exec_time = end_time - start_time

        readable = AntController.translate_route(route, self.node_names)

        self.result_label.config(text=f"Tujuan: {tujuan}  |  Jarak: {dist:.2f}  |  Waktu: {exec_time:.3f} detik")

        G = nx.DiGraph()
        for u, v in readable:
            G.add_edge(u, v)

        fig = plt.figure(figsize=(6, 4))
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=1000, arrows=True)

        if self.canvas_widget:
            self.canvas_widget.get_tk_widget().destroy()

        self.canvas_widget = FigureCanvasTkAgg(fig, master=self.window)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack()