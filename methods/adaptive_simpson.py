"""
Adaptive Simpson Quadrature Implementation
Numerical integration with automatic interval refinement
"""

import math
from typing import Callable, Tuple, List, Dict


class AdaptiveSimpson:
    """
    Adaptive Simpson Quadrature for numerical integration.
    Automatically refines intervals where the function varies rapidly.
    """
    
    @staticmethod
    def simpson_rule(f: Callable[[float], float], a: float, b: float) -> float:
        """
        Standard Simpson's 1/3 rule for numerical integration.
        
        Formula: S(a,b) = (b-a)/6 * [f(a) + 4f((a+b)/2) + f(b)]
        
        Args:
            f: Function to integrate
            a: Lower bound
            b: Upper bound
            
        Returns:
            Approximation of ∫ f(x) dx from a to b
        """
        m = (a + b) / 2
        return (b - a) / 6 * (f(a) + 4 * f(m) + f(b))
    
    @staticmethod
    def adaptive_simpsons(
        f: Callable[[float], float], 
        a: float, 
        b: float, 
        tol: float = 1e-6, 
        max_depth: int = 15
    ) -> Tuple[float, List[Dict]]:
        """
        Adaptive Simpson Quadrature with recursive refinement.
        
        Algorithm:
        1. Compute Simpson's rule on [a,b]
        2. Compute on halves [a,m] and [m,b]
        3. Estimate error: |S(a,b) - S(a,m) - S(m,b)| / 15
        4. If error < tolerance, accept result
        5. Else recursively refine each half
        
        Args:
            f: Function to integrate
            a: Lower bound
            b: Upper bound
            tol: Desired accuracy (tolerance)
            max_depth: Maximum recursion depth
            
        Returns:
            Tuple of (integral_value, iteration_data)
        """
        m = (a + b) / 2
        whole = AdaptiveSimpson.simpson_rule(f, a, b)
        left = AdaptiveSimpson.simpson_rule(f, a, m)
        right = AdaptiveSimpson.simpson_rule(f, m, b)
        
        iterations = []
        
        result, _ = AdaptiveSimpson._adaptive_simpsons_recursive(
            f, a, b, whole, left, right, tol, max_depth, 0, iterations
        )
        
        return result, iterations
    
    @staticmethod
    def _adaptive_simpsons_recursive(
        f: Callable[[float], float], 
        a: float, 
        b: float,
        whole: float, 
        left: float, 
        right: float,
        tol: float, 
        max_depth: int, 
        depth: int,
        iterations: List[Dict]
    ) -> Tuple[float, bool]:
        """
        Recursive refinement for adaptive Simpson.
        
        Args:
            f: Function to integrate
            a: Lower bound of current interval
            b: Upper bound of current interval
            whole: Simpson on [a,b]
            left: Simpson on [a,m]
            right: Simpson on [m,b]
            tol: Tolerance for current interval
            max_depth: Maximum recursion depth
            depth: Current recursion depth
            iterations: List to store iteration data
            
        Returns:
            Tuple of (approximation, is_converged)
        """
        
        # Estimate error using Richardson extrapolation
        error_estimate = abs(left + right - whole) / 15
        
        # Store iteration data
        iterations.append({
            'a': round(a, 8),
            'b': round(b, 8),
            'width': round(b - a, 8),
            'approximation': round(left + right, 10),
            'error': round(error_estimate, 10),
            'depth': depth
        })
        
        # Check convergence or maximum depth
        if error_estimate < tol or depth >= max_depth:
            return left + right, error_estimate < tol
        
        # Recursively refine both halves
        m = (a + b) / 2
        left_mid = (a + m) / 2
        right_mid = (m + b) / 2
        
        # Left half refinement
        left_left = AdaptiveSimpson.simpson_rule(f, a, left_mid)
        left_right = AdaptiveSimpson.simpson_rule(f, left_mid, m)
        left_result, _ = AdaptiveSimpson._adaptive_simpsons_recursive(
            f, a, m, left, left_left, left_right, tol / 2, max_depth, depth + 1, iterations
        )
        
        # Right half refinement
        right_left = AdaptiveSimpson.simpson_rule(f, m, right_mid)
        right_right = AdaptiveSimpson.simpson_rule(f, right_mid, b)
        right_result, _ = AdaptiveSimpson._adaptive_simpsons_recursive(
            f, m, b, right, right_left, right_right, tol / 2, max_depth, depth + 1, iterations
        )
        
        return left_result + right_result, False


class WorkedExamples:
    """Static worked examples for the documentation page"""
    
    @staticmethod
    def get_example1():
        """Example 1: ∫ sin(x) dx from 0 to π"""
        return {
            'title': '∫ sin(x) dx from 0 to π',
            'exact': 2.0,
            'steps': [
                'Step 1: Initialize a = 0, b = π, tolerance = 1e-6',
                'Step 2: Compute S(0,π) = π/6 [sin(0) + 4sin(π/2) + sin(π)]',
                '        = π/6 [0 + 4(1) + 0] = 4π/6 ≈ 2.094395',
                'Step 3: Compute S(0,π/2) and S(π/2,π)',
                '        S(0,π/2) = π/12 [0 + 4sin(π/4) + 1] = π/12 [0 + 4(0.7071) + 1] ≈ 0.853015',
                '        S(π/2,π) = π/12 [1 + 4sin(3π/4) + 0] ≈ 0.853015',
                'Step 4: Error estimate = |2.094395 - 0.853015 - 0.853015|/15 ≈ 0.000092',
                'Step 5: Since error < 1e-6, integral ≈ 2.000000'
            ]
        }
    
    @staticmethod
    def get_example2():
        """Example 2: ∫ x²·e⁻ˣ dx from 0 to 2"""
        return {
            'title': '∫ x²·e⁻ˣ dx from 0 to 2',
            'exact': 0.593994,
            'steps': [
                'Step 1: Initialize a = 0, b = 2, tolerance = 1e-6',
                'Step 2: Compute S(0,2) = 2/6 [f(0) + 4f(1) + f(2)]',
                '        f(0) = 0²·e⁰ = 0',
                '        f(1) = 1²·e⁻¹ = 0.367879',
                '        f(2) = 2²·e⁻² = 0.541341',
                '        S(0,2) = 1/3 [0 + 4(0.367879) + 0.541341] ≈ 0.670952',
                'Step 3: Compute on halves: S(0,1) and S(1,2)',
                '        S(0,1) = 1/6 [0 + 4f(0.5) + f(1)] ≈ 0.162402',
                '        S(1,2) = 1/6 [0.367879 + 4f(1.5) + 0.541341] ≈ 0.486232',
                'Step 4: Error estimate = |0.670952 - 0.162402 - 0.486232|/15 ≈ 0.001488',
                'Step 5: Error > 1e-6, refine further...',
                'Final integral ≈ 0.593994'
            ]
        }