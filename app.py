import streamlit as st
import streamlit_authenticator as stauth

st.set_page_config(page_title="ETC 88 · Panel de Finanzas", layout="wide", initial_sidebar_state="collapsed")

# ------------------------------------------------------------------
# Autenticación
# ------------------------------------------------------------------
if "gcp_service_account" in st.secrets and "auth" in st.secrets:
    credentials = {"usernames": {}}
    for username, info in st.secrets["auth"]["credentials"]["usernames"].items():
        credentials["usernames"][username] = {
            "name":     info["name"],
            "password": info["password"],
        }

    authenticator = stauth.Authenticate(
        credentials,
        cookie_name=st.secrets["auth"]["cookie_name"],
        cookie_key=st.secrets["auth"]["cookie_key"],
        cookie_expiry_days=st.secrets["auth"].get("cookie_expiry_days", 7),
    )

    authenticator.login(location="main")

    if not st.session_state.get("authentication_status"):
        if st.session_state.get("authentication_status") is False:
            st.error("Usuario o contraseña incorrectos.")
        st.stop()

    # Logout en sidebar
    with st.sidebar:
        st.markdown(f"<div style='padding:8px 12px 4px;color:#94A3B8;font-size:0.75rem;'>👤 {st.session_state.get('name','')}</div>", unsafe_allow_html=True)
        authenticator.logout("Cerrar sesión", location="sidebar")

# ------------------------------------------------------------------
# Navegación
# ------------------------------------------------------------------
dashboard     = st.Page("pages/dashboard.py",   title="Dashboard",   icon="📊", default=True)
registrar     = st.Page("pages/registrar.py",   title="Registrar",   icon="➕")
participantes = st.Page("pages/participantes.py", title="Participantes", icon="🏕️")
actividad     = st.Page("pages/actividad.py",   title="Actividad",   icon="📋")

pg = st.navigation([dashboard, registrar, participantes, actividad])
pg.run()
