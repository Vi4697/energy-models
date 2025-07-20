# Energy Models for Space-Like Rovers

A Python simulation framework for modeling energy consumption of Mars-like space rovers during terrain traversal and task execution. This project implements physics-based energy modeling with task prioritization based on energy constraints, mission urgency, and scientific value.

## Overview

This project simulates the energy consumption patterns of a Mars rover performing various scientific tasks while traversing different terrain types. The simulation considers:

- **Terrain-based energy consumption**: Slope, roughness, and rolling resistance
- **Task prioritization**: Energy cost, urgency, and scientific reward
- **Battery management**: Energy reserves and critical level detection
- **Mission planning**: Optimal task scheduling under energy constraints

## Features

- 🔋 **Realistic Energy Modeling**: Physics-based calculations for movement and task execution
- 🎯 **Task Prioritization**: Multi-criteria optimization (energy, urgency, reward)
- 🗺️ **Terrain Analysis**: Support for various terrain profiles and conditions
- 📊 **Mission Simulation**: Complete mission planning with energy constraints
- 🧪 **Comprehensive Testing**: Unit tests for all major components
- 📈 **Analysis Tools**: Energy consumption analysis for different scenarios

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd energy-models
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**:
   ```bash
   python -m pytest tests/
   ```

## Quick Start

### Basic Simulation

Run a complete mission simulation with sample tasks and terrain:

```bash
python main.py
```

This will:
- Load sample mission tasks and terrain data
- Prioritize tasks based on energy, urgency, and reward
- Simulate terrain traversal and task execution
- Display completion rates and energy consumption

### Terrain Analysis

Analyze energy consumption for different terrain types:

```bash
python main.py --mode terrain
```

### Task Analysis

Compare energy requirements for different task types:

```bash
python main.py --mode tasks
```

### Custom Simulation

Run simulation with custom data files:

```bash
python main.py --mode custom --tasks custom_tasks.json --terrain custom_terrain.csv
```

## Project Structure

```
energy-models/
├── main.py                    # Main entry point
├── README.md                  # This file
├── requirements.txt           # Python dependencies
├── data/
│   └── terrain_profiles.csv   # Sample terrain data
├── models/
│   ├── energy_model.py        # Energy consumption calculations
│   └── rover_config.py        # Rover specifications and constants
├── sim/
│   └── simulate_mission.py    # Mission simulation and task prioritization
├── tests/
│   └── test_energy_model.py   # Unit tests
└── docs/
    └── model_description.md   # Technical documentation
```

## Usage Examples

### Energy Model

```python
from models.energy_model import EnergyModel
from models.rover_config import RoverConfig

# Initialize energy model
config = RoverConfig()
energy_model = EnergyModel(config)

# Calculate energy for terrain traversal
result = energy_model.calculate_energy_consumption(
    distance=100,        # meters
    slope_degrees=15,    # degrees
    velocity=0.042,      # m/s
    roughness=0.3        # 0-1 scale
)

print(f"Energy required: {result['energy_kwh']:.3f} kWh")
print(f"Power consumption: {result['power_watts']:.1f} W")
```

### Mission Simulation

```python
from sim.simulate_mission import MissionSimulator, Task

# Create mission simulator
simulator = MissionSimulator()

# Define mission tasks
tasks = [
    Task("T001", "sample_collection", 2.0, urgency=8.0, reward=10.0),
    Task("T002", "imaging", 0.5, urgency=6.0, reward=5.0),
    Task("T003", "drilling", 3.0, urgency=9.0, reward=15.0)
]

# Run simulation
results = simulator.run_mission_simulation(tasks, "data/terrain_profiles.csv")

print(f"Completed: {results['mission_summary']['completed_tasks']} tasks")
print(f"Battery remaining: {results['mission_summary']['final_battery_level']:.1%}")
```

## Configuration

### Rover Parameters

Modify rover specifications in `models/rover_config.py`:

- **Mass**: 899 kg (Perseverance rover)
- **Battery**: 42.24 kWh capacity
- **Wheels**: 6 wheels, 0.27m radius
- **Velocity**: 0.042 m/s nominal speed
- **Efficiency**: 85% motor, 90% drivetrain

### Task Types

Supported task types and their power requirements:

| Task Type | Power (W) | Description |
|-----------|-----------|-------------|
| navigation | 50 | Basic movement and pathfinding |
| sample_collection | 80 | Collecting soil/rock samples |
| drilling | 120 | Core drilling operations |
| imaging | 30 | Camera and panoramic imaging |
| spectrometry | 45 | Chemical analysis |
| communication | 25 | Data transmission to Earth |
| idle | 10 | Standby operations |

### Energy Management

- **Energy Reserve**: 20% battery kept as reserve
- **Critical Level**: 10% battery triggers emergency mode
- **Safety Margins**: Conservative energy estimates for mission planning

## Terrain Data Format

Terrain profiles are stored in CSV format with columns:

```csv
distance,slope_deg,roughness
5,10,0.2
10,5,0.1
3,15,0.4
```

- **distance**: Segment length in meters
- **slope_deg**: Terrain slope in degrees (positive = uphill)
- **roughness**: Surface roughness coefficient (0-1 scale)

## Task Data Format

Custom tasks can be defined in JSON format:

```json
[
  {
    "task_id": "T001",
    "task_type": "sample_collection",
    "duration_hours": 2.0,
    "urgency": 8.0,
    "reward": 10.0,
    "location": "Crater A"
  }
]
```

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=models --cov=sim

# Run specific test file
python -m pytest tests/test_energy_model.py -v
```

## Physics Model

The energy model is based on fundamental physics principles:

### Movement Energy

```
Power = (Slope_Force + Rolling_Resistance) × Velocity / Efficiency

Where:
- Slope_Force = Mass × Gravity × sin(slope_angle)
- Rolling_Resistance = Coefficient × Mass × Gravity × cos(slope_angle)
- Efficiency = Motor_Efficiency × Drivetrain_Efficiency
```

### Task Prioritization

Tasks are prioritized using a multi-criteria cost function:

```
Cost = λ₁ × Energy + λ₂ × (1/Urgency) + λ₃ × Reward

Where:
- λ₁ = 1.0 (energy weight)
- λ₂ = 0.5 (urgency weight)  
- λ₃ = -2.0 (reward weight, negative to maximize)
```

Lower cost values indicate higher priority tasks.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on research in "Task Prioritization and Energy Estimation for Space-Like Rovers"
- Mars rover specifications inspired by NASA's Perseverance rover
- Physics models based on established rover mobility research

## Future Enhancements

- [ ] Dynamic terrain mapping and path planning
- [ ] Solar panel energy generation modeling
- [ ] Multi-sol mission planning
- [ ] Thermal management considerations
- [ ] Communication window optimization
- [ ] Fault tolerance and backup systems