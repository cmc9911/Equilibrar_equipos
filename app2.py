import streamlit as st
import pandas as pd
from io import StringIO
import base64

# ---------- INICIALIZACIÓN ----------
if "scene" not in st.session_state:
    st.session_state.scene = "inicio"

if "data" not in st.session_state:
    st.session_state.data = None
    
st.set_page_config(layout="wide")

# ---------- FUNCIONES DE NAVEGACIÓN ----------
def cambiar_escena(nueva_escena):
    st.session_state.scene = nueva_escena

# ---------- ESCENA 1: INICIO ----------
def mostrar_inicio():
    
    # URL del archivo Excel en GitHub (asegúrate de usar la URL "raw")
    url = "https://raw.githubusercontent.com/tu-usuario/tu-repo/main/data/archivo.xlsx"
    st.session_state.data = pd.read_excel(url)
    #st.session_state.data = pd.read_excel("Hola.xlsx")


    if st.session_state.scene == "inicio":
        st.title("⚽ Bienvenido al Equilibrador de Equipos")

        st.button("👥 Empezar selección de jugadores", on_click=lambda: cambiar_escena("seleccion"))


# ---------- ESCENA 2: SELECCIÓN DE JUGADORES ----------
def mostrar_seleccion():
    st.title("🔍 Seleccionar jugadores")

    df = st.session_state.data

    nombres_disponibles = df["Nombre del jugador"].dropna().unique()

    seleccionados = st.multiselect("Selecciona 10 jugadores", nombres_disponibles)

    if len(seleccionados) != 10:
        st.warning("Selecciona exactamente 10 jugadores.")
    else:
        if st.button("✅ Generar Equipos"):
            st.session_state.jugadores_seleccionados = seleccionados
            cambiar_escena("resultados")
        

    st.button("⬅ Volver al inicio", on_click=lambda: cambiar_escena("inicio"))

# ---------- ESCENA 4: RESULTADOS DE EQUIPOS ----------
from itertools import combinations

def generar_equipos(jugadores):
    mejores_opciones = []
    ya_vistos = set()
    mitad = len(jugadores) // 2

    for combinacion in combinations(jugadores, mitad):
        equipo_a = list(combinacion)
        equipo_b = [j for j in jugadores if j not in equipo_a]

        # ⚠️ Para evitar duplicados tipo espejo
        nombres_a = sorted(j["Nombre del jugador"] for j in equipo_a)
        nombres_b = sorted(j["Nombre del jugador"] for j in equipo_b)
        clave_equipo = (tuple(nombres_a), tuple(nombres_b))
        clave_invertida = (tuple(nombres_b), tuple(nombres_a))

        if clave_equipo in ya_vistos or clave_invertida in ya_vistos:
            continue  # Ya hemos visto esta combinación o su espejo

        ya_vistos.add(clave_equipo)

        # 🔢 Calcular nivel total
        total_a = sum(j['Nivel general (1 a 10)'] for j in equipo_a)
        total_b = sum(j['Nivel general (1 a 10)'] for j in equipo_b)

        # # ⚽ Porteros (opcional)
        # porteros_a = sum(j.get('Portero', 0) for j in equipo_a)
        # porteros_b = sum(j.get('Portero', 0) for j in equipo_b)

        # diferencia_porteros = abs(porteros_a - porteros_b)

        # # ⚠️ Filtrar si la diferencia de porteros es mayor a 1
        # if diferencia_porteros > 1:
        #     continue

        diferencia = abs(total_a - total_b)
        mejores_opciones.append((equipo_a, equipo_b, diferencia))

    # Ordenar por diferencia total
    mejores_opciones.sort(key=lambda x: x[2])

    # Devolver las 3 mejores combinaciones únicas
    return mejores_opciones[:3]



