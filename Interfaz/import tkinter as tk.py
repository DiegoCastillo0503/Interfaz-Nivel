import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import time
import threading

# Variables globales
nivel = 50
setpoint = 70
kp = 1.0
ki = 0.0
kd = 0.0
error_anterior = 0
integral = 0

datos_nivel = []
datos_tiempo = []

# Función PID
def calcular_pid(setpoint, nivel):
    global error_anterior, integral
    
    error = setpoint - nivel
    integral += error
    derivada = error - error_anterior
    
    salida = kp * error + ki * integral + kd * derivada
    
    error_anterior = error
    return salida

# Simulación del tanque
def actualizar():
    global nivel
    
    while True:
        control = calcular_pid(setpoint, nivel)
        
        # Simulación dinámica simple
        nivel += control * 0.01
        
        # Saturación
        if nivel > 100:
            nivel = 100
        if nivel < 0:
            nivel = 0
        
        datos_nivel.append(nivel)
        datos_tiempo.append(time.time())
        
        if len(datos_nivel) > 100:
            datos_nivel.pop(0)
            datos_tiempo.pop(0)
        
        actualizar_grafica()
        actualizar_tanque()
        
        time.sleep(0.1)

def actualizar_grafica():
    ax.clear()
    ax.plot(datos_nivel)
    ax.set_ylim(0,100)
    canvas.draw()

def actualizar_tanque():
    canvas_tanque.delete("nivel")
    altura = 200 * (nivel / 100)
    canvas_tanque.create_rectangle(50, 250-altura, 150, 250, fill="blue", tags="nivel")

def iniciar():
    hilo = threading.Thread(target=actualizar)
    hilo.daemon = True
    hilo.start()

def actualizar_pid():
    global kp, ki, kd
    kp = float(entry_kp.get())
    ki = float(entry_ki.get())
    kd = float(entry_kd.get())

# Ventana principal
root = tk.Tk()
root.title("Control de Nivel PID")

# Tanque
canvas_tanque = tk.Canvas(root, width=200, height=300)
canvas_tanque.pack(side=tk.LEFT)

# Gráfica
fig, ax = plt.subplots(figsize=(4,3))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.RIGHT)

# Panel PID
frame_pid = tk.Frame(root)
frame_pid.pack()

tk.Label(frame_pid, text="Kp").grid(row=0,column=0)
entry_kp = tk.Entry(frame_pid)
entry_kp.insert(0,"1.0")
entry_kp.grid(row=0,column=1)

tk.Label(frame_pid, text="Ki").grid(row=1,column=0)
entry_ki = tk.Entry(frame_pid)
entry_ki.insert(0,"0.0")
entry_ki.grid(row=1,column=1)

tk.Label(frame_pid, text="Kd").grid(row=2,column=0)
entry_kd = tk.Entry(frame_pid)
entry_kd.insert(0,"0.0")
entry_kd.grid(row=2,column=1)

tk.Button(frame_pid, text="Actualizar PID", command=actualizar_pid).grid(row=3,column=0,columnspan=2)
tk.Button(frame_pid, text="Iniciar", command=iniciar).grid(row=4,column=0,columnspan=2)

root.mainloop()