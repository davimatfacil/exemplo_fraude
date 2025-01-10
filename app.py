import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(
    page_title="Monitor de Fraudes",
    page_icon="🔍",
    layout="wide"
)

# Função para gerar dados simulados
def gerar_dados_transacoes(n_transacoes):
    np.random.seed(42)
    
    # Dados base
    datas = [datetime.now() - timedelta(days=x) for x in range(n_transacoes)]
    valores = np.random.lognormal(mean=4.0, sigma=1.0, size=n_transacoes)
    
    # Adicionar algumas transações fraudulentas
    categorias = np.random.choice(['Compras', 'Saques', 'Transferências'], n_transacoes)
    localizacoes = np.random.choice(['SP', 'RJ', 'MG', 'RS', 'PR'], n_transacoes)
    
    # Criar algumas características suspeitas
    horarios = []
    for _ in range(n_transacoes):
        if np.random.random() < 0.1:  # 10% de chance de ser em horário suspeito
            hora = np.random.randint(0, 5)  # Horário entre 0h e 5h
        else:
            hora = np.random.randint(6, 23)
        horarios.append(f"{hora:02d}:{np.random.randint(0, 59):02d}")
    
    # Definir algumas transações como fraudulentas
    is_fraude = []
    for i in range(n_transacoes):
        # Critérios para considerar uma transação como suspeita
        valor_alto = valores[i] > np.percentile(valores, 95)
        horario_suspeito = int(horarios[i].split(':')[0]) < 5
        
        if (valor_alto and horario_suspeito) or np.random.random() < 0.05:
            is_fraude.append(1)
        else:
            is_fraude.append(0)
    
    # Criar DataFrame
    df = pd.DataFrame({
        'data': datas,
        'valor': valores,
        'categoria': categorias,
        'localizacao': localizacoes,
        'horario': horarios,
        'fraude': is_fraude
    })
    
    return df

# Título principal
st.title("🔍 Monitor de Fraudes em Tempo Real")

# Sidebar com filtros
st.sidebar.header("Filtros")
n_dias = st.sidebar.slider("Número de dias para análise", 1, 30, 7)
limite_valor = st.sidebar.number_input("Limite de valor suspeito", 1000.0, 10000.0, 5000.0)

# Gerar dados simulados
df = gerar_dados_transacoes(n_dias * 100)

# Métricas principais
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_transacoes = len(df)
    st.metric("Total de Transações", f"{total_transacoes:,}")

with col2:
    total_fraudes = df['fraude'].sum()
    st.metric("Transações Suspeitas", f"{total_fraudes:,}")

with col3:
    taxa_fraude = (total_fraudes / total_transacoes) * 100
    st.metric("Taxa de Fraude", f"{taxa_fraude:.2f}%")

with col4:
    valor_total_fraudes = df[df['fraude'] == 1]['valor'].sum()
    st.metric("Valor Total Suspeito", f"R$ {valor_total_fraudes:,.2f}")

# Gráficos
st.subheader("Análise Visual")

col1, col2 = st.columns(2)

with col1:
    # Gráfico de fraudes por categoria
    fraudes_categoria = df[df['fraude'] == 1]['categoria'].value_counts()
    fig_categoria = px.pie(
        values=fraudes_categoria.values,
        names=fraudes_categoria.index,
        title="Distribuição de Fraudes por Categoria"
    )
    st.plotly_chart(fig_categoria)

with col2:
    # Gráfico de fraudes por localização
    fraudes_local = df[df['fraude'] == 1]['localizacao'].value_counts()
    fig_local = px.bar(
        x=fraudes_local.index,
        y=fraudes_local.values,
        title="Fraudes por Localização"
    )
    st.plotly_chart(fig_local)

# Tabela de transações suspeitas
st.subheader("Transações Suspeitas Recentes")
transacoes_suspeitas = df[df['fraude'] == 1].sort_values('data', ascending=False)
st.dataframe(
    transacoes_suspeitas[['data', 'valor', 'categoria', 'localizacao', 'horario']],
    hide_index=True
)

# Alertas em tempo real
st.subheader("Alertas em Tempo Real")
for _, transacao in transacoes_suspeitas.head(3).iterrows():
    st.warning(f"""
        🚨 Transação suspeita detectada:
        - Data/Hora: {transacao['data'].strftime('%d/%m/%Y')} {transacao['horario']}
        - Valor: R$ {transacao['valor']:,.2f}
        - Categoria: {transacao['categoria']}
        - Localização: {transacao['localizacao']}
    """)

# Regras de detecção
st.sidebar.subheader("Regras de Detecção")
st.sidebar.markdown("""
- Transações de alto valor em horários suspeitos
- Múltiplas transações em locais diferentes
- Padrões atípicos de comportamento
""")