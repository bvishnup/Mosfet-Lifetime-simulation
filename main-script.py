import logging
import os
from typing import Dict, Any, List, Tuple
import matplotlib.pyplot as plt
import numpy as np
from mosfet_params import MOSFET_PARAMS, VRT, IRT
from thermal_simulation import run_thermal_simulation
from lifetime_estimation import estimate_lifetime
import json

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
T_AMB: float = 50.0  # Ambient temperature in °C
T_MAX: float = 15.0  # Simulation time in seconds (adjust if needed)
F_SW: float = 10.0   # Switching frequency in Hz

# Get the directory of the current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'output')

SimulationResult = Dict[str, Any]

def run_simulation() -> Dict[str, SimulationResult]:
    """Run simulation for all MOSFETs."""
    results = {}
    
    for mosfet_name, params in MOSFET_PARAMS.items():
        logger.info(f"Simulating {mosfet_name}")
        try:
            t, t_j, v_ds, i_d, p_total, p_cond, p_sw, p_cap = run_thermal_simulation(params, VRT, IRT, T_AMB, F_SW)
            degradation, estimated_years, total_cycles, cycles_to_failure = estimate_lifetime(t_j, params['LIFETIME_PARAMS'])
            
            results[mosfet_name] = {
                't': t,
                't_j': t_j,
                'v_ds': v_ds,
                'i_d': i_d,
                'p_total': p_total,
                'p_cond': p_cond,
                'p_sw': p_sw,
                'p_cap': p_cap,
                'degradation': degradation,
                'estimated_years': estimated_years,
                'total_cycles': total_cycles,
                'cycles_to_failure': cycles_to_failure
            }
            logger.info(f"Simulation for {mosfet_name} completed successfully")
        except Exception as e:
            logger.exception(f"Error simulating {mosfet_name}: {str(e)}")
    
    return results

def plot_results(results: Dict[str, SimulationResult]) -> None:
    """Plot simulation results."""
    try:
        fig, axes = plt.subplots(3, 1, figsize=(12, 15))
        
        plot_data = [
            ('Junction Temperature', 't_j', '°C'),
            ('Drain-Source Voltage', 'v_ds', 'V'),
            ('Drain Current', 'i_d', 'A')
        ]
        
        for (title, key, unit), ax in zip(plot_data, axes):
            for mosfet_name, data in results.items():
                ax.plot(data['t'], data[key], label=mosfet_name)
            ax.set_title(f'MOSFET {title} Comparison')
            ax.set_xlabel('Time (s)')
            ax.set_ylabel(f'{title} ({unit})')
            ax.legend()
            ax.grid(True)

        plt.tight_layout()
        
        # Ensure the output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        file_path = os.path.join(OUTPUT_DIR, 'simulation_results.png')
        plt.savefig(file_path)
        logger.info(f"Simulation results plot saved as {file_path}")
        plt.close()
    except Exception as e:
        logger.exception(f"Error plotting results: {str(e)}")

def print_results(results: Dict[str, SimulationResult]) -> None:
    """Print detailed simulation results."""
    for mosfet_name, data in results.items():
        print(f"\n{'='*50}")
        print(f"Results for {mosfet_name}:")
        print(f"{'='*50}")
        print(f"Initial junction temperature: {data['t_j'][0]:.2f}°C")
        print(f"Final junction temperature: {data['t_j'][-1]:.2f}°C")
        print(f"Peak junction temperature: {np.max(data['t_j']):.2f}°C")
        print(f"Estimated lifetime: {data['estimated_years']:.2f} years")
        print(f"Degradation: {data['degradation']:.6f}")
        print(f"Total thermal cycles: {data['total_cycles']}")
        print(f"Number of cycles to failure:")
        for delta_T, N_f in data['cycles_to_failure']:
            print(f"  Delta T: {delta_T:.2f}°C, Cycles to failure: {N_f:.2e}")
        
        # Calculate total cycles to failure
        total_cycles_to_failure = sum(N_f for _, N_f in data['cycles_to_failure'])
        print(f"Total cycles to failure: {total_cycles_to_failure:.2e}")
        
        # Print power dissipation metrics
        print("\nPower Dissipation Metrics:")
        print(f"Peak Total Power Dissipation: {np.max(data['p_total']):.2f} W")
        print(f"Peak Conduction Loss: {np.max(data['p_cond']):.2f} W")
        print(f"Peak Switching Loss: {np.max(data['p_sw']):.2f} W")
        print(f"Peak Capacitive Loss: {np.max(data['p_cap']):.2f} W")
        
        print(f"\nAverage Total Power Dissipation: {np.mean(data['p_total']):.2f} W")
        print(f"Average Conduction Loss: {np.mean(data['p_cond']):.2f} W")
        print(f"Average Switching Loss: {np.mean(data['p_sw']):.2f} W")
        print(f"Average Capacitive Loss: {np.mean(data['p_cap']):.2f} W")

def export_results_as_json(results: Dict[str, SimulationResult]) -> None:
    """Export simulation results as JSON for the dashboard."""
    try:
        json_data = {}
        for mosfet_name, data in results.items():
            json_data[mosfet_name] = {
                't': data['t'].tolist(),
                't_j': data['t_j'].tolist(),
                'v_ds': data['v_ds'].tolist(),
                'i_d': data['i_d'].tolist(),
                'p_total': data['p_total'].tolist(),
                'p_cond': data['p_cond'].tolist(),
                'p_sw': data['p_sw'].tolist(),
                'p_cap': data['p_cap'].tolist(),
                'peak_power': float(np.max(data['p_total'])),
                'peak_temp': float(np.max(data['t_j'])),
                'degradation': float(data['degradation']),
                'estimated_years': float(data['estimated_years']),
                'total_cycles': int(data['total_cycles']),
                'cycles_to_failure': [[float(delta_T), float(N_f)] for delta_T, N_f in data['cycles_to_failure']],
                'total_cycles_to_failure': sum(N_f for _, N_f in data['cycles_to_failure'])
            }
        
        # Ensure the output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        file_path = os.path.join(OUTPUT_DIR, 'simulation_results.json')
        with open(file_path, 'w') as f:
            json.dump(json_data, f, indent=2)
        logger.info(f"Results exported as JSON to {file_path}")
    except Exception as e:
        logger.exception(f"Error exporting results as JSON: {str(e)}")

def main() -> None:
    """Main function to run the simulation and display results."""
    try:
        results = run_simulation()
        if results:
            logger.info("Simulation completed successfully")
            logger.info("Generating plots")
            plot_results(results)
            logger.info("Printing detailed results")
            print_results(results)
            
            # Export results as JSON
            export_results_as_json(results)
        else:
            logger.warning("No valid results to display")
    except Exception as e:
        logger.exception(f"An error occurred in the main function: {str(e)}")

if __name__ == "__main__":
    main()
