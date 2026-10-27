import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import matplotlib.pyplot as plt


# =========================================================
# ESCENARIOS DE LA PRÁCTICA
# =========================================================

ESCENARIOS = {
    "A - Condición inicial": {
        "P": 60,
        "k": 1
    },

    "B - Menor carga": {
        "P": 35,
        "k": 1
    },

    "C - Mejor ventilación": {
        "P": 60,
        "k": 2
    }
}


# =========================================================
# VARIABLES GLOBALES
# =========================================================

resultados = {}

animando = False
segundo_actual = 0
temperaturas_animacion = []
tiempos_animacion = []


# =========================================================
# SIMULACIÓN
# =========================================================

def simular_escenario(T_inicial, T_ambiente, C, duracion, P, k):

    tiempos = []
    temperaturas = []

    T = T_inicial

    for t in range(duracion + 1):

        tiempos.append(t)
        temperaturas.append(T)

        # Ecuación del modelo
        T = T + (
            (P - k * (T - T_ambiente)) / C
        )

    return tiempos, temperaturas


# =========================================================
# BUSCAR PRIMERA ALERTA
# =========================================================

def buscar_alerta(tiempos, temperaturas, umbral):

    for i in range(len(temperaturas)):

        if temperaturas[i] >= umbral:
            return tiempos[i]

    return None


# =========================================================
# EJECUTAR A, B Y C
# =========================================================

def ejecutar_simulacion():

    try:

        T_inicial = float(entrada_inicial.get())
        T_ambiente = float(entrada_ambiente.get())
        C = float(entrada_capacidad.get())
        duracion = int(entrada_duracion.get())
        umbral = float(entrada_umbral.get())

        if C <= 0:
            raise ValueError

        if duracion <= 0:
            raise ValueError

    except ValueError:

        messagebox.showerror(
            "Error",
            "Introduce valores numéricos válidos."
        )

        return


    resultados.clear()


    for nombre, datos in ESCENARIOS.items():

        P = datos["P"]
        k = datos["k"]

        tiempos, temperaturas = simular_escenario(
            T_inicial,
            T_ambiente,
            C,
            duracion,
            P,
            k
        )

        alerta = buscar_alerta(
            tiempos,
            temperaturas,
            umbral
        )

        resultados[nombre] = {
            "tiempos": tiempos,
            "temperaturas": temperaturas,
            "P": P,
            "k": k,
            "alerta": alerta
        }


    actualizar_tabla()

    # Mostrar temperatura inicial
    actualizar_componente(T_inicial)

    etiqueta_tiempo.config(
        text="Tiempo: 0 s"
    )

    messagebox.showinfo(
        "Simulación terminada",
        "Se calcularon correctamente los escenarios A, B y C."
    )


# =========================================================
# ACTUALIZAR TABLA
# =========================================================

def actualizar_tabla():

    for fila in tabla.get_children():
        tabla.delete(fila)

    try:
        umbral = float(entrada_umbral.get())
    except ValueError:
        return


    for nombre, datos in resultados.items():

        temperaturas = datos["temperaturas"]

        temperatura_final = temperaturas[-1]

        alerta = datos["alerta"]

        if alerta is None:
            texto_alerta = "No alcanzó"
        else:
            texto_alerta = f"{alerta} s"


        if temperatura_final >= umbral:
            alcanzo = "Sí"
        else:
            alcanzo = "No"


        tabla.insert(
            "",
            "end",
            values=(
                nombre,
                datos["P"],
                datos["k"],
                f"{temperatura_final:.2f} °C",
                alcanzo,
                texto_alerta
            )
        )


# =========================================================
# ACTUALIZAR COMPONENTE VISUAL
# =========================================================

