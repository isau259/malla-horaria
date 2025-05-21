import streamlit as st

st.set_page_config(page_title="Malla Horaria", layout="centered")

if "pagina" not in st.session_state:
    st.session_state.pagina = "inicio"

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
        if usuario == "admin" and clave == "1234":
            st.success("Acceso correcto")
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
    st.write("Aquí podrás crear y editar horarios (próximamente).")
    if st.button("Cerrar sesión"):
        st.session_state.pagina = "inicio"

def pagina_trabajador():
    st.title("Horario del trabajador")
    st.write("Aquí verás tu horario personalizado (próximamente).")
    if st.button("Volver al inicio"):
        st.session_state.pagina = "inicio"

# Render según estado
paginas = {
    "inicio": pagina_inicio,
    "login": pagina_login,
    "ver_horario": pagina_ver_horario,
    "usuario": pagina_usuario,
    "trabajador": pagina_trabajador
}
paginas[st.session_state.pagina]()
