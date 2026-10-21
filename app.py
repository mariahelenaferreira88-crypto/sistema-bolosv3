import firebase_admin
from firebase_admin import credentials, firestore
import os
import time
import textwrap

# 1. Conecta ao Firebase usando o seu arquivo JSON
cred = credentials.Certificate("chave.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def imprimir_pedido(pedido, doc_id):
    # Largura máxima de caracteres para impressoras térmicas (32 para 58mm, 48 para 80mm)
    LARGURA = 32
    
    def quebrar(texto):
        """Quebra textos longos para não cortarem no papel"""
        if not texto:
            return ""
        return "\n".join(textwrap.wrap(str(texto), width=LARGURA))

    # Desenho do cupom térmico
    cupom = f"""
{'-'*LARGURA}
{'DOCERIA DA VOVO'.center(LARGURA)}
{'NOVA ENCOMENDA'.center(LARGURA)}
{'-'*LARGURA}

CLIENTE: 
{quebrar(pedido.get('cliente', ''))}
FONE: {pedido.get('telefone', '')}

DATA: {pedido.get('data_entrega', '')}
HORA: {pedido.get('horario_retirada', '')}
LOCAL: {pedido.get('local_retirada', '')}

ENDERECO:
{quebrar(pedido.get('endereco', ''))}
{'-'*LARGURA}
BOLO: 
{quebrar(pedido.get('sabor', ''))}

TAMANHO/PESO: 
{quebrar(pedido.get('tamanho', ''))}
{'-'*LARGURA}
OBSERVACOES:
{quebrar(pedido.get('observacoes', ''))}
{'-'*LARGURA}
.
.
.
"""
    
    # Salva o formato estreito em um arquivo temporário
    with open("cupom_temp.txt", "w", encoding="utf-8") as f:
        f.write(cupom)
    
    # Manda o Windows imprimir o arquivo
    try:
        os.startfile("cupom_temp.txt", "print")
        print(f"✅ Cupom enviado para a impressora: {pedido.get('cliente', '')}")
    except Exception as e:
        print("Erro ao tentar imprimir:", e)

# Função que "ouve" o banco de dados em tempo real
def ao_receber_dados(col_snapshot, changes, read_time):
    for change in changes:
        if change.type.name == 'ADDED':
            pedido = change.document.to_dict()
            if pedido.get("status") == "Pendente":
                imprimir_pedido(pedido, change.document.id)

print("🤖 Robô da Doceria iniciado! Aguardando novos pedidos para impressão térmica...")
col_query = db.collection("encomendas")
watch = col_query.on_snapshot(ao_receber_dados)

while True:
    time.sleep(1)
