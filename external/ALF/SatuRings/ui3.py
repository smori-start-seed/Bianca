import threading
import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import saturings


# ============================================================
#  ROOT WINDOW
# ============================================================

root = tk.Tk()
root.title("SatuRings Control Panel")
root.geometry("500x900")


# ============================================================
#  VARIABLES
# ============================================================

drift_var = tk.DoubleVar(value=0.5)
harmony_var = tk.DoubleVar(value=0.5)
awareness_var = tk.DoubleVar(value=0.5)


# ============================================================
#  PORT SEND FUNCTIONS
# ============================================================

def send_Z():
    saturings.inject_Z(drift_var.get())
    status_label.config(text=f"Sent Z = {drift_var.get():.3f}")

def send_M():
    saturings.inject_M(harmony_var.get())
    status_label.config(text=f"Sent M = {harmony_var.get():.3f}")

def send_N():
    saturings.inject_N(awareness_var.get())
    status_label.config(text=f"Sent N = {awareness_var.get():.3f}")


# ============================================================
#  UI LAYOUT
# ============================================================

ttk.Label(root, text="Drift (Z)").pack()
ttk.Scale(root, from_=0, to=1, variable=drift_var, orient="horizontal").pack(fill="x")
ttk.Button(root, text="Send Z", command=send_Z).pack()

ttk.Label(root, text="Harmony (M)").pack()
ttk.Scale(root, from_=0, to=1, variable=harmony_var, orient="horizontal").pack(fill="x")
ttk.Button(root, text="Send M", command=send_M).pack()

ttk.Label(root, text="Awareness (N)").pack()
ttk.Scale(root, from_=0, to=1, variable=awareness_var, orient="horizontal").pack(fill="x")
ttk.Button(root, text="Send N", command=send_N).pack()

status_label = ttk.Label(root, text="Status: waiting...")
status_label.pack(pady=10)


# ============================================================
#  RING HARMONIES GRAPH
# ============================================================

fig_h = Figure(figsize=(4, 2), dpi=100)
ax_h = fig_h.add_subplot(111)
bars = ax_h.bar([1,2,3,4], [0,0,0,0])
ax_h.set_ylim(0, 1)
ax_h.set_title("Ring Harmonies")

canvas_h = FigureCanvasTkAgg(fig_h, master=root)
canvas_h.get_tk_widget().pack(fill="both", expand=True)


# ============================================================
#  AWARENESS OSCILLATOR
# ============================================================

fig_aw = Figure(figsize=(4, 2), dpi=100)
ax_aw = fig_aw.add_subplot(111)
ax_aw.set_ylim(0, 1)
ax_aw.set_title("Awareness Oscillator")

aw_x = list(range(200))
aw_y = [0] * 200
aw_line, = ax_aw.plot(aw_x, aw_y, color="orange")

canvas_aw = FigureCanvasTkAgg(fig_aw, master=root)
canvas_aw.get_tk_widget().pack(fill="both", expand=True)


# ============================================================
#  KERNEL HEATMAP
# ============================================================

fig_k = Figure(figsize=(5, 4), dpi=100)
ax_k = fig_k.add_subplot(111)
kernel_matrix = [[0]*12 for _ in range(24)]
heatmap = ax_k.imshow(kernel_matrix, cmap="viridis", vmin=0, vmax=1)
ax_k.set_title("Kernel Heatmap (24 Paare × 12 Kanäle)")

canvas_k = FigureCanvasTkAgg(fig_k, master=root)
canvas_k.get_tk_widget().pack(fill="both", expand=True)


# ============================================================
#  PAIR DETAIL WINDOW
# ============================================================

def show_pair_details(ring_i, pair_i):
    win = tk.Toplevel(root)
    win.title(f"Pair {ring_i+1}-{pair_i+1} Details")

    fig_p = Figure(figsize=(4, 2), dpi=100)
    ax_p = fig_p.add_subplot(111)

    pair = saturings.rings[ring_i][pair_i]
    k = pair["kernel"]

    labels = list(k.keys())
    values = list(k.values())

    ax_p.bar(labels, values)
    ax_p.set_ylim(0, 1)
    ax_p.set_title(f"Kernel Pair {ring_i+1}-{pair_i+1}")

    canvas_p = FigureCanvasTkAgg(fig_p, master=win)
    canvas_p.get_tk_widget().pack(fill="both", expand=True)


ttk.Button(root, text="Explode Pair 1-1",
           command=lambda: show_pair_details(0, 0)).pack(pady=10)


# ============================================================
#  UPDATE LOOP
# ============================================================

def update_status():
    # Status
    status_label.config(
        text=f"M={saturings.M:.3f} | N={saturings.N:.3f} | Awareness={saturings.AWARENESS['value']:.3f}"
    )

    # Ring Harmonies
    harmonies = saturings.compute_ring_harmonies(saturings.rings)
    for i, h in enumerate(harmonies):
        bars[i].set_height(h)
    canvas_h.draw()

    # Awareness Oscillator
    aw_y.pop(0)
    aw_y.append(saturings.AWARENESS["value"])
    aw_line.set_ydata(aw_y)
    canvas_aw.draw()

    # Kernel Heatmap
    kernel_matrix = []
    for ring in saturings.rings:
        for pair in ring:
            kernel_matrix.append(list(pair["kernel"].values()))
    kernel_matrix = kernel_matrix[:24]

    heatmap.set_data(kernel_matrix)
    canvas_k.draw()

    root.after(100, update_status)


# ============================================================
#  START SATURINGS THREAD
# ============================================================

def run_saturings():
    saturings.main_loop()

threading.Thread(target=run_saturings, daemon=True).start()


# ============================================================
#  START UI
# ============================================================

update_status()
root.mainloop()

