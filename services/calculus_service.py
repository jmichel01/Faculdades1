import sympy as sp
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger("optilogix.service.calculus")

class CalculusService:
    """
    Applies continuous calculus and symbolic mathematics using SymPy.
    Resolves analytical economic order sizes and warehousing congestion scaling.
    """
    def __init__(self) -> None:
        # Define symbols globally
        self.Q, self.D, self.S, self.H, self.alpha = sp.symbols("Q D S H alpha", positive=True)

    def get_symbolic_cost_function(self) -> Tuple[sp.Expr, sp.Expr]:
        """
        Formulates the symbolic inventory cost model and its first derivative.
        C(Q) = (D * S)/Q + (Q * H)/2 + alpha * Q^2
        """
        # Continuous holding, setup, and nonlinear congestion cost function
        cost_expr = (self.D * self.S) / self.Q + (self.Q * self.H) / 2 + self.alpha * (self.Q ** 2)
        
        # Take the derivative with respect to Q
        derivative_expr = sp.diff(cost_expr, self.Q)
        
        return cost_expr, derivative_expr

    def solve_optimal_order_quantity(self, demand: float, setup_cost: float, holding_cost: float, congestion_coef: float) -> Dict[str, Any]:
        """
        Analytically resolves the optimal ordering size Q* by plugging in concrete values.
        Utilizes SymPy solvers to guarantee algebraic correctness.
        """
        cost_expr, derivative_expr = self.get_symbolic_cost_function()
        
        # Substitute concrete values into the derivative expression
        subbed_derivative = derivative_expr.subs({
            self.D: demand,
            self.S: setup_cost,
            self.H: holding_cost,
            self.alpha: congestion_coef
        })
        
        # Solve subbed_derivative = 0 for positive real Q
        solutions = sp.solve(subbed_derivative, self.Q)
        
        # Filter positive real solutions
        real_solutions = [float(sol.evalf()) for sol in solutions if sol.is_real and sol > 0]
        
        if not real_solutions:
            # Fallback to standard EOQ if solver struggles with congestion
            logger.warning("SymPy could not resolve real positive solution. Falling back to classical EOQ.")
            eoq_fallback = float(sp.sqrt((2 * demand * setup_cost) / holding_cost).evalf())
            real_solutions = [eoq_fallback]
            
        optimal_Q = real_solutions[0]
        
        # Calculate minimum cost at optimal Q
        subbed_cost = cost_expr.subs({
            self.Q: optimal_Q,
            self.D: demand,
            self.S: setup_cost,
            self.H: holding_cost,
            self.alpha: congestion_coef
        })
        min_cost = float(subbed_cost.evalf())
        
        # LaTeX rendering for Streamlit math display
        latex_cost = sp.latex(cost_expr)
        latex_derivative = sp.latex(derivative_expr)
        
        return {
            "optimal_q": round(optimal_Q, 2),
            "min_cost": round(min_cost, 2),
            "latex_cost_function": latex_cost,
            "latex_derivative": latex_derivative,
            "formula_unicode": sp.pretty(cost_expr, use_unicode=True),
            "derivative_unicode": sp.pretty(derivative_expr, use_unicode=True)
        }
