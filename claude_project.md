# Claude Setup Project Prompt: Energy Model for Space-Like Rovers

This file will guide Claude to generate a complete energy modeling simulation project, based on the thesis "Task Prioritization and Energy Estimation for Space-Like Rovers."


---

## 🧠 Claude Project Description

You are a smart AI assistant helping me write a full Python simulation project. The project simulates **energy consumption of a Mars-like space rover** during terrain traversal and task execution, based on real-world terrain parameters and mission priorities.

---

## 🔧 Project Requirements

Create a structured Python project named `energy-models` with the following:

### 📁 Folder Structure
energy-model-rover/
├── main.py
├── README.md
├── requirements.txt
├── data/
│ └── terrain_profiles.csv
├── models/
│ ├── energy_model.py
│ └── rover_config.py
├── sim/
│ └── simulate_mission.py
├── tests/
│ └── test_energy_model.py
└── docs/
└── model_description.md

### 📄 File Requirements

#### `README.md`
Explain the purpose of the project, how to run simulations, and how to modify terrain/task settings.

#### `requirements.txt`
List libraries: `numpy`, `pandas`, `matplotlib`, etc.

#### `models/energy_model.py`
Python class `EnergyModel` that:
- Calculates energy usage based on slope, velocity, distance, and rover mass.
- Formula:
```python
power = mass * gravity * slope_force + rolling_resistance
energy = power * time
models/rover_config.py

Stores rover constants (mass, wheel radius, battery capacity).

sim/simulate_mission.py

Runs a mission simulation by:

Loading terrain profiles from CSV
Using EnergyModel to estimate total energy use
Logging task execution and skipped tasks based on energy availability
tests/test_energy_model.py

Simple unit tests for EnergyModel functions.

data/terrain_profiles.csv

Example file:
distance,slope_deg,roughness
5,10,0.2
10,5,0.1
3,15,0.4

docs/model_description.md

Summarize how the model works (inputs, physics assumptions, and simplifications).


Behavior Requirements

Tasks should be prioritized based on energy cost, urgency, and mission value.
Include a simple cost function:
cost = lambda1 * energy + lambda2 * (1 / urgency) + lambda3 * reward

Defer tasks that exceed energy limit.



Goal

Generate the full project structure and file contents. Return each file content separately so I can create them in my local repository.

