import logging
import math
import networkx as nx
import osmnx as ox
from typing import Dict, Any, List, Tuple, Optional
from geopy.distance import geodesic
import streamlit as st

# Silence OSMnx logs to keep console clean
import logging
logging.getLogger('OSMnx').setLevel(logging.ERROR)

logger = logging.getLogger("smart_routing.routing.engine")

class RoutingEngine:
    """
    Handles geographical calculations and street network routing.
    Integrates OpenStreetMap (OSMnx/NetworkX) with a smart grid fallback engine.
    """
    
    @staticmethod
    @st.cache_resource(show_spinner="Downloading street network from OpenStreetMap...")
    def get_street_network(min_lat: float, max_lat: float, min_lng: float, max_lng: float) -> Optional[nx.MultiDiGraph]:
        """
        Downloads and caches the street network graph for the given bounding box.
        Returns None if offline or if download fails.
        """
        # Quick internet access check to fail fast offline
        import socket
        try:
            # 1-second timeout on the socket instance (avoids modifying global defaults)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            s.connect(("overpass-api.de", 80))
            s.close()
        except Exception:
            logger.warning("System offline or Overpass API unreachable. Bypassing to city-grid fallback.")
            return None

        # Safeguard: Bypassing huge bounding boxes (e.g., mixing Seattle and São Paulo coordinates)
        if (max_lat - min_lat) > 0.25 or (max_lng - min_lng) > 0.25:
            logger.warning("Bounding box too large for OSMnx download. Bypassing to city-grid fallback.")
            return None

        try:
            logger.info(f"Downloading street network for bbox: lat=[{min_lat}, {max_lat}], lng=[{min_lng}, {max_lng}]")
            # Download drive network type for routing
            ox.settings.timeout = 5
            ox.settings.use_cache = True
            G = ox.graph_from_bbox(
                bbox=(min_lng, min_lat, max_lng, max_lat),
                network_type="drive",
                retain_all=True
            )
            logger.info("Successfully loaded network graph from OpenStreetMap.")
            return G
        except Exception as e:
            logger.warning(f"Failed to fetch street network from OSMnx: {e}. Switching to city-grid fallback mode.")
            return None

    @classmethod
    def calculate_route(cls, lat_A: float, lng_A: float, lat_B: float, lng_B: float, G: Optional[nx.MultiDiGraph] = None) -> Tuple[List[Tuple[float, float]], float]:
        """
        Calculates the route path (list of coordinates) and total distance (km) between A and B.
        If G is provided, uses NetworkX Dijkstra pathfinding on real roads.
        Otherwise, falls back to a smart city-grid path generator.
        """
        # Try OSMnx routing first
        if G is not None:
            try:
                # Find nearest graph nodes to starting and ending coordinates
                node_A = ox.nearest_nodes(G, X=lng_A, Y=lat_A)
                node_B = ox.nearest_nodes(G, X=lng_B, Y=lat_B)
                
                # Dijkstra shortest path based on length
                path_nodes = nx.shortest_path(G, node_A, node_B, weight="length")
                
                # Extract coordinates from path nodes
                route_coords = []
                for node in path_nodes:
                    node_data = G.nodes[node]
                    route_coords.append((node_data['y'], node_data['x']))
                
                # Calculate total geodesic distance along the route path
                total_dist = 0.0
                for i in range(len(route_coords) - 1):
                    total_dist += geodesic(route_coords[i], route_coords[i+1]).kilometers
                
                logger.info(f"OSMnx Route solved: {len(route_coords)} points, distance = {total_dist:.2f} km")
                return route_coords, total_dist
            except Exception as e:
                logger.debug(f"OSMnx pathfinding error: {e}. Falling back to city-grid.")

        # Fallback: Smart City-Grid staircase routing
        return cls.generate_grid_path(lat_A, lng_A, lat_B, lng_B)

    @staticmethod
    def generate_grid_path(lat_A: float, lng_A: float, lat_B: float, lng_B: float, num_blocks: int = 5) -> Tuple[List[Tuple[float, float]], float]:
        """
        Smart City-Grid Fallback Engine.
        Simulates realistic street-grid staircase route paths (Manhattan-style).
        """
        points = []
        lat_step = (lat_B - lat_A) / num_blocks
        lng_step = (lng_B - lng_A) / num_blocks
        
        curr_lat, curr_lng = lat_A, lng_A
        points.append((curr_lat, curr_lng))
        
        for i in range(num_blocks):
            # Alternating movement to look like a city grid
            # Add small random street perturbations (0.00005 deg) for realistic organic shape
            perturbation = 0.00002
            
            # Step 1: Move in latitude direction
            curr_lat += lat_step
            points.append((curr_lat + (perturbation if i%2==0 else -perturbation), curr_lng))
            
            # Step 2: Move in longitude direction
            curr_lng += lng_step
            points.append((curr_lat, curr_lng + (perturbation if i%2!=0 else -perturbation)))
            
        # Ensure exact end point matches B
        points.append((lat_B, lng_B))
        
        # Calculate grid distance
        total_dist = 0.0
        for i in range(len(points) - 1):
            total_dist += geodesic(points[i], points[i+1]).kilometers
            
        logger.debug(f"City-Grid Fallback Route generated: {len(points)} nodes, distance = {total_dist:.2f} km")
        return points, total_dist

    @staticmethod
    def calculate_direct_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Geodesic (great-circle) direct distance helper.
        """
        return geodesic((lat1, lon1), (lat2, lon2)).kilometers
