import streamlit as st

st.set_page_config(page_title="ETC 88 · Panel de Finanzas", layout="wide")

dashboard     = st.Page("pages/dashboard.py",     title="Dashboard",     icon="📊", default=True)
registrar     = st.Page("pages/registrar.py",     title="Registrar",     icon="➕")
participantes = st.Page("pages/participantes.py", title="Participantes",  icon="🏕️")

pg = st.navigation([dashboard, registrar, participantes])
pg.run()