def actualizar_componente(temperatura):

    try:
        umbral = float(entrada_umbral.get())
    except ValueError:
        umbral = 60


    if temperatura < 40:

        color = "lightblue"
        estado = "Normal"

    elif temperatura < 50:

        color = "yellow"
        estado = "Temperatura moderada"

    elif temperatura < umbral:

        color = "orange"
        estado = "Temperatura elevada"

    else:

        color = "red"
        estado = "ALERTA"


    canvas.itemconfig(
        componente,
        fill=color
    )


    etiqueta_temperatura.config(
        text=f"Temperatura: {temperatura:.2f} °C"
    )


    etiqueta_estado.config(
        text=f"Estado: {estado}"
    )


# =========================================================
# INICIAR ANIMACIÓN
# =========================================================

def iniciar_simulacion():

    global animando
    global segundo_actual
    global temperaturas_animacion
    global tiempos_animacion


    nombre = selector_escenario.get()

    if nombre not in resultados:

        messagebox.showwarning(
            "Aviso",
            "Primero presiona 'SIMULAR A, B Y C'."
        )

        return


    datos = resultados[nombre]

    tiempos_animacion = datos["tiempos"]
    temperaturas_animacion = datos["temperaturas"]

    segundo_actual = 0
    animando = True

    avanzar_simulacion()


# =========================================================
# ANIMACIÓN
# =========================================================

def avanzar_simulacion():

    global segundo_actual
    global animando


    if not animando:
        return


    if segundo_actual >= len(temperaturas_animacion):

        animando = False
        return


    temperatura = temperaturas_animacion[segundo_actual]

    actualizar_componente(temperatura)


    etiqueta_tiempo.config(
        text=f"Tiempo: {segundo_actual} s"
    )


    segundo_actual += 1


    ventana.after(
        50,
        avanzar_simulacion
    )


# =========================================================
# DETENER ANIMACIÓN
# =========================================================

def detener_simulacion():

    global animando

    animando = False


# =========================================================
# MOSTRAR GRÁFICA
# =========================================================

def mostrar_grafica():

    if not resultados:

        messagebox.showwarning(
            "Aviso",
            "Primero ejecuta la simulación."
        )

        return


    plt.figure(figsize=(8, 5))


    for nombre, datos in resultados.items():

        plt.plot(
            datos["tiempos"],
            datos["temperaturas"],
            label=nombre
        )


    try:
        umbral = float(entrada_umbral.get())
    except ValueError:
        umbral = 60


    plt.axhline(
        y=umbral,
        linestyle="--",
        label=f"Límite de {umbral} °C"
    )


    plt.xlabel("Tiempo (s)")
    plt.ylabel("Temperatura (°C)")

    plt.title(
        "Temperatura de los escenarios A, B y C"
    )

    plt.legend()

    plt.grid(True)

    plt.tight_layout()

    plt.show()


# =========================================================
# EXPORTAR CSV
# =========================================================

def exportar_csv():

    if not resultados:

        messagebox.showwarning(
            "Aviso",
            "Primero ejecuta la simulación."
        )

        return


    archivo = filedialog.asksaveasfilename(
        title="Guardar resultados",
        defaultextension=".csv",
        filetypes=[
            ("Archivo CSV", "*.csv")
        ]
    )


    if not archivo:
        return


    try:

        with open(
            archivo,
            "w",
            newline="",
            encoding="utf-8"
        ) as f:

            escritor = csv.writer(f)


            escritor.writerow([
                "Tiempo (s)",
                "Escenario A (°C)",
                "Escenario B (°C)",
                "Escenario C (°C)"
            ])


            cantidad = len(
                resultados[
                    "A - Condición inicial"
                ]["tiempos"]
            )


            for i in range(cantidad):

                escritor.writerow([
                    resultados[
                        "A - Condición inicial"
                    ]["tiempos"][i],

                    resultados[
                        "A - Condición inicial"
                    ]["temperaturas"][i],

                    resultados[
                        "B - Menor carga"
                    ]["temperaturas"][i],

                    resultados[
                        "C - Mejor ventilación"
                    ]["temperaturas"][i]
                ])


        messagebox.showinfo(
            "CSV creado",
            "Los resultados se guardaron correctamente."
        )


    except Exception as error:

        messagebox.showerror(
            "Error",
            f"No se pudo guardar el archivo:\n{error}"
        )


