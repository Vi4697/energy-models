# Energy Model Technical Description

This document provides detailed technical information about the energy modeling framework for Mars-like rovers, including physics assumptions, mathematical formulations, and implementation details.

## Table of Contents

1. [Overview](#overview)
2. [Physics Model](#physics-model)
3. [Energy Calculations](#energy-calculations)
4. [Task Prioritization](#task-prioritization)
5. [Assumptions and Limitations](#assumptions-and-limitations)
6. [Implementation Details](#implementation-details)
7. [Validation and Testing](#validation-and-testing)

## Overview

The energy modeling framework simulates the power consumption of a Mars rover during:
- **Terrain traversal**: Moving across various surface conditions
- **Task execution**: Performing scientific and operational activities
- **Mission planning**: Optimizing task schedules under energy constraints

The model combines fundamental physics principles with empirical relationships to provide realistic energy estimates for mission planning.

## Physics Model

### Coordinate System and Conventions

- **Slope angles**: Positive values indicate uphill motion, negative values indicate downhill
- **Velocity**: Always positive, representing rover speed in the forward direction
- **Forces**: Calculated in the direction of motion
- **Gravity**: Mars gravity (3.71 m/s²) used throughout

### Force Analysis

The rover experiences several forces during motion:

#### 1. Gravitational Slope Force

When traversing sloped terrain, gravity creates a component parallel to the surface:

```
F_slope = m × g × sin(θ)
```

Where:
- `m` = rover mass (kg)
- `g` = Mars gravitational acceleration (3.71 m/s²)
- `θ` = slope angle in radians

For uphill motion, this force opposes movement. For downhill motion, it assists movement but the absolute value is used in power calculations to account for required braking energy.

#### 2. Rolling Resistance

Rolling resistance arises from wheel deformation and surface interaction:

```
F_rolling = μ_r × N = μ_r × m × g × cos(θ)
```

Where:
- `μ_r` = rolling resistance coefficient (dimensionless, ≈ 0.15 for Mars terrain)
- `N` = normal force = `m × g × cos(θ)`

The rolling resistance coefficient is based on studies of rover wheel-soil interaction on Mars-analog surfaces.

#### 3. Total Resistance Force

```
F_total = |F_slope| + F_rolling
```

The absolute value of slope force accounts for energy required for both uphill climbing and downhill braking.

### Power Consumption Model

#### Mechanical Power

The mechanical power required to overcome resistance forces:

```
P_mechanical = F_total × v
```

Where `v` is the rover velocity (m/s).

#### Roughness Penalty

Terrain roughness increases power consumption due to:
- Additional wheel slip
- Increased suspension work
- Navigation complexity

The roughness penalty is modeled empirically:

```
P_roughness = roughness × velocity × 50.0 [W]
```

This relationship is based on rover performance studies on various surface types.

#### Electrical Power

The electrical power drawn from batteries accounts for system inefficiencies:

```
P_electrical = (P_mechanical + P_roughness) / (η_motor × η_drivetrain)
```

Where:
- `η_motor` = motor efficiency (≈ 0.85)
- `η_drivetrain` = drivetrain efficiency (≈ 0.90)

## Energy Calculations

### Movement Energy

For a terrain segment of distance `d` traversed at velocity `v`:

```
Time = d / v
Energy = P_electrical × Time
```

The energy is calculated in kilowatt-hours (kWh) for consistency with battery capacity units.

### Task Energy

Each task type has a characteristic power consumption:

```
E_task = P_task × duration
```

Task power values are based on:
- **Drilling**: High power for rock penetration (120 W)
- **Sample collection**: Moderate power for arm movements (80 W)
- **Imaging**: Low power for cameras and processing (30 W)
- **Communication**: Variable power for data transmission (25 W)
- **Navigation**: Processing and sensor power (50 W)
- **Spectrometry**: Instrument heating and analysis (45 W)
- **Idle**: Minimal power for essential systems (10 W)

## Task Prioritization

### Multi-Criteria Optimization

Tasks are prioritized using a weighted cost function:

```
Cost(task) = λ₁ × E(task) + λ₂ × (1/U(task)) + λ₃ × R(task)
```

Where:
- `E(task)` = energy requirement (kWh)
- `U(task)` = urgency score (1-10 scale)
- `R(task)` = scientific reward/value
- `λ₁, λ₂, λ₃` = weighting factors

### Weighting Factors

Default weights in the implementation:
- `λ₁ = 1.0`: Energy cost weight (positive, favors low-energy tasks)
- `λ₂ = 0.5`: Urgency weight (positive, favors urgent tasks via 1/urgency)
- `λ₃ = -2.0`: Reward weight (negative, favors high-reward tasks)

### Priority Ranking

Tasks are sorted by ascending cost values:
- Lower cost = higher priority
- Higher priority tasks are executed first
- Tasks exceeding energy limits are deferred

## Assumptions and Limitations

### Physics Assumptions

1. **Steady-state motion**: Acceleration/deceleration effects ignored
2. **Uniform terrain**: Properties constant within each segment
3. **No wheel slip**: Perfect traction assumed
4. **Linear efficiency**: Motor/drivetrain efficiency constant across operating range
5. **No thermal effects**: Temperature impacts on battery/motors ignored

### Environmental Assumptions

1. **Mars gravity**: Constant 3.71 m/s² (actual variation ±0.13%)
2. **No atmosphere**: Atmospheric drag negligible at rover speeds
3. **No solar charging**: Conservative battery-only analysis
4. **Flat wheel contact**: Complex wheel-terrain interaction simplified

### Operational Assumptions

1. **Perfect navigation**: No path finding energy overhead
2. **Instant task switching**: No energy cost for mode changes
3. **Reliable systems**: No fault recovery energy requirements
4. **Constant velocity**: Speed maintained throughout segments

### Model Limitations

1. **Empirical relationships**: Roughness penalty based on limited data
2. **Static terrain**: No dynamic obstacles or changing conditions
3. **Single rover**: No multi-rover coordination
4. **Simplified tasks**: Complex operations reduced to power × time
5. **Battery model**: Simplified discharge characteristics

## Implementation Details

### Numerical Precision

- All calculations performed in double precision
- Energy values rounded to 3 decimal places in output
- Angle conversions use `math.radians()` for consistency
- Battery levels stored as fractions (0-1) for numerical stability

### Performance Considerations

- Vectorized operations avoided for clarity over speed
- Mission simulations typically complete in <1 second
- Memory usage scales linearly with number of tasks/terrain segments
- No optimization for large-scale simulations implemented

### Error Handling

- Invalid input validation (negative distances, velocities)
- Division by zero protection in priority calculations
- File I/O error handling for terrain/task data
- Graceful degradation for missing task types

### Configuration Management

All physical constants and parameters centralized in `RoverConfig` class:
- Easy modification for different rover designs
- Version control of parameter changes
- Clear separation of physics from implementation

## Validation and Testing

### Unit Test Coverage

1. **Physics calculations**: Force and power computation accuracy
2. **Energy integration**: Correct energy accumulation over distance/time
3. **Boundary conditions**: Zero slope, velocity, roughness cases
4. **Task prioritization**: Cost function implementation
5. **Battery management**: Energy reserve and critical level logic

### Validation Approaches

1. **Analytical verification**: Simple cases with hand calculations
2. **Comparative analysis**: Results vs. literature values
3. **Sensitivity analysis**: Parameter variation impacts
4. **Regression testing**: Consistent results across versions

### Known Test Cases

1. **Flat terrain**: Rolling resistance only, matches theoretical values
2. **Steep slopes**: Force calculations verified against physics
3. **Zero velocity**: Graceful error handling
4. **Critical battery**: Proper mission termination

### Future Validation

1. **Hardware comparison**: Validate against actual rover data
2. **Terrain correlation**: Compare with Mars surface missions
3. **Extended missions**: Multi-sol energy balance verification
4. **Monte Carlo analysis**: Statistical validation under uncertainty

## References

1. NASA Mars rover specifications and performance data
2. Terramechanics research on wheel-soil interaction
3. Planetary rover mobility studies
4. Mars environmental conditions and gravity measurements
5. Battery and motor efficiency studies for space applications

---

*This document describes the current model implementation and should be updated as the framework evolves.*