def mostrar_resultados():
    st.title("📊 Equipos generados")

    df = st.session_state.data
    seleccionados = st.session_state.jugadores_seleccionados
    jugadores_df = df[df["Nombre del jugador"].isin(seleccionados)]
    jugadores = jugadores_df.to_dict("records")

    # Asegúrate de esto antes de pasar los datos a la función
    #df['¿Portero? (Sí/No)'] = df['¿Portero? (Sí/No)'].str.lower().map({'sí': 1, 'si': 1, 'no': 0})


    ejemplos = generar_equipos(jugadores)

    # Elegimos el ejemplo más equilibrado (primero) y los otros dos
    ejemplo_central = ejemplos[0]
    ejemplo_izq = ejemplos[1]
    ejemplo_der = ejemplos[2]


    nombres_1equipo_1 = [j["Nombre del jugador"] for j in ejemplo_central[0]]
    nombres_1equipo_2 = [j["Nombre del jugador"] for j in ejemplo_central[1]]
    
    nombres_2equipo_1 = [j["Nombre del jugador"] for j in ejemplo_izq[0]]
    nombres_2equipo_2 = [j["Nombre del jugador"] for j in ejemplo_izq[1]]
    
    nombres_3equipo_1 = [j["Nombre del jugador"] for j in ejemplo_der[0]]
    nombres_3equipo_2 = [j["Nombre del jugador"] for j in ejemplo_der[1]]
    
    # CONFIGURACIÓN
    
    st.markdown("""
        <style>
        body {
            background-color: #2e7d32; /* Fondo verde tipo césped */
        }
        .campo {
            background-color: green;
            background-image: url('data:image/png;base64,{}');
            background-size: cover;
            background-position: center;
            width: 100%;
            max-width: 600px;
            height: 400px;
            margin: 20px auto;
            position: relative;
            border: 2px solid white;
            border-radius: 15px;
        }
        .jugador {
            position: absolute;
            background-color: #000000cc;
            color: white;
            padding: 4px 8px;
            border-radius: 8px;
            font-size: 12px;
            text-align: center;
            transform: translate(-50%, -50%);
        }
        .lista {
            background-color: black;
            padding: 20px;
            border-radius: 10px;
            margin-top: 10px;
            text-align: center;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
            font-weight: bold;
            font-size: 16px;
        }

        </style>
    """, unsafe_allow_html=True)

    # CARGAR IMAGEN DE CAMPO
    def get_base64_image(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()

    campo_base64 = get_base64_image("Imagenes/campofutbol.jpg")  # imagen 1 sola vez, luego se usa 3 veces

    # FUNCIÓN PARA MOSTRAR CAMPO + EQUIPOS
    def dibujar_enfrentamiento(jugadores):
        jugador_base64 = get_base64_image("Imagenes/jugador.png")
        
        html = f'<div class="campo" style="background-image: url(\'data:image/png;base64,{campo_base64}\')">'
        for j in jugadores:
            html += f'''
                <div style="position: absolute; top: {j["y"]}%; left: {j["x"]}%; transform: translate(0%, 0%); text-align: center;">
                    <img src="data:image/png;base64,{jugador_base64}" style="width:30px; height:20px; display:block; margin-bottom:4px;transform: translate(-15px, -12.5px);" />
                    <div class="jugador">{j["nombre"]}</div>
                </div>
            '''
            
            html += '</div>'
        st.markdown(html, unsafe_allow_html=True)

    # Función para renderizar listas
    def mostrar_lista(equipo_a, equipo_b, titulo):
        st.markdown(f"<h2 style='text-align: center;'>{titulo}</h2>", unsafe_allow_html=True)
        
        # Crear dos columnas para mostrar los equipos
        col1, col2 = st.columns([1, 1])  # Puedes ajustar proporción si quieres
        
        with col1:
            st.markdown("<h4 style='text-align: center;'>Equipo A</h4>", unsafe_allow_html=True)
            st.markdown("<div class='lista'>" + "<br>".join(equipo_a) + "</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<h4 style='text-align: center;'>Equipo B</h4>", unsafe_allow_html=True)
            st.markdown("<div class='lista'>" + "<br>".join(equipo_b) + "</div>", unsafe_allow_html=True)
            
        

    # DATOS DE EQUIPOS
    enfrentamiento_1 = [
        {"nombre": nombres_1equipo_1[0],     "x": 20, "y": 16},
        {"nombre": nombres_1equipo_1[1],    "x": 42.5, "y": 35},
        {"nombre": nombres_1equipo_1[2],  "x": 32.5, "y": 50},
        {"nombre": nombres_1equipo_1[3],    "x": 42.5, "y": 65},
        {"nombre": nombres_1equipo_1[4],   "x": 37.5, "y": 80},

        {"nombre": nombres_1equipo_2[0],   "x": 62.5, "y": 20},
        {"nombre": nombres_1equipo_2[1],    "x": 57.5, "y": 35},
        {"nombre": nombres_1equipo_2[2],   "x": 67.5, "y": 50},
        {"nombre": nombres_1equipo_2[3],    "x": 57.5, "y": 65},
        {"nombre": nombres_1equipo_2[4],   "x": 62.5, "y": 80},

    ]

    # MOSTRAR ENFRENTAMIENTOS
    st.markdown(f"<h2 style='text-align: center;'>Propuesta 1 (Diff: {ejemplo_central[2]:.2f})</h2>", unsafe_allow_html=True)
    
    dibujar_enfrentamiento(enfrentamiento_1)

    cols = st.columns(2)
    with cols[0]:
        mostrar_lista(nombres_2equipo_1, nombres_2equipo_2, f"Propuesta 2 (Diff: {ejemplo_izq[2]:.2f})")


    with cols[1]:
        mostrar_lista(nombres_3equipo_1, nombres_3equipo_2, f"Propuesta 2 (Diff: {ejemplo_der[2]:.2f})")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.button("🔙 Volver al inicio", on_click=lambda: cambiar_escena("inicio"))

    

# ---------- MOSTRAR ESCENA SEGÚN ESTADO ----------
if st.session_state.scene == "inicio":
    mostrar_inicio()
elif st.session_state.scene == "cargar":
    mostrar_carga()
elif st.session_state.scene == "seleccion":
    mostrar_seleccion()
elif st.session_state.scene == "resultados":
    mostrar_resultados()