# =========================================================
# MOSTRAR ECUACIÓN
# =========================================================

def mostrar_ecuacion():

    ventana_ecuacion = tk.Toplevel(ventana)

    ventana_ecuacion.title(
        "Ecuación del modelo"
    )

    ventana_ecuacion.geometry(
        "500x350"
    )

    ventana_ecuacion.resizable(
        False,
        False
    )


    tk.Label(
        ventana_ecuacion,
        text="Modelo de calentamiento",
        font=("Arial", 15, "bold")
    ).pack(pady=15)


    tk.Label(
        ventana_ecuacion,
        text="T nueva = T actual + [P - k(T actual - Ta)] / C × Δt",
        font=("Arial", 12, "bold")
    ).pack(pady=15)


    texto = (
        "T = temperatura del componente\n"
        "P = potencia eléctrica de entrada (W)\n"
        "k = coeficiente de disipación (W/°C)\n"
        "Ta = temperatura ambiente (°C)\n"
        "C = capacidad térmica (J/°C)\n"
        "Δt = incremento de tiempo (s)"
    )


    tk.Label(
        ventana_ecuacion,
        text=texto,
        font=("Arial", 10),
        justify="left"
    ).pack(pady=10)


    tk.Button(
        ventana_ecuacion,
        text="Cerrar",
        command=ventana_ecuacion.destroy
    ).pack(pady=10)


# =========================================================
# COMPARAR AMBIENTE 25 °C / 30 °C
# =========================================================

def comparar_ambiente():

    try:

        T_inicial = float(entrada_inicial.get())
        C = float(entrada_capacidad.get())
        duracion = int(entrada_duracion.get())
        umbral = float(entrada_umbral.get())

    except ValueError:

        messagebox.showerror(
            "Error",
            "Revisa los valores introducidos."
        )

        return


    ambiente_25 = 25
    ambiente_30 = 30


    ventana_comparacion = tk.Toplevel(ventana)

    ventana_comparacion.title(
        "Comparación de temperatura ambiente"
    )

    ventana_comparacion.geometry(
        "750x500"
    )

    ventana_comparacion.resizable(
        False,
        False
    )


    tk.Label(
        ventana_comparacion,
        text="Ambiente: 25 °C vs 30 °C",
        font=("Arial", 15, "bold")
    ).pack(pady=10)


    columnas = (
        "Escenario",
        "T final 25 °C",
        "Alerta 25 °C",
        "T final 30 °C",
        "Alerta 30 °C"
    )


    tabla_comparacion = ttk.Treeview(
        ventana_comparacion,
        columns=columnas,
        show="headings",
        height=5
    )


    for columna in columnas:

        tabla_comparacion.heading(
            columna,
            text=columna
        )

        tabla_comparacion.column(
            columna,
            width=135,
            anchor="center"
        )


    tabla_comparacion.pack(
        padx=10,
        pady=10
    )


    for nombre, datos in ESCENARIOS.items():

        P = datos["P"]
        k = datos["k"]


        tiempos25, temperaturas25 = simular_escenario(
            T_inicial,
            ambiente_25,
            C,
            duracion,
            P,
            k
        )


        alerta25 = buscar_alerta(
            tiempos25,
            temperaturas25,
            umbral
        )


        tiempos30, temperaturas30 = simular_escenario(
            T_inicial,
            ambiente_30,
            C,
            duracion,
            P,
            k
        )


        alerta30 = buscar_alerta(
            tiempos30,
            temperaturas30,
            umbral
        )


        texto25 = (
            f"{alerta25} s"
            if alerta25 is not None
            else "No alcanzó"
        )


        texto30 = (
            f"{alerta30} s"
            if alerta30 is not None
            else "No alcanzó"
        )


        tabla_comparacion.insert(
            "",
            "end",
            values=(
                nombre,
                f"{temperaturas25[-1]:.2f} °C",
                texto25,
                f"{temperaturas30[-1]:.2f} °C",
                texto30
            )
        )


    tk.Label(
        ventana_comparacion,
        text=(
            "Al aumentar la temperatura ambiente, "
            "el componente tiene menor margen térmico "
            "antes de alcanzar el límite."
        ),
        font=("Arial", 10),
        wraplength=650
    ).pack(pady=15)


    tk.Button(
        ventana_comparacion,
        text="Cerrar",
        command=ventana_comparacion.destroy
    ).pack()


