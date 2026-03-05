import streamlit as st

st.set_page_config(page_title="Avogadro Optimizer", page_icon="🔥")

st.title("🔥 Biomass Optimizer v1.0")
st.write("Analisi efficienza caldaie industriali")

# Input tecnici
temp_fumi = st.number_input("Temperatura Fumi (°C)", value=200)
o2_residuo = st.number_input("O2 Residuo (%)", value=7.0)

if st.button("Analizza Rendimento"):
    if o2_residuo > 8:
        st.error("Diagnosi: Eccesso d'aria elevato.")
        st.info("Azione: Controllare tenuta portelli o ridurre giri ventilatore.")
    elif temp_fumi > 220:
        st.warning("Diagnosi: Scambiatore sporco.")
        st.info("Azione: Avviare ciclo di pulizia automatico.")
    else:
        st.success("Diagnosi: Parametri ottimali!")
    
    st.balloons()
