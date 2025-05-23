import streamlit as st
import hashlib
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

st.set_page_config(page_title="Malla Horaria", layout="centered")

# -------------------
# CONEXIÓN GOOGLE SHEETS
# -------------------

def conectar_google_sheet():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    cred_dict = st.secrets["google_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(cred_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open("Usuarios Malla Horaria").sheet1
    return sheet

def conectar_hoja_trabajadores():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    cred_dict = st.secrets["google_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(cred_dict, scope)
    client = gspread.authorize(creds)
    return client.open("Usuarios Malla Horaria").worksheet("Trabajadores")

def hash_clave(clave):
    return hashlib.sha256(clave.encode()).hexdigest()

def validar_usuario(usuario, clave):
    sheet = conectar_google_sheet()
    registros = sheet.get_all_records()
    clave_input = hash_clave(clave)
    for fila in registros:
        if fila["usuario"] == usuario and fila["clave_hash"] == clave_input:
            return True
    return False

# -------------------
# INICIALIZACIÓN
# -------------------

if "pagina" not in st.session_state:
    st.session_state.pagina = "inicio"

if "panel_opcion" not in st.session_state:
    st.session_state.panel_opcion = None

if "actualizar_trabajadores" not in st.session_state:
    st.session_state.actualizar_trabajadores = False

# -------------------
# PÁGINAS
# -------------------

def pagina_inicio():
    st.title("Malla horaria")
    st.markdown("Solo los administradores autorizados pueden iniciar sesión.")
    if st.button("Iniciar sesión como administrador"):
        st.session_state.pagina = "login"
    if st.button("Revisar tu horario"):
        st.session_state.pagina = "ver_horario"

def pagina_login():
    st.title("Iniciar sesión")
    usuario = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if validar_usuario(usuario, clave):
            st.success("Acceso correcto")
            st.session_state.usuario = usuario
            st.session_state.pagina = "usuario"
        else:
            st.error("Usuario o clave incorrectos")
    if st.button("Volver al inicio"):
        st.session_state.pagina = "inicio"

def pagina_ver_horario():
    st.title("Consulta de Horario")
    nombre = st.text_input("Nombre")
    apellido = st.text_input("Apellido")

    if st.button("Buscar"):
        st.session_state.pagina = "trabajador"
    if st.button("Volver al inicio"):
        st.session_state.pagina = "inicio"

def pagina_usuario():
    st.title("Panel de administración")
    st.markdown(f"Bienvenido, **{st.session_state.get('usuario', '')}**")

    if st.button("Crear horario"):
        st.session_state.pagina = "crear_nuevo_horario"
    if st.button("Ver horario actual"):
        st.session_state.pagina = "ver_horario_actual"
    if st.button("Ver horarios pasados"):
        st.session_state.pagina = "ver_horarios_pasados"
    if st.button("Administrar trabajadores"):
        st.session_state.pagina = "administrar_trabajadores"
    if st.button("Cerrar sesión"):
        st.session_state.pagina = "inicio"

def pagina_crear_nuevo_horario():
    st.title("🗓 Crear nuevo horario")
    st.write("Aquí irá el formulario para crear horarios (próximamente).")
    if st.button("Volver al inicio"):
        st.session_state.pagina = "usuario"

def pagina_ver_horario_actual():
    st.title("👀 Horario actual")
    st.write("Aquí verás el horario actual (próximamente).")
    if st.button("Volver al inicio"):
        st.session_state.pagina = "usuario"

def pagina_ver_horarios_pasados():
    st.title("📅 Horarios anteriores")
    st.write("Aquí verás los horarios anteriores (próximamente).")
    if st.button("Volver al inicio"):
        st.session_state.pagina = "usuario"

def pagina_administrar_trabajadores():
    st.title("👥 Administrar trabajadores")
    st.write("Aquí podras visualizar, agregar y eliminar trabajadores (próximamente).")

    hoja = conectar_hoja_trabajadores()
    registros = hoja.get_all_records()

    if st.button("Agregar nuevo trabajador"):
        st.session_state.pagina = "agregar_trabjador"

    # Refrescar tabla tras agregar o eliminar
    if st.session_state.actualizar_trabajadores:
        st.session_state.actualizar_trabajadores = False
        st.stop()

    # Buscador tipo filtro
    busqueda = st.text_input("Buscar trabajador por nombre:")
    resultados = [r for r in registros if busqueda.lower() in r["nombre_completo"].lower()] if busqueda else registros

    st.markdown("### Lista actual de trabajadores")
    for i, trabajador in enumerate(resultados):
        cols = st.columns((3, 2, 2, 2, 1))
        cols[0].write(trabajador["nombre_completo"])
        cols[1].write(trabajador["horas_semanales"])
        cols[2].write(trabajador["rotativo"])
        cols[3].write(trabajador["cargo"])
        if cols[4].button("❌", key=f"eliminar_{i}"):
            index_en_hoja = registros.index(trabajador) + 2
            hoja.delete_rows(index_en_hoja)
            st.success(f"{trabajador['nombre_completo']} eliminado correctamente.")
            st.session_state.actualizar_trabajadores = True
            st.stop()
            st.session_state.pagina = "administrar_trabajadores"

    # Formulario para agregar nuevo trabajador
    st.markdown("### ➕ Agregar nuevo trabajador")
    with st.form("nuevo_trabajador", clear_on_submit=True):
        nombre = st.text_input("Nombre completo")
        horas = st.number_input("Horas semanales", min_value=1, step=1)
        rotativo = st.selectbox("¿Turno rotativo?", ["Sí", "No"])
        cargo = st.selectbox("Cargo", ["Caja", "Sala", "Roticería", "Panadería", "Carnicería", "Bodega"])

        enviar = st.form_submit_button("Agregar")
        if enviar:
            hoja.append_row([nombre, horas, rotativo, cargo])
            st.success("Trabajador agregado correctamente.")
            st.session_state.actualizar_trabajadores = True
            st.session_state.pagina = "ver_horario"
            st.stop()

    if st.button("Volver al inicio"):
        st.session_state.pagina = "usuario"

def pagina_trabajador():
    st.title("Horario del trabajador")
    st.write("Aquí verás tu horario personalizado (próximamente).")
    if st.button("Volver al inicio"):
        st.session_state.pagina = "inicio"

def pagina_agregar_trabjador():
    hoja = conectar_hoja_trabajadores()
    registros = hoja.get_all_records()
    st.markdown("### ➕ Agregar nuevo trabajador")
    with st.form("nuevo_trabajador", clear_on_submit=True):
        nombre = st.text_input("Nombre completo")
        horas = st.number_input("Horas semanales", min_value=1, step=1)
        rotativo = st.selectbox("¿Turno rotativo?", ["Sí", "No"])
        cargo = st.selectbox("Cargo", ["Caja", "Sala", "Roticería", "Panadería", "Carnicería", "Bodega"])

        enviar = st.form_submit_button("Agregar")
        if enviar:
            hoja.append_row([nombre, horas, rotativo, cargo])
            st.success("Trabajador agregado correctamente.")
            st.session_state.actualizar_trabajadores = True
            st.session_state.pagina = "ver_horario"
            st.stop()

    if st.button("Volver al inicio"):
        st.session_state.pagina = "usuario"
# -------------------
# FUNCIONES DEL PANEL
# -------------------


def administrar_trabajadores():
    st.subheader("👥 Administrar trabajadores")

    hoja = conectar_hoja_trabajadores()
    registros = hoja.get_all_records()

    # Refrescar tabla tras agregar o eliminar
    if st.session_state.actualizar_trabajadores:
        st.session_state.actualizar_trabajadores = False
        st.stop()

    # Buscador tipo filtro
    busqueda = st.text_input("Buscar trabajador por nombre:")
    resultados = [r for r in registros if busqueda.lower() in r["nombre_completo"].lower()] if busqueda else registros

    st.markdown("### Lista actual de trabajadores")
    for i, trabajador in enumerate(resultados):
        cols = st.columns((3, 2, 2, 2, 1))
        cols[0].write(trabajador["nombre_completo"])
        cols[1].write(trabajador["horas_semanales"])
        cols[2].write(trabajador["rotativo"])
        cols[3].write(trabajador["cargo"])
        if cols[4].button("❌", key=f"eliminar_{i}"):
            index_en_hoja = registros.index(trabajador) + 2
            hoja.delete_rows(index_en_hoja)
            st.success(f"{trabajador['nombre_completo']} eliminado correctamente.")
            st.session_state.actualizar_trabajadores = True
            st.stop()
            st.session_state.pagina = "ver_horario"

    # Formulario para agregar nuevo trabajador
    st.markdown("### ➕ Agregar nuevo trabajador")
    with st.form("nuevo_trabajador", clear_on_submit=True):
        nombre = st.text_input("Nombre completo")
        horas = st.number_input("Horas semanales", min_value=1, step=1)
        rotativo = st.selectbox("¿Turno rotativo?", ["Sí", "No"])
        cargo = st.selectbox("Cargo", ["Caja", "Sala", "Roticería", "Panadería", "Carnicería", "Bodega"])

        enviar = st.form_submit_button("Agregar")
        if enviar:
            hoja.append_row([nombre, horas, rotativo, cargo])
            st.success("Trabajador agregado correctamente.")
            st.session_state.actualizar_trabajadores = True
            st.session_state.pagina = "ver_horario"
            st.stop()

# -------------------
# NAVEGACIÓN
# -------------------

if st.session_state.pagina == "inicio":
    pagina_inicio()
elif st.session_state.pagina == "login":
    pagina_login()
elif st.session_state.pagina == "ver_horario":
    pagina_ver_horario()
elif st.session_state.pagina == "usuario":
    pagina_usuario()
elif st.session_state.pagina == "trabajador":
    pagina_trabajador()
elif st.session_state.pagina == "ver_horario_actual":
    pagina_ver_horario_actual()
elif st.session_state.pagina == "crear_nuevo_horario":
    pagina_crear_nuevo_horario()
elif st.session_state.pagina == "ver_horarios_pasados":
    pagina_ver_horarios_pasados()
elif st.session_state.pagina == "administrar_trabajadores":
    pagina_administrar_trabajadores()
elif st.session_state.pagina == "agregar_trabjador":
    pagina_agregar_trabjador()