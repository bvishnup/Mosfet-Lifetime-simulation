from typing import Dict, Any

MOSFETParams = Dict[str, Any]

MOSFET_PARAMS: Dict[str, MOSFETParams] = {
    'SPB20N60C3': {
        'R_DS_ON_25': 0.19,
        'R_DS_ON_TEMP_COEFF': 0.01,
        'T_ON_25': 25e-9,
        'T_OFF_25': 35e-9,
        'E_OSS_25': 3.2e-6,
        'Q_RR_25': 0.8e-6,
        'R_TH': [0.05, 0.1, 0.15, 0.2, 0.25],
        'C_TH': [1.5e-6, 1.5e-5, 1.5e-4, 1.5e-3, 1.5e-2],
        'K_T_SW': 0.004,
        'K_E_OSS': 0.0015,
        'K_Q_RR': 0.0025,
        'C_OSS': 150e-12,
        'COOLING_COEFF': 15,
        'SURFACE_AREA': 0.0012,
        'MAX_TEMP': 175,
        'LIFETIME_PARAMS': {
            'A': 3.5e5,
            'n': 5.1,
            'Ea': 0.54,
        }
    },
    'STB7ANM60N': {
        'R_DS_ON_25': 0.95,
        'R_DS_ON_TEMP_COEFF': 0.01,
        'T_ON_25': 30e-9,
        'T_OFF_25': 100e-9,
        'E_OSS_25': 1.5e-6,
        'Q_RR_25': 0.5e-6,
        'R_TH': [0.1, 0.15, 0.2, 0.25, 0.3],
        'C_TH': [0.8e-6, 0.8e-5, 0.8e-4, 0.8e-3, 0.8e-2],
        'K_T_SW': 0.005,
        'K_E_OSS': 0.002,
        'K_Q_RR': 0.003,
        'C_OSS': 80e-12,
        'COOLING_COEFF': 12,
        'SURFACE_AREA': 0.0008,
        'MAX_TEMP': 175,
        'LIFETIME_PARAMS': {
            'A': 2.8e5,
            'n': 5.3,
            'Ea': 0.49,
        }
    }
}

# Voltage and current waveforms
VRT = [
    (0.0, 0), (0.2, 286), (0.5, 203), (3.0, 203),
    (3.5, 96), (13.8, 96), (14.0, -302), (14.2, 0), (14.8, 0)
]
IRT = [
    (0.0, 0.0), (0.2, 0.5), (0.5, 1.1), (3.0, 1.1),
    (3.5, 0.53), (13.8, 0.53), (14.0, 0.0), (14.2, 0.0), (14.8, 0.0)
]