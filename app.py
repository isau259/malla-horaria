import streamlit as st
import hashlib
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Malla Horaria", layout="centered")

# -------------------
# CONEXIÓN GOOGLE SHEETS
# -------------------

def conectar_google_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("Usuarios Malla Horaria").sheet1  # cambia por el nombre exacto si es distinto
    return sheet

def hash_clave(clave):
    return hashlib.sha256(clave.encode()).hexdigest()

def guardar_usuario_en_sheet(usuario, clave_hash, correo):
    sheet = conectar_google_sheet()
    sheet.append_row([usuario, clave_hash, correo])

def usuario_existe(usuario):
    sheet = conectar_google_sheet()
    usuarios = sheet.col_values(1)[1:]  # salta la cabecera
    return usuario in usuarios

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

# -------------------
# PÁGINAS
# -------------------

def pagina_inicio():
    st.title("Malla horaria")
    st.markdown("Bienvenido. ¿Qué deseas hacer?")
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
    if st.button("¿No tienes cuenta? Crear usuario"):
        st.session_state.pagina = "crear_usuario"
    if st.button("Volver al inicio"):
        st.session_state.pagina = "inicio"

def pagina_crear_usuario():
    st.title("Crear nueva cuenta")
    nuevo_usuario = st.text_input("Nuevo usuario")
    nueva_clave = st.text_input("Contraseña", type="password")
    repetir_clave = st.text_input("Repetir contraseña", type="password")
    correo = st.text_input("Correo electrónico")

    if st.button("Registrar"):
        if nueva_clave != repetir_clave:
            st.error("Las contraseñas no coinciden")
        elif usuario_existe(nuevo_usuario):
            st.error("El usuario ya existe")
        else:
            guardar_usuario_en_sheet(nuevo_usuario, hash_clave(nueva_clave), correo)
            st.success("Usuario creado correctamente. Ahora puedes iniciar sesión.")
            st.session_state.pagina = "login"
    if st.button("Volver"):
        st.session_state.pagina = "login"

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
    st.write("Aquí irá el editor de horarios.")
    if st.button("Cerrar sesión"):
        st.session_state.pagina = "inicio"

def pagina_trabajador():
    st.title("Horario del trabajador")
    st.write("Aquí verás tu horario personalizado (próximamente).")
    if st.button("Volver al inicio"):
        st.session_state.pagina = "inicio"

# -------------------
# NAVEGACIÓN
# -------------------

if st.session_state.pagina == "inicio":
    pagina_inicio()
elif st.session_state.pagina == "login":
    pagina_login()
elif st.session_state.pagina == "crear_usuario":
    pagina_crear_usuario()
elif st.session_state.pagina == "ver_horario":
    pagina_ver_horario()
elif st.session_state.pagina == "usuario":
    pagina_usuario()
elif st.session_state.pagina == "trabajador":
    pagina_trabajador()
