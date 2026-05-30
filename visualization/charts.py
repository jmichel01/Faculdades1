import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Dict, Any

class ChartVisualizer:
    
    COLOR_MAP = {
        "Carro": "#2563eb",
        "Motocicleta": "#a3a3a3",
        "Bicicleta": "#ffffff"
    }
    
    @classmethod
    def plot_time_comparison(cls, metrics: List[Dict[str, Any]]) -> go.Figure:
        data = []
        for m in metrics:
            data.append({
                "Modo de Veículo": m["vehicle"],
                "Tempo (Minutos)": round(m["time_hours"] * 60.0, 1),
                "Color": cls.COLOR_MAP.get(m["vehicle"], "#94a3b8")
            })
            
        df = pd.DataFrame(data)
        fig = px.bar(
            df,
            x="Modo de Veículo",
            y="Tempo (Minutos)",
            color="Modo de Veículo",
            color_discrete_map=cls.COLOR_MAP,
            text_auto=True,
            title="Comparativo de Tempo Total"
        )
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            yaxis=dict(title="Minutos", showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
            xaxis=dict(title="", showgrid=False)
        )
        return fig

    @classmethod
    def plot_cost_comparison(cls, metrics: List[Dict[str, Any]]) -> go.Figure:
        data = []
        for m in metrics:
            data.append({
                "Modo de Veículo": m["vehicle"],
                "Custo (R$)": m["fuel_cost_usd"],
                "Color": cls.COLOR_MAP.get(m["vehicle"], "#94a3b8")
            })
            
        df = pd.DataFrame(data)
        fig = px.bar(
            df,
            x="Modo de Veículo",
            y="Custo (R$)",
            color="Modo de Veículo",
            color_discrete_map=cls.COLOR_MAP,
            text_auto="R$0.2f",
            title="Comparativo de Custo de Combustível"
        )
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            yaxis=dict(title="Reais (R$)", showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
            xaxis=dict(title="", showgrid=False)
        )
        return fig

    @classmethod
    def plot_emissions_comparison(cls, metrics: List[Dict[str, Any]]) -> go.Figure:
        data = []
        for m in metrics:
            data.append({
                "Modo de Veículo": m["vehicle"],
                "Pegada de CO2 (g)": m["co2_emissions_g"]
            })
            
        df = pd.DataFrame(data)
        fig = px.bar(
            df,
            x="Modo de Veículo",
            y="Pegada de CO2 (g)",
            color="Modo de Veículo",
            color_discrete_map=cls.COLOR_MAP,
            text_auto=True,
            title="Pegada de Carbono Total (Emissões de CO2)"
        )
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            yaxis=dict(title="Gramas de CO2", showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
            xaxis=dict(title="", showgrid=False)
        )
        return fig

    @classmethod
    def plot_radar_rankings(cls, metrics: List[Dict[str, Any]]) -> go.Figure:
        fig = go.Figure()
        
        for m in metrics:
            vehicle = m["vehicle"]
            eco = m["sustainability_score"]
            cost_val = m["fuel_cost_usd"]
            cost_score = 100 if cost_val == 0.0 else max(10, min(95, 100 - (cost_val * 8)))
            
            time_val = m["time_hours"] * 60.0
            time_score = max(15, min(95, 100 - (time_val * 0.8)))
            
            if vehicle == "Bicicleta":
                resilience = 95
            elif vehicle == "Motocicleta":
                resilience = 75
            else:
                resilience = 30
                
            categories = ['Eficiência de Tempo', 'Economia de Custo', 'Eco-Amigável', 'Resiliência ao Trânsito']
            values = [time_score, cost_score, eco, resilience]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=vehicle,
                line_color=cls.COLOR_MAP.get(vehicle)
            ))
            
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,0.05)"),
                angularaxis=dict(gridcolor="rgba(255,255,255,0.05)")
            ),
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            title="Atributos Operacionais Multidimensionais"
        )
        return fig
#A
