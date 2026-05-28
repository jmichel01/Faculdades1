import os
import streamlit as st
import pandas as pd
import json
import folium
import random
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from config.settings import Settings
from services.optimizer_service import OptimizerService
from maps.visualizer import MapVisualizer
from visualization.charts import ChartVisualizer
from reports.generator import ReportGenerator
from database.manager import DatabaseManager
from analytics.processor import AnalyticsProcessor
from utils.helpers import GeoHelpers
from streamlit_folium import st_folium

# 1. Page Configuration & Theme
st.set_page_config(
    page_title="OptiLogix Enterprise & Smart Routing SaaS",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom styling from assets/style.css
def load_css():
    css_path = "assets/style.css"
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("Styling stylesheet not found.")

load_css()

# 2. Services Initialization
@st.cache_resource
def get_optimizer_service():
    return OptimizerService()

optimizer_service = get_optimizer_service()

def generate_random_route_points() -> None:
    """
    Generates random coordinates (origin + 3 delivery destinations)
    around the default Lat/Lng location for routing simulations.
    """
    st.session_state.locations = []
    # Origin
    start_lat = Settings.DEFAULT_LAT + random.uniform(-0.005, 0.005)
    start_lng = Settings.DEFAULT_LNG + random.uniform(-0.005, 0.005)
    st.session_state.locations.append({"lat": start_lat, "lng": start_lng})
    # 3 destinations
    for _ in range(3):
        st.session_state.locations.append({
            "lat": Settings.DEFAULT_LAT + random.uniform(-0.012, 0.012),
            "lng": Settings.DEFAULT_LNG + random.uniform(-0.012, 0.012)
        })
    st.session_state.optimization_results = None

# 3. Session State Initialization
if "locations" not in st.session_state:
    st.session_state.locations = []
if "last_click" not in st.session_state:
    st.session_state.last_click = None
if "optimization_results" not in st.session_state:
    st.session_state.optimization_results = None

# --- SIDEBAR CONTROL PANEL ---
st.sidebar.markdown(
    "<h2 style='text-align: center; color: #ffffff; font-weight: 700;'>🗺️ MOBILIDADE</h2>"
    "<p style='text-align: center; font-size: 13px; color: #a3a3a3; margin-top: -10px;'>OTIMIZAÇÃO DE ROTAS INTELIGENTE</p>",
    unsafe_allow_html=True
)
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "PAINEL DE NAVEGAÇÃO",
    [
        "💡 Roteador Interativo",
        "📊 Histórico e Estatísticas",
        "🗄️ Configurações do Sistema"
    ]
)

# Sidebar Configs (Fallback defaults)
traffic_intensity = "Medium"
weather = "Sunny"
fuel_price = 5.50
return_to_start = True
prioritize_eco = True

if menu == "💡 Roteador Interativo":
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Parâmetros de Otimização")
    
    traffic_intensity_pt = st.sidebar.select_slider(
        "Intensidade do Trânsito",
        options=["Baixo", "Médio", "Alto", "Horário de Pico"],
        value="Médio"
    )
    traffic_map = {"Baixo": "Low", "Médio": "Medium", "Alto": "High", "Horário de Pico": "Peak Hour"}
    traffic_intensity = traffic_map[traffic_intensity_pt]
    
    weather_pt = st.sidebar.selectbox(
        "Simulação Climática",
        options=["Ensolarado", "Chuvoso", "Nevando", "Tempestuoso"],
        index=0
    )
    weather_map = {"Ensolarado": "Sunny", "Chuvoso": "Rainy", "Nevando": "Snowy", "Tempestuoso": "Stormy"}
    weather = weather_map[weather_pt]
    
    fuel_price = st.sidebar.number_input(
        "Preço do Combustível (R$/L)",
        min_value=0.50,
        max_value=15.00,
        value=5.50,
        step=0.10
    )
    
    return_to_start = st.sidebar.checkbox(
        "Retornar ao Ponto de Partida (Circuito Fechado)",
        value=True
    )
    
    recommendation_priority = st.sidebar.selectbox(
        "Critério de Recomendação",
        options=["Equilibrado (Tempo, Custo e Eco)", "Realista (Apenas Tempo e Custo)"],
        index=0
    )
    prioritize_eco = (recommendation_priority == "Equilibrado (Tempo, Custo e Eco)")
    
    st.sidebar.markdown("---")
    
    # Columns for sidebar buttons
    col_side1, col_side2 = st.sidebar.columns(2)
    with col_side1:
        if st.button("🎲 Rotas Aleatórias", use_container_width=True):
            generate_random_route_points()
            st.rerun()
            
    with col_side2:
        if st.button("🗑️ Limpar Tudo", use_container_width=True):
            st.session_state.locations = []
            st.session_state.last_click = None
            st.session_state.optimization_results = None
            st.rerun()



