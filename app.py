import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit.components.v1 as components

# 1. Configuração da Página
st.set_page_config(page_title="Doceria da Vovó - Encomendas", page_icon="🍰", layout="wide")

# 2. CUSTOMIZAÇÃO AVANÇADA DE UI/UX (CSS - Fundo, Fontes e Botões)
st.markdown("""
    <style>
    /* Importar fontes chiques do Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Montserrat:wght@300;400;500;600&display=swap');

    /* Fundo da página: tom rosa/creme muito delicado que combina com a logo */
    .stApp { 
        background-color: #FFF3F5; 
    }

    /* Fonte principal para todo o texto */
    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif !important;
        color: #333333;
    }

    /* Fonte sofisticada (serifada) para os Títulos */
    h1, h2, h3, h4, h5, h6, .streamlit-expanderHeader { 
        font-family: 'Cormorant Garamond', serif !important; 
        color: #9b1a1a !important; 
        letter-spacing: 0.5px;
    }
    
    /* Design sofisticado para a caixa do Formulário */
    div[data-testid="stForm"] { 
        background-color: #ffffff; 
        border: none; 
        border-radius: 15px; 
        padding: 35px; 
        box-shadow: 0px 10px 30px rgba(155, 26, 26, 0.05); 
    }
    
    /* Botão Principal: Criar Encomenda Oficial (Muito mais chique) */
    div.stButton > button[kind="primary"] { 
        background: linear-gradient(135deg, #9b1a1a 0%, #7a1414 100%);
        color: #ffffff; 
        border: none; 
        border-radius: 30px; /* Bordas bem arredondadas */
        padding: 12px 30px; 
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 600; 
        text-transform: uppercase; /* Letras maiúsculas */
        letter-spacing: 1.5px;
        transition: all 0.4s ease; 
        box-shadow: 0px 6px 15px rgba(155, 26, 26, 0.25);
    }
    div.stButton > button[kind="primary"]:hover { 
        background: linear-gradient(135deg, #ddaf25 0%, #b88f1a 100%);
        box-shadow: 0px 8px 20px rgba(221, 175, 37, 0.4); 
        transform: translateY(-3px); 
    }

    /* Botões Secundários */
    div.stButton > button[kind="secondary"] { 
        background-color: transparent; 
        color: #9b1a1a; 
        border: 1px solid #9b1a1a; 
        border-radius: 20px; 
        font-weight: 500; 
        transition: all 0.3s ease; 
    }
    div.stButton > button[kind="secondary"]:hover { 
        background-color: #9b1a1a; 
        color: white; 
    }

    /* Campos de Input arredondados e elegantes */
    .stTextInput input, .stSelectbox select, .stTextArea textarea, .stDateInput input, .stTimeInput input { 
        border-radius: 10px !important; 
        border: 1px solid #e0e0e0 !important; 
        background-color: #fcfcfc !important;
    }
    .stTextInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus, .stDateInput input:focus, .stTimeInput input:focus { 
        border-color: #ddaf25 !important; 
        box-shadow: 0 0 0 1.5px #ddaf25 !important; 
        background-color: #ffffff !important;
    }

    /* Caixas de Encomenda na Aba de Visualizar */
    div[data-testid="stExpander"] { 
        background-color: #ffffff; 
        border-radius: 12px; 
        border: none; 
        box-shadow: 0px 4px 15px rgba(0,0,0,0.04); 
        margin-bottom: 15px; 
    }
    .streamlit-expanderHeader { 
        font-size: 18px !important; 
        font-weight: 600 !important; 
    }
    
    /* Divisórias suaves */
    hr { margin: 1.5em 0; border-top: 1px solid #f2e6e6; }
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
    try: st.image("logo.png", width=130)
    except: st.write("*(Logo)*")
with col_titulo:
    st.markdown("<h1 style='margin-bottom: 0; padding-bottom: 0;'>Sistema de Encomendas</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#ddaf25; font-size:22px; font-weight:500; font-family: \"Cormorant Garamond\", serif; margin-top: -5px;'>Doceria da Vovó ✨</p>", unsafe_allow_html=True)

st.markdown("---")

# 5. Abas Principais
aba_lancar, aba_visualizar = st.tabs(["📝 Lançar Novo Pedido", "📋 Painel de Controle"])

# ================= ABA 1: LANÇAR PEDIDO =================
with aba_lancar:
    with st.form("form_encomenda"):
        st.markdown("<h3 style='color:#9b1a1a;'>👤 Dados do Cliente</h3>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: cliente = st.text_input("Nome Completo *", placeholder="Ex: Maria Helena")
        with c2: telefone = st.text_input("WhatsApp / Telefone", placeholder="(00) 00000-0000")
        
        st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        
        st.markdown("<h3 style='color:#9b1a1a;'>🎂 Detalhes do Bolo</h3>", unsafe_allow_html=True)
        c3, c4 = st.columns([2, 1])
        with c3: sabor = st.text_input("Sabor e Recheio *", placeholder="Ex: Massa branca, recheio de ninho com morangos")
        with c4: tamanho = st.text_input("Tamanho/Peso *", placeholder="Ex: uma tira, meia tira, meia receita ou receita inteira")
        observacoes = st.text_area("Observações Especiais", placeholder="Mensagens para o topo, restrições alimentares, cor da decoração, etc.")

        st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        
        st.markdown("<h3 style='color:#9b1a1a;'>🚚 Logística de Entrega</h3>", unsafe_allow_html=True)
        c5, c6, c7 = st.columns(3)
        with c5: data_entrega = st.date_input("Data do Evento *")
        with c6: horario_retirada = st.time_input("Horário Combinado")
        with c7: local_retirada = st.selectbox("Local de Saída", ["Loja cofesa", "Loja centro", "Casa"])
        endereco = st.text_input("Endereço Completo (Obrigatório caso a opção seja entrega em 'Casa')")
        
        st.write("") 
        submit = st.form_submit_button("Criar Encomenda Oficial", type="primary", use_container_width=True)

        if submit and cliente and sabor and tamanho:
            doc_ref = db.collection("encomendas").document()
            doc_ref.set({"cliente": cliente, "telefone": telefone, "sabor": sabor, "tamanho": tamanho, "local_retirada": local_retirada, "endereco": endereco, "data_entrega": str(data_entrega), "horario_retirada": str(horario_retirada), "observacoes": observacoes, "status": "Pendente"})
            st.success(f"🎉 Fantástico! A encomenda de {cliente} foi registada e sincronizada.")
        elif submit:
            st.error("⚠️ Atenção: Os campos Nome, Sabor e Tamanho são obrigatórios.")

# ================= ABA 2: PAINEL DE CONTROLE =================
with aba_visualizar:
    docs = db.collection("encomendas").stream()
    pedidos = [dict(d.to_dict(), id=d.id) for d in docs]
    
    pendentes = sum(1 for p in pedidos if p.get('status') == 'Pendente')
    entregues = sum(1 for p in pedidos if p.get('status') == 'Entregue')
    
    dash1, dash2, dash3, dash4 = st.columns(4)
    dash1.metric("📦 Total de Pedidos", len(pedidos))
    dash2.metric("⏳ Pendentes", pendentes)
    dash3.metric("✅ Entregues", entregues)
    with dash4:
        st.write("") 
        if st.button("🔄 Atualizar Pedidos", use_container_width=True):
            st.rerun()
            
    st.markdown("<hr style='margin: 10px 0 20px 0;'>", unsafe_allow_html=True)

    if len(pedidos) == 0:
        st.info("Nenhuma encomenda registada no sistema até ao momento.")
        
    for p in pedidos:
        status_atual = p.get('status', 'Pendente')
        cor_badge = "#d4edda" if status_atual == "Entregue" else "#fcf2c5"
        cor_texto = "#155724" if status_atual == "Entregue" else "#856404"
        badge_html = f"<span style='background-color:{cor_badge}; color:{cor_texto}; padding:5px 15px; border-radius:20px; font-size:12px; font-family: \"Montserrat\", sans-serif; font-weight:600; letter-spacing: 0.5px;'>{status_atual.upper()}</span>"
        titulo_card = f"📅 {p.get('data_entrega')} às {p.get('horario_retirada', '--:--')} | {p.get('cliente', 'Sem nome')}"
        
        with st.expander(f"{titulo_card}"):
            html_card = f"""
            <div style='background-color: #fafafa; padding: 20px; border-radius: 12px; border-left: 6px solid #ddaf25;'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;'><span style='font-size: 20px; font-family: \"Cormorant Garamond\", serif; font-weight: 700; color: #9b1a1a;'>{p.get('cliente', 'Cliente')}</span>{badge_html}</div>
                <p style='margin: 0; color: #555; font-size: 14px;'><strong>📞 Fone:</strong> {p.get('telefone', 'Não informado')} &nbsp;|&nbsp; <strong>📍 Local:</strong> <span style='color: #9b1a1a; font-weight: 600;'>{p.get('local_retirada', '')}</span></p>
                <p style='margin: 8px 0 18px 0; color: #555; font-size: 14px;'><strong>🏠 Endereço:</strong> {p.get('endereco', 'Não preenchido')}</p>
                <div style='background-color: #ffffff; padding: 15px; border: 1px dashed #e0e0e0; border-radius: 8px;'>
                    <p style='margin: 0; font-size: 15px; color:#333;'><strong>🍰 Bolo:</strong> {p.get('sabor', '')}</p>
                    <p style='margin: 8px 0 0 0; font-size: 15px; color:#333;'><strong>⚖️ Tamanho/Peso:</strong> {p.get('tamanho', '')}</p>
                </div>
                <p style='margin-top: 18px; color: #555; font-size: 14px;'><strong>📝 Observações:</strong> <i style='color:#777;'>{p.get('observacoes', 'Nenhuma observação registada.')}</i></p>
            </div>
            """
            st.markdown(html_card, unsafe_allow_html=True)
            
            st.write("") # Espaçamento
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
                components.html(f"""
                    <style>.btn-print {{background-color: #ddaf25; border: none; color: white; padding: 10px 15px; font-weight: 600; border-radius: 20px; cursor: pointer; width: 100%; font-family: 'Montserrat', sans-serif; transition: all 0.3s ease; box-shadow: 0 4px 10px rgba(221,175,37,0.3);}} .btn-print:hover {{ background-color: #c79b1d; transform: translateY(-2px); }}</style>
                    <script> function imprimir() {{ window.parent.print(); }} </script>
                    <button class="btn-print" onclick="imprimir()">🖨️ Imprimir Pedido</button>
                """, height=50)
