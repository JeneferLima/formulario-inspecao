import streamlit as st
from datetime import date
import streamlit.components.v1 as components

st.set_page_config(page_title="Formulário de Inspeção", layout="centered")

st.title("📋 Formulário de Inspeção")

# 1 - Data
data_inicio = st.date_input("1️⃣ Insira a data de início da inspeção", date.today())

# 2 - Nome
nome = st.text_input("2️⃣ Insira seu nome")

# 3 - Localização automática via navegador (JS + HTML)
st.markdown("### 3️⃣ Local da inspeção")
components.html("""
<script>
navigator.geolocation.getCurrentPosition(
  function(position) {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;
    const coord = lat + "," + lon;
    window.parent.postMessage({type: 'coords', data: coord}, "*");
  },
  function(error) {
    window.parent.postMessage({type: 'coords', data: 'Erro ao obter localização'}, "*");
  }
);
</script>
""", height=0)

coords = st.empty()

# Captura da coordenada enviada por JS
import streamlit_js_eval
coord_val = streamlit_js_eval.streamlit_js_eval(js_expressions="parent.window._lastCoord", key="get_coords")
if coord_val and isinstance(coord_val, str) and ',' in coord_val:
    coords.write(f"📍 Localização detectada: {coord_val}")
else:
    coords.write("🔍 Aguardando localização...")

# 4 - Condições do local
st.markdown("### 4️⃣ O local apresenta boas condições?")
condicao = st.radio("Selecione uma opção:", ["Sim", "Não"])

if condicao == "Não":
    st.file_uploader("📸 Tire ou envie uma foto do local", type=["png", "jpg", "jpeg"])
    motivo = st.text_area("📝 Descreva o motivo")

# Botão para enviar
if st.button("✅ Enviar formulário"):
    st.success("Formulário enviado com sucesso!")
    st.write("### Resumo da Inspeção:")
    st.write(f"**Data:** {data_inicio}")
    st.write(f"**Nome:** {nome}")
    st.write(f"**Localização:** {coord_val if coord_val else 'Não capturada'}")
    st.write(f"**Condições:** {condicao}")
    if condicao == "Não":
        st.write(f"**Motivo:** {motivo if motivo else 'Não preenchido'}")