# --- LIVE ROUTING ENGINE ---
if menu == "💡 Roteador Interativo":
    st.markdown("<h1 class='grad-header'>💡 Roteador Interativo de Entregas</h1>", unsafe_allow_html=True)
    st.markdown(
        "Defina itinerários de entrega de forma interativa. "
        "Escolha entre clicar no mapa ou digitar os endereços manualmente."
    )
    
    input_method = st.radio(
        "Método de Entrada de Endereços",
        ["Digitar Endereços", "Clicar no Mapa"],
        horizontal=True
    )
    
    loc_count = len(st.session_state.locations)
    
    # 1. Input Logic Selection
    if input_method == "Clicar no Mapa":
        # Instruction Panel for Clicks
        if loc_count == 0:
            st.info("📌 **Ação Necessária**: Clique no mapa para definir o **Ponto de Partida**.")
        elif loc_count < 4:
            st.info(f"📌 **Ação Necessária**: Clique para adicionar o **Ponto de Entrega {loc_count}** (Máx 3).")
        else:
            st.success("✅ **Localizações Definidas**: Pronto para rodar a otimização. Selecione os modos de transporte ao lado!")
            
        # Add random route generator button directly on main map view instructions for convenience
        if st.button("🎲 Gerar Rotas e Pontos Aleatórios no Mapa", type="secondary", use_container_width=True):
            generate_random_route_points()
            st.rerun()
    else:
        # Form for Address Input
        st.info("📝 **Digitar Endereços**: Insira os endereços abaixo. Usaremos geocodificação para determinar as coordenadas.")
        with st.form("address_form"):
            addr_start = st.text_input("Endereço do Ponto de Partida", value="Avenida Paulista, 1000, São Paulo, SP")
            addr_del1 = st.text_input("Endereço do Ponto de Entrega 1", value="MASP, São Paulo, SP")
            addr_del2 = st.text_input("Endereço do Ponto de Entrega 2", value="Rua Augusta, 1500, São Paulo, SP")
            addr_del3 = st.text_input("Endereço do Ponto de Entrega 3", value="Parque do Ibirapuera, São Paulo, SP")
            
            submit_addr = st.form_submit_button("🔍 Buscar Coordenadas (Geocodificar)", type="primary")
            
            if submit_addr:
                with st.spinner("Resolvendo coordenadas a partir dos endereços..."):
                    try:
                        pts = []
                        for label, addr in [("Partida", addr_start), ("Entrega 1", addr_del1), ("Entrega 2", addr_del2), ("Entrega 3", addr_del3)]:
                            if not addr.strip():
                                raise ValueError(f"O endereço de {label} não pode estar vazio.")
                            coords = optimizer_service.geocode_address(addr)
                            pts.append({
                                "lat": coords["lat"],
                                "lng": coords["lng"]
                            })
                        st.session_state.locations = pts
                        st.session_state.optimization_results = None
                        st.success("✅ Coordenadas resolvidas com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro de Geocodificação: {e}")

        # Refresh loc_count after geocoding
        loc_count = len(st.session_state.locations)

    # Grid columns
    col_map, col_details = st.columns([2, 1])

    with col_details:
        st.markdown("### 📍 Registro de Localizações")
        
        # Display registered coordinates
        if loc_count > 0:
            for idx, loc in enumerate(st.session_state.locations):
                label = "Origem / Partida" if idx == 0 else f"Entrega {idx}"
                st.markdown(
                    f"<div style='background: rgba(255,255,255,0.02); padding: 8px; border-radius: 8px; margin-bottom: 5px; border: 1px solid rgba(255,255,255,0.05);'>"
                    f"<span style='color: #ffffff; font-weight: bold;'>{label}:</span><br/>"
                    f"Lat: {loc['lat']:.5f} | Lng: {loc['lng']:.5f}"
                    f"</div>",
                    unsafe_allow_html=True
                )
        else:
            st.write("Nenhuma localização clicada ou geocodificada ainda.")

        # Transport Modes Selector
        st.markdown("### 🚲 Modos de Transporte")
        selected_vehicles = st.multiselect(
            "Selecione os Veículos para Comparar",
            options=["Bicicleta", "Motocicleta", "Carro"],
            default=["Bicicleta", "Motocicleta", "Carro"]
        )

        # Trigger button
        can_optimize = loc_count >= 2 and len(selected_vehicles) > 0
        if st.button("🚀 Calcular Rota Otimizada", type="primary", disabled=not can_optimize):
            with st.spinner("Processando caminhos de ruas e resolvendo TSP..."):
                try:
                    res = optimizer_service.run_routing_optimization(
                        locations=st.session_state.locations,
                        selected_vehicles=selected_vehicles,
                        traffic_intensity=traffic_intensity,
                        weather=weather,
                        fuel_price=fuel_price,
                        return_to_start=return_to_start,
                        prioritize_eco=prioritize_eco
                    )
                    st.session_state.optimization_results = res
                    st.success("Otimização concluída!")
                except Exception as e:
                    st.error(f"Erro de Roteamento: {e}")
                    st.exception(e)

    with col_map:
        # 1. Initialize Map Center
        map_lat = Settings.DEFAULT_LAT
        map_lng = Settings.DEFAULT_LNG
        if loc_count > 0:
            map_lat = st.session_state.locations[0]["lat"]
            map_lng = st.session_state.locations[0]["lng"]
            
        # 2. Build map and draw markers
        fig_map = MapVisualizer.create_base_map(map_lat, map_lng)
        
        # Draw optimal order markers if solved, else normal sequence
        opt_order = None
        if st.session_state.optimization_results:
            opt_order = st.session_state.optimization_results["optimal_order"]
            
        MapVisualizer.plot_markers(fig_map, st.session_state.locations, opt_order)
        
        # 3. Draw routes on the map if solved
        if st.session_state.optimization_results:
            MapVisualizer.draw_vehicle_routes(
                fig_map,
                st.session_state.optimization_results["legs_per_vehicle"]
            )
            
        # 4. Render map and capture clicks only if in click mode
        has_results = st.session_state.optimization_results is not None
        if input_method == "Clicar no Mapa":
            output = st_folium(fig_map, height=500, use_container_width=True, key=f"live_map_click_{loc_count}_{has_results}")
            if output and output.get("last_clicked"):
                click = output["last_clicked"]
                # Prevent duplicate inserts on reruns
                if click != st.session_state.last_click:
                    st.session_state.last_click = click
                    if len(st.session_state.locations) < 4:
                        st.session_state.locations.append(click)
                        st.rerun()
        else:
            st_folium(fig_map, height=500, use_container_width=True, key=f"live_map_show_{loc_count}_{has_results}")

    # --- RESULTS DASHBOARD ---
    if st.session_state.optimization_results:
        st.markdown("---")
        st.markdown("<h2 class='grad-header'>📊 Painel de Resultados e Otimização</h2>", unsafe_allow_html=True)
        
        res = st.session_state.optimization_results
        metrics = res["metrics"]
        
        # AI Recommendation Box
        rec = res["recommendation"]
        st.markdown(
            f"<div class='math-block' style='background: rgba(255, 255, 255, 0.03) !important; border: 1px solid rgba(255, 255, 255, 0.15) !important;'>"
            f"<h3 style='margin-top: 0; color: #ffffff;'>🏆 Veículo Recomendado: {rec['best_vehicle']}</h3>"
            f"<p style='margin-bottom: 0; font-size: 15px;'>{rec['reason']}</p>"
            f"</div>",
            unsafe_allow_html=True
        )

        # KPI Metrics Cards Row
        kpi_cols = st.columns(len(metrics))
        for idx, m in enumerate(metrics):
            with kpi_cols[idx]:
                time_str = GeoHelpers.format_time_hours(m["time_hours"])
                v_name = m["vehicle"]
                
                # Customize content based on vehicle type
                if v_name == "Bicicleta":
                    details_html = (
                        f"Distância: <b>{m['distance_km']:.2f} km</b><br/>"
                        f"Eco-Score: <b style='color: #ffffff;'>{m['sustainability_score']}/100</b><br/>"
                        f"Calorias Queimadas: <b>{m['calories_burned']:.0f} kcal</b><br/>"
                        f"Combustível: <b style='color: #ffffff;'>Zero</b><br/>"
                    )
                elif v_name == "Motocicleta":
                    details_html = (
                        f"Consumo: <b>{m['fuel_liters']:.2f} L</b><br/>"
                        f"Custo Combustível: <b>R$ {m['fuel_cost_usd']:.2f}</b><br/>"
                        f"Eficiência de Tráfego: <b>{m['traffic_efficiency']:.1f}%</b><br/>"
                        f"Velocidade Média: <b>{m['average_speed']:.1f} km/h</b><br/>"
                    )
                else: # Carro
                    details_html = (
                        f"Consumo: <b>{m['fuel_liters']:.2f} L</b><br/>"
                        f"Custo Combustível: <b>R$ {m['fuel_cost_usd']:.2f}</b><br/>"
                        f"Estimativa de CO2: <b>{m['co2_emissions_g']:.1f} g</b><br/>"
                        f"Impacto do Trânsito: <b>{m['traffic_impact']:.1f}%</b><br/>"
                        f"Pontuação de Conforto: <b>{m['comfort_score']:.0f}/100</b><br/>"
                    )
                
                st.markdown(
                    f"<div class='kpi-card'>"
                    f"<div class='kpi-title'>Métricas - {v_name}</div>"
                    f"<div class='kpi-value'>{time_str}</div>"
                    f"<p style='margin: 5px 0 0 0; font-size: 13px; color: #94a3b8; line-height: 1.45;'>"
                    f"{details_html}"
                    f"Pontuação de Eficiência: <b style='color: #ffffff;'>{m['overall_ranking_score']:.0f}/100</b>"
                    f"</p>"
                    f"</div>",
                    unsafe_allow_html=True
                )

        # Charts Section
        st.markdown("### 📈 Gráficos Comparativos de Desempenho")
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            fig_time = ChartVisualizer.plot_time_comparison(metrics)
            st.plotly_chart(fig_time, use_container_width=True)
            
            fig_co2 = ChartVisualizer.plot_emissions_comparison(metrics)
            st.plotly_chart(fig_co2, use_container_width=True)
            
        with chart_col2:
            fig_cost = ChartVisualizer.plot_cost_comparison(metrics)
            st.plotly_chart(fig_cost, use_container_width=True)
            
            fig_radar = ChartVisualizer.plot_radar_rankings(metrics)
            st.plotly_chart(fig_radar, use_container_width=True)

        # Report Downloads Section
        st.markdown("### 📄 Exportar Relatórios de Operação")
        exp_col1, exp_col2, exp_col3 = st.columns(3)
        
        with exp_col1:
            pdf_buf = ReportGenerator.generate_pdf_report(
                locations=st.session_state.locations,
                traffic=traffic_intensity,
                weather=weather,
                metrics=metrics,
                optimal_order=res["optimal_order"],
                recommendation=res["recommendation"]
            )
            st.download_button(
                label="📄 Baixar Relatório Executivo em PDF",
                data=pdf_buf,
                file_name=f"Relatorio_Rota_Otimizada_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                type="primary"
            )
            st.write("Gera um PDF formal (ReportLab) contendo o itinerário, tabelas de trechos e pareceres analíticos.")
            
        with exp_col2:
            xls_buf = ReportGenerator.generate_excel_report(
                locations=st.session_state.locations,
                traffic=traffic_intensity,
                weather=weather,
                metrics=metrics,
                legs_data=res["legs_per_vehicle"]
            )
            st.download_button(
                label="📊 Baixar Planilha Excel Formatada",
                data=xls_buf,
                file_name=f"Planilha_Metricas_Rotas_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.write("Gera uma planilha Excel multi-abas estruturada (openpyxl) com formatação financeira e de unidades.")
            
        with exp_col3:
            # JSON Route exporter
            route_json = json.dumps({
                "timestamp": datetime.now().isoformat(),
                "locations": st.session_state.locations,
                "traffic_intensity": traffic_intensity,
                "weather": weather,
                "optimal_order": res["optimal_order"],
                "metrics": metrics
            }, indent=2)
            st.download_button(
                label="⚙️ Exportar Dados Brutos em JSON",
                data=route_json,
                file_name=f"dados_rota_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
            st.write("Exporta o formato JSON estruturado com coordenadas e sequência de entrega para sistemas GIS externos.")


# --- HISTORICAL ANALYTICS ---
elif menu == "📊 Histórico e Estatísticas":
    st.markdown("<h1 class='grad-header'>📊 Histórico e Estatísticas de Mobilidade</h1>", unsafe_allow_html=True)
    st.markdown("Acompanhe o histórico de otimizações de rotas resolvidas pelo sistema, rankings de veículos e impactos do trânsito.")
    
    runs = DatabaseManager.get_historical_runs()
    
    if runs:
        # Process metrics using processor
        summary = AnalyticsProcessor.get_summary_stats(runs)
        inflation = AnalyticsProcessor.get_peak_hour_comparison(runs)
        rankings = AnalyticsProcessor.get_vehicle_performance_rankings(runs)
        
        # Summary Row
        s_col1, s_col2, s_col3 = st.columns(3)
        with s_col1:
            st.metric("Total de Rotas Calculadas", summary["total_runs"])
        with s_col2:
            st.metric("Distância Média da Rota", f"{summary['avg_distance']:.2f} km")
        with s_col3:
            st.metric("Impacto do Trânsito em Horário de Pico", f"+{inflation['time_inflation_pct']}%", help="Percentual de aumento do tempo do Carro comparado ao trânsito baixo.")
            
        # Comparison Table
        st.markdown("### Ranking de Desempenho Médio por Veículo")
        df_rank = pd.DataFrame(rankings)
        df_rank.rename(columns={
            "vehicle": "Modo de Veículo",
            "avg_time_mins": "Duração Média (Minutos)",
            "avg_cost_usd": "Custo Médio (R$)",
            "avg_co2_g": "Emissões de CO2 Médias (g)",
            "sustainability_score": "Pontuação Ecológica (100)"
        }, inplace=True)
        st.table(df_rank)
        
        # History table log
        st.markdown("### Log de Execuções Recentes")
        runs_display = []
        traffic_pt_map = {"Low": "Baixo", "Medium": "Médio", "High": "Alto", "Peak Hour": "Horário de Pico"}
        weather_pt_map = {"Sunny": "Ensolarado", "Rainy": "Chuvoso", "Snowy": "Nevando", "Stormy": "Tempestuoso"}
        for r in runs:
            runs_display.append({
                "ID": r["id"],
                "Data/Hora": r["timestamp"],
                "Coordenada Inicial": f"{r['start_lat']:.4f}, {r['start_lng']:.4f}",
                "Entregas": r["dest_count"],
                "Trânsito": traffic_pt_map.get(r["traffic_intensity"], r["traffic_intensity"]),
                "Clima": weather_pt_map.get(r["weather"], r["weather"])
            })
        st.dataframe(pd.DataFrame(runs_display), use_container_width=True)
    else:
        st.info("Nenhum histórico de roteamento encontrado no banco de dados. Execute uma rota primeiro!")


# --- SYSTEM MANAGEMENT ---
elif menu == "🗄️ Configurações do Sistema":
    st.markdown("<h1 class='grad-header'>🗄️ Configurações do Sistema</h1>", unsafe_allow_html=True)
    st.markdown("Gerenciamento de cache de mapas locais e registros de execuções salvas.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Cache e Recursos de Memória")
        st.write("O Streamlit e o OSMnx armazenam mapas e grafos locais de ruas para agilizar as pesquisas futuras.")
        if st.button("🧹 Limpar Caches do Sistema", type="primary"):
            st.cache_resource.clear()
            st.success("Caches e recursos de memória limpos com sucesso!")
            
    with col2:
        st.markdown("### Limpeza do Histórico de Otimização")
        st.write("Apagar permanentemente todos os registros e estatísticas salvos no banco de dados local.")
        if st.button("🗑️ Limpar Histórico de Rotas", type="secondary"):
            DatabaseManager.clear_history()
            st.success("Histórico do banco de dados apagado com sucesso!")
