import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import requests
import json

# API KEY de OpenRouter
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# -------------------------------
# Clase que representa un Riesgo
# -------------------------------
class Riesgo:
    def __init__(self, nombre, probabilidad, impacto):
        self.nombre = nombre
        self.probabilidad = probabilidad
        self.impacto = impacto
        self.prioridad = self.calcular_prioridad()
        self.categoria = self.categorizar_prioridad()
        self.mitigacion = self.sugerir_mitigacion()

    def calcular_prioridad(self):
        return round(self.probabilidad * self.impacto, 2)

    def categorizar_prioridad(self):
        if self.prioridad < 3:
            return "Bajo"
        elif 3 <= self.prioridad < 6:
            return "Medio"
        else:
            return "Alto"

    def sugerir_mitigacion(self):
        try:
            prompt = (
                        f"Proporcióname tres estrategias concreta y breve para mitigar el riesgo '{self.nombre}', "
                        f"con prioridad {self.categoria}. No incluyas más de opciónes ni nada de conlcuiones ni otra cosa mas que las sugerencias."
                    )

            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "X-Title": "SimuladorTP2"
                },
                data=json.dumps({
                    "model": "deepseek/deepseek-prover-v2:free",
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()

        except Exception as e:
            print(f"Error al obtener mitigación: {e}")
            return "Mitigación no disponible."

    def __str__(self):
        return (f"Riesgo: {self.nombre}\n"
                f"Probabilidad: {self.probabilidad}\n"
                f"Impacto: {self.impacto}\n"
                f"Prioridad: {self.prioridad} ({self.categoria})\n"
                f"Estrategia: {self.mitigacion}\n")

# -------------------------------
# Funciones de la Interfaz
# -------------------------------
riesgos_generados = []

def generar_riesgo_aleatorio():
    prompt = (
        "Genera un riesgo aleatorio de proyecto en formato JSON. "
        "Debe incluir: nombre (str), probabilidad (float entre 0.1 y 1.0), impacto (int entre 1 y 10). "
        "Ejemplo de salida: {\"nombre\": \"Falla en el servidor\", \"probabilidad\": 0.75, \"impacto\": 9} "
        "Solo responde con el JSON."
    )
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "X-Title": "SimuladorTP2"
            },
            data=json.dumps({
                "model": "deepseek/deepseek-prover-v2:free",
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        response.raise_for_status()

        # Imprimir la respuesta cruda para depurar
        print(f"Respuesta cruda de la API: {response.text}")

        # Verificar si la respuesta es vacía o inválida
        if not response.text.strip():
            raise ValueError("Respuesta vacía de la API")

        # Extraer el JSON dentro del bloque de código
        contenido = response.json()["choices"][0]["message"]["content"].strip()
        json_string = contenido.replace("```json\n", "").replace("\n```", "")  # Eliminar las marcas de código
        
        # Parsear el contenido como JSON
        datos = json.loads(json_string)
        nombre = datos["nombre"]
        probabilidad = float(datos["probabilidad"])
        impacto = int(datos["impacto"])

        riesgo = Riesgo(nombre, probabilidad, impacto)
        riesgos_generados.append(riesgo)
        mostrar_riesgos()

    except requests.exceptions.HTTPError as http_err:
        print(f"Error HTTP: {http_err}")
        messagebox.showerror("Error HTTP", f"Error en la API: {http_err}")
    except ValueError as ve:
        print(f"Error de valor: {ve}")
        messagebox.showerror("Error de valor", f"Respuesta vacía o no válida de la API.\n{ve}")
    except Exception as e:
        print(f"Error general: {e}")
        messagebox.showerror("Error", f"No se pudo generar riesgo desde la API.\n{e}")

def generar_varios_riesgos():
    try:
        cantidad = int(simpledialog.askinteger("Cantidad", "¿Cuántos riesgos desea generar?", minvalue=1, maxvalue=100))
        for _ in range(cantidad):
            generar_riesgo_aleatorio()
    except:
        messagebox.showerror("Error", "Ingrese un número válido.")

def ingresar_riesgo_manual():
    nombre = simpledialog.askstring("Nombre del Riesgo", "Ingrese el nombre del riesgo:")
    if not nombre:
        return

    nivel = ""
    while nivel not in ["bajo", "medio", "alto"]:
        nivel = simpledialog.askstring("Nivel del Riesgo", "Ingrese el nivel (bajo, medio, alto):")
        if nivel:
            nivel = nivel.lower()

    if nivel == "bajo":
        probabilidad = round(random.uniform(0.1, 0.3), 2)
        impacto = random.randint(1, 3)
    elif nivel == "medio":
        probabilidad = round(random.uniform(0.4, 0.6), 2)
        impacto = random.randint(4, 6)
    else:
        probabilidad = round(random.uniform(0.7, 1.0), 2)
        impacto = random.randint(7, 10)

    riesgo = Riesgo(nombre, probabilidad, impacto)
    riesgos_generados.append(riesgo)
    mostrar_riesgos()

def mostrar_riesgos():
    texto = "\n".join([str(r) for r in riesgos_generados])
    salida_text.delete(1.0, tk.END)
    salida_text.insert(tk.END, texto)

def exportar_a_txt():
    if not riesgos_generados:
        messagebox.showinfo("Exportar", "No hay riesgos para exportar.")
        return

    with open("riesgos_exportados.txt", "w") as f:
        for r in riesgos_generados:
            f.write(str(r) + "\n")

    messagebox.showinfo("Exportar", "Riesgos exportados correctamente.")

def limpiar():
    riesgos_generados.clear()
    salida_text.delete(1.0, tk.END)

# -------------------------------
# Interfaz Gráfica (Tkinter)
# -------------------------------
ventana = tk.Tk()
ventana.title("Simulador de Riesgos - TP2")
ventana.geometry("700x500")

# Título
titulo = ttk.Label(ventana, text="Simulador de Riesgos en Sprints Ágiles", font=("Arial", 16, "bold"))
titulo.pack(pady=10)

# Botones
frame_botones = ttk.Frame(ventana)
frame_botones.pack(pady=5)

ttk.Button(frame_botones, text="Generar 1 Riesgo Aleatorio", command=generar_riesgo_aleatorio).grid(row=0, column=0, padx=5, pady=5)
ttk.Button(frame_botones, text="Generar Varios Riesgos", command=generar_varios_riesgos).grid(row=0, column=1, padx=5, pady=5)
ttk.Button(frame_botones, text="Ingresar Riesgo Manual", command=ingresar_riesgo_manual).grid(row=0, column=2, padx=5, pady=5)

# Texto de salida
salida_text = tk.Text(ventana, height=15, width=80, font=("Courier", 10))
salida_text.pack(pady=10)

# Botones inferiores
frame_exportar = ttk.Frame(ventana)
frame_exportar.pack(pady=5)

ttk.Button(frame_exportar, text="Exportar a .txt", command=exportar_a_txt).grid(row=0, column=0, padx=10)
ttk.Button(frame_exportar, text="Limpiar", command=limpiar).grid(row=0, column=1, padx=10)

# Ejecutar
ventana.mainloop()
