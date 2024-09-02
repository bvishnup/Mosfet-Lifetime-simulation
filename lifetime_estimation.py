import numpy as np
from scipy.constants import k as boltzmann_constant
from typing import Dict, Tuple, List

def rainflow(signal: np.ndarray, min_delta_T: float = 0.1) -> Tuple[np.ndarray, int]:
    """Rainflow counting algorithm for cycle counting."""
    diff = np.diff(signal)
    peaks = np.where((diff[:-1] > 0) & (diff[1:] <= 0))[0] + 1
    valleys = np.where((diff[:-1] < 0) & (diff[1:] >= 0))[0] + 1
    extrema = np.sort(np.concatenate((peaks, valleys, [0, len(signal)-1])))
    
    cycles = []
    stack = []
    for i in range(len(extrema) - 1):
        stack.append(i)
        while len(stack) >= 3:
            i1, i2, i3 = stack[-3:]
            x1, x2, x3 = signal[extrema[i1]], signal[extrema[i2]], signal[extrema[i3]]
            delta_T = abs(x2 - x1)
            if delta_T >= min_delta_T and abs(x3 - x2) <= abs(x2 - x1):
                amplitude = delta_T / 2
                mean = (x1 + x2) / 2
                cycles.append([amplitude, mean, 1])
                stack.pop(-2)
            else:
                break
    
    while len(stack) >= 2:
        i1, i2 = stack[-2:]
        x1, x2 = signal[extrema[i1]], signal[extrema[i2]]
        delta_T = abs(x2 - x1)
        if delta_T >= min_delta_T:
            amplitude = delta_T / 2
            mean = (x1 + x2) / 2
            cycles.append([amplitude, mean, 0.5])
        stack.pop()
    
    return np.array(cycles), len(cycles)

def calculate_cycles_to_failure(delta_T: float, T_mean: float, params: Dict[str, float]) -> float:
    """Calculate cycles to failure based on temperature cycle amplitude and mean temperature."""
    A, n, Ea = params['A'], params['n'], params['Ea']
    kb = boltzmann_constant / 1.60218e-19  # Convert to eV/K
    T_kelvin = T_mean + 273.15
    N_f = A * (delta_T ** -n) * np.exp(Ea / (kb * T_kelvin))
    return max(N_f, 1)

def miners_rule_degradation(cycles: np.ndarray, params: Dict[str, float]) -> Tuple[float, List[Tuple[float, float]]]:
    """Calculate degradation using Miner's rule and return cycles to failure for each temperature cycle."""
    if len(cycles) == 0:
        return 0, []
    
    damage = 0
    cycles_to_failure = []
    for delta_T, T_mean, n in cycles:
        N_f = calculate_cycles_to_failure(delta_T, T_mean, params)
        damage += n / N_f
        cycles_to_failure.append((delta_T, N_f))
    
    return max(damage, 1e-10), cycles_to_failure  # Ensure some minimal degradation

def estimate_lifetime_years(degradation: float, cycles_per_year: int = 100000) -> float:
    """Estimate lifetime in years based on degradation."""
    if degradation <= 0:
        return float('inf')  # Return infinity for zero degradation
    return min((1 / degradation) / cycles_per_year, 100)  # Cap at 100 years for realism

def estimate_lifetime(t_j: np.ndarray, lifetime_params: Dict[str, float]) -> Tuple[float, float, int, List[Tuple[float, float]]]:
    """Estimate MOSFET lifetime based on junction temperature profile."""
    temp_cycles, total_cycles = rainflow(t_j, min_delta_T=0.1)
    degradation, cycles_to_failure = miners_rule_degradation(temp_cycles, lifetime_params)
    estimated_years = estimate_lifetime_years(degradation)
    return degradation, estimated_years, total_cycles, cycles_to_failure