# =========================================================
# RECOMENDACIÓN
# =========================================================

def mostrar_recomendacion():

    if not resultados:

        messagebox.showwarning(
            "Aviso",
            "Primero ejecuta la simulación."
        )

        return


    temperaturas_finales = {}


    for nombre, datos in resultados.items():

        temperaturas_finales[nombre] = (
            datos["temperaturas"][-1]
        )


    mejor = min(
        temperaturas_finales,
        key=temperaturas_finales.get
    )


    temperatura = temperaturas_finales[mejor]


    mensaje = (
        "RECOMENDACIÓN\n\n"
        f"Escenario con menor temperatura final:\n"
        f"{mejor}\n\n"
        f"Temperatura final: {temperatura:.2f} °C\n\n"
        "Bajo las condiciones del modelo, este "
        "escenario presenta la menor temperatura "
        "final y, por lo tanto, un mayor margen "
        "respecto al límite térmico."
    )


    messagebox.showinfo(
        "Recomendación",
        mensaje
    )


# =========================================================
# CONCLUSIÓN
# =========================================================

def mostrar_conclusion():

    if not resultados:

        messagebox.showwarning(
            "Aviso",
            "Primero ejecuta la simulación."
        )

        return


    try:
        umbral = float(entrada_umbral.get())
    except ValueError:
        umbral = 60


    finales = {}


    for nombre, datos in resultados.items():

        finales[nombre] = (
            datos["temperaturas"][-1]
        )


    mejor = min(
        finales,
        key=finales.get
    )


    temperatura_mejor = finales[mejor]

    temperatura_A = finales[
        "A - Condición inicial"
    ]


    margen = umbral - temperatura_mejor


    if temperatura_mejor < umbral:

        estado = "se encuentra por debajo del límite de alerta."

    else:

        estado = "supera el límite de alerta."


    mensaje = (
        "CONCLUSIÓN DE LA SIMULACIÓN\n\n"
        f"Escenario con menor temperatura final:\n"
        f"{mejor}\n\n"
        f"Temperatura final: {temperatura_mejor:.2f} °C\n"
        f"Límite de alerta: {umbral:.2f} °C\n"
        f"Margen térmico: {margen:.2f} °C\n\n"
        f"El escenario A termina en "
        f"{temperatura_A:.2f} °C.\n\n"
        f"El escenario seleccionado {estado}\n\n"
        "De acuerdo con el modelo, reducir la "
        "carga de procesamiento o mejorar la "
        "disipación de calor puede disminuir "
        "la temperatura del componente."
    )


    messagebox.showinfo(
        "Conclusión",
        mensaje
    )


# =========================================================
# PRUEBAS DEL MODELO
# =========================================================

