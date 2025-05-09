import streamlit as st
from datetime import date
from streamlit_js_eval import streamlit_js_eval
import pandas as pd
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
import base64

st.set_page_config(page_title="Formulário de Inspeção", layout="centered")
st.title("📋 Formulário de Inspeção")

# 1 - Data
data_inicio = st.date_input("1️⃣ Insira a data de início da inspeção", date.today())

# 2 - Nome
nome = st.text_input("2️⃣ Insira seu nome")

# 3 - Localização automática via navegador (corrigida)
st.markdown("### 3️⃣ Local da inspeção")
coord_val = streamlit_js_eval(
    js_expressions="""
        navigator.geolocation.getCurrentPosition(
            (pos) => { window._coords = `${pos.coords.latitude},${pos.coords.longitude}`; },
            (err) => { window._coords = "Erro"; }
        );
        window._coords;
    """,
    key="get_location"
)
coords = st.empty()
if coord_val and isinstance(coord_val, str) and "," in coord_val:
    coords.write(f"📍 Localização detectada: {coord_val}")
else:
    coords.write("🔍 Aguardando localização...")

# 4 - Condições
st.markdown("### 4️⃣ O local apresenta boas condições?")
condicao = st.radio("Selecione uma opção:", ["Sim", "Não"])

# 5 - Motivo e foto (se necessário)
foto = None
if condicao == "Não":
    foto = st.file_uploader("📸 Tire ou envie uma foto do local", type=["png", "jpg", "jpeg"])
    motivo = st.text_area("📝 Descreva o motivo")
else:
    motivo = ""

# 6 - Enviar formulário
if st.button("✅ Enviar formulário"):
    st.success("Formulário enviado com sucesso!")
    st.write("### Resumo da Inspeção:")
    st.write(f"**Data:** {data_inicio}")
    st.write(f"**Nome:** {nome}")
    st.write(f"**Localização:** {coord_val if coord_val else 'Não capturada'}")
    st.write(f"**Condições:** {condicao}")
    if condicao == "Não":
        st.write(f"**Motivo:** {motivo if motivo else 'Não preenchido'}")

    # Salvar CSV
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

    # Criar PDF
    pdf_path = f"relatorios/Relatorio_{nome}_{data_inicio}.pdf".replace(" ", "_")
    os.makedirs("relatorios", exist_ok=True)
    c = canvas.Canvas(pdf_path, pagesize=A4)
    largura, altura = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, altura - 50, "Relatório de Inspeção")

    c.setFont("Helvetica", 12)
    c.drawString(50, altura - 100, f"Data: {data_inicio}")
    c.drawString(50, altura - 120, f"Nome: {nome}")
    c.drawString(50, altura - 140, f"Localização: {coord_val}")
    c.drawString(50, altura - 160, f"Condições: {condicao}")
    if motivo:
        c.drawString(50, altura - 180, f"Motivo: {motivo}")

    if foto:
        try:
            img = ImageReader(io.BytesIO(foto.getvalue()))
            c.drawImage(img, 50, altura - 450, width=200, preserveAspectRatio=True, mask='auto')
        except:
            c.drawString(50, altura - 200, "Erro ao adicionar imagem.")

    c.showPage()
    c.save()

    # Download PDF
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
        b64_pdf = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{os.path.basename(pdf_path)}" target="_blank">📄 Baixar relatório em PDF</a>'
        st.markdown(href, unsafe_allow_html=True)

# 7 - Acesso ao relatório completo com senha
st.markdown("---")
st.markdown("## 🔐 Área restrita para download completo")
senha = st.text_input("Digite a senha para baixar o relatório geral:", type="password")
if senha == "inspecao2024":
    if os.path.exists("respostas.csv"):
        with open("respostas.csv", "rb") as f:
            st.download_button(
                label="⬇️ Baixar respostas completas (CSV)",
                data=f,
                file_name="respostas.csv",
                mime="text/csv"
            )
    else:
        st.warning("Nenhum dado disponível para download.")
elif senha:
    st.error("Senha incorreta.")


