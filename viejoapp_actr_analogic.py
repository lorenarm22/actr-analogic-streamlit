
import streamlit as st
import math
import random
import csv
import os
from datetime import datetime
import matplotlib.pyplot as plt

# Parámetros globales
F = 0.5
UMBRAL_RECUPERACION = 1.5

# Definición de clases
class Chunk:
    def __init__(self, concepto, definicion, analogia=None, fuente_externa=None):
        self.concepto = concepto
        self.definicion = definicion
        self.analogia = analogia
        self.fuente_externa = fuente_externa
        self.frecuencia = 1
        self.recencia = 1
        self.associaciones = {}
        self.estimulo_externo = 0.0
        self.ruido = random.gauss(0, 0.1)

    def calcular_activacion(self, contexto=None, pesos=None):
        B = math.log(self.frecuencia / self.recencia + 1)
        suma_asociaciones = 0
        if contexto and pesos:
            for j, c in enumerate(contexto):
                fuerza = self.associaciones.get(c, 0.0)
                suma_asociaciones += pesos[j] * fuerza
        A = B + suma_asociaciones + self.estimulo_externo + self.ruido
        self.activacion = A
        return A

    def tiempo_recuperacion(self):
        return F * math.exp(-self.activacion)

class MemoriaDeclarativa:
    def __init__(self):
        self.chunks = []

    def agregar(self, chunk):
        self.chunks.append(chunk)

    def buscar(self, termino, contexto=None, pesos=None, externo=False):
        mejor_chunk = None
        max_A = float('-inf')

        for ch in self.chunks:
            ch.recencia += 1

        for ch in self.chunks:
            if termino.lower() in ch.concepto.lower():
                if externo:
                    ch.estimulo_externo = 0.5
                A = ch.calcular_activacion(contexto, pesos)
                if A > max_A:
                    max_A = A
                    mejor_chunk = ch

        if mejor_chunk and max_A > UMBRAL_RECUPERACION:
            mejor_chunk.recencia = 1
            mejor_chunk.frecuencia += 1
            return mejor_chunk
        return None

# Inicializar conceptos
def crear_memoria_iso():
    memoria = MemoriaDeclarativa()

    chunks_data = [
        ("Enfoque basado en procesos", "Gestión de actividades como procesos interrelacionados que contribuyen al valor del cliente.",
         "Como una orquesta: cada instrumento (proceso) aporta a la sinfonía.", "Foro ISO, infografía digital, simulación empresarial",
         {"orquesta": 0.8, "flujo": 0.6}),
        ("Mejora continua", "Compromiso permanente con la mejora del desempeño global.",
         "Como escalar una montaña paso a paso.", "Estudio de caso, retroalimentación grupal",
         {"montaña": 0.9, "escalada": 0.6}),
        ("Enfoque al cliente", "Satisfacer y superar las expectativas del cliente es el objetivo central.",
         "Como un restaurante que adapta sus recetas según las opiniones de los comensales.", "Encuestas de satisfacción, plataformas de reseñas",
         {"cliente": 0.9, "satisfacción": 0.7}),
        ("Liderazgo", "Los líderes establecen dirección y fomentan una cultura de compromiso.",
         "Como el capitán de un barco que guía el rumbo de su tripulación.", "Simuladores de liderazgo, entrevistas con directivos",
         {"capitán": 0.85, "dirección": 0.6}),
        ("Toma de decisiones basada en la evidencia", "Las decisiones eficaces se fundamentan en el análisis de datos y hechos.",
         "Como un médico que receta basado en exámenes clínicos, no suposiciones.", "Indicadores de gestión, trazabilidad, informes analíticos",
         {"datos": 0.8, "hechos": 0.7}),
    ]

    for concepto, definicion, analogia, fuente, asociaciones in chunks_data:
        c = Chunk(concepto, definicion, analogia, fuente)
        c.associaciones = asociaciones
        memoria.agregar(c)

    return memoria

# Archivo para guardar registro
registro_file = "registros_aprendizaje.csv"

def guardar_registro(concepto, analogia_sist, analogia_pers, csd, activacion, tiempo):
    existe = os.path.exists(registro_file)
    with open(registro_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(["Fecha", "Concepto", "Analogía_Sugerida", "Analogía_Personal", "Elementos_CSD", "Activación", "Tiempo_Recuperacion"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), concepto, analogia_sist, analogia_pers, csd, round(activacion,2), round(tiempo,2)])

# INTERFAZ STREAMLIT
st.set_page_config(page_title="ACTR-Analogic ISO 9001", layout="centered")
st.title("🧠 Simulación Cognitiva ACTR-Analogic")
st.markdown("Simula el aprendizaje de los principios de la norma ISO 9001:2015")

memoria = crear_memoria_iso()
conceptos = [ch.concepto for ch in memoria.chunks]

seleccion = st.selectbox("📘 Selecciona un concepto para aprender:", conceptos)

palabras = st.text_input("🔎 Ingresa palabras clave relacionadas (separadas por espacio):")
contexto = palabras.strip().split()
pesos = [1.0 / len(contexto)] * len(contexto) if contexto else []

if st.button("🚀 Iniciar Simulación"):
    chunk = memoria.buscar(seleccion, contexto, pesos, externo=True)
    if chunk:
        st.success("✅ Concepto recuperado correctamente.")
        st.write("**Definición:**", chunk.definicion)
        st.write("**Analogía sugerida:**", chunk.analogia)
        st.write("**Fuente externa sugerida:**", chunk.fuente_externa)

        analogia_pers = st.text_input("✍️ Escribe tu propia analogía:")
        csd = st.text_input("🌐 Herramientas, personas o recursos externos usados:")

        if st.button("💾 Guardar Registro"):
            guardar_registro(chunk.concepto, chunk.analogia, analogia_pers, csd, chunk.activacion, chunk.tiempo_recuperacion())
            st.success("📁 Registro guardado exitosamente.")
    else:
        st.error("❌ No se pudo recuperar el concepto. Intenta con otro contexto.")
