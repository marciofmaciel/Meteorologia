import streamlit as st
import requests
import plotly.graph_objects as go

# --- FASE 1: CONFIGURAÇÃO DA UI E ESTILO (Modern Dark) ---
st.set_page_config(page_title="Dashboard Meteorológico", page_icon="🌤️", layout="centered")

# Injeção de CSS para o esquema de cores Modern Dark e design de cards
st.markdown("""
    <style>
    .main { background-color: #f4f4f4; color: #222222; }
    .stMetric { background-color: #ffffff; color: #222222; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.08); }
    .weather-card { 
        background-color: #ffffff; 
        color: #222222;
        padding: 30px; 
        border-radius: 15px; 
        text-align: center; 
        margin-bottom: 25px;
        border: 1px solid #e5e7eb;
    }
    h1, h2, h3 { color: #222222; font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- FASE 2 & 6: INTEGRAÇÃO DE API E REFINAMENTO (Caching) ---
@st.cache_data(ttl=600) # Fase 6.1: Cache de 10 minutos para otimização
def buscar_clima(cidade, api_key):
    # Fase 2.1 e 2.2: Endpoint e pontos de dados (temp, umidade, vento)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={api_key}&units=metric&lang=pt_br"
    
    try:
        # Fase 4.1: Tratamento de erros de rede e conexão
        response = requests.get(url, timeout=10)
        
        # Fase 4.1: Tratamento de localização inválida (Erro 404)
        if response.status_code == 404:
            return {"erro": "Cidade não encontrada. Verifique o nome e tente novamente."}
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return {"erro": "Erro de conexão. Verifique sua internet."}

# --- FASE 3: FUNCIONALIDADE DE LOCALIZAÇÃO ---
st.title("🌤️ Previsão do Tempo")
st.write("Consulte as condições climáticas de qualquer cidade em tempo real.")

# Fase 3.1: Elemento de UI para seleção de localização
with st.sidebar:
    st.header("Configurações")
    # API Key fixa para acesso automático
    api_key = "38654a38af0983bee7a5e7d127961968"
    st.info("A chave de API já está configurada automaticamente.")

cidade = st.text_input("Buscar cidade:", placeholder="Ex: São Paulo, BR", value="São Paulo")

# Função para retornar ícone e texto de risco do vento
def risco_vento_icon(vento):
    if vento < 10:
        return "🌴", "Baixo risco para pessoas"
    elif vento < 20:
        return "🌴‍➡️", "Atenção: vento moderado"
    else:
        return "🌴💨", "Perigo: vento forte"

# Função para retornar ícone e texto de risco da sensação térmica
def risco_sensacao_icon(feels_like):
    if feels_like < 10:
        return "❄️", "Risco: frio intenso"
    elif feels_like < 25:
        return "😊", "Confortável para a maioria"
    else:
        return "🥵", "Risco: calor intenso"

# Função para retornar texto de risco da umidade
def risco_umidade_texto(umidade):
    if umidade < 30:
        return "Alerta: Umidade muito baixa, risco para saúde."
    elif umidade < 60:
        return "Umidade moderada, atenção para hidratação."
    else:
        return "Umidade confortável para a maioria das pessoas."

# --- FASE 5: PRIORIZAÇÃO E EXECUÇÃO ---
if api_key:
    if cidade:
        dados = buscar_clima(cidade, api_key)
        
        if "erro" in dados:
            st.error(dados["erro"])
        else:
            # Extração dos dados para exibição
            temp = dados['main']['temp']
            feels_like = dados['main']['feels_like']
            umidade = dados['main']['humidity']
            vento = dados['wind']['speed']
            desc = dados['weather'][0]['description'].capitalize()
            icon_id = dados['weather'][0]['icon']

            # Fase 1.2 e 1.4: Layout do Painel e Ícones Gráficos
            st.markdown(f"""
                <div class="weather-card">
                    <h2>{dados['name']}, {dados['sys']['country']}</h2>
                    <img src="http://openweathermap.org/img/wn/{icon_id}@4x.png" width="120">
                    <h1 style="font-size: 60px; margin: 0;">{temp:.1f}°C</h1>
                    <p style="font-size: 20px; color: #9ca3af;">{desc}</p>
                </div>
            """, unsafe_allow_html=True)

            # Ponteiro analógico para umidade
            gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=umidade,
                title={'text': "Umidade (%)", 'font': {'size': 16}},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#222222"},
                    'steps': [
                        {'range': [0, 30], 'color': "red"},
                        {'range': [30, 60], 'color': "yellow"},
                        {'range': [60, 100], 'color': "green"},
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': umidade
                    }
                }
            ))
            gauge.update_layout(
                margin=dict(l=10, r=10, t=30, b=10),
                height=180,  # Altura reduzida
            )
            # Colunas para métricas secundárias
            col1, col2, col3 = st.columns([1,1,1])  # Proporção igual, responsivo

            # Coluna 1: Barra de umidade colorida + métrica
            with col1:
                col1.metric("Umidade", f"{umidade} %")
                st.markdown(
                    f"""
                    <div style="width: 100%; min-width: 80px; height: 28px; background: linear-gradient(to right, red 0%, red 30%, yellow 30%, yellow 60%, green 60%, green 100%); border-radius: 8px; margin-top: 8px; position: relative;">
                        <div style="position: absolute; left: {umidade}%; top: 0; height: 100%; width: 2px; background: #222; border-radius: 2px;"></div>
                        <div style="position: absolute; left: {umidade-4 if umidade>4 else 0}%; top: 0; height: 100%; width: 40px; color: #222; font-weight: bold; font-size: 14px; display: flex; align-items: center; justify-content: center;">
                            {umidade}%
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 12px; color: #666; margin-top: 2px;">
                        <span>0%</span>
                        <span>30%</span>
                        <span>60%</span>
                        <span>100%</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<div style='text-align:center; font-size: 0.95em; color: #666;'>{risco_umidade_texto(umidade)}</div>",
                    unsafe_allow_html=True
                )

            with col2:
                vento_icon, vento_texto = risco_vento_icon(vento)
                st.markdown(f"<div style='font-size: 2.2em; text-align:center'>{vento_icon}</div>", unsafe_allow_html=True)
                col2.metric("Vento", f"{vento} km/h")
                st.markdown(f"<div style='text-align:center; font-size: 0.95em; color: #666;'>{vento_texto}</div>", unsafe_allow_html=True)

            with col3:
                sensacao_icon, sensacao_texto = risco_sensacao_icon(feels_like)
                st.markdown(f"<div style='font-size: 2.2em; text-align:center'>{sensacao_icon}</div>", unsafe_allow_html=True)
                col3.metric("Sensação", f"{feels_like:.1f} °C")
                st.markdown(f"<div style='text-align:center; font-size: 0.95em; color: #666;'>{sensacao_texto}</div>", unsafe_allow_html=True)
else:
    st.warning("Por favor, insira sua chave de API na barra lateral para começar.")

# --- FASE 6: ITERAÇÃO E REFINAMENTO ---
# Nota: O estado atual utiliza st.cache_data para performance.
# Próximas iterações sugeridas: Gráficos de previsão para 5 dias e mapas.

# Ajuste responsivo para elementos customizados
st.markdown("""
    <style>
    @media (max-width: 900px) {
        .weather-card { padding: 16px !important; font-size: 16px !important; }
        .stMetric { padding: 10px !important; font-size: 15px !important; }
        img { width: 80px !important; }
    }
    @media (max-width: 600px) {
        .weather-card { padding: 8px !important; font-size: 13px !important; }
        .stMetric { padding: 6px !important; font-size: 13px !important; }
        img { width: 50px !important; }
        h1 { font-size: 32px !important; }
        h2 { font-size: 18px !important; }
    }
    </style>
""", unsafe_allow_html=True)