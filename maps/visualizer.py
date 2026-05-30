import folium
import logging
from typing import Dict, Any, List
from config.settings import Settings

logger = logging.getLogger("smart_routing.maps.visualizer")

class MapVisualizer:
    
    VEHICLE_COLORS = {
        "Carro": "#2563eb",
        "Motocicleta": "#a3a3a3",
        "Bicicleta": "#ffffff"
    }
    
    @classmethod
    def create_base_map(cls, center_lat: float, center_lng: float, zoom: int = 13) -> folium.Map:
        fig_map = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=zoom,
            tiles="CartoDB dark_matter",
            control_scale=True
        )
        return fig_map

    @classmethod
    def plot_markers(cls, fig_map: folium.Map, locations: List[Dict[str, Any]], optimal_order: List[int] = None) -> None:
        if not locations:
            return
            
        start_loc = locations[0]
        folium.Marker(
            location=[start_loc["lat"], start_loc["lng"]],
            popup="<b>Ponto de Partida</b>",
            tooltip="Origem",
            icon=folium.Icon(color="green", icon="play", prefix="fa")
        ).add_to(fig_map)
        
        delivery_locs = locations[1:]
        
        visit_order_map = {}
        if optimal_order is not None and len(optimal_order) == len(delivery_locs):
            for visit_seq, dest_idx in enumerate(optimal_order, 1):
                visit_order_map[dest_idx] = visit_seq

        for idx, loc in enumerate(delivery_locs):
            if idx in visit_order_map:
                order_num = visit_order_map[idx]
                label = f"<b>Ponto de Entrega {idx+1}</b><br/>Sequência de Visita: <b>#{order_num}</b>"
                icon_color = "red"
                icon_char = str(order_num)
            else:
                label = f"<b>Ponto de Entrega {idx+1}</b>"
                icon_color = "cadetblue"
                icon_char = "?"
                
            custom_icon = folium.DivIcon(
                html=f"""
                <div style="
                    background-color: {'#2563eb' if icon_color=='red' else '#525252'};
                    color: #ffffff;
                    border: 2px solid white;
                    border-radius: 50%;
                    width: 24px;
                    height: 24px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    font-weight: bold;
                    font-size: 13px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.4);
                ">{icon_char}</div>
                """,
                icon_anchor=(12, 12)
            )
            
            folium.Marker(
                location=[loc["lat"], loc["lng"]],
                popup=label,
                tooltip=f"Ponto de Entrega {idx+1}",
                icon=custom_icon
            ).add_to(fig_map)

    @classmethod
    def draw_vehicle_routes(cls, fig_map: folium.Map, routes_data: Dict[str, List[Dict[str, Any]]]) -> None:
        for vehicle_name, legs in routes_data.items():
            color = cls.VEHICLE_COLORS.get(vehicle_name, "#ffffff")
            vehicle_group = folium.FeatureGroup(name=f"Rota de {vehicle_name}")
            
            for leg in legs:
                coords = leg["path_coords"]
                folium.PolyLine(
                    locations=coords,
                    color=color,
                    weight=4,
                    opacity=0.85,
                    tooltip=f"{vehicle_name}: {leg['from_node']} -> {leg['to_node']} ({leg['distance_km']:.2f} km)"
                ).add_to(vehicle_group)
                
            vehicle_group.add_to(fig_map)
            
        if routes_data:
            folium.LayerControl(position="topright").add_to(fig_map)
#A
