"""
Mission simulation module for Mars rover energy modeling.
Handles task prioritization, energy estimation, and mission execution simulation.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
import logging
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from models.energy_model import EnergyModel
from models.rover_config import RoverConfig


class Task:
    """Represents a mission task with energy and priority attributes."""
    
    def __init__(self, task_id: str, task_type: str, duration_hours: float,
                 urgency: float, reward: float, location: str = "unknown"):
        """
        Initialize a task.
        
        Args:
            task_id (str): Unique task identifier
            task_type (str): Type of task (must be in RoverConfig.TASK_POWER)
            duration_hours (float): Task duration in hours
            urgency (float): Task urgency (1-10, higher is more urgent)
            reward (float): Mission value/reward for completing task
            location (str): Task location description
        """
        self.task_id = task_id
        self.task_type = task_type
        self.duration_hours = duration_hours
        self.urgency = urgency
        self.reward = reward
        self.location = location
        self.completed = False
        self.deferred = False
        self.energy_cost = 0.0
    
    def __repr__(self):
        return f"Task({self.task_id}, {self.task_type}, {self.duration_hours}h)"


class MissionSimulator:
    """
    Simulates rover mission execution with energy constraints and task prioritization.
    """
    
    def __init__(self, energy_model: EnergyModel = None, config: RoverConfig = None):
        """
        Initialize mission simulator.
        
        Args:
            energy_model (EnergyModel): Energy calculation model
            config (RoverConfig): Rover configuration
        """
        self.config = config if config else RoverConfig()
        self.energy_model = energy_model if energy_model else EnergyModel(self.config)
        
        # Cost function weights (lambda parameters)
        self.lambda1 = 1.0    # Energy cost weight
        self.lambda2 = 0.5    # Urgency weight
        self.lambda3 = -2.0   # Reward weight (negative because we want to maximize reward)
        
        # Mission state
        self.current_battery_level = 1.0  # Start with full battery
        self.completed_tasks = []
        self.deferred_tasks = []
        self.mission_log = []
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def load_terrain_data(self, csv_path: str) -> pd.DataFrame:
        """
        Load terrain profile data from CSV file.
        
        Args:
            csv_path (str): Path to terrain CSV file
            
        Returns:
            pd.DataFrame: Terrain data
        """
        try:
            terrain_data = pd.read_csv(csv_path)
            required_columns = ['distance', 'slope_deg', 'roughness']
            
            if not all(col in terrain_data.columns for col in required_columns):
                raise ValueError(f"CSV must contain columns: {required_columns}")
            
            return terrain_data
        except Exception as e:
            self.logger.error(f"Error loading terrain data: {e}")
            raise
    
    def calculate_task_priority(self, task: Task) -> float:
        """
        Calculate task priority using cost function.
        Lower values indicate higher priority.
        
        Args:
            task (Task): Task to evaluate
            
        Returns:
            float: Priority cost (lower = higher priority)
        """
        # Calculate energy cost for the task
        energy_cost = self.energy_model.calculate_task_energy(
            task.task_type, task.duration_hours
        )
        task.energy_cost = energy_cost
        
        # Cost function: lambda1 * energy + lambda2 * (1/urgency) + lambda3 * reward
        cost = (self.lambda1 * energy_cost + 
                self.lambda2 * (1.0 / max(task.urgency, 0.1)) + 
                self.lambda3 * task.reward)
        
        return cost
    
    def prioritize_tasks(self, tasks: List[Task]) -> List[Task]:
        """
        Sort tasks by priority (lowest cost first).
        
        Args:
            tasks (List[Task]): List of tasks to prioritize
            
        Returns:
            List[Task]: Sorted tasks by priority
        """
        return sorted(tasks, key=self.calculate_task_priority)
    
    def can_execute_task(self, task: Task) -> bool:
        """
        Check if task can be executed given current energy constraints.
        
        Args:
            task (Task): Task to check
            
        Returns:
            bool: True if task can be executed
        """
        # Check if rover is in critical energy state
        if self.config.is_critical_energy(self.current_battery_level):
            return False
        
        # Calculate available energy
        available_energy = self.config.get_available_energy(self.current_battery_level)
        
        # Check if task energy requirement is within available energy
        return task.energy_cost <= available_energy
    
    def execute_task(self, task: Task) -> bool:
        """
        Execute a task and update energy state.
        
        Args:
            task (Task): Task to execute
            
        Returns:
            bool: True if task was successfully executed
        """
        if not self.can_execute_task(task):
            task.deferred = True
            self.deferred_tasks.append(task)
            self.logger.warning(f"Task {task.task_id} deferred due to energy constraints")
            return False
        
        # Execute task and consume energy
        energy_consumed = task.energy_cost
        energy_fraction = energy_consumed / self.config.BATTERY_CAPACITY
        self.current_battery_level -= energy_fraction
        
        # Mark task as completed
        task.completed = True
        self.completed_tasks.append(task)
        
        # Log execution
        log_entry = {
            'task_id': task.task_id,
            'task_type': task.task_type,
            'duration_hours': task.duration_hours,
            'energy_consumed_kwh': energy_consumed,
            'battery_level_after': self.current_battery_level,
            'status': 'completed'
        }
        self.mission_log.append(log_entry)
        
        self.logger.info(f"Task {task.task_id} completed. Battery: {self.current_battery_level:.1%}")
        return True
    
    def simulate_terrain_traversal(self, terrain_data: pd.DataFrame, 
                                 velocity: float = None) -> Dict[str, float]:
        """
        Simulate energy consumption for terrain traversal.
        
        Args:
            terrain_data (pd.DataFrame): Terrain segment data
            velocity (float): Rover velocity (default from config)
            
        Returns:
            Dict[str, float]: Traversal energy summary
        """
        if velocity is None:
            velocity = self.config.NOMINAL_VELOCITY
        
        total_energy = 0.0
        total_distance = 0.0
        total_time = 0.0
        
        for _, segment in terrain_data.iterrows():
            result = self.energy_model.calculate_energy_consumption(
                distance=segment['distance'],
                slope_degrees=segment['slope_deg'],
                velocity=velocity,
                roughness=segment['roughness']
            )
            
            total_energy += result['energy_kwh']
            total_distance += result['distance_m']
            total_time += result['time_hours']
        
        # Update battery level
        energy_fraction = total_energy / self.config.BATTERY_CAPACITY
        self.current_battery_level -= energy_fraction
        
        traversal_summary = {
            'total_distance_m': total_distance,
            'total_time_hours': total_time,
            'total_energy_kwh': total_energy,
            'battery_level_after': self.current_battery_level
        }
        
        self.logger.info(f"Terrain traversal completed. Distance: {total_distance}m, "
                        f"Energy: {total_energy:.3f} kWh, Battery: {self.current_battery_level:.1%}")
        
        return traversal_summary
    
    def run_mission_simulation(self, tasks: List[Task], 
                             terrain_csv_path: str = None,
                             velocity: float = None) -> Dict[str, any]:
        """
        Run complete mission simulation.
        
        Args:
            tasks (List[Task]): List of mission tasks
            terrain_csv_path (str): Path to terrain data CSV
            velocity (float): Rover velocity for traversal
            
        Returns:
            Dict[str, any]: Mission simulation results
        """
        self.logger.info(f"Starting mission simulation with {len(tasks)} tasks")
        
        # Reset mission state
        self.current_battery_level = 1.0
        self.completed_tasks = []
        self.deferred_tasks = []
        self.mission_log = []
        
        # Simulate terrain traversal if provided
        traversal_summary = None
        if terrain_csv_path:
            terrain_data = self.load_terrain_data(terrain_csv_path)
            traversal_summary = self.simulate_terrain_traversal(terrain_data, velocity)
        
        # Prioritize tasks
        prioritized_tasks = self.prioritize_tasks(tasks)
        self.logger.info(f"Tasks prioritized. Order: {[t.task_id for t in prioritized_tasks]}")
        
        # Execute tasks in priority order
        for task in prioritized_tasks:
            if self.config.is_critical_energy(self.current_battery_level):
                self.logger.warning("Critical energy level reached. Stopping mission.")
                # Defer remaining tasks
                remaining_tasks = [t for t in prioritized_tasks if not t.completed and not t.deferred]
                for remaining_task in remaining_tasks:
                    remaining_task.deferred = True
                    self.deferred_tasks.append(remaining_task)
                break
            
            self.execute_task(task)
        
        # Calculate mission statistics
        total_completed = len(self.completed_tasks)
        total_deferred = len(self.deferred_tasks)
        completion_rate = total_completed / len(tasks) if tasks else 0
        
        total_task_energy = sum(task.energy_cost for task in self.completed_tasks)
        total_energy_consumed = (1.0 - self.current_battery_level) * self.config.BATTERY_CAPACITY
        
        mission_results = {
            'mission_summary': {
                'total_tasks': len(tasks),
                'completed_tasks': total_completed,
                'deferred_tasks': total_deferred,
                'completion_rate': completion_rate,
                'final_battery_level': self.current_battery_level,
                'total_energy_consumed_kwh': total_energy_consumed,
                'task_energy_kwh': total_task_energy
            },
            'completed_tasks': [
                {'task_id': t.task_id, 'type': t.task_type, 'energy_kwh': t.energy_cost}
                for t in self.completed_tasks
            ],
            'deferred_tasks': [
                {'task_id': t.task_id, 'type': t.task_type, 'energy_kwh': t.energy_cost}
                for t in self.deferred_tasks
            ],
            'traversal_summary': traversal_summary,
            'mission_log': self.mission_log
        }
        
        self.logger.info(f"Mission completed. Completion rate: {completion_rate:.1%}, "
                        f"Final battery: {self.current_battery_level:.1%}")
        
        return mission_results


def create_sample_tasks() -> List[Task]:
    """Create sample tasks for demonstration."""
    return [
        Task("T001", "sample_collection", 2.0, 8.0, 10.0, "Crater A"),
        Task("T002", "imaging", 0.5, 6.0, 5.0, "Rock Formation B"),
        Task("T003", "drilling", 3.0, 9.0, 15.0, "Mineral Deposit C"),
        Task("T004", "spectrometry", 1.0, 7.0, 8.0, "Soil Sample D"),
        Task("T005", "navigation", 0.25, 5.0, 3.0, "Waypoint E"),
        Task("T006", "communication", 0.5, 4.0, 2.0, "Earth Contact"),
        Task("T007", "sample_collection", 1.5, 8.5, 12.0, "Unusual Rock F"),
        Task("T008", "imaging", 0.75, 6.5, 6.0, "Panoramic View G")
    ]


if __name__ == "__main__":
    # Example usage
    simulator = MissionSimulator()
    
    # Create sample tasks
    tasks = create_sample_tasks()
    
    # Run mission simulation
    data_path = Path(__file__).parent.parent / "data" / "terrain_profiles.csv"
    results = simulator.run_mission_simulation(tasks, str(data_path))
    
    # Print results
    print("\n=== MISSION SIMULATION RESULTS ===")
    print(f"Tasks completed: {results['mission_summary']['completed_tasks']}/{results['mission_summary']['total_tasks']}")
    print(f"Completion rate: {results['mission_summary']['completion_rate']:.1%}")
    print(f"Final battery level: {results['mission_summary']['final_battery_level']:.1%}")
    print(f"Total energy consumed: {results['mission_summary']['total_energy_consumed_kwh']:.3f} kWh")
    
    print("\nCompleted tasks:")
    for task in results['completed_tasks']:
        print(f"  - {task['task_id']}: {task['type']} ({task['energy_kwh']:.3f} kWh)")
    
    if results['deferred_tasks']:
        print("\nDeferred tasks:")
        for task in results['deferred_tasks']:
            print(f"  - {task['task_id']}: {task['type']} ({task['energy_kwh']:.3f} kWh)")