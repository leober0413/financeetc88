import streamlit as st
import streamlit_authenticator as stauth

st.set_page_config(page_title="ETC 88 · Panel de Finanzas", layout="wide", initial_sidebar_state="collapsed")

_ADMIN_BTN_CSS = """
<style>
div[data-testid="stSidebar"] .admin-login-btn button {
    background: transparent !important;
    border: 1px solid #1E293B !important;
    color: #475569 !important;
    font-size: 0.7rem !important;
    padding: 4px 8px !important;
    min-height: 28px !important;
    width: auto !important;
}
div[data-testid="stSidebar"] .admin-login-btn button:hover {
    border-color: #334155 !important;
    color: #64748B !important;
}
</style>
"""

# ------------------------------------------------------------------
# Estado de sesión
# ------------------------------------------------------------------
if "guest_mode" not in st.session_state:
    st.session_state["guest_mode"] = True   # arranca como invitado por defecto
if "show_login" not in st.session_state:
    st.session_state["show_login"] = False

guest_mode = st.session_state["guest_mode"]

# ------------------------------------------------------------------
# Login admin (solo si fue solicitado)
# ------------------------------------------------------------------
if not guest_mode and "gcp_service_account" in st.secrets and "auth" in st.secrets:
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
        if st.button("← Volver a vista pública"):
            st.session_state["guest_mode"] = True
            st.rerun()
        st.stop()

    # Logout en sidebar
    with st.sidebar:
        st.markdown(f"<div style='padding:8px 12px 4px;color:#94A3B8;font-size:0.75rem;'>👤 {st.session_state.get('name','')}</div>", unsafe_allow_html=True)
        authenticator.logout("Cerrar sesión", location="sidebar")

# ------------------------------------------------------------------
# Navegación
# ------------------------------------------------------------------
if guest_mode:
    invitado = st.Page("pages/invitado.py", title="Vista Invitado", icon="👁️", default=True)
    with st.sidebar:
        st.markdown(_ADMIN_BTN_CSS, unsafe_allow_html=True)
        st.markdown("<div style='position:absolute;bottom:16px;width:calc(100% - 32px)'>", unsafe_allow_html=True)
        st.markdown('<div class="admin-login-btn">', unsafe_allow_html=True)
        if st.button("Acceso admin", key="btn_admin"):
            st.session_state["guest_mode"] = False
            st.rerun()
        st.markdown("</div></div>", unsafe_allow_html=True)
    pg = st.navigation([invitado])
else:
    dashboard     = st.Page("pages/dashboard.py",     title="Dashboard",    icon="📊", default=True)
    registrar     = st.Page("pages/registrar.py",     title="Registrar",    icon="➕")
    participantes = st.Page("pages/participantes.py", title="Participantes", icon="🏕️")
    presupuesto   = st.Page("pages/presupuesto.py",   title="Presupuesto",  icon="💰")
    actividad     = st.Page("pages/actividad.py",     title="Actividad",    icon="📋")
    pg = st.navigation([dashboard, registrar, participantes, presupuesto, actividad])

pg.run()
