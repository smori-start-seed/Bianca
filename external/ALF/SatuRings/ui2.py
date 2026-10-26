import threading
import tkinter as tk
from tkinter import ttk

# Importiere dein SatuRings-System
import saturings   # <-- dein großes Skript als Modul

#metplot für regler
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

root = tk.Tk()
root.title("SatuRings Control Panel")
root.geometry("400x600")

# --- Helper: send to ports ---
def send_Z():
    value = drift_var.get()
    saturings.inject_Z({"drift": value})
    status_label.config(text=f"Sent Z drift={value:.3f}")

def send_M():
    value = harmony_var.get()
    saturings.inject_M({"harmony": value})
    status_label.config(text=f"Sent M harmony={value:.3f}")

def send_N():
    value = awareness_var.get()
    saturings.inject_N({"awareness": value})
    status_label.config(text=f"Sent N awareness={value:.3f}")

# --- UI Variablen ---
drift_var = tk.DoubleVar(value=0.5)
harmony_var = tk.DoubleVar(value=0.5)
awareness_var = tk.DoubleVar(value=0.5)

# --- Slider ---
ttk.Label(root, text="Drift (Z)").pack()
ttk.Scale(root, from_=0, to=1, variable=drift_var, orient="horizontal").pack(fill="x")
ttk.Button(root, text="Send to Z", command=send_Z).pack()

ttk.Label(root, text="Harmony (M)").pack()
ttk.Scale(root, from_=0, to=1, variable=harmony_var, orient="horizontal").pack(fill="x")
ttk.Button(root, text="Send to M", command=send_M).pack()

ttk.Label(root, text="Awareness (N)").pack()
ttk.Scale(root, from_=0, to=1, variable=awareness_var, orient="horizontal").pack(fill="x")
ttk.Button(root, text="Send to N", command=send_N).pack()

# --- Live-Anzeige ---
status_label = ttk.Label(root, text="Status: waiting...")
status_label.pack(pady=20)
# --- Graph für Ring-Harmonien ---
fig = Figure(figsize=(4, 2), dpi=100)
ax = fig.add_subplot(111)
bars = ax.bar([1,2,3,4], [0,0,0,0])
ax.set_ylim(0, 1)
ax.set_title("Ring Harmonies")

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill="both", expand=True)

# --- Awareness Oscillator Graph ---
fig_aw = Figure(figsize=(4, 2), dpi=100)
ax_aw = fig_aw.add_subplot(111)
ax_aw.set_ylim(0, 1)
ax_aw.set_title("Awareness Oscillator")

# 200 Punkte für die Wellenform
aw_x = list(range(200))
aw_y = [0] * 200
aw_line, = ax_aw.plot(aw_x, aw_y, color="orange")

canvas_aw = FigureCanvasTkAgg(fig_aw, master=root)
canvas_aw.get_tk_widget().pack(fill="both", expand=True)

# --- Kernel Heatmap ---
fig_k = Figure(figsize=(5, 4), dpi=100)
ax_k = fig_k.add_subplot(111)
kernel_matrix = [[0]*12 for _ in range(24)]
heatmap = ax_k.imshow(kernel_matrix, cmap="viridis", vmin=0, vmax=1)
ax_k.set_title("Kernel Heatmap (24 Paare × 12 Kanäle)")
canvas_k = FigureCanvasTkAgg(fig_k, master=root)
canvas_k.get_tk_widget().pack(fill="both", expand=True)

def update_status():
    # Text aktualisieren
    status_label.config(
        text=f"M={saturings.M:.3f} | N={saturings.N:.3f} | Awareness={saturings.AWARENESS['value']:.3f}"
    )

    # Ring-Harmonien aktualisieren
    harmonies = saturings.compute_ring_harmonies(saturings.rings)
    for i, h in enumerate(harmonies):
        bars[i].set_height(h)
    canvas.draw()

    # Awareness-Wellenform aktualisieren
    aw_y.pop(0)
    aw_y.append(saturings.AWARENESS["value"])
    aw_line.set_ydata(aw_y)
    canvas_aw.draw()

    # NACH allen Updates erneut planen
    root.after(100, update_status)

def show_pair_details(ring_i, pair_i):
    win = tk.Toplevel(root)
    win.title(f"Pair {ring_i+1}-{pair_i+1} Details")

    fig_p = Figure(figsize=(4, 2), dpi=100)
    ax_p = fig_p.add_subplot(111)

    pair = saturings.rings[ring_i][pair_i]
    k = pair["kernel"]

    values = [
        k["R"], k["G"], k["B"], k["Y"], k["C"], k["M"],
        k["O"], k["P"], k["W"], k["K"], k["L"], k["S"]
    ]
    labels = ["R","G","B","Y","C","M","O","P","W","K","L","S"]

    ax_p.bar(labels, values)
    ax_p.set_ylim(0, 1)
    ax_p.set_title(f"Kernel Pair {ring_i+1}-{pair_i+1}")

    canvas_p = FigureCanvasTkAgg(fig_p, master=win)
    canvas_p.get_tk_widget().pack(fill="both", expand=True)

# Button für Explosionsansicht
    ttk.Button(root, text="Explode Pair 1-1",
        command=lambda: show_pair_details(0, 0)).pack()

    # Awareness-Wellenform aktualisieren
    aw_y.pop(0)
    aw_y.append(saturings.AWARENESS["value"])
    aw_line.set_ydata(aw_y)
    canvas_aw.draw()

# --- SatuRings in Thread starten ---
def run_saturings():
    saturings.main_loop()   # du musst deine while True in eine Funktion packen

threading.Thread(target=run_saturings, daemon=True).start()
update_status()
root.mainloop()