def ejecutar_pruebas():

    resultados_prueba = []


    # -----------------------------------------------------
    # PRUEBA 1
    # -----------------------------------------------------

    tiempos, temperaturas = simular_escenario(
        25,
        25,
        100,
        1,
        600,
        1
    )


    temperatura_1 = temperaturas[1]


    # Con los valores de A, el resultado matemático es 31 °C
    prueba1 = abs(temperatura_1 - 31) < 0.0001


    resultados_prueba.append(
        (
            "Primer segundo del escenario A",
            prueba1,
            f"Resultado: {temperatura_1:.2f} °C"
        )
    )


    # -----------------------------------------------------
    # PRUEBA 2
    # -----------------------------------------------------

    tiempos, temperaturas = simular_escenario(
        25,
        25,
        100,
        10,
        0,
        1
    )


    temperatura_final = temperaturas[-1]


    prueba2 = abs(
        temperatura_final - 25
    ) < 0.0001


    resultados_prueba.append(
        (
            "P = 0 y T inicial = T ambiente",
            prueba2,
            f"Resultado final: {temperatura_final:.2f} °C"
        )
    )


    # -----------------------------------------------------
    # PRUEBA 3
    # -----------------------------------------------------

    tiempos, temperaturas = simular_escenario(
        440,
        25,
        100,
        100,
        0,
        1
    )


    temperatura_inicial = temperaturas[0]
    temperatura_final = temperaturas[-1]


    prueba3 = temperatura_final < temperatura_inicial


    resultados_prueba.append(
        (
            "P = 0 y temperatura inicial alta",
            prueba3,
            (
                f"Inicial: {temperatura_inicial:.2f} °C | "
                f"Final: {temperatura_final:.2f} °C"
            )
        )
    )


    # -----------------------------------------------------
    # PRUEBA 4
    # -----------------------------------------------------

    _, temperaturas_A = simular_escenario(
        25,
        25,
        100,
        10,
        600,
        1
    )


    _, temperaturas_C = simular_escenario(
        25,
        25,
        100,
        10,
        60,
        2
    )


    prueba4 = (
        temperaturas_C[1]
        <
        temperaturas_A[1]
    )


    resultados_prueba.append(
        (
            "C tiene menor temperatura que A",
            prueba4,
            (
                f"A: {temperaturas_A[1]:.2f} °C | "
                f"C: {temperaturas_C[1]:.2f} °C"
            )
        )
    )


    # -----------------------------------------------------
    # VENTANA DE RESULTADOS
    # -----------------------------------------------------

    ventana_pruebas = tk.Toplevel(ventana)

    ventana_pruebas.title(
        "Pruebas del modelo"
    )

    ventana_pruebas.geometry(
        "650x400"
    )

    ventana_pruebas.resizable(
        False,
        False
    )


    tk.Label(
        ventana_pruebas,
        text="VERIFICACIÓN DEL MODELO",
        font=("Arial", 15, "bold")
    ).pack(pady=15)


    for nombre, correcta, detalle in resultados_prueba:

        if correcta:

            simbolo = "✓"
            estado = "CORRECTA"

        else:

            simbolo = "✗"
            estado = "REVISAR"


        tk.Label(
            ventana_pruebas,
            text=f"{simbolo} {nombre}",
            font=("Arial", 11, "bold")
        ).pack(
            anchor="w",
            padx=25,
            pady=3
        )


        tk.Label(
            ventana_pruebas,
            text=f"    {estado} — {detalle}",
            font=("Arial", 10)
        ).pack(
            anchor="w",
            padx=40
        )


    tk.Button(
        ventana_pruebas,
        text="Cerrar",
        command=ventana_pruebas.destroy
    ).pack(pady=15)


# =========================================================
# VENTANA PRINCIPAL
# =========================================================

ventana = tk.Tk()

ventana.title(
    "Simulador térmico"
)

# Ventana compacta
ventana.geometry(
    "800x650"
)

ventana.resizable(
    False,
    False
)


# =========================================================
# TÍTULO
# =========================================================

titulo = tk.Label(
    ventana,
    text="SIMULADOR TÉRMICO DE COMPUTADORA",
    font=("Arial", 14, "bold")
)

titulo.pack(pady=8)


# =========================================================
# PANEL DE DATOS
# =========================================================

marco_datos = tk.LabelFrame(
    ventana,
    text="Parámetros de la simulación",
    font=("Arial", 10, "bold"),
    padx=8,
    pady=5
)

marco_datos.pack(
    padx=10,
    pady=5,
    fill="x"
)


