import itertools
import logging
from typing import List, Dict, Any, Tuple
from routing.engine import RoutingEngine

logger = logging.getLogger("smart_routing.optimization.tsp_solver")

class TspSolver:
    
    @classmethod
    def optimize_route(
        cls,
        start_point: Dict[str, float],
        destinations: List[Dict[str, float]],
        G: Any = None,
        return_to_start: bool = True
    ) -> Tuple[List[int], float, List[Dict[str, Any]]]:
        num_dests = len(destinations)
        if num_dests == 0:
            return [], 0.0, []
            
        all_points = [start_point] + destinations
        num_points = len(all_points)
        
        matrix = [[0.0 for _ in range(num_points)] for _ in range(num_points)]
        paths_cache = {}
        
        for i in range(num_points):
            for j in range(num_points):
                if i == j:
                    matrix[i][j] = 0.0
                    continue
                pt_A = all_points[i]
                pt_B = all_points[j]
                coords, dist = RoutingEngine.calculate_route(pt_A["lat"], pt_A["lng"], pt_B["lat"], pt_B["lng"], G)
                matrix[i][j] = dist
                paths_cache[(i, j)] = (coords, dist)

        dest_indices = list(range(1, num_points))
        best_perm = None
        min_total_dist = float("inf")
        
        for perm in itertools.permutations(dest_indices):
            current_dist = matrix[0][perm[0]]
            
            for k in range(len(perm) - 1):
                current_dist += matrix[perm[k]][perm[k+1]]
                
            if return_to_start:
                current_dist += matrix[perm[-1]][0]
                
            if current_dist < min_total_dist:
                min_total_dist = current_dist
                best_perm = perm

        leg_details = []
        optimal_perm = list(best_perm)
        optimized_order = [idx - 1 for idx in optimal_perm]
        
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
#A
