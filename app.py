import streamlit as st
import pandas as pd
import os
from pathlib import Path
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import json
import requests
import seaborn as sns

st.set_page_config(page_title="Dashboard de Incidentes", layout="wide")

# Cores base do CSS (copiadas de :root)
PRIMARY_COLOR = "#004D7F"        # --primary-color
ACCENT_COLOR = "#007BFF"         # --accent-color
TEXT_COLOR = "#2F3645"           # --text-color
LIGHT_TEXT_COLOR = "#555A68"     # --light-text-color
CARD_BACKGROUND = "#FFFFFF"      # --card-background
BACKGROUND_COLOR = "#E6EEF5"     # --background-color
BORDER_COLOR = "#CDD5DB"         # --border-color
SHADOW_COLOR = "rgba(0, 0, 0, 0.15)"  # --shadow-color



st.markdown("""
<style>
/* Cor de fundo das abas */
.stTabs [data-baseweb="tab-list"] {
    background-color: #E6EEF5;
    border-radius: 8px;
    padding: 0.5rem;
}

/* Aba ativa (selecionada) */
.stTabs [data-baseweb="tab"] {
    font-weight: 500;
    color: #004D7F;
    border-bottom: 3px solid transparent;
}

.stTabs [aria-selected="true"] {
    background-color: #FFFFFF;
    color: #004D7F !important;
    border-bottom: 3px solid #007BFF;
    border-radius: 8px 8px 0 0;
}

/* Aba inativa */
.stTabs [aria-selected="false"]:hover {
    background-color: #dce7f1;
    color: #004D7F;
}
</style>
""", unsafe_allow_html=True)


