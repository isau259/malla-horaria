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
    sheet = client.open("Usuarios Malla Horaria").sheet1  # cambia el nombre si es necesario
    return sheet

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

    opcion = st.radio("Selecciona una opción:", [
        "Crear nuevo horario",
        "Ver horario actual",
        "Ver horarios pasados",
        "Administrar trabajadores"
    ])

    st.session_state.panel_opcion = opcion

    if opcion == "Crear nuevo horario":
        crear_horario()
    elif opcion == "Ver horario actual":
        ver_horario_actual()
    elif opcion == "Ver horarios pasados":
        ver_horarios_pasados()
    elif opcion == "Administrar trabajadores":
        administrar_trabajadores()

    if st.button("Cerrar sesión"):
        st.session_state.pagina = "inicio"

def pagina_trabajador():
    st.title("Horario del trabajador")
    st.write("Aquí verás tu horario personalizado (próximamente).")
    if st.button("Volver al inicio"):
        st.session_state.pagina = "inicio"

# -------------------
# FUNCIONES DEL PANEL
# -------------------

def crear_horario():
    st.subheader("🗓 Crear nuevo horario")
    st.info("Aquí irá el formulario para crear horarios. (próximamente)")

def ver_horario_actual():
    st.subheader("👀 Horario actual")
    st.info("Visualización del horario actual. (próximamente)")

def ver_horarios_pasados():
    st.subheader("📅 Horarios pasados")
    st.info("Aquí se mostrarán horarios de semanas anteriores. (próximamente)")

def administrar_trabajadores():
    st.subheader("👥 Administrar trabajadores")
    st.info("Desde aquí podrás crear o eliminar trabajadores. (próximamente)")

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
