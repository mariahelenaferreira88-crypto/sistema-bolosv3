import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit.components.v1 as components

# 1. Configuração da Página
st.set_page_config(page_title="Doceria da Vovó - Encomendas", page_icon="🍰", layout="wide")

# 2. CUSTOMIZAÇÃO AVANÇADA DE UI/UX (CSS)
st.markdown("""
    <style>
    /* Fundo geral ligeiramente acinzentado para dar destaque aos cartões brancos */
    .stApp {
        background-color: #fdfdfd;
    }
    
    /* Títulos com a cor oficial da marca e fonte elegante */
    h1, h2, h3 {
        color: #9b1a1a !important;
        font-family: 'Georgia', serif;
    }
    
    /* Design sofisticado para o Formulário */
    div[data-testid="stForm"] {
        background-color: #ffffff;
        border: 1px solid #f0f0f0;
        border-radius: 12px;
        padding: 30px;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.04);
    }
    
    /* Botões Primários (Formulário) */
    div.stButton > button[kind="primary"] {
        background-color: #9b1a1a;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #ddaf25;
        box-shadow: 0px 4px 12px rgba(221, 175, 37, 0.4);
        transform: translateY(-2px);
    }

    /* Botões Secundários (Ações normais) */
    div.stButton > button[kind="secondary"] {
        background-color: transparent;
        color: #9b1a1a;
        border: 1px solid #9b1a1a;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    div.stButton > button[kind="secondary"]:hover {
        background-color: #9b1a1a;
        color: white;
    }

    /* Campos de Input mais elegantes */
    .stTextInput input, .stSelectbox select, .stTextArea textarea, .stDateInput input, .stTimeInput input {
        border-radius: 6px !important;
        border: 1px solid #e0e0e0 !important;
    }
    .stTextInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus, .stDateInput input:focus, .stTimeInput input:focus {
        border-color: #ddaf25 !important;
        box-shadow: 0 0 0 1.5px #ddaf25 !important;
    }

    /* Design das Caixas de Encomenda (Expanders) */
    div[data-testid="stExpander"] {
        background-color: #ffffff;
        border-radius: 10px;
        border: 1px solid #eaeaea;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.03);
        margin-bottom: 12px;
    }
    .streamlit-expanderHeader {
        color: #9b1a1a !important;
        font-size: 16px !important;
        font-weight: bold !important;
    }
    
    /* Divisórias suaves */
    hr {
        margin: 1.5em 0;
        border-top: 1px solid #f0f0f0;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Conexão com o Firebase
if not firebase_admin._apps:
    key_dict = dict(st.secrets["firebase"])
    key_dict["private_key"] = key_dict["private_key"].replace("\\n", "\n")
    cred = credentials.Certificate(key_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 4. Cabeçalho Sofisticado
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    try:
        st.image("logo.jpg", width=120)
    except:
        st.write("*(Logo)*")
with col_titulo:
    st.title("Sistema de Encomendas")
    st.markdown("<p style='color:#ddaf25; font-size:18px; font-weight:600; margin-top:-15px;'>Doceria da Vovó ✨</p>", unsafe_allow_html=True)

st.markdown("---")

# 5. Abas Principais
aba_lancar, aba_visualizar = st.tabs(["📝 Lançar Novo Pedido", "📋 Painel de Controle"])

# ================= ABA 1: LANÇAR PEDIDO =================
with aba_lancar:
    with st.form("form_encomenda"):
        
        # Grupo 1: Cliente
        st.markdown("<h4 style='color:#9b1a1a;'>👤 Dados do Cliente</h4>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: cliente = st.text_input("Nome Completo *", placeholder="Ex: Maria Joaquina")
        with c2: telefone = st.text_input("WhatsApp / Telefone", placeholder="(00) 00000-0000")
        
        st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        
        # Grupo 2: O Bolo
        st.markdown("<h4 style='color:#9b1a1a;'>🎂 Detalhes do Bolo</h4>", unsafe_allow_html=True)
        c3, c4 = st.columns([2, 1])
        with c3: sabor = st.text_input("Sabor e Recheio *", placeholder="Ex: Massa branca, recheio de ninho com morangos")
        with c4: tamanho = st.text_input("Tamanho/Peso *", placeholder="Ex: 2kg ou 20 fatias")
        observacoes = st.text_area("Observações Especiais", placeholder="Mensagens para o topo, restrições alimentares, cor da decoração, etc.")

        st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        
        # Grupo 3: Entrega
        st.markdown("<h4 style='color:#9b1a1a;'>🚚 Logística de Entrega</h4>", unsafe_allow_html=True)
        c5, c6, c7 = st.columns(3)
        with c5: data_entrega = st.date_input("Data do Evento *")
        with c6: horario_retirada = st.time_input("Horário Combinado")
        with c7: local_retirada = st.selectbox("Local de Saída", ["Loja cofesa", "Loja centro", "Casa"])
        endereco = st.text_input("Endereço Completo (Obrigatório caso a opção seja entrega em 'Casa')")
        
        st.write("") # Espaço
        submit = st.form_submit_button("Criar Encomenda Oficial", type="primary", use_container_width=True)

        if submit and cliente and sabor and tamanho:
            doc_ref = db.collection("encomendas").document()
            doc_ref.set({
                "cliente": cliente, "telefone": telefone, "sabor": sabor, "tamanho": tamanho,
                "local_retirada": local_retirada, "endereco": endereco, 
                "data_entrega": str(data_entrega), "horario_retirada": str(horario_retirada),
                "observacoes": observacoes, "status": "Pendente"
            })
            st.success(f"🎉 Fantástico! A encomenda de {cliente} foi registada e sincronizada.")
        elif submit:
            st.error("⚠️ Atenção: Os campos Nome, Sabor e Tamanho são obrigatórios.")


# ================= ABA 2: PAINEL DE CONTROLE =================
with aba_visualizar:
    # Ler dados primeiro para criar o Dashboard
    docs = db.collection("encomendas").stream()
    pedidos = []
    for d in docs:
        p = d.to_dict()
        p['id'] = d.id
        pedidos.append(p)
    
    pendentes = sum(1 for p in pedidos if p.get('status') == 'Pendente')
    entregues = sum(1 for p in pedidos if p.get('status') == 'Entregue')
    
    # Linha de Dashboard e Botão de Atualizar
    dash1, dash2, dash3, dash4 = st.columns(4)
    dash1.metric("📦 Total de Pedidos", len(pedidos))
    dash2.metric("⏳ Pendentes", pendentes)
    dash3.metric("✅ Entregues", entregues)
    with dash4:
        st.write("") # Alinhar verticalmente
        if st.button("🔄 Puxar Novos Pedidos", use_container_width=True):
            st.rerun()
            
    st.markdown("<hr style='margin: 10px 0 20px 0;'>", unsafe_allow_html=True)

    # Listar os pedidos com design de Recibo
    if len(pedidos) == 0:
        st.info("Nenhuma encomenda registada no sistema até ao momento.")
        
    for p in pedidos:
        status_atual = p.get('status', 'Pendente')
        
        # Etiqueta visual de status
        cor_badge = "#d4edda" if status_atual == "Entregue" else "#fff3cd"
        cor_texto = "#155724" if status_atual == "Entregue" else "#856404"
        badge_html = f"<span style='background-color:{cor_badge}; color:{cor_texto}; padding:4px 12px; border-radius:12px; font-size:12px; font-weight:bold;'>{status_atual}</span>"
        
        titulo_card = f"📅 {p.get('data_entrega')} às {p.get('horario_retirada', '--:--')} | {p.get('cliente', 'Sem nome')}"
        
        with st.expander(f"{titulo_card} ({status_atual})"):
            
            # Layout interno estilo "Recibo" com a linha lateral dourada (#ddaf25)
            st.markdown(f"""
            <div style='background-color: #fafafa; padding: 15px; border-radius: 8px; border-left: 5px solid #ddaf25;'>
                <div style='display: flex; justify-content: space-between; margin-bottom: 10px;'>
                    <span style='font-size: 16px; font-weight: bold; color: #9b1a1a;'>{p.get('cliente', 'Cliente')}</span>
                    {badge_html}
                </div>
                <p style='margin: 0; color: #555;'><strong>📞 Fone:</strong> {p.get('telefone', 'Não informado')} | <strong>📍 Local:</strong> {p.get('local_retirada', '')}</p>
                <p style='margin: 5px 0 15px 0; color: #555;'><strong>🏠 Endereço:</strong> {p.get('endereco', 'Não preenchido')}</p>
                
                <div style='background-color: #fff; padding: 12px; border: 1px dashed #ccc; border-radius: 6px;'>
                    <p style='margin: 0; font-size: 15px;'><strong>🍰 Bolo:</strong> {p.get('sabor', '')}</p>
                    <p style='margin: 5px 0 0 0; font-size: 15px;'><strong>⚖️ Peso/Tamanho:</strong> {p.get('tamanho', '')}</p>
                </div>
                
                <p style='margin-top: 15px; color: #444;'><strong>📝 Obs:</strong> <i>{p.get('observacoes', 'Nenhuma observação registada.')}</i></p>
            </div>
            <br>
            """, unsafe_allow_html=True)
            
            # Botões de Ação Redesenhados
            ca, cb, cc = st.columns(3)
            with ca:
                if status_atual == "Pendente":
                    if st.button("✅ Concluir/Entregue", key=f"ent_{p['id']}", use_container_width=True):
                        db.collection("encomendas").document(p['id']).update({"status": "Entregue"})
                        st.rerun()
                else:
                    if st.button("↩️ Reabrir Pedido", key=f"reab_{p['id']}", use_container_width=True):
                        db.collection("encomendas").document(p['id']).update({"status": "Pendente"})
                        st.rerun()
            with cb:
                if st.button("🗑️ Apagar Permanente", key=f"del_{p['id']}", use_container_width=True):
                    db.collection("encomendas").document(p['id']).delete()
                    st.rerun()
            with cc:
                # Botão de impressão com hover dourado
                components.html(f"""
                    <style>
                        .btn-print {{
                            background-color: #ddaf25; border: none; color: white; padding: 9px 15px; 
                            font-weight: 600; border-radius: 8px; cursor: pointer; width: 100%;
                            font-family: sans-serif; transition: background 0.3s;
                        }}
                        .btn-print:hover {{ background-color: #c79b1d; }}
                    </style>
                    <script> function imprimir() {{ window.parent.print(); }} </script>
                    <button class="btn-print" onclick="imprimir()">🖨️ Imprimir Pedido</button>
                """, height=50)
