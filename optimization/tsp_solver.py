import itertools
import logging
from typing import List, Dict, Any, Tuple, Optional
from routing.engine import RoutingEngine

logger = logging.getLogger("smart_routing.optimization.tsp_solver")

class TspSolver:
    """
    Solves the Traveling Salesman Problem (TSP) for small delivery routing.
    Evaluates exact permutations to find the optimal sequence of visits.
    """
    
    @classmethod
    def optimize_route(
        cls,
        start_point: Dict[str, float],
        destinations: List[Dict[str, float]],
        G: Any = None,
        return_to_start: bool = True
    ) -> Tuple[List[int], float, List[Dict[str, Any]]]:
        """
        Calculates the mathematically optimal order to visit destinations.
        
        Args:
            start_point: Dict with 'lat' and 'lng'
            destinations: List of 3 Dicts with 'lat' and 'lng'
            G: Optional networkx graph for real road calculations
            return_to_start: Whether to add distance back to starting point
            
        Returns:
            Tuple containing:
            - List of indices in optimized order (e.g. [2, 0, 1])
            - Total distance of the optimal route (km)
            - List of routing leg details (route points and leg distances)
        """
        num_dests = len(destinations)
        if num_dests == 0:
            return [], 0.0, []
            
        # Combine all points: index 0 is Start, indices 1..N are destinations
        all_points = [start_point] + destinations
        num_points = len(all_points)
        
        # 1. Build Distance Matrix using RoutingEngine
        # matrix[i][j] = route distance from all_points[i] to all_points[j]
        matrix = [[0.0 for _ in range(num_points)] for _ in range(num_points)]
        paths_cache = {}  # Cache route coords to avoid recalculation
        
        for i in range(num_points):
            for j in range(num_points):
                if i == j:
                    matrix[i][j] = 0.0
                    continue
                # Calculate path and distance
                pt_A = all_points[i]
                pt_B = all_points[j]
                coords, dist = RoutingEngine.calculate_route(pt_A["lat"], pt_A["lng"], pt_B["lat"], pt_B["lng"], G)
                matrix[i][j] = dist
                paths_cache[(i, j)] = (coords, dist)

        # 2. Evaluate all permutations of visiting indices 1..N
        dest_indices = list(range(1, num_points))
        best_perm = None
        min_total_dist = float("inf")
        
        # Test each permutation sequence (e.g. 0 -> p1 -> p2 -> p3 -> 0)
        for perm in itertools.permutations(dest_indices):
            # Calculate distance of this path
            current_dist = matrix[0][perm[0]]  # Start to first point
            
            # Distance between consecutive points
            for k in range(len(perm) - 1):
                current_dist += matrix[perm[k]][perm[k+1]]
                
            # Optionally add distance back to starting point (closed loop)
            if return_to_start:
                current_dist += matrix[perm[-1]][0]
                
            if current_dist < min_total_dist:
                min_total_dist = current_dist
                best_perm = perm

        # 3. Build leg details for the optimal path
        leg_details = []
        optimal_perm = list(best_perm)
        # Convert optimal perm indices back to 0-indexed destination indices (perm[i] - 1)
        optimized_order = [idx - 1 for idx in optimal_perm]
        
        # Construct path sequences
        sequence = [0] + list(optimal_perm)
        if return_to_start:
            sequence.append(0)
            
        for s in range(len(sequence) - 1):
            from_idx = sequence[s]
            to_idx = sequence[s+1]
            coords, dist = paths_cache[(from_idx, to_idx)]
            
            from_label = "Ponto de Partida" if from_idx == 0 else f"Entrega {from_idx}"
            to_label = "Ponto de Partida" if to_idx == 0 else f"Entrega {to_idx}"
            
            leg_details.append({
                "from_node": from_label,
                "to_node": to_label,
                "distance_km": round(dist, 2),
                "path_coords": coords
            })

        logger.info(f"TSP Optimization resolved: order={optimized_order}, total_dist={min_total_dist:.2f} km")
        return optimized_order, min_total_dist, leg_details
