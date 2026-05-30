import networkx as nx
import logging
import math
from typing import List, Dict, Any, Tuple
from repositories.route_repo import RouteRepository
from repositories.inventory_repo import InventoryRepository

logger = logging.getLogger("optilogix.service.network")

class NetworkService:
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        a = (math.sin(delta_phi / 2) ** 2 +
             math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def __init__(self) -> None:
        self.route_repo = RouteRepository()
        self.inventory_repo = InventoryRepository()
        self._graph = nx.DiGraph()

    def build_network_graph(self) -> nx.DiGraph:
        self._graph.clear()
        
        hubs = self.inventory_repo.list_hubs()
        retailers = self.inventory_repo.list_retailers()
        
        for h in hubs:
            self._graph.add_node(h.id, type="hub", name=h.name, pos=(h.longitude, h.latitude), capacity=h.capacity)
            
        for r in retailers:
            self._graph.add_node(r.id, type="retailer", name=r.name, pos=(r.longitude, r.latitude))
            
        routes = self.route_repo.list_routes()
        for route in routes:
            routing_weight = route.distance * route.congestion_factor
            self._graph.add_edge(
                route.origin_id,
                route.destination_id,
                id=route.id,
                distance=route.distance,
                base_cost=route.base_cost,
                congestion_factor=route.congestion_factor,
                weight=routing_weight
            )
            
        logger.debug(f"NetworkX graph built: {len(self._graph.nodes)} nodes, {len(self._graph.edges)} edges.")
        return self._graph

    def get_shortest_path(self, origin: str, destination: str) -> Tuple[List[str], float]:
        if not self._graph.nodes:
            self.build_network_graph()
            
        try:
            path = nx.dijkstra_path(self._graph, origin, destination, weight="weight")
            cost = nx.dijkstra_path_length(self._graph, origin, destination, weight="weight")
            return path, cost
        except (nx.NetworkXNoPath, KeyError) as e:
            logger.error(f"Routing path not found from {origin} to {destination}: {e}")
            raise ValueError(f"No valid shipping route connects {origin} to {destination}.")

    def calculate_network_kpis(self) -> Dict[str, Any]:
        if not self._graph.nodes:
            self.build_network_graph()
            
        density = nx.density(self._graph)
        degree_centrality = nx.degree_centrality(self._graph)
        is_weakly_connected = nx.is_weakly_connected(self._graph)
        
        return {
            "node_count": len(self._graph.nodes),
            "edge_count": len(self._graph.edges),
            "density": round(density, 4),
            "degree_centrality": degree_centrality,
            "is_weakly_connected": is_weakly_connected,
        }
        
    def get_route_details(self) -> List[Dict[str, Any]]:
        if not self._graph.nodes:
            self.build_network_graph()
            
        route_list = []
        for u, v, d in self._graph.edges(data=True):
            route_list.append({
                "origin": u,
                "destination": v,
                "distance": d["distance"],
                "base_cost": d["base_cost"],
                "congestion_factor": d["congestion_factor"],
                "routing_weight": round(d["weight"], 2)
            })
        return route_list
#A
