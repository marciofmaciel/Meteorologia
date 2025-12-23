def desc_alerta(desc):
    desc = desc.lower()
    if "chuva" in desc:
        return "Leve guarda-chuva e atenção a vias escorregadias."
    if "nublado" in desc:
        return "Céu encoberto, boa opção para atividades ao ar livre."
    if "limpo" in desc or "ensolarado" in desc:
        return "Use protetor solar e hidrate-se."
    if "tempestade" in desc:
        return "Evite áreas abertas e fique atento a alagamentos."
    return "Consulte sempre as condições antes de sair."

import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd

# --- FASE EXTRA: PREVISÃO DE 5 DIAS ---
@st.cache_data(ttl=600)
def buscar_previsao_5dias(cidade, api_key):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={cidade}&appid={api_key}&units=metric&lang=pt_br"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 404:
            return {"erro": "Cidade não encontrada para previsão de 5 dias."}
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return {"erro": "Erro de conexão na previsão de 5 dias."}

# --- FASE 1: CONFIGURAÇÃO DA UI E ESTILO (Modern Dark) ---
st.set_page_config(page_title="Dashboard Meteorológico", page_icon="🌤️", layout="wide")

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
        max-width: 500px;
        margin-left: auto;
        margin-right: auto;
        box-sizing: border-box;
    }
    h1, h2, h3 { color: #222222; font-family: 'Inter', sans-serif; }
    @media (max-width: 900px) {
        .weather-card { padding: 15px; max-width: 98vw; }
        .stMetric { padding: 10px; font-size: 0.95em; }
    }
    @media (max-width: 600px) {
        .weather-card { padding: 8px; max-width: 100vw; }
        .stMetric { padding: 6px; font-size: 0.85em; }
    }
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
    # Ícones distintos para cada nível de risco de vento
    if vento < 10:
        return "💨", "Baixo risco para pessoas"  # vento leve
    elif vento < 20:
        return "🌬️", "Atenção: vento moderado"  # vento moderado
    else:
        return "🌪️", "Perigo: vento forte"  # vento forte

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
            pressao_hpa = dados['main']['pressure']
            pressao_mmhg = pressao_hpa * 0.750062
            desc = dados['weather'][0]['description'].capitalize()
            icon_id = dados['weather'][0]['icon']

            # Fase 1.2 e 1.4: Layout do Painel e Ícones Gráficos

            # Layout 4 colunas minimalistas
            # Layout 5 colunas: cidade, temperatura, umidade, vento, pressão
            col1, col2, col3, col4, col5 = st.columns(5)
            with col5:
                st.markdown("""
                <div style='text-align:center; background:#f8fafc; border-radius:12px; padding:12px 6px 10px 6px; box-shadow:0 2px 8px #0001; margin-bottom:8px;'>
                    <div style='font-weight:bold; font-size:1.1em; margin-bottom:2px;'>Pressão Atmosférica</div>
                    <div style='font-size:1.6em; color:#1e293b; font-weight:600;'>{:.0f} <span style='font-size:0.6em; color:#64748b;'>hPa</span></div>
                    <div style='font-size:1.15em; color:#334155; margin-bottom:4px;'>{:.1f} <span style='font-size:0.7em; color:#64748b;'>mmHg</span></div>
                    <div style='font-size:0.90em; color:#666; margin-top:4px;'>
                        <span title='hectopascal'>hPa</span> (<a href='https://pt.wikipedia.org/wiki/Hectopascal' target='_blank' style='color:#2563eb;'>saiba mais</a>)<br>
                        <span title='milímetro de mercúrio'>mmHg</span> (<a href='https://pt.wikipedia.org/wiki/Mil%C3%ADmetro_de_merc%C3%BArio' target='_blank' style='color:#2563eb;'>saiba mais</a>)
                    </div>
                </div>
                """.format(pressao_hpa, pressao_mmhg), unsafe_allow_html=True)

            # --- PREVISÃO DE 5 DIAS ---
            st.markdown("""
                <h3 style='margin-top:32px; margin-bottom:8px; color:#222; text-align:left;'>Previsão para os próximos 5 dias</h3>
            """, unsafe_allow_html=True)
            previsao = buscar_previsao_5dias(cidade, api_key)
            if "erro" in previsao:
                st.warning(previsao["erro"])
            else:
                lista = previsao["list"]
                dados_5dias = []
                for item in lista:
                    dt_txt = item["dt_txt"]
                    temp = item["main"]["temp"]
                    desc = item["weather"][0]["description"].capitalize()
                    icon = item["weather"][0]["icon"]
                    dados_5dias.append({"data": dt_txt, "temp": temp, "desc": desc, "icon": icon})
                df = pd.DataFrame(dados_5dias)
                # Seleciona apenas 1 previsão por dia (meio-dia)
                df["data"] = pd.to_datetime(df["data"])
                df_dia = df[df["data"].dt.hour == 12].copy()
                if df_dia.empty:
                    df_dia = df.iloc[::8].copy()  # fallback: 1 a cada 8 (3h*8=24h)
                dias = df_dia["data"].dt.strftime("%d/%m")
                temps = df_dia["temp"]
                descricoes = df_dia["desc"]
                icones = df_dia["icon"]
                # Gráfico de linha de temperatura
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=dias, y=temps, mode='lines+markers', name='Temp. (°C)', line=dict(color='#2563eb', width=3)))
                fig.update_layout(
                    xaxis_title='Dia',
                    yaxis_title='Temperatura (°C)',
                    template='plotly_white',
                    height=320,
                    margin=dict(l=20, r=20, t=30, b=20),
                    plot_bgcolor='#f8fafc',
                    paper_bgcolor='#f8fafc',
                )
                st.plotly_chart(fig, use_container_width=True)
                # Cards resumidos
                cols = st.columns(len(dias))
                for i, col in enumerate(cols):
                    col.markdown(f"<div style='text-align:center;'><img src='http://openweathermap.org/img/wn/{icones.iloc[i]}@2x.png' width='38'><br><span style='font-size:1.1em; font-weight:600'>{temps.iloc[i]:.1f}°C</span><br><span style='font-size:0.95em; color:#666'>{dias.iloc[i]}</span><br><span style='font-size:0.85em; color:#888'>{descricoes.iloc[i]}</span></div>", unsafe_allow_html=True)

            with col1:
                st.markdown(f"<div style='text-align:center'><h4 style='margin-bottom:2px'>{dados['name']}, {dados['sys']['country']}</h4>"
                            f"<img src='http://openweathermap.org/img/wn/{icon_id}@4x.png' width='48'></div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align:center; color:#9ca3af; font-size:0.95em'>{desc}</div>", unsafe_allow_html=True)
                # Recomendação/alerta para cidade/condição (sempre mostra algo)
                obs1 = desc_alerta(desc)
                if not obs1:
                    obs1 = "Consulte sempre as condições antes de sair."
                st.markdown(f"<div style='text-align:center; font-size:0.95em; color:#666'>{obs1}</div>", unsafe_allow_html=True)

            with col2:
                st.markdown(f"<div style='text-align:center; font-size:2.2em; font-weight:bold'>{temp:.1f}°C</div>", unsafe_allow_html=True)
                sensacao_icon, sensacao_texto = risco_sensacao_icon(feels_like)
                st.markdown(f"<div style='text-align:center; font-size:1.2em'>{sensacao_icon} <span style='font-size:0.95em'>{feels_like:.1f}°C</span></div>", unsafe_allow_html=True)
                # Recomendação/alerta para temperatura/sensação (sempre mostra algo)
                obs2 = sensacao_texto
                if not obs2:
                    obs2 = "Temperatura confortável."
                st.markdown(f"<div style='text-align:center; font-size:0.95em; color:#666'>{obs2}</div>", unsafe_allow_html=True)

            with col3:
                # Barra de progresso moderna para umidade
                st.markdown("<div style='text-align:center; font-weight:bold; font-size:1.1em'>Umidade</div>", unsafe_allow_html=True)
                st.markdown(f'''
                    <div style="width: 100%; background: #e0e7ef; border-radius: 12px; height: 22px; box-shadow: 0 2px 8px #0001; margin-bottom: 6px; position: relative;">
                        <div style="width: {umidade}%; background: linear-gradient(90deg, #00BFFF 0%, #7be495 100%); height: 100%; border-radius: 12px; transition: width 0.6s;"></div>
                        <div style="position: absolute; left: 50%; top: 0; transform: translateX(-50%); height: 100%; display: flex; align-items: center; font-weight: bold; color: #222; font-size: 1em;">{umidade}%</div>
                    </div>
                ''', unsafe_allow_html=True)
                # Recomendação/alerta para umidade (sempre mostra algo)
                obs3 = risco_umidade_texto(umidade)
                if not obs3:
                    obs3 = "Umidade confortável."
                st.markdown(f"<div style='text-align:center; font-size:0.95em; color:#666'>{obs3}</div>", unsafe_allow_html=True)

        with col4:
            vento_icon, vento_texto = risco_vento_icon(vento)
            st.markdown(f"<div style='text-align:center; font-size:2em'>{vento_icon}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center; font-size:1.1em'>{vento} km/h</div>", unsafe_allow_html=True)
            # Recomendação/alerta para vento (sempre mostra algo)
            obs4 = vento_texto
            if not obs4:
                obs4 = "Vento tranquilo."
            st.markdown(f"<div style='text-align:center; font-size:0.95em; color:#666'>{obs4}</div>", unsafe_allow_html=True)

# Fim do bloco if api_key



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