# Temperatura inicial
tk.Label(
    marco_datos,
    text="T inicial (°C):"
).grid(
    row=0,
    column=0,
    padx=5,
    pady=3
)


entrada_inicial = tk.Entry(
    marco_datos,
    width=8
)

entrada_inicial.insert(
    0,
    "25"
)

entrada_inicial.grid(
    row=0,
    column=1,
    padx=5,
    pady=3
)


# Temperatura ambiente
tk.Label(
    marco_datos,
    text="T ambiente (°C):"
).grid(
    row=0,
    column=2,
    padx=5,
    pady=3
)


entrada_ambiente = tk.Entry(
    marco_datos,
    width=8
)

entrada_ambiente.insert(
    0,
    "25"
)

entrada_ambiente.grid(
    row=0,
    column=3,
    padx=5,
    pady=3
)


# Capacidad térmica
tk.Label(
    marco_datos,
    text="C (J/°C):"
).grid(
    row=1,
    column=0,
    padx=5,
    pady=3
)


entrada_capacidad = tk.Entry(
    marco_datos,
    width=8
)

entrada_capacidad.insert(
    0,
    "100"
)

entrada_capacidad.grid(
    row=1,
    column=1,
    padx=5,
    pady=3
)


# Duración
tk.Label(
    marco_datos,
    text="Duración (s):"
).grid(
    row=1,
    column=2,
    padx=5,
    pady=3
)


entrada_duracion = tk.Entry(
    marco_datos,
    width=8
)

entrada_duracion.insert(
    0,
    "600"
)

entrada_duracion.grid(
    row=1,
    column=3,
    padx=5,
    pady=3
)


# Umbral
tk.Label(
    marco_datos,
    text="Alerta (°C):"
).grid(
    row=2,
    column=0,
    padx=5,
    pady=3
)


entrada_umbral = tk.Entry(
    marco_datos,
    width=8
)

entrada_umbral.insert(
    0,
    "60"
)

entrada_umbral.grid(
    row=2,
    column=1,
    padx=5,
    pady=3
)


# =========================================================
# BOTÓN PRINCIPAL
# =========================================================

boton_simular = tk.Button(
    ventana,
    text="SIMULAR A, B Y C",
    font=("Arial", 10, "bold"),
    command=ejecutar_simulacion,
    padx=15,
    pady=5
)

boton_simular.pack(pady=5)


# =========================================================
# TABLA
# =========================================================

marco_tabla = tk.LabelFrame(
    ventana,
    text="Resultados",
    font=("Arial", 10, "bold"),
    padx=5,
    pady=5
)

marco_tabla.pack(
    padx=10,
    pady=5,
    fill="both"
)


columnas = (
    "Escenario",
    "P",
    "k",
    "T final",
    "60 °C",
    "Alerta"
)


tabla = ttk.Treeview(
    marco_tabla,
    columns=columnas,
    show="headings",
    height=3
)


for columna in columnas:

    tabla.heading(
        columna,
        text=columna
    )

    tabla.column(
        columna,
        width=115,
        anchor="center"
    )


tabla.pack(
    padx=5,
    pady=5
)


# =========================================================
# INDICADOR VISUAL
# =========================================================

marco_visual = tk.LabelFrame(
    ventana,
    text="Estado del componente",
    font=("Arial", 10, "bold"),
    padx=5,
    pady=3
)

marco_visual.pack(
    padx=10,
    pady=5,
    fill="x"
)


canvas = tk.Canvas(
    marco_visual,
    width=350,
    height=60,
    bg="white"
)

canvas.pack(
    pady=3
)


componente = canvas.create_rectangle(
    100,
    10,
    250,
    50,
    fill="lightblue",
    outline="black",
    width=2
)


etiqueta_temperatura = tk.Label(
    marco_visual,
    text="Temperatura: 25.00 °C",
    font=("Arial", 11, "bold")
)

etiqueta_temperatura.pack(
    pady=2
)


etiqueta_estado = tk.Label(
    marco_visual,
    text="Estado: Normal",
    font=("Arial", 10)
)

