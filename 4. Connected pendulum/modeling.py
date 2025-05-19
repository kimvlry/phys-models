import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def calculate_and_plot():
    try:
        # # Считывание параметров
        m = float(entry_m.get())          # mass of pendulums (kg)
        L = float(entry_L.get())          # length of pendulum string (m)
        L1 = float(entry_L1.get())        # distance from suspension point to spring attachment (m)
        k = float(entry_k.get())          # spring stiffness (N/m)
        beta = float(entry_beta.get())    # damping coefficient (kg/s)

        phi1_0 = float(entry_phi1.get())  # initial angle of first pendulum (rad)
        phi2_0 = float(entry_phi2.get())  # initial angle of second pendulum (rad)

        v1_0 = float(entry_v1.get())      # initial angular velocity of first pendulum (rad/s)
        v2_0 = float(entry_v2.get())      # initial angular velocity of second pendulum (rad/s)

        t_max = float(entry_time.get())   # maximum simulation time (s)

        t = np.linspace(0, t_max, 1000)

        # Система ОДУ
        def system(y, t, m, L, L1, k, beta, g=9.81):
            phi1, v1, phi2, v2 = y
            K = k * L1 ** 2 / (m * L ** 2)
            omega0_sq = g / L
            dydt = [
                v1,
                -(beta / m) * v1 - (omega0_sq + K) * phi1 + K * phi2,
                v2,
                -(beta / m) * v2 - (omega0_sq + K) * phi2 + K * phi1
            ]
            return dydt

        # Решение
        y0 = [phi1_0, v1_0, phi2_0, v2_0]
        sol = odeint(system, y0, t, args=(m, L, L1, k, beta))
        phi1, v1, phi2, v2 = sol[:, 0], sol[:, 1], sol[:, 2], sol[:, 3]

        # Очистка предыдущих графиков
        for widget in graph_frame.winfo_children():
            widget.destroy()

        # Создание новых графиков
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
        ax1.plot(t, phi1, label='φ₁(t)')
        ax1.plot(t, phi2, label='φ₂(t)')
        ax1.set_xlabel('Время (с)')
        ax1.set_ylabel('Угол (рад)')
        ax1.legend()

        ax2.plot(t, v1, label='v₁(t)')
        ax2.plot(t, v2, label='v₂(t)')
        ax2.set_xlabel('Время (с)')
        ax2.set_ylabel('Скорость (рад/с)')
        ax2.legend()

        plt.tight_layout()

        # Встраивание в Tkinter
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    except ValueError as e:
        error_label.config(text=f"Ошибка: {str(e)}")


# Создание GUI
root = tk.Tk()
root.title("Связанные маятники")

input_frame = ttk.Frame(root, padding="10")
input_frame.pack(side=tk.LEFT, fill=tk.Y)

# Поля ввода
ttk.Label(input_frame, text="Масса (kg):").grid(row=0, column=0, sticky="w")
entry_m = ttk.Entry(input_frame)
entry_m.grid(row=0, column=1)
entry_m.insert(0, "1.0")

ttk.Label(input_frame, text="Длина подвеса (m):").grid(row=1, column=0, sticky="w")
entry_L = ttk.Entry(input_frame)
entry_L.grid(row=1, column=1)
entry_L.insert(0, "1.0")

ttk.Label(input_frame, text="L1 (m):").grid(row=2, column=0, sticky="w")
entry_L1 = ttk.Entry(input_frame)
entry_L1.grid(row=2, column=1)
entry_L1.insert(0, "0.5")

ttk.Label(input_frame, text="Жесткость пружины (N/m):").grid(row=3, column=0, sticky="w")
entry_k = ttk.Entry(input_frame)
entry_k.grid(row=3, column=1)
entry_k.insert(0, "10.0")

ttk.Label(input_frame, text="Коэф. затухания (kg/s):").grid(row=4, column=0, sticky="w")
entry_beta = ttk.Entry(input_frame)
entry_beta.grid(row=4, column=1)
entry_beta.insert(0, "0.1")

ttk.Label(input_frame, text="Начальный θ1 (rad):").grid(row=5, column=0, sticky="w")
entry_phi1 = ttk.Entry(input_frame)
entry_phi1.grid(row=5, column=1)
entry_phi1.insert(0, "0.1")

ttk.Label(input_frame, text="Начальный θ2 (rad):").grid(row=6, column=0, sticky="w")
entry_phi2 = ttk.Entry(input_frame)
entry_phi2.grid(row=6, column=1)
entry_phi2.insert(0, "0.0")

ttk.Label(input_frame, text="Начальная v1 (rad/s):").grid(row=7, column=0, sticky="w")
entry_v1 = ttk.Entry(input_frame)
entry_v1.grid(row=7, column=1)
entry_v1.insert(0, "0.0")

ttk.Label(input_frame, text="Начальная v2 (rad/s):").grid(row=8, column=0, sticky="w")
entry_v2 = ttk.Entry(input_frame)
entry_v2.grid(row=8, column=1)
entry_v2.insert(0, "0.0")

ttk.Label(input_frame, text="Время моделирования (s):").grid(row=9, column=0, sticky="w")
entry_time = ttk.Entry(input_frame)
entry_time.grid(row=9, column=1)
entry_time.insert(0, "10")

calculate_btn = ttk.Button(input_frame, text="Рассчитать", command=calculate_and_plot)
calculate_btn.grid(row=10, columnspan=2, pady=10)

error_label = ttk.Label(input_frame, text="", foreground="red")
error_label.grid(row=11, columnspan=2)

graph_frame = ttk.Frame(root)
graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

root.mainloop()