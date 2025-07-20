"""
Energy consumption model for Mars rover simulation.
Calculates energy usage based on terrain parameters and rover dynamics.
"""

import math
from typing import Dict, List, Tuple
from .rover_config import RoverConfig


class EnergyModel:
    """
    Energy consumption model for rover terrain traversal and task execution.
    
    This model calculates energy consumption based on:
    - Terrain slope and roughness
    - Rover velocity and distance
    - Rolling resistance
    - Motor and drivetrain efficiency
    """
    
    def __init__(self, config: RoverConfig = None):
        """
        Initialize the energy model with rover configuration.
        
        Args:
            config (RoverConfig): Rover configuration object
        """
        self.config = config if config else RoverConfig()
    
    def calculate_slope_force(self, slope_degrees: float, mass: float = None) -> float:
        """
        Calculate gravitational force component due to slope.
        
        Args:
            slope_degrees (float): Terrain slope in degrees
            mass (float): Rover mass in kg (default from config)
            
        Returns:
            float: Slope force in Newtons
        """
        if mass is None:
            mass = self.config.MASS
            
        slope_radians = math.radians(slope_degrees)
        return mass * self.config.GRAVITY_MARS * math.sin(slope_radians)
    
    def calculate_rolling_resistance(self, mass: float = None, slope_degrees: float = 0) -> float:
        """
        Calculate rolling resistance force.
        
        Args:
            mass (float): Rover mass in kg (default from config)
            slope_degrees (float): Terrain slope in degrees
            
        Returns:
            float: Rolling resistance force in Newtons
        """
        if mass is None:
            mass = self.config.MASS
            
        slope_radians = math.radians(slope_degrees)
        normal_force = mass * self.config.GRAVITY_MARS * math.cos(slope_radians)
        return self.config.ROLLING_RESISTANCE_COEFF * normal_force
    
    def calculate_roughness_penalty(self, roughness: float, velocity: float) -> float:
        """
        Calculate additional power penalty due to terrain roughness.
        
        Args:
            roughness (float): Terrain roughness coefficient (0-1)
            velocity (float): Rover velocity in m/s
            
        Returns:
            float: Additional power penalty in Watts
        """
        return roughness * velocity * 50.0  # Empirical relationship
    
    def calculate_power_consumption(self, 
                                  slope_degrees: float,
                                  velocity: float,
                                  roughness: float = 0.0,
                                  mass: float = None) -> float:
        """
        Calculate instantaneous power consumption for rover movement.
        
        Args:
            slope_degrees (float): Terrain slope in degrees
            velocity (float): Rover velocity in m/s
            roughness (float): Terrain roughness coefficient (0-1)
            mass (float): Rover mass in kg (default from config)
            
        Returns:
            float: Power consumption in Watts
        """
        if mass is None:
            mass = self.config.MASS
        
        # Calculate forces
        slope_force = self.calculate_slope_force(slope_degrees, mass)
        rolling_resistance = self.calculate_rolling_resistance(mass, slope_degrees)
        
        # Total force opposing motion
        total_force = abs(slope_force) + rolling_resistance
        
        # Mechanical power required
        mechanical_power = total_force * velocity
        
        # Account for roughness
        roughness_penalty = self.calculate_roughness_penalty(roughness, velocity)
        
        # Account for motor and drivetrain efficiency
        electrical_power = (mechanical_power + roughness_penalty) / (
            self.config.MOTOR_EFFICIENCY * self.config.DRIVETRAIN_EFFICIENCY
        )
        
        return electrical_power
    
    def calculate_energy_consumption(self,
                                   distance: float,
                                   slope_degrees: float,
                                   velocity: float,
                                   roughness: float = 0.0,
                                   mass: float = None) -> Dict[str, float]:
        """
        Calculate energy consumption for a terrain segment.
        
        Args:
            distance (float): Distance to travel in meters
            slope_degrees (float): Terrain slope in degrees
            velocity (float): Rover velocity in m/s
            roughness (float): Terrain roughness coefficient (0-1)
            mass (float): Rover mass in kg (default from config)
            
        Returns:
            Dict[str, float]: Energy consumption details
        """
        if velocity <= 0:
            raise ValueError("Velocity must be positive")
        
        # Calculate time to traverse segment
        time_hours = distance / (velocity * 3600)  # Convert to hours
        
        # Calculate power consumption
        power_watts = self.calculate_power_consumption(
            slope_degrees, velocity, roughness, mass
        )
        
        # Calculate energy consumption
        energy_kwh = power_watts * time_hours / 1000  # Convert to kWh
        
        return {
            'distance_m': distance,
            'time_hours': time_hours,
            'power_watts': power_watts,
            'energy_kwh': energy_kwh,
            'slope_degrees': slope_degrees,
            'velocity_ms': velocity,
            'roughness': roughness
        }
    
    def calculate_task_energy(self, task_type: str, duration_hours: float) -> float:
        """
        Calculate energy consumption for a specific task.
        
        Args:
            task_type (str): Type of task (from TASK_POWER config)
            duration_hours (float): Task duration in hours
            
        Returns:
            float: Energy consumption in kWh
        """
        if task_type not in self.config.TASK_POWER:
            raise ValueError(f"Unknown task type: {task_type}")
        
        power_watts = self.config.TASK_POWER[task_type]
        return power_watts * duration_hours / 1000  # Convert to kWh
    
    def estimate_mission_energy(self, terrain_segments: List[Dict], 
                              tasks: List[Dict]) -> Dict[str, float]:
        """
        Estimate total energy consumption for a complete mission.
        
        Args:
            terrain_segments (List[Dict]): List of terrain segment parameters
            tasks (List[Dict]): List of task parameters
            
        Returns:
            Dict[str, float]: Total energy breakdown
        """
        total_movement_energy = 0.0
        total_task_energy = 0.0
        total_time = 0.0
        
        # Calculate movement energy
        for segment in terrain_segments:
            result = self.calculate_energy_consumption(
                distance=segment['distance'],
                slope_degrees=segment.get('slope_degrees', 0),
                velocity=segment.get('velocity', self.config.NOMINAL_VELOCITY),
                roughness=segment.get('roughness', 0)
            )
            total_movement_energy += result['energy_kwh']
            total_time += result['time_hours']
        
        # Calculate task energy
        for task in tasks:
            task_energy = self.calculate_task_energy(
                task_type=task['type'],
                duration_hours=task['duration_hours']
            )
            total_task_energy += task_energy
            total_time += task['duration_hours']
        
        total_energy = total_movement_energy + total_task_energy
        
        return {
            'movement_energy_kwh': total_movement_energy,
            'task_energy_kwh': total_task_energy,
            'total_energy_kwh': total_energy,
            'total_time_hours': total_time,
            'battery_usage_percent': (total_energy / self.config.BATTERY_CAPACITY) * 100
        }