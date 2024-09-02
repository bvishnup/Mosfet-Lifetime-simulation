# MOSFET Lifetime Simulation

## Overview

This project simulates the lifetime of MOSFETs (Metal-Oxide-Semiconductor Field-Effect Transistors) under specific operating conditions. It combines thermal modeling, power loss calculations, and reliability estimation to provide insights into MOSFET performance and longevity in power electronic applications.

## Simulation Process

The simulation process involves several key steps:

1. **Thermal Modeling**: We use a non-linear thermal model to simulate the junction temperature of the MOSFET over time. This model accounts for:
   - Temperature-dependent thermal resistance and capacitance
   - Power dissipation in the device
   - Cooling effects

2. **Power Loss Calculation**: The simulation calculates various power loss components:
   - Conduction losses
   - Switching losses (turn-on and turn-off)
   - Capacitive losses
   - Reverse recovery losses

3. **Lifetime Estimation**: Using the thermal cycling data from the simulation, we estimate the MOSFET's lifetime based on:
   - Rainflow counting algorithm for cycle counting
   - Miner's rule for cumulative damage calculation
   - Temperature-dependent lifetime model parameters

4. **Data Visualization**: The results are presented through:
   - Interactive plots of junction temperature, voltage, and current
   - Comparison of different MOSFETs' lifetimes
   - Summary statistics of peak temperatures and power losses

## Key Features

- Accurate thermal modeling with temperature-dependent parameters
- Comprehensive power loss calculations including switching and capacitive losses
- Advanced lifetime estimation using rainflow counting and Miner's rule
- Interactive dashboard for result visualization
- Comparison of multiple MOSFET models

## Files Description

- `main-script.py`: The main script that orchestrates the simulation process
- `thermal_simulation.py`: Contains the thermal model and simulation logic
- `lifetime_estimation.py`: Implements the lifetime estimation algorithms
- `mosfet_params.py`: Defines the MOSFET parameters and operating conditions
- `mosfet-simulation-dashboard.py`: Creates an interactive dashboard to visualize results

## How to Use

1. Ensure all required dependencies are installed (numpy, scipy, dash, plotly, pandas)
2. Run `main-script.py` to perform the simulation
3. The script will generate JSON output with simulation results
4. Run `mosfet-simulation-dashboard.py` to view the interactive dashboard

## Technical Details

### Thermal Model

The thermal model uses a state-space representation of the MOSFET's thermal network. It accounts for:
- Non-linear thermal resistance and capacitance
- Temperature-dependent electrical parameters (e.g., on-state resistance)
- Cooling effects based on surface area and cooling coefficient

### Power Loss Calculation

Power losses are calculated dynamically based on instantaneous voltage and current. The model includes:
- Temperature-dependent on-state resistance for accurate conduction loss
- Switching loss calculation with temperature-dependent switching times
- Capacitive losses considering output capacitance
- Reverse recovery losses

### Lifetime Estimation

The lifetime estimation process involves:
1. Using the rainflow counting algorithm to identify thermal cycles
2. Calculating damage for each cycle using a temperature-dependent Coffin-Manson model
3. Applying Miner's rule to estimate cumulative damage and predict lifetime

## Limitations and Future Work

- The current model assumes a simplified cooling mechanism. Future versions could incorporate more detailed thermal management models.
- The lifetime model parameters are based on general data. For more accurate results, device-specific reliability data should be used.
- The simulation could be extended to include more complex power electronic circuits and systems.

## Contributing

Contributions to improve the simulation accuracy, add new features, or enhance the visualization are welcome. Please submit a pull request or open an issue to discuss proposed changes.

## License

[MIT License](LICENSE)

---

This project provides valuable insights into MOSFET behavior and reliability in power electronic applications. It serves as a useful tool for engineers and researchers in the field of power electronics for component selection and system design optimization.
