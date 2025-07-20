#!/usr/bin/env python3
"""
Energy Models for Space-Like Rovers
Main entry point for the rover energy modeling simulation.

This script demonstrates the energy modeling capabilities for Mars-like rovers,
including terrain traversal energy consumption and task prioritization based
on energy constraints.
"""

import sys
import argparse
from pathlib import Path
import json

# Import project modules
from models.energy_model import EnergyModel
from models.rover_config import RoverConfig
from sim.simulate_mission import MissionSimulator, Task, create_sample_tasks


def run_basic_simulation():
    """Run a basic simulation with default parameters."""
    print("=== BASIC ROVER ENERGY SIMULATION ===\n")
    
    # Initialize components
    config = RoverConfig()
    energy_model = EnergyModel(config)
    simulator = MissionSimulator(energy_model, config)
    
    # Display rover specifications
    print("Rover Specifications:")
    print(f"  Mass: {config.MASS} kg")
    print(f"  Battery Capacity: {config.BATTERY_CAPACITY} kWh")
    print(f"  Nominal Velocity: {config.NOMINAL_VELOCITY} m/s")
    print(f"  Energy Reserve: {config.ENERGY_RESERVE_RATIO:.0%}")
    print()
    
    # Create sample tasks
    tasks = create_sample_tasks()
    print(f"Mission Tasks ({len(tasks)} total):")
    for task in tasks:
        print(f"  {task.task_id}: {task.task_type} ({task.duration_hours}h) "
              f"- Urgency: {task.urgency}, Reward: {task.reward}")
    print()
    
    # Run simulation
    terrain_csv_path = Path("data/terrain_profiles.csv")
    results = simulator.run_mission_simulation(tasks, str(terrain_csv_path))
    
    # Display results
    print("=== SIMULATION RESULTS ===")
    summary = results['mission_summary']
    print(f"Tasks Completed: {summary['completed_tasks']}/{summary['total_tasks']} "
          f"({summary['completion_rate']:.1%})")
    print(f"Final Battery Level: {summary['final_battery_level']:.1%}")
    print(f"Total Energy Consumed: {summary['total_energy_consumed_kwh']:.3f} kWh")
    print(f"Task Energy: {summary['task_energy_kwh']:.3f} kWh")
    
    if results['traversal_summary']:
        trav = results['traversal_summary']
        print(f"Traversal Distance: {trav['total_distance_m']:.0f} m")
        print(f"Traversal Energy: {trav['total_energy_kwh']:.3f} kWh")
    
    print("\nCompleted Tasks:")
    for task in results['completed_tasks']:
        print(f"  ✓ {task['task_id']}: {task['type']} ({task['energy_kwh']:.3f} kWh)")
    
    if results['deferred_tasks']:
        print("\nDeferred Tasks (insufficient energy):")
        for task in results['deferred_tasks']:
            print(f"  ✗ {task['task_id']}: {task['type']} ({task['energy_kwh']:.3f} kWh)")
    
    return results


def run_terrain_analysis():
    """Analyze energy consumption for different terrain scenarios."""
    print("\n=== TERRAIN ENERGY ANALYSIS ===\n")
    
    config = RoverConfig()
    energy_model = EnergyModel(config)
    
    # Test different terrain scenarios
    scenarios = [
        {"name": "Flat terrain", "slope": 0, "roughness": 0.02},
        {"name": "Gentle slope", "slope": 5, "roughness": 0.1},
        {"name": "Moderate slope", "slope": 15, "roughness": 0.3},
        {"name": "Steep slope", "slope": 25, "roughness": 0.5},
        {"name": "Very rough", "slope": 10, "roughness": 0.8}
    ]
    
    distance = 100  # 100 meters
    velocity = config.NOMINAL_VELOCITY
    
    print(f"Energy consumption for {distance}m traversal at {velocity:.3f} m/s:\n")
    
    for scenario in scenarios:
        result = energy_model.calculate_energy_consumption(
            distance=distance,
            slope_degrees=scenario["slope"],
            velocity=velocity,
            roughness=scenario["roughness"]
        )
        
        print(f"{scenario['name']:15} | "
              f"Slope: {scenario['slope']:2d}° | "
              f"Roughness: {scenario['roughness']:4.2f} | "
              f"Power: {result['power_watts']:6.1f} W | "
              f"Energy: {result['energy_kwh']:7.4f} kWh | "
              f"Time: {result['time_hours']*3600:5.0f} s")


