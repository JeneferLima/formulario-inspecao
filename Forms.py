import streamlit as st
from datetime import date
import streamlit.components.v1 as components
import streamlit_js_eval
import pandas as pd
import os

st.set_page_config(page_title="Formulário de Inspeção", layout="centered")

st.title("📋 Formulário de Inspeção")

# 1 - Data
data_inicio = st.date_input("1️⃣ Insira a data de início da inspeção", date.today())

# 2 - Nome
nome = st.text_input("2️⃣ Insira seu nome")

# 3 - Localização automática via navegador
st.markdown("### 3️⃣ Local da inspeção")
components.html("""
<script>
navigator.geolocation.getCurrentPosition(
  function(position) {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;
    const coord = lat + "," + lon;
    window.parent._lastCoord = coord;
    window.parent.postMessage({type: 'coords', data: coord}, "*");
  },
  function(error) {
    window.parent._lastCoord = 'Erro ao obter localização';
    window.parent.postMessage({type: 'coords', data: 'Erro ao obter localização'}, "*");
  }
);
</script>
""", height=0)

coords = st.empty()

# Captura coordenada do navegador
coord_val = streamlit_js_eval.streamlit_js_eval(js_expressions="parent.window._lastCoord", key="get_coords")
if coord_val and isinstance(coord_val, str) and ',' in coord_val:
    coords.write(f"📍 Localização detectada: {coord_val}")
else:
    coords.write("🔍 Aguardando localização...")

# 4 - Condições
st.markdown("### 4️⃣ O local apresenta boas condições?")
condicao = st.radio("Selecione uma opção:", ["Sim", "Não"])

# Se não estiver ok
if condicao == "Não":
    st.file_uploader("📸 Tire ou envie uma foto do local", type=["png", "jpg", "jpeg"])
    motivo = st.text_area("📝 Descreva o motivo")
else:
    motivo = ""

# 5 - Enviar formulário
if st.button("✅ Enviar formulário"):
    st.success("Formulário enviado com sucesso!")
    st.write("### Resumo da Inspeção:")
    st.write(f"**Data:** {data_inicio}")
    st.write(f"**Nome:** {nome}")
    st.write(f"**Localização:** {coord_val if coord_val else 'Não capturada'}")
    st.write(f"**Condições:** {condicao}")
    if condicao == "Não":
        st.write(f"**Motivo:** {motivo if motivo else 'Não preenchido'}")

    # 🔽 SALVAR DADOS NO CSV
    dados = {
        "Data": [data_inicio],
        "Nome": [nome],
        "Localização": [coord_val],
        "Condições": [condicao],
        "Motivo": [motivo]
    }

    df = pd.DataFrame(dados)

    if not os.path.exists("respostas.csv"):
        df.to_csv("respostas.csv", index=False)
    else:
        df.to_csv("respostas.csv", mode='a', header=False, index=False)

# =========================
# 🔐 DOWNLOAD COM SENHA
# =========================
st.markdown("---")
st.markdown("## 📥 Relatório de Inspeções")

if st.button("🔐 Baixar relatório (acesso restrito)"):
    with st.expander("🔑 Digite a senha para continuar"):
        senha = st.text_input("Senha:", type="password")
        senha_correta = "minhasenha123"  # Altere conforme necessário

        if senha == senha_correta:
            if os.path.exists("respostas.csv"):
                df = pd.read_csv("respostas.csv")
                st.success("✅ Acesso liberado! Você pode baixar o relatório abaixo:")
                st.download_button(
                    label="📥 Baixar CSV",
                    data=df.to_csv(index=False).encode("utf-8"),
                    file_name="relatorio_inspecao.csv",
                    mime="text/csv"
                )
            else:
                st.warning("⚠️ Nenhum dado foi registrado ainda.")
        elif senha != "":
            st.error("❌ Senha incorreta. Tente novamente.")


