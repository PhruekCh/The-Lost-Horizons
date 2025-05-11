import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk
import threading

battle_records = []

def save_battle_record(battle_dict):
    battle_records.append(battle_dict.copy())

def get_aggregated_data():
    return battle_records

def open_stats_window():
    if not battle_records:
        print("No data to plot yet.")
        return

    def show():
        root = tk.Tk()
        root.title("Custom Battle Statistics")

        fig, axs = plt.subplots(2, 2, figsize=(12, 8))
        fig.tight_layout(pad=4.0)

        data = get_aggregated_data()
        stages = [f"Stage {i+3}" for i in range(len(data))]

        element_dmg = {"fire": 0, "wind": 0, "water": 0}
        quick_dmg = charge_dmg = 0

        for b in data:
            quick_dmg += b.get("quick_dmg", 0)
            charge_dmg += b.get("charge_dmg", 0)
            for e in element_dmg:
                element_dmg[e] += b.get("element_dmg", {}).get(e, 0)

        attack_types = ["Special Attack", "Quick Attack", "Charge", "Heal (HP)"]
        attack_values = [
            sum(b.get("element_dmg", {}).get(e, 0) for e in ["fire", "wind", "water"]),
            sum(b.get("quick_dmg", 0) for b in data),
            sum(b.get("charge_dmg", 0) for b in data),
            sum(b.get("heal_amount", 0) for b in data),
        ]


        axs[0, 0].bar(attack_types, attack_values, color=["gray", "purple", "red", "green", "blue"])
        axs[0, 0].set_title("Total Damage by Attack Type")
        axs[0, 0].set_ylabel("Damage Done")

        player_dmg = [b.get("player_dmg", 0) for b in data]
        enemy_dmg = [b.get("enemy_dmg", 0) for b in data]
        axs[0, 1].plot(stages, player_dmg, label="Player", marker="o")
        axs[0, 1].plot(stages, enemy_dmg, label="Enemy", marker="x")
        axs[0, 1].set_title("Damage Distribution per Stage")
        axs[0, 1].legend()
        axs[0, 1].set_ylabel("Damage")


        axs[1, 1].boxplot([
            [b.get("player_dmg", 0) for b in data],
            [b.get("enemy_dmg", 0) for b in data]
        ], vert=True, labels=["Player", "Enemy"])
        axs[1, 1].set_title("Damage Distribution (Box)")

        total_received = sum(b.get("dmg_received", 0) for b in data)
        total_done = sum(b.get("player_dmg", 0) for b in data)
        axs[1, 0].pie(
            [total_received, total_done],
            labels=["Damage Received", "Damage Dealt"],
            autopct="%1.1f%%",
            colors=["orange", "cyan"]
        )
        axs[1, 0].set_title("Total Damage Share")

        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack()

        table_frame = tk.Frame(root)
        table_frame.pack(pady=10)

        columns = ("stage", "dmg_received", "player_dmg", "heal_amount", "crits")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col.replace("_", " ").title())

        for i, b in enumerate(data):
            crits = b.get("crits", 0)  # must be collected in game
            tree.insert("", "end", values=(
                f"Stage {i+1}",
                b.get("dmg_received", 0),
                b.get("player_dmg", 0),
                b.get("heal_amount", 0),
                crits
            ))

        tree.pack()

        root.mainloop()

    threading.Thread(target=show, daemon=True).start()