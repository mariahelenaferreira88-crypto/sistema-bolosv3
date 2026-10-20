import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# 1. Configuração da Página
st.set_page_config(page_title="Sistema de Encomendas", layout="wide")
st.title("🎂 Sistema de Encomendas de Bolo")

# 2. Conexão com o Firebase (Base de Dados na Nuvem)
if not firebase_admin._apps:
    # Puxa as informações dos Secrets
    key_dict = dict(st.secrets["firebase"])
    # Força o sistema a ler as quebras de linha corretamente
    key_dict["private_key"] = key_dict["private_key"].replace("\\n", "\n")
    
    cred = credentials.Certificate(key_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 3. Criar Abas para o Sistema
aba_lancar, aba_visualizar = st.tabs(["📝 Lançar Nova Encomenda", "📋 Ver Encomendas"])

with aba_lancar:
    st.subheader("Nova Encomenda")
    with st.form("form_encomenda"):
        cliente = st.text_input("Nome do Cliente")
        sabor = st.selectbox("Sabor do Bolo", ["Chocolate", "Morango", "Baunilha", "Prestigio", "Red Velvet"])
        peso = st.number_input("Peso (Kg)", min_value=0.5, step=0.5)
        data_entrega = st.date_input("Data de Entrega")
        submit = st.form_submit_button("Salvar Pedido")

        if submit and cliente:
            doc_ref = db.collection("encomendas").document()
            doc_ref.set({
                "cliente": cliente,
                "sabor": sabor,
                "peso": peso,
                "data_entrega": str(data_entrega),
                "status": "Pendente"
            })
            st.success("✅ Encomenda enviada para o sistema com sucesso!")

with aba_visualizar:
    st.subheader("Encomendas Registradas (Sincronizado nos dois PCs)")
    encomendas_ref = db.collection("encomendas").stream()
    for doc in encomendas_ref:
        pedido = doc.to_dict()
        with st.expander(f"Pedido: {pedido['cliente']} - {pedido['data_entrega']}"):
            st.write(f"**Sabor:** {pedido['sabor']}")
            st.write(f"**Peso:** {pedido['peso']} Kg")
            st.write(f"**Status:** {pedido['status']}")
            if st.button("Marcar como Entregue", key=doc.id):
                db.collection("encomendas").document(doc.id).update({"status": "Entregue"})
                st.rerun()