def run_task_analysis():
    """Analyze energy consumption for different task types."""
    print("\n=== TASK ENERGY ANALYSIS ===\n")
    
    config = RoverConfig()
    energy_model = EnergyModel(config)
    
    duration = 1.0  # 1 hour
    
    print(f"Energy consumption for {duration:.1f}-hour task execution:\n")
    
    for task_type, power in config.TASK_POWER.items():
        energy = energy_model.calculate_task_energy(task_type, duration)
        battery_percent = (energy / config.BATTERY_CAPACITY) * 100
        
        print(f"{task_type:18} | "
              f"Power: {power:5.1f} W | "
              f"Energy: {energy:7.4f} kWh | "
              f"Battery: {battery_percent:5.2f}%")


def run_custom_simulation(tasks_file: str = None, terrain_file: str = None):
    """Run simulation with custom tasks and terrain data."""
    print("=== CUSTOM SIMULATION ===\n")
    
    # Initialize components
    config = RoverConfig()
    energy_model = EnergyModel(config)
    simulator = MissionSimulator(energy_model, config)
    
    # Load custom tasks if provided
    if tasks_file and Path(tasks_file).exists():
        print(f"Loading tasks from: {tasks_file}")
        with open(tasks_file, 'r') as f:
            tasks_data = json.load(f)
        
        tasks = []
        for task_data in tasks_data:
            task = Task(
                task_id=task_data['task_id'],
                task_type=task_data['task_type'],
                duration_hours=task_data['duration_hours'],
                urgency=task_data['urgency'],
                reward=task_data['reward'],
                location=task_data.get('location', 'unknown')
            )
            tasks.append(task)
    else:
        print("Using sample tasks")
        tasks = create_sample_tasks()
    
    # Use custom terrain file if provided
    if terrain_file and Path(terrain_file).exists():
        print(f"Using terrain data from: {terrain_file}")
        terrain_path = terrain_file
    else:
        print("Using default terrain data")
        terrain_path = "data/terrain_profiles.csv"
    
    # Run simulation
    results = simulator.run_mission_simulation(tasks, terrain_path)
    
    # Display results (reuse display logic from basic simulation)
    summary = results['mission_summary']
    print(f"\nCompleted: {summary['completed_tasks']}/{summary['total_tasks']} tasks")
    print(f"Battery remaining: {summary['final_battery_level']:.1%}")
    print(f"Total energy used: {summary['total_energy_consumed_kwh']:.3f} kWh")
    
    return results


def main():
    """Main entry point with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Energy Models for Space-Like Rovers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Run basic simulation
  python main.py --mode terrain            # Analyze terrain energy consumption  
  python main.py --mode tasks              # Analyze task energy consumption
  python main.py --mode custom --tasks custom_tasks.json --terrain custom_terrain.csv
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['basic', 'terrain', 'tasks', 'custom'],
        default='basic',
        help='Simulation mode (default: basic)'
    )
    
    parser.add_argument(
        '--tasks',
        type=str,
        help='JSON file with custom task definitions'
    )
    
    parser.add_argument(
        '--terrain',
        type=str,
        help='CSV file with custom terrain data'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output file for simulation results (JSON format)'
    )
    
    args = parser.parse_args()
    
    # Run appropriate simulation mode
    try:
        if args.mode == 'basic':
            results = run_basic_simulation()
        elif args.mode == 'terrain':
            run_terrain_analysis()
            results = None
        elif args.mode == 'tasks':
            run_task_analysis()
            results = None
        elif args.mode == 'custom':
            results = run_custom_simulation(args.tasks, args.terrain)
        else:
            parser.print_help()
            return 1
        
        # Save results if output file specified
        if args.output and results:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to: {args.output}")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())