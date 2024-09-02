import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d
from typing import Tuple, List, Callable, Dict, Any

MOSFETParams = Dict[str, Any]
InterpolatedFunc = Callable[[np.ndarray], np.ndarray]

def create_interpolation_function(waveform: List[Tuple[float, float]]) -> InterpolatedFunc:
    """Create an interpolation function for a given waveform."""
    t, y = zip(*waveform)
    return interp1d(t, y, kind='linear', bounds_error=False, fill_value='extrapolate')

def interpolate_waveforms(vrt: List[Tuple[float, float]], irt: List[Tuple[float, float]]) -> Tuple[InterpolatedFunc, InterpolatedFunc]:
    """Create interpolation functions for voltage and current waveforms."""
    v_interp = create_interpolation_function(vrt)
    i_interp = create_interpolation_function(irt)
    return v_interp, i_interp

def calculate_power_dissipation(v_ds: float, i_d: float, t_j: float, params: MOSFETParams, f_sw: float) -> Tuple[float, float, float, float]:
    """Calculate power dissipation with enhanced switching loss and capacitive loss."""
    r_ds_on = params['R_DS_ON_25'] * (1 + params['R_DS_ON_TEMP_COEFF'] * (t_j - 25))
    p_cond = i_d**2 * r_ds_on
    
    t_on = params['T_ON_25'] * (1 + params['K_T_SW'] * (t_j - 25))
    t_off = params['T_OFF_25'] * (1 + params['K_T_SW'] * (t_j - 25))
    e_oss = params['E_OSS_25'] * (1 + params['K_E_OSS'] * (t_j - 25))
    q_rr = params['Q_RR_25'] * (1 + params['K_Q_RR'] * (t_j - 25))
    
    e_on = 0.5 * v_ds * i_d * t_on
    e_off = 0.5 * v_ds * i_d * t_off
    e_rr = v_ds * q_rr
    
    p_sw = (e_on + e_off + e_oss + e_rr) * f_sw
    p_cap = 0.5 * params['C_OSS'] * v_ds**2 * f_sw
    
    p_total = p_cond + p_sw + p_cap
    return p_total, p_cond, p_sw, p_cap

def non_linear_thermal_properties(t_j: float, params: MOSFETParams) -> Tuple[List[float], List[float]]:
    """Calculate non-linear thermal resistance and capacitance based on junction temperature."""
    r_th = [r * (1 + 0.005 * (t_j - 25)) for r in params['R_TH']]
    c_th = [c * (1 + 0.002 * (t_j - 25)) for c in params['C_TH']]
    return r_th, c_th

def thermal_model(t: float, y: np.ndarray, params: MOSFETParams, v_ds_func: InterpolatedFunc, i_d_func: InterpolatedFunc, t_amb: float, f_sw: float) -> np.ndarray:
    """Enhanced thermal model with cooling effects."""
    t_j = y[0] + t_amb
    r_th, c_th = non_linear_thermal_properties(t_j, params)
    n = len(r_th)
    
    v_ds = v_ds_func(np.array([t]))[0]
    i_d = i_d_func(np.array([t]))[0]
    p_total, _, _, _ = calculate_power_dissipation(v_ds, i_d, t_j, params, f_sw)
    
    # Cooling effect
    p_cool = params['COOLING_COEFF'] * params['SURFACE_AREA'] * (t_j - t_amb)
    
    dy = np.zeros(n)
    for i in range(n):
        if i == 0:
            dy[i] = (p_total - p_cool - (y[i] - (y[i+1] if i+1 < n else 0)) / r_th[i]) / c_th[i]
        elif i == n-1:
            dy[i] = ((y[i-1] - y[i]) / r_th[i] - (y[i] - t_amb) / r_th[i]) / c_th[i]
        else:
            dy[i] = ((y[i-1] - y[i]) / r_th[i] - (y[i] - y[i+1]) / r_th[i+1]) / c_th[i]
    
    return dy

def run_thermal_simulation(params: MOSFETParams, vrt: List[Tuple[float, float]], irt: List[Tuple[float, float]], t_amb: float, f_sw: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Run thermal simulation for a single MOSFET."""
    # Create time array based on the data points in VRT
    t = np.unique(np.array([point[0] for point in vrt + irt]))
    t.sort()
    
    v_func, i_func = interpolate_waveforms(vrt, irt)
    
    y0 = np.zeros(len(params['R_TH']))
    
    solution = solve_ivp(
        lambda t, y: thermal_model(t, y, params, v_func, i_func, t_amb, f_sw),
        (t[0], t[-1]),
        y0,
        t_eval=t,
        method='Radau',
        rtol=1e-8,
        atol=1e-8,
        max_step=1e-4
    )
    
    t_j = solution.y[0, :] + t_amb
    v_ds = v_func(t)
    i_d = i_func(t)
    
    # Calculate power dissipation components for each time step
    p_total = np.zeros_like(t)
    p_cond = np.zeros_like(t)
    p_sw = np.zeros_like(t)
    p_cap = np.zeros_like(t)
    
    for i in range(len(t)):
        p_total[i], p_cond[i], p_sw[i], p_cap[i] = calculate_power_dissipation(v_ds[i], i_d[i], t_j[i], params, f_sw)
    
    return t, t_j, v_ds, i_d, p_total, p_cond, p_sw, p_cap
