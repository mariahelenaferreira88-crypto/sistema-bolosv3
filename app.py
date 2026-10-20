import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit.components.v1 as components

# 1. Configuração da Página
st.set_page_config(page_title="Doceria da Vovó - Encomendas", layout="wide")

# CUSTOMIZAÇÃO DE CORES (#9b1a1a principal e #ddaf25 detalhes)
st.markdown("""
    <style>
    /* Cor dos Títulos e Textos principais */
    h1, h2, h3 {
        color: #9b1a1a !important;
    }
    
    /* Cor dos Botões Principais */
    div.stButton > button {
        background-color: #9b1a1a;
        color: white;
        border: 2px solid #9b1a1a;
        border-radius: 8px;
    }
    
    /* Cor dos Botões ao passar o rato (Hover) */
    div.stButton > button:hover {
        background-color: #ddaf25;
        border: 2px solid #ddaf25;
        color: white;
    }

    /* Cor de Links e textos de destaque */
    a, .st-emotion-cache-1kyxreq {
        color: #ddaf25 !important;
    }
    
    /* Cor da caixa dos pedidos */
    .streamlit-expanderHeader {
        color: #9b1a1a !important;
        font-weight: bold !important;
        font-size: 18px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Conexão com o Firebase
if not firebase_admin._apps:
    key_dict = dict(st.secrets["firebase"])
    key_dict["private_key"] = key_dict["private_key"].replace("\\n", "\n")
    cred = credentials.Certificate(key_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Cabeçalho com Logomarca
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    try:
        st.image("logo.jpg", width=150)
    except:
        st.write("*(Logo em falta)*")
with col_titulo:
    st.title("Sistema de Encomendas")
    st.markdown("<p style='color:#ddaf25; font-size:20px; font-weight:bold;'>🍰 Gestão Oficial da Doceria</p>", unsafe_allow_html=True)

# 3. Criar Abas para o Sistema
aba_lancar, aba_visualizar = st.tabs(["📝 Lançar Nova Encomenda", "📋 Ver Encomendas"])

with aba_lancar:
    st.subheader("Nova Encomenda")
    with st.form("form_encomenda"):
        col1, col2 = st.columns(2)
        with col1:
            cliente = st.text_input("Nome do Cliente *")
            telefone = st.text_input("Telefone do Cliente")
            data_entrega = st.date_input("Data de Entrega *")
        with col2:
            local_retirada = st.selectbox("Local de Retirada / Entrega", ["Loja cofesa", "Loja centro", "Casa"])
            sabor = st.text_input("Sabor do Bolo (Digite o sabor e detalhes) *")
            tamanho = st.text_input("Tamanho/Peso (Ex: 2kg, 20 fatias, Grande) *")
        
        # Novos campos de endereço e observações
        endereco = st.text_input("Endereço para Entrega (Preencha caso a opção seja 'Casa')")
        observacoes = st.text_area("Observações (Opcional - Ex: Alergias, detalhes na decoração, mensagem, etc.)")
        
        submit = st.form_submit_button("Salvar Pedido")

        if submit and cliente and sabor and tamanho:
            doc_ref = db.collection("encomendas").document()
            doc_ref.set({
                "cliente": cliente,
                "telefone": telefone,
                "sabor": sabor,
                "tamanho": tamanho,
                "local_retirada": local_retirada,
                "endereco": endereco,
                "data_entrega": str(data_entrega),
                "observacoes": observacoes,
                "status": "Pendente"
            })
            st.success(f"✅ Encomenda de {cliente} lançada com sucesso!")
        elif submit:
            st.warning("Por favor, preencha o Nome, Sabor e Tamanho do bolo.")

with aba_visualizar:
    st.subheader("Encomendas Registradas (Sincronizado)")
    encomendas_ref = db.collection("encomendas").stream()
    
    for doc in encomendas_ref:
        pedido = doc.to_dict()
        
        # O '.get()' evita erros em pedidos antigos
        nome_cli = pedido.get('cliente', 'Sem Nome')
        data_ent = pedido.get('data_entrega', '')
        tamanho_bolo = pedido.get('tamanho', pedido.get('peso', 'Não informado'))
        endereco_entrega = pedido.get('endereco', 'Não informado')
        
        with st.expander(f"📦 Pedido: {nome_cli} - Para: {data_ent} ({pedido.get('status', 'Pendente')})"):
            st.markdown(f"""
            - **Telefone:** {pedido.get('telefone', 'Não informado')}
            - **Local de Retirada/Entrega:** <span style='color:#9b1a1a; font-weight:bold;'>{pedido.get('local_retirada', 'Não informado')}</span>
            - **Endereço:** {endereco_entrega}
            - **Sabor:** {pedido.get('sabor', 'Não informado')}
            - **Tamanho/Peso:** {tamanho_bolo}
            - **Observações:** {pedido.get('observacoes', 'Nenhuma observação')}
            - **Status:** {pedido.get('status', 'Pendente')}
            """, unsafe_allow_html=True)
            
            # Botões de Ação
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("✅ Marcar Entregue", key=f"ent_{doc.id}"):
                    db.collection("encomendas").document(doc.id).update({"status": "Entregue"})
                    st.rerun()
            with col_b:
                if st.button("🗑️ Apagar Pedido", key=f"apagar_{doc.id}"):
                    db.collection("encomendas").document(doc.id).delete()
                    st.rerun()
            with col_c:
                # Botão de impressão
                components.html(f"""
                    <script>
                        function imprimir() {{
                            window.parent.print();
                        }}
                    </script>
                    <button onclick="imprimir()" style="background-color: #ddaf25; border: none; color: white; padding: 8px 15px; font-weight: bold; border-radius: 8px; cursor: pointer; width: 100%;">
                        🖨️ Imprimir Página
                    </button>
                """, height=50)