# --- CSS Embutido ---
# Usando Path para um caminho mais robusto
css_file_path = Path("assecs") / "style.css"
if css_file_path.exists():
    with open(css_file_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    st.warning(
        f"⚠️ Arquivo de estilo CSS não encontrado em: {css_file_path}. Verifique o caminho e a estrutura de pastas.")



# Carregamento de dados


@st.cache_data
def load_data():
    df_loaded = pd.read_csv(
        "https://docs.google.com/spreadsheets/d/e/2PACX-1vQAgKT04JKwpEfS-_TVFBUwWVhxSKJsZz7tgohIJ-0YCAqNhBMjkwgMjzxSUm8-eonbxYv6hGrbhE8X/pub?output=csv"
    )
    df_loaded["Abertura"] = pd.to_datetime(
        df_loaded["Abertura"], errors='coerce', dayfirst=True)
    df_loaded = df_loaded.dropna(subset=["Abertura"])
    df_loaded = df_loaded.sort_values("Abertura")
    df_loaded["Month"] = df_loaded["Abertura"].apply(
        lambda x: f"{x.year}-{x.month:02d}")
    return df_loaded


df = load_data()

st.markdown(
    """
    <div style='position: relative; bottom: 0; text-align: center; color: #B0C4D6; font-size: 0.75rem; margin-top: 2rem;'>
    </div>
    """, unsafe_allow_html=True
)

with st.sidebar:
    st.markdown(
        """
        <div style="text-align: center; margin: 0.5rem 0 1rem;">
            <h2 style="
                color: #FFFFFF;
                font-family: 'Segoe UI', sans-serif;
                font-size: 1.5rem;
                font-weight: 100;
                margin-bottom: 0.2rem;
            ">T.I MOSELE</h2>
            <p style="
                color: #B0C4D6;
                font-size: 0.95rem;
                font-style: italic;
                margin: 0;
            ">Tecnologia e Inovação</p>
        </div>
        <hr style="border: 0; height: 1px; background-color: #ffffff33; margin: 0.8rem 0;">
        """,
        unsafe_allow_html=True
    )



# Filtros
months = sorted(df["Month"].dropna().unique())
loja_options = sorted(df["Loja"].dropna().unique())
solicit_options = sorted(df["Solicitante"].dropna().unique())
status_options = sorted(df["Status"].dropna().unique())
analista_options = sorted(df["Analista"].dropna().unique())
prioridade_options = sorted(df["NV. Prioridade"].dropna().unique())
sla_options = sorted(df["SLA"].dropna().unique())
setor_options = sorted(df["Setor"].dropna().unique())

with st.sidebar.expander("Filtrar por Mês", expanded=False):
    sel_todos_meses = st.checkbox("Selecionar todos os meses", value=True)
    selected_months = months if sel_todos_meses else st.multiselect(
        "Meses:", months, default=[])


with st.sidebar.expander("Filtrar por Período", expanded=False):
    sel_filtrar_periodo = st.checkbox("Selecionar por período", value=False)
    if sel_filtrar_periodo:
        data_min = df["Abertura"].min()
        data_max = df["Abertura"].max()
        selected_period = st.date_input("Selecione o período:", [
                                        data_min.date(), data_max.date()])
    else:
        selected_period = None

with st.sidebar.expander("Filtrar por Loja", expanded=False):
    sel_todas_lojas = st.checkbox("Selecionar todas as lojas", value=True)
    selected_loja = loja_options if sel_todas_lojas else st.multiselect(
        "Lojas:", loja_options, default=[])

with st.sidebar.expander("Filtrar por Solicitante", expanded=False):
    sel_todos_solicit = st.checkbox(
        "Selecionar todos os solicitantes", value=True)
    selected_solicit = solicit_options if sel_todos_solicit else st.multiselect(
        "Solicitantes:", solicit_options, default=[])

with st.sidebar.expander("Filtrar por Status", expanded=False):
    sel_todos_status = st.checkbox("Selecionar todos os status", value=True)
    selected_status = status_options if sel_todos_status else st.multiselect(
        "Status:", status_options, default=[])

with st.sidebar.expander("Filtrar por Analista", expanded=False):
    sel_todos_analistas = st.checkbox(
        "Selecionar todos os analistas", value=True)
    selected_analista = analista_options if sel_todos_analistas else st.multiselect(
        "Analistas:", analista_options, default=[])

with st.sidebar.expander("Filtrar por NV. Prioridade", expanded=False):
    sel_todas_prioridades = st.checkbox(
        "Selecionar todas as prioridades", value=True)
    selected_prioridade = prioridade_options if sel_todas_prioridades else st.multiselect(
        "Prioridades:", prioridade_options, default=[])

with st.sidebar.expander("Filtrar por SLA", expanded=False):
    sel_todos_sla = st.checkbox("Selecionar todos os SLA", value=True)
    selected_sla = sla_options if sel_todos_sla else st.multiselect(
        "SLA:", sla_options, default=[])

with st.sidebar.expander("Filtrar por Setor", expanded=False):
    sel_setor = st.checkbox("Selecionar todos os setores", value=True)
    selected_setor = setor_options if sel_setor else st.multiselect(
        "Setor", setor_options, default=[])


# Filtros
df_filtered = df[
    (df["Month"].isin(selected_months)) &
    (df["Loja"].isin(selected_loja)) &
    (df["Solicitante"].isin(selected_solicit)) &
    (df["Status"].isin(selected_status)) &
    (df["Analista"].isin(selected_analista)) &
    (df["NV. Prioridade"].isin(selected_prioridade)) &
    (df["SLA"].isin(selected_sla)) &
    (df["Setor"].isin(selected_setor))
]

if sel_filtrar_periodo and selected_period is not None and len(selected_period) == 2:
    start_date, end_date = pd.to_datetime(
        selected_period[0]), pd.to_datetime(selected_period[1])
    df_filtered = df_filtered[(df_filtered["Abertura"] >= start_date) & (
        df_filtered["Abertura"] <= end_date)]


# Conversão
def converter_para_dias(coluna):
    return (
        coluna.astype(str)
              .str.lower()
              .str.replace("h", "", regex=False)
              .str.replace(",", ".", regex=False)
              .str.extract(r"([\d\.]+)")
              .astype(float) / 24
    )


df_status = df_filtered.copy()
df_status["Solu. Real (dias)"] = converter_para_dias(df_status["Solu. Real"])
df_status["Atend. Real (dias)"] = converter_para_dias(df_status["Atend. Real"])

# KPIs
total_eventos = len(df_filtered)
media_resolucao = df_status["Solu. Real (dias)"].mean()
media_resolucao_display = f"{media_resolucao:.1f} dias" if not pd.isna(
    media_resolucao) else "N/A"

media_atendimento = df_status["Atend. Real (dias)"].mean()
media_atendimento_display = f"{media_atendimento:.1f} dias" if not pd.isna(
    media_atendimento) else "N/A"
# Nota média (avaliações)
media_nota = df_filtered["Nota"].mean()
media_nota_display = f"{media_nota:.1f}" if not pd.isna(media_nota) else "N/A"
avaliacoes_validas = df_filtered["Nota"].dropna()
qtd_avaliacoes = len(avaliacoes_validas)
media_nota = avaliacoes_validas.mean()
media_nota_display = f"{media_nota:.1f}" if qtd_avaliacoes > 0 else "N/A"


# Cor condicional para avaliação
if media_nota >= 4.5:
    nota_class = "kpi-green"
elif media_nota >= 3.0:
    nota_class = "kpi-yellow"
else:
    nota_class = "kpi-red"


qtd_critico = df_filtered["NV. Prioridade"].fillna(
    "").str.lower().eq("crítico").sum()
# Porcentagem de atendimento de status
total_status = df_filtered["Status"].value_counts(normalize=True) * 100
pct_aberto = total_status.get("Em aberto", 0)
pct_andamento = total_status.get("Em atendimento", 0)
pct_solu = total_status.get("Encerrado", 0)
pct_aberto = round(total_status.get("Em aberto", 0), 1)
pct_andamento = round(total_status.get("Em atendimento", 0), 1)
pct_solu = round(total_status.get("Encerrado", 0), 1)

# Em Aberto
if pct_aberto == 0:
    aberto_value = "0.0%"
    status_class_aberto = "kpi-gray"
else:
    aberto_value = f"{pct_aberto:.1f}%"
    status_class_aberto = "kpi-red" if pct_aberto > 10 else "kpi-green"

# Em Atendimento
if pct_andamento == 0:
    andamento_value = "0.0%"
    status_class_andamento = "kpi-gray"
else:
    andamento_value = f"{pct_andamento:.1f}%"
    status_class_andamento = "kpi-yellow" if pct_andamento > 5 else "kpi-green"

# Encerrados
if pct_solu == 0:
    encerrado_value = "0.0%"
    status_class_solu = "kpi-gray"
else:
    encerrado_value = f"{pct_solu:.1f}%"
    status_class_solu = "kpi-green" if pct_solu > 85 else "kpi-red"

# Sla em porcentagem
df_status["Solu. Prevista"] = pd.to_datetime(
    df_status["Solu. Prevista"], dayfirst=True, errors="coerce")
df_status["Solu. Real"] = pd.to_datetime(
    df_status["Solu. Real"], dayfirst=True, errors="coerce")
df_status["SLA Cumprido"] = df_status["Solu. Real"] <= df_status["Solu. Prevista"]
sla_atingido_pct = df_status["SLA Cumprido"].mean() * 100
sla_atingido_pct = round(sla_atingido_pct, 1)


col1, col2, col3, col4, col5= st.columns(5)

with col1:
    st.markdown(f"""
    <div class="kpi-card" title="Total de registros filtrados no período e critérios selecionados.">
        <div class="kpi-value">{total_eventos}</div>
        <div class="kpi-title">📊 Eventos</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card kpi-blue" title="Tempo médio para solução completa dos chamados.">
        <div class="kpi-value">{media_resolucao_display}</div>
        <div class="kpi-title">⏱️ Resolução</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card kpi-blue" title="Tempo médio de início de atendimento após a abertura.">
        <div class="kpi-value">{media_atendimento_display}</div>
        <div class="kpi-title">🕑 Atendimento</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card {status_class_solu}" title="Chamados finalizados com atendimento concluído.">
        <div class="kpi-value">{encerrado_value}</div>
        <div class="kpi-title">✅ Encerrados</div>
    </div>
    """, unsafe_allow_html=True)
with col5:
    st.markdown(f"""
    <div class="kpi-card {nota_class}" title="Média das avaliações (de 1 a 5)">
        <div class="kpi-value">{media_nota_display}</div>
        <div class="kpi-title">⭐ Avaliação</div>
    </div>
    """, unsafe_allow_html=True)


def aplicar_tema_padrao(fig, titulo=None):
    fig.update_layout(
        title=titulo,
        plot_bgcolor=BACKGROUND_COLOR,
        paper_bgcolor=CARD_BACKGROUND,
        font_color=TEXT_COLOR,
        title_font_color=PRIMARY_COLOR,
        xaxis_title_font_color=TEXT_COLOR,
        yaxis_title_font_color=TEXT_COLOR,
        legend_title_font=dict(size=14, family="Segoe UI", color=TEXT_COLOR),
        legend_font=dict(size=12, family="Segoe UI", color=LIGHT_TEXT_COLOR),
        legend_bgcolor='rgba(0,0,0,0)',
        hovermode="x unified",
        autosize=True,
        margin=dict(l=40, r=40, t=50, b=80),
        font=dict(family="Segoe UI", size=12, color=TEXT_COLOR),
        transition=dict(duration=500, easing='cubic-in-out')
    )
    fig.update_xaxes(
        tickangle=45,
        showgrid=True,
        gridcolor=BORDER_COLOR,
        tickfont_color=TEXT_COLOR
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=BORDER_COLOR,
        tickfont_color=TEXT_COLOR
    )
    return fig


# --- TABS PARA ORGANIZAÇÃO ---
tab1, tab2, tab3, tab4 = st.tabs(["🧠 Relatório Inteligente","📊 Indicadores Gerais", "📈 Desempenho por Equipe", "⭐Avaliação", ])



# ============================
# 🧠  RELATÓRIO INTELIGENTE 
# ============================
with tab1:
       
    
    # Analista com melhor média (se houver dados)
    df_nota_analista = df_filtered.dropna(subset=["Nota"])
    analista_top = "N/A"
    nota_top_analista = 0
    if not df_nota_analista.empty:
        media_analista_nota = df_nota_analista.groupby("Analista")["Nota"].mean().reset_index()
        media_analista_nota = media_analista_nota.sort_values("Nota", ascending=False)
        analista_top = media_analista_nota.iloc[0]["Analista"]
        nota_top_analista = media_analista_nota.iloc[0]["Nota"]

    # Setor com melhor tempo médio de solução
    setor_top = "N/A"
    if "Setor" in df_status.columns:
        setor_solucao = df_status.groupby("Setor")["Solu. Real (dias)"].mean().reset_index()
        setor_solucao = setor_solucao.dropna().sort_values("Solu. Real (dias)")
        if not setor_solucao.empty:
            setor_top = setor_solucao.iloc[0]["Setor"]

    # Loja com mais avaliações
    loja_top = "N/A"
    qtd_av_loja_top = 0
    if "Loja" in df_filtered.columns:
        loja_aval = df_filtered.dropna(subset=["Nota"]).groupby("Loja")["Nota"].count().reset_index()
        loja_aval.columns = ["Loja", "Qtd"]
        loja_aval = loja_aval.sort_values("Qtd", ascending=False)
        if not loja_aval.empty:
            loja_top = loja_aval.iloc[0]["Loja"]
            qtd_av_loja_top = loja_aval.iloc[0]["Qtd"]

    # Construção com estilo "report-section"
    with st.container():
        st.markdown(f"""
        <div class="report-section">
        <h3 style='margin-top: 0;'>🧠 Relatório Inteligente</h3>

        <div class="report-badges-container">
            <div class="report-badge report-badge-info">
                📄 Total de chamados:<br><strong>{total_eventos}</strong>
            </div>
            <div class="report-badge report-badge-info">
                ⏱️ Tempo médio de resolução:<br><strong>{media_resolucao_display}</strong>
            </div>
            <div class="report-badge report-badge-info">
                🕑 Tempo médio até atendimento:<br><strong>{media_atendimento_display}</strong>
            </div>
        </div>


        <div class="report-badges-container">
            <div class="report-badge report-badge-info">
            📊 SLA cumprido em <strong>{sla_atingido_pct:.1f}%</strong> dos chamados.
            </div>
            <div class="report-badge report-badge-error">
            🚨 Abertos: <strong>{aberto_value}</strong>
            </div>
            <div class="report-badge report-badge-warning">
            🛠️ Em Atendimento: <strong>{andamento_value}</strong>
            </div>
            <div class="report-badge report-badge-success">
            ✅ Encerrados: <strong>{encerrado_value}</strong>
            </div>
            <div class="report-badge report-badge-error">
            🔥 Críticos (prioridade alta): <strong>{qtd_critico}</strong>
            </div>
        </div>

        <h4>📊 Análise Gráfica</h4>
        <div class="report-badge report-badge-info">
            📈 Os gráficos apresentados mostram a distribuição dos chamados ao longo do tempo, destacando os principais setores demandantes e os analistas com maior volume de atendimentos.<br>
            🔍 Também foi possível observar uma concentração significativa de solicitações em horários específicos (via mapa de calor), e uma forte presença de registros em determinadas lojas da rede.<br>
            ✅ A distribuição por status evidencia a eficiência do time, enquanto os gráficos de prioridade e SLA ajudam a identificar pontos de atenção estratégicos.
        </div>

        <h4>💡 Sugestões Estratégicas</h4>
        <div class="report-badges-container">
            <div class="report-badge {'report-badge-success' if pct_solu > 85 else 'report-badge-warning'}">
            {'✅ Ótimo índice de encerramento de chamados.' if pct_solu > 85 else '⚠️ A taxa de encerramento está abaixo do ideal. Avaliar atrasos ou reaberturas.'}
            </div>
            <div class="report-badge {'report-badge-success' if qtd_critico <= 10 else 'report-badge-error'}">
            {'✅ A quantidade de chamados críticos está sob controle.' if qtd_critico <= 10 else '🔥 Alto número de chamados críticos identificados. Priorizar essas demandas.'}
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)


# ============================
# 📊 INDICADORES GERAIS
# ============================
with tab2:
    
        # Linha temporal
    fig6 = px.line(
        df_filtered,
        x="Abertura",
        color_discrete_sequence=[PRIMARY_COLOR]
    )
    media_diaria = df_filtered.groupby("Abertura").size().mean()

    fig6.add_annotation(
    text=f"Média diária: {media_diaria:.1f} chamados",
    xref="paper", yref="paper",
    x=0.5, y=1.12, showarrow=False,
    font=dict(size=14, color=PRIMARY_COLOR))

    fig6 = aplicar_tema_padrao(fig6, "Chamados Abertos por Dia")
    st.plotly_chart(fig6, use_container_width=True)

        # Mês de encerramento com % e total
    df_filtered["Encerramento"] = pd.to_datetime(
        df_filtered["Encerramento"], dayfirst=True, errors="coerce")
    df_filtered = df_filtered.dropna(subset=["Encerramento"])
    df_filtered["Month"] = df_filtered["Encerramento"].dt.to_period(
        "M").astype(str)
    contagem = df_filtered["Month"].value_counts().sort_index()
    total_chamados = contagem.sum()
    df_mes = contagem.reset_index()
    df_mes.columns = ["Month", "Chamados"]
    df_mes["Porcentagem"] = (df_mes["Chamados"] /
                             total_chamados * 100).round(1)
    df_mes["Rótulo"] = df_mes["Chamados"].astype(
        str) + " chamados - " + df_mes["Porcentagem"].astype(str) + "%"
    fig = px.bar(
        df_mes,
        x="Month",
        y="Chamados",
        text="Rótulo",
        labels={"Month": "Mês", "Chamados": "Encerrados"},
        color_discrete_sequence=["#004D7F"]
    )
    media_mensal = df_mes["Chamados"].mean()

    fig.add_annotation(
    text=f"Média mensal: {media_mensal:.1f} encerramentos",
    xref="paper", yref="paper",
    x=0.5, y=1.12, showarrow=False,
    font=dict(size=14, color=PRIMARY_COLOR)
)

    fig.update_traces(textposition="outside")
    fig = aplicar_tema_padrao(
        fig, "Chamados Encerrados por Mês com Porcentagem")
    st.plotly_chart(fig, use_container_width=True)
    

    # Status - Pizza
    fig5 = px.pie(
        df_filtered,
        names="Status",
        hole=0.4,
        color_discrete_sequence=[PRIMARY_COLOR]
    )
    fig5 = aplicar_tema_padrao(fig5, "Distribuição por Status")
    st.plotly_chart(fig5, use_container_width=True)
    
    # SLA
    fig = px.histogram(
        df_filtered,
        x="SLA",
        text_auto=True,
        color_discrete_sequence=[PRIMARY_COLOR, ACCENT_COLOR]
    )
    sla_moda = df_filtered["SLA"].mode().iloc[0]

    fig.add_annotation(
    text=f"SLA mais comum: {sla_moda}",
    xref="paper", yref="paper",
    x=0.5, y=1.12, showarrow=False,
    font=dict(size=14, color=PRIMARY_COLOR)
)
    fig = aplicar_tema_padrao(fig, "Distribuição de SLA dos Chamados")
    st.plotly_chart(fig, use_container_width=True)
    
        # Prioridade - Pizza
    fig_prioridade = px.pie(
        df_filtered,
        names="NV. Prioridade",
        hole=0.4,
        color_discrete_sequence=[PRIMARY_COLOR, ACCENT_COLOR],
    )
    fig_prioridade = aplicar_tema_padrao(
        fig_prioridade, "Percentual por Prioridade")
    st.plotly_chart(fig_prioridade, use_container_width=True)
    
    # Top 10 Solicitantes
    top_solicitantes = df_filtered["Solicitante"].value_counts().head(
        10).reset_index()
    top_solicitantes.columns = ["Solicitante", "Total"]
    fig0 = px.bar(
        top_solicitantes, x="Solicitante", y="Total",
        text="Total",
        color_discrete_sequence=[PRIMARY_COLOR, ACCENT_COLOR]
    )
    fig0 = aplicar_tema_padrao(fig0, "👥 Top 10 Solicitantes com Mais Chamados")
    st.plotly_chart(fig0, use_container_width=True)
    
    
    # Heatmap de horários
    df_filtered["Dia da Semana"] = df_filtered["Abertura"].dt.day_name()
    df_filtered["Hora"] = df_filtered["Abertura"].dt.hour
    fig_heatmap = px.density_heatmap(
        df_filtered,
        x="Hora",
        y="Dia da Semana",
        color_continuous_scale="blues"
    )
    hora_pico = df_filtered["Hora"].value_counts().idxmax()

    fig_heatmap.add_annotation(
    text=f"Horário de pico: {hora_pico}h",
    xref="paper", yref="paper",
    x=0.5, y=1.12, showarrow=False,
    font=dict(size=14, color=PRIMARY_COLOR)
)

    fig_heatmap = aplicar_tema_padrao(
        fig_heatmap, "Horários de Pico de chamados")
    st.plotly_chart(fig_heatmap, use_container_width=True)

    # WordCloud
    st.markdown("### ☁️ Principais Assuntos dos Chamados")
    texto_assuntos = " ".join(df_filtered["Assunto"].dropna().astype(str))
    wordcloud = WordCloud(background_color="white", width=800,
                          height=400).generate(texto_assuntos)
    fig_wc, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig_wc)


    # Mapa por estado
    geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    geojson_data = requests.get(geojson_url).json()
    df_filtered["Estado"] = df_filtered["Estado"].str.strip().replace({
        "Tocatins": "Tocantins"})
    chamados_estado = df_filtered["Estado"].value_counts().reset_index()
    chamados_estado.columns = ["Estado", "Chamados"]
    fig6 = px.choropleth(
        chamados_estado,
        geojson=geojson_data,
        locations="Estado",
        featureidkey="properties.name",
        color="Chamados",
        color_continuous_scale=["#A0C4FF", "#007BFF", "#004D7F"],
        scope="south america"
    )
    fig6.update_geos(fitbounds="locations", visible=False)
    fig6 = aplicar_tema_padrao(
        fig6, "Distribuição de Chamados por Estado (Brasil)")
    st.plotly_chart(fig6, use_container_width=True)


# ============================
# 📈 DESEMPENHO POR EQUIPE
# ============================

with tab3:
    
    # Calcular média de atendimento por analista (baseado em df_status)
    media_analista = (
        df_status.groupby("Analista")["Atend. Real (dias)"]
        .mean()
        .reset_index()
        .sort_values("Atend. Real (dias)", ascending=False))
    # Tempo médio por analista (já estava fora)
    fig2 = px.bar(
        media_analista,
        x="Analista",
        y="Atend. Real (dias)",
        text_auto=".2f",
        labels={"Atend. Real (dias)": "Média de Atendimento (dias)"},
        color_discrete_sequence=[PRIMARY_COLOR, ACCENT_COLOR]
    )
    fig2 = aplicar_tema_padrao(fig2, "Tempo Médio de Atendimento por Analista")
    st.plotly_chart(fig2, use_container_width=True)

    # Gráficos comparativos por loja, analista, setor

    def plot_media_por(campo, titulo):
        medias = df_status.groupby(
        campo
    )[["Atend. Real (dias)", "Solu. Real (dias)"]].mean().dropna().reset_index()

        if not medias.empty:
         medias["Média Geral"] = medias[["Atend. Real (dias)", "Solu. Real (dias)"]].mean(axis=1)
         medias = medias.sort_values("Média Geral", ascending=False)

        fig8 = px.bar(
            medias,
            x=campo,
            y=["Atend. Real (dias)", "Solu. Real (dias)"],
            barmode="group",
            text_auto=".1f",
            labels={"value": "Dias", campo: campo},
            color_discrete_sequence=["#004D7F", "#007BFF"]
        )

        # CORREÇÃO: calculando a média geral da coluna "Média Geral" da variável `medias`, não `df_filtered`
        media_geral = medias["Média Geral"].mean()

        # CORREÇÃO: adicionar anotação ao gráfico correto (fig8, não fig_avaliacao)
        fig8.add_annotation(
            text=f"Média geral: {media_geral:.1f} dias",
            xref="paper", yref="paper",
            x=0.5, y=1.12, showarrow=False,
            font=dict(size=14, color=PRIMARY_COLOR)
        )

        fig8 = aplicar_tema_padrao(fig8, titulo)
        st.plotly_chart(fig8, use_container_width=True)

    # Agora SIM dentro da aba:
    plot_media_por("Loja", "Média de Atendimento e Solução por Loja")
    plot_media_por("Analista", "Média de Atendimento e Solução por Analista")
    plot_media_por("Setor", "Média de Atendimento e Solução por Setor")


# ============================
# ⭐ Avaliação
# ============================

with tab4:
    

    avaliacoes_analista = df_filtered.dropna(subset=["Nota"])
    if not avaliacoes_analista.empty:
        fig_avaliacao = px.box(
            avaliacoes_analista,
            x="Analista",
            y="Nota",
            points="all",  # Mostra todos os pontos
            color_discrete_sequence=[PRIMARY_COLOR],
            labels={"Nota": "Avaliação (1 a 5)", "Analista": "Analista"}
        )
        media_geral_nota = df_filtered["Nota"].dropna().mean()

        fig_avaliacao.add_annotation(
        text=f"Média geral: {media_geral_nota:.1f}",
        xref="paper", yref="paper",
        x=0.5, y=1.12, showarrow=False,
        font=dict(size=14, color=PRIMARY_COLOR)
    )

        fig_avaliacao = aplicar_tema_padrao(
            fig_avaliacao, "Avaliações por Analista")
        st.plotly_chart(fig_avaliacao, use_container_width=True)
    else:
        st.info("Ainda não há avaliações suficientes para exibir esse gráfico.")
        

    st.markdown("### 🧮 Quantidade de Avaliações por Analista")

    avaliacoes_por_analista = (
    df_filtered.dropna(subset=["Nota"])
    .groupby("Analista")["Nota"]
    .count()
    .reset_index()
    .rename(columns={"Nota": "Quantidade de Avaliações"})
    .sort_values("Quantidade de Avaliações", ascending=False)
)

    fig_qtd_avaliacoes = px.bar(
        avaliacoes_por_analista,
        x="Analista",
        y="Quantidade de Avaliações",
        text="Quantidade de Avaliações",
        color_discrete_sequence=[PRIMARY_COLOR],
        )
    fig_qtd_avaliacoes = aplicar_tema_padrao(
        fig_qtd_avaliacoes, "⭐Avaliações Recebidas por Analista")
    st.plotly_chart(fig_qtd_avaliacoes, use_container_width=True)
    
    # Média de Avaliação por Setor
    def plot_media_nota_por(campo, titulo):
        df_nota = df_filtered.dropna(subset=["Nota"])
        medias = df_nota.groupby(campo)["Nota"].mean().reset_index()
        if not medias.empty:
            medias = medias.sort_values("Nota", ascending=False)
            fig = px.bar(
                medias,
                x=campo,
                y="Nota",
                text_auto=".1f",
                labels={"Nota": "Média de Nota"},
                color_discrete_sequence=[PRIMARY_COLOR]
            )
        fig = aplicar_tema_padrao(fig, titulo)
        st.plotly_chart(fig, use_container_width=True)
    plot_media_nota_por("Setor", "⭐Média de Avaliação por Setor")
    plot_media_nota_por("Loja", "⭐Média de Avaliação por Loja")

    
# Tabela
st.dataframe(df_filtered)

# --- Rodapé ---
st.markdown("---", unsafe_allow_html=True)
st.markdown("<div style='text-align:center; color: gray;'><em>Desenvolvido por <strong>T.I MOSELE</strong></em> — Indicadores atualizados para <strong>Julho de 2025</strong></div>", unsafe_allow_html=True)
