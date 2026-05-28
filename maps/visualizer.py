import folium
import logging
from typing import Dict, Any, List, Tuple
from config.settings import Settings

logger = logging.getLogger("smart_routing.maps.visualizer")

class MapVisualizer:
    """
    Renders beautiful dark-mode Leaflet maps using Folium.
    Handles marker plotting, route paths rendering, and legends.
    """
    
    # Theme line colors per vehicle (Black, White, Gray, and Blue)
    VEHICLE_COLORS = {
        "Carro": "#2563eb",         # Premium Blue
        "Motocicleta": "#a3a3a3",  # Neutral Gray
        "Bicicleta": "#ffffff"      # Pure White
    }
    
    @classmethod
    def create_base_map(cls, center_lat: float, center_lng: float, zoom: int = 13) -> folium.Map:
        """
        Initializes a beautiful CartoDB Dark Matter map.
        """
        fig_map = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=zoom,
            tiles="CartoDB dark_matter",
            control_scale=True
        )
        return fig_map

    @classmethod
    def plot_markers(cls, fig_map: folium.Map, locations: List[Dict[str, Any]], optimal_order: List[int] = None) -> None:
        """
        Plots markers for Start and Delivery locations.
        Lables delivery points with their visit sequence number (e.g. 1st, 2nd, 3rd) if solved.
        """
        if not locations:
            return
            
        # Plot Start location
        start_loc = locations[0]
        folium.Marker(
            location=[start_loc["lat"], start_loc["lng"]],
            popup="<b>Ponto de Partida</b>",
            tooltip="Origem",
            icon=folium.Icon(color="green", icon="play", prefix="fa")
        ).add_to(fig_map)
        
        # Plot Delivery points
        delivery_locs = locations[1:]
        
        # Create mapping of destination index to visit order number (1-based index)
        visit_order_map = {}
        if optimal_order is not None and len(optimal_order) == len(delivery_locs):
            for visit_seq, dest_idx in enumerate(optimal_order, 1):
                visit_order_map[dest_idx] = visit_seq

        for idx, loc in enumerate(delivery_locs):
            # Check if optimal order is calculated
            if idx in visit_order_map:
                order_num = visit_order_map[idx]
                label = f"<b>Ponto de Entrega {idx+1}</b><br/>Sequência de Visita: <b>#{order_num}</b>"
                icon_color = "red"
                icon_char = str(order_num)
            else:
                label = f"<b>Ponto de Entrega {idx+1}</b>"
                icon_color = "cadetblue"
                icon_char = "?"
                
            # Create Custom HTML Marker Icon to display visit order character clearly
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
        """
        Draws colored polyline paths on the map for each selected vehicle's route.
        """
        # Feature group to toggle layers
        for vehicle_name, legs in routes_data.items():
            color = cls.VEHICLE_COLORS.get(vehicle_name, "#ffffff")
            vehicle_group = folium.FeatureGroup(name=f"Rota de {vehicle_name}")
            
            for leg in legs:
                # Add route path coords
                coords = leg["path_coords"]
                folium.PolyLine(
                    locations=coords,
                    color=color,
                    weight=4,
                    opacity=0.85,
                    tooltip=f"{vehicle_name}: {leg['from_node']} -> {leg['to_node']} ({leg['distance_km']:.2f} km)"
                ).add_to(vehicle_group)
                
            vehicle_group.add_to(fig_map)
            
        # Add layer control to toggle vehicles
        if routes_data:
            folium.LayerControl(position="topright").add_to(fig_map)
