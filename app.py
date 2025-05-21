import streamlit as st
import json
import hashlib
import os
import time

st.set_page_config(page_title="Malla Horaria", layout="centered")

# -------------------
# FUNCIONES AUXILIARES
# -------------------

def cargar_usuarios():
    if os.path.exists("usuarios.json"):
        with open("usuarios.json", "r") as f:
            return json.load(f)
    return []

def guardar_usuarios(usuarios):
    with open("usuarios.json", "w") as f:
        json.dump(usuarios, f, indent=2)

def hash_clave(clave):
    return hashlib.sha256(clave.encode()).hexdigest()

def validar_usuario(usuario, clave):
    usuarios = cargar_usuarios()
    for u in usuarios:
        if u["usuario"] == usuario and u["clave"] == hash_clave(clave):
            return True
    return False

def usuario_existe(usuario):
    usuarios = cargar_usuarios()
    return any(u["usuario"] == usuario for u in usuarios)

def recargar_pagina():
    st.markdown("""
        <script>
            window.location.reload();
        </script>
    """, unsafe_allow_html=True)

# -------------------
# CONTROL DE PÁGINAS
# -------------------

if "pagina" not in st.session_state:
    st.session_state.pagina = "inicio"

def pagina_inicio():
    st.title("Malla horaria")
    st.markdown("Bienvenido. ¿Qué deseas hacer?")
    if st.button("Iniciar sesión como administrador"):
        time.sleep(0.1)
        st.session_state.pagina = "login"
        recargar_pagina()
    if st.button("Revisar tu horario"):
        time.sleep(0.1)
        st.session_state.pagina = "ver_horario"
        recargar_pagina()

def pagina_login():
    st.title("Iniciar sesión")
    usuario = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if validar_usuario(usuario, clave):
            st.success("Acceso correcto")
            st.session_state.usuario = usuario
            st.session_state.pagina = "usuario"
            time.sleep(0.5)
            recargar_pagina()
        else:
            st.error("Usuario o clave incorrectos")
    if st.button("¿No tienes cuenta? Crear usuario"):
        st.session_state.pagina = "crear_usuario"
        recargar_pagina()
    if st.button("Volver al inicio"):
        st.session_state.pagina = "inicio"
        recargar_pagina()

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
            usuarios = cargar_usuarios()
            usuarios.append({
                "usuario": nuevo_usuario,
                "clave": hash_clave(nueva_clave),
                "correo": correo
            })
            guardar_usuarios(usuarios)
            st.success("Usuario creado correctamente. Redirigiendo al inicio de sesión...")
            st.session_state.pagina = "login"
            time.sleep(0.5)
            recargar_pagina()
    if st.button("Volver"):
        st.session_state.pagina = "login"
        recargar_pagina()

def pagina_ver_horario():
    st.title("Consulta de Horario")
    nombre = st.text_input("Nombre")
    apellido = st.text_input("Apellido")
    if st.button("Buscar"):
        st.session_state.pagina = "trabajador"
        recargar_pagina()
    if st.button("Volver al inicio"):
        st.session_state.pagina = "inicio"
        recargar_pagina()

def pagina_usuario():
    st.title("Panel de administración")
    st.markdown(f"Bienvenido, **{st.session_state.get('usuario', '')}**")
    st.write("Aquí irá el editor de horarios.")
    if st.button("Cerrar sesión"):
        st.session_state.pagina = "inicio"
        recargar_pagina()

def pagina_trabajador():
    st.title("Horario del trabajador")
    st.write("Aquí verás tu horario personalizado (próximamente).")
    if st.button("Volver al inicio"):
        st.session_state.pagina = "inicio"
        recargar_pagina()

# Render de página según estado
paginas = {
    "inicio": pagina_inicio,
    "login": pagina_login,
    "crear_usuario": pagina_crear_usuario,
    "ver_horario": pagina_ver_horario,
    "usuario": pagina_usuario,
    "trabajador": pagina_trabajador
}
paginas[st.session_state.pagina]()