etiqueta_estado.pack()


etiqueta_tiempo = tk.Label(
    marco_visual,
    text="Tiempo: 0 s",
    font=("Arial", 9)
)

etiqueta_tiempo.pack(
    pady=2
)


# =========================================================
# PANEL DE ANIMACIÓN
# =========================================================

marco_animacion = tk.LabelFrame(
    ventana,
    text="Simulación paso a paso",
    font=("Arial", 10, "bold"),
    padx=5,
    pady=4
)

marco_animacion.pack(
    padx=10,
    pady=3,
    fill="x"
)


tk.Label(
    marco_animacion,
    text="Escenario:"
).grid(
    row=0,
    column=0,
    padx=5
)


selector_escenario = ttk.Combobox(
    marco_animacion,
    values=list(ESCENARIOS.keys()),
    state="readonly",
    width=24
)

selector_escenario.current(0)

selector_escenario.grid(
    row=0,
    column=1,
    padx=5
)


boton_iniciar = tk.Button(
    marco_animacion,
    text="▶ INICIAR",
    command=iniciar_simulacion,
    font=("Arial", 9, "bold"),
    padx=8,
    pady=3
)

boton_iniciar.grid(
    row=0,
    column=2,
    padx=3
)


boton_detener = tk.Button(
    marco_animacion,
    text="■ DETENER",
    command=detener_simulacion,
    font=("Arial", 9, "bold"),
    padx=8,
    pady=3
)

boton_detener.grid(
    row=0,
    column=3,
    padx=3
)


# =========================================================
# BOTONES DE FUNCIONES
# =========================================================

marco_botones = tk.Frame(
    ventana
)

marco_botones.pack(
    pady=3
)


boton_grafica = tk.Button(
    marco_botones,
    text="📈 GRÁFICA",
    font=("Arial", 8, "bold"),
    command=mostrar_grafica,
    padx=7,
    pady=3
)

boton_grafica.grid(
    row=0,
    column=0,
    padx=3
)


boton_csv = tk.Button(
    marco_botones,
    text="📄 CSV",
    font=("Arial", 8, "bold"),
    command=exportar_csv,
    padx=7,
    pady=3
)

boton_csv.grid(
    row=0,
    column=1,
    padx=3
)


boton_ecuacion = tk.Button(
    marco_botones,
    text="🧮 ECUACIÓN",
    font=("Arial", 8, "bold"),
    command=mostrar_ecuacion,
    padx=7,
    pady=3
)

boton_ecuacion.grid(
    row=0,
    column=2,
    padx=3
)


boton_comparacion = tk.Button(
    marco_botones,
    text="🌡️ 25/30 °C",
    font=("Arial", 8, "bold"),
    command=comparar_ambiente,
    padx=7,
    pady=3
)

boton_comparacion.grid(
    row=1,
    column=0,
    padx=3,
    pady=3
)


boton_recomendacion = tk.Button(
    marco_botones,
    text="💡 RECOMENDACIÓN",
    font=("Arial", 8, "bold"),
    command=mostrar_recomendacion,
    padx=7,
    pady=3
)

boton_recomendacion.grid(
    row=1,
    column=1,
    padx=3,
    pady=3
)


boton_pruebas = tk.Button(
    marco_botones,
    text="✓ PRUEBAS",
    font=("Arial", 8, "bold"),
    command=ejecutar_pruebas,
    padx=7,
    pady=3
)

boton_pruebas.grid(
    row=1,
    column=2,
    padx=3,
    pady=3
)


boton_conclusion = tk.Button(
    marco_botones,
    text="📝 CONCLUSIÓN",
    font=("Arial", 8, "bold"),
    command=mostrar_conclusion,
    padx=15,
    pady=3
)

boton_conclusion.grid(
    row=2,
    column=0,
    columnspan=3,
    pady=3
)


# =========================================================
# INICIAR PROGRAMA
# =========================================================

ventana.mainloop()