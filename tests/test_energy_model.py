"""
Unit tests for the energy model components.
"""

import unittest
import sys
from pathlib import Path
import math

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from models.energy_model import EnergyModel
from models.rover_config import RoverConfig
from sim.simulate_mission import Task, MissionSimulator


class TestRoverConfig(unittest.TestCase):
    """Test cases for RoverConfig class."""
    
    def setUp(self):
        self.config = RoverConfig()
    
    def test_available_energy_full_battery(self):
        """Test available energy calculation with full battery."""
        available = self.config.get_available_energy(1.0)
        expected = self.config.BATTERY_CAPACITY * (1.0 - self.config.ENERGY_RESERVE_RATIO)
        self.assertAlmostEqual(available, expected, places=3)
    
    def test_available_energy_half_battery(self):
        """Test available energy calculation with half battery."""
        available = self.config.get_available_energy(0.5)
        total_energy = self.config.BATTERY_CAPACITY * 0.5
        reserve_energy = self.config.BATTERY_CAPACITY * self.config.ENERGY_RESERVE_RATIO
        expected = max(0, total_energy - reserve_energy)
        self.assertAlmostEqual(available, expected, places=3)
    
    def test_critical_energy_detection(self):
        """Test critical energy level detection."""
        self.assertTrue(self.config.is_critical_energy(0.05))
        self.assertTrue(self.config.is_critical_energy(0.10))
        self.assertFalse(self.config.is_critical_energy(0.15))
        self.assertFalse(self.config.is_critical_energy(0.50))


class TestEnergyModel(unittest.TestCase):
    """Test cases for EnergyModel class."""
    
    def setUp(self):
        self.config = RoverConfig()
        self.model = EnergyModel(self.config)
    
    def test_slope_force_calculation(self):
        """Test gravitational force component calculation."""
        # Test flat terrain (0 degrees)
        force_flat = self.model.calculate_slope_force(0)
        self.assertAlmostEqual(force_flat, 0, places=3)
        
        # Test 45-degree slope
        force_45 = self.model.calculate_slope_force(45)
        expected_45 = self.config.MASS * self.config.GRAVITY_MARS * math.sin(math.radians(45))
        self.assertAlmostEqual(force_45, expected_45, places=3)
        
        # Test negative slope (downhill)
        force_negative = self.model.calculate_slope_force(-30)
        expected_negative = self.config.MASS * self.config.GRAVITY_MARS * math.sin(math.radians(-30))
        self.assertAlmostEqual(force_negative, expected_negative, places=3)
    
    def test_rolling_resistance_calculation(self):
        """Test rolling resistance force calculation."""
        # Test flat terrain
        resistance_flat = self.model.calculate_rolling_resistance(slope_degrees=0)
        expected_flat = (self.config.ROLLING_RESISTANCE_COEFF * 
                        self.config.MASS * self.config.GRAVITY_MARS)
        self.assertAlmostEqual(resistance_flat, expected_flat, places=3)
        
        # Test sloped terrain (normal force should be reduced)
        resistance_slope = self.model.calculate_rolling_resistance(slope_degrees=30)
        expected_slope = (self.config.ROLLING_RESISTANCE_COEFF * 
                         self.config.MASS * self.config.GRAVITY_MARS * 
                         math.cos(math.radians(30)))
        self.assertAlmostEqual(resistance_slope, expected_slope, places=3)
    
    def test_roughness_penalty(self):
        """Test roughness penalty calculation."""
        penalty = self.model.calculate_roughness_penalty(0.5, 0.1)
        expected = 0.5 * 0.1 * 50.0  # roughness * velocity * 50.0
        self.assertAlmostEqual(penalty, expected, places=3)
        
        # Test zero roughness
        penalty_zero = self.model.calculate_roughness_penalty(0.0, 0.1)
        self.assertAlmostEqual(penalty_zero, 0.0, places=3)
    
    def test_power_consumption_flat_terrain(self):
        """Test power consumption on flat terrain."""
        power = self.model.calculate_power_consumption(
            slope_degrees=0,
            velocity=self.config.NOMINAL_VELOCITY,
            roughness=0.0
        )
        
        # Should only have rolling resistance
        expected_force = self.model.calculate_rolling_resistance()
        expected_power = (expected_force * self.config.NOMINAL_VELOCITY) / (
            self.config.MOTOR_EFFICIENCY * self.config.DRIVETRAIN_EFFICIENCY
        )
        self.assertAlmostEqual(power, expected_power, places=1)
    
    def test_energy_consumption_calculation(self):
        """Test energy consumption for a terrain segment."""
        result = self.model.calculate_energy_consumption(
            distance=100,  # 100 meters
            slope_degrees=10,
            velocity=self.config.NOMINAL_VELOCITY,
            roughness=0.1
        )
        
        # Check result structure
        required_keys = ['distance_m', 'time_hours', 'power_watts', 'energy_kwh', 
                        'slope_degrees', 'velocity_ms', 'roughness']
        for key in required_keys:
            self.assertIn(key, result)
        
        # Check values are positive
        self.assertGreater(result['time_hours'], 0)
        self.assertGreater(result['power_watts'], 0)
        self.assertGreater(result['energy_kwh'], 0)
        self.assertEqual(result['distance_m'], 100)
    
    def test_energy_consumption_invalid_velocity(self):
        """Test error handling for invalid velocity."""
        with self.assertRaises(ValueError):
            self.model.calculate_energy_consumption(
                distance=100,
                slope_degrees=0,
                velocity=0,  # Invalid velocity
                roughness=0
            )
    
    def test_task_energy_calculation(self):
        """Test energy calculation for different task types."""
        # Test valid task type
        energy = self.model.calculate_task_energy('drilling', 2.0)
        expected = self.config.TASK_POWER['drilling'] * 2.0 / 1000  # Convert to kWh
        self.assertAlmostEqual(energy, expected, places=3)
        
        # Test invalid task type
        with self.assertRaises(ValueError):
            self.model.calculate_task_energy('invalid_task', 1.0)
    
    def test_mission_energy_estimation(self):
        """Test total mission energy estimation."""
        terrain_segments = [
            {'distance': 10, 'slope_degrees': 5, 'roughness': 0.1},
            {'distance': 15, 'slope_degrees': 0, 'roughness': 0.05}
        ]
        
        tasks = [
            {'type': 'imaging', 'duration_hours': 0.5},
            {'type': 'sample_collection', 'duration_hours': 1.0}
        ]
        
        result = self.model.estimate_mission_energy(terrain_segments, tasks)
        
        # Check result structure
        required_keys = ['movement_energy_kwh', 'task_energy_kwh', 'total_energy_kwh',
                        'total_time_hours', 'battery_usage_percent']
        for key in required_keys:
            self.assertIn(key, result)
        
        # Check energy conservation
        self.assertAlmostEqual(
            result['total_energy_kwh'],
            result['movement_energy_kwh'] + result['task_energy_kwh'],
            places=6
        )
        
        # Check all values are positive
        for key in required_keys:
            self.assertGreaterEqual(result[key], 0)


class TestTask(unittest.TestCase):
    """Test cases for Task class."""
    
    def test_task_creation(self):
        """Test task object creation."""
        task = Task("T001", "drilling", 2.0, 8.0, 10.0, "Site A")
        
        self.assertEqual(task.task_id, "T001")
        self.assertEqual(task.task_type, "drilling")
        self.assertEqual(task.duration_hours, 2.0)
        self.assertEqual(task.urgency, 8.0)
        self.assertEqual(task.reward, 10.0)
        self.assertEqual(task.location, "Site A")
        self.assertFalse(task.completed)
        self.assertFalse(task.deferred)
        self.assertEqual(task.energy_cost, 0.0)


class TestMissionSimulator(unittest.TestCase):
    """Test cases for MissionSimulator class."""
    
    def setUp(self):
        self.config = RoverConfig()
        self.energy_model = EnergyModel(self.config)
        self.simulator = MissionSimulator(self.energy_model, self.config)
    
    def test_task_priority_calculation(self):
        """Test task priority calculation."""
        task = Task("T001", "drilling", 2.0, 8.0, 10.0)
        priority = self.simulator.calculate_task_priority(task)
        
        # Priority should be a number
        self.assertIsInstance(priority, (int, float))
        
        # Task should have energy cost assigned
        self.assertGreater(task.energy_cost, 0)
    
    def test_task_prioritization(self):
        """Test task sorting by priority."""
        tasks = [
            Task("T001", "drilling", 3.0, 5.0, 5.0),      # High energy, low urgency
            Task("T002", "imaging", 0.5, 9.0, 10.0),      # Low energy, high urgency, high reward
            Task("T003", "sample_collection", 1.0, 7.0, 8.0)  # Medium energy, medium urgency
        ]
        
        prioritized = self.simulator.prioritize_tasks(tasks)
        
        # Should return same number of tasks
        self.assertEqual(len(prioritized), 3)
        
        # All original tasks should be present
        task_ids = {task.task_id for task in prioritized}
        expected_ids = {"T001", "T002", "T003"}
        self.assertEqual(task_ids, expected_ids)
    
    def test_can_execute_task(self):
        """Test task execution feasibility check."""
        # Create a low-energy task
        task = Task("T001", "communication", 0.1, 5.0, 5.0)
        self.simulator.calculate_task_priority(task)  # Calculate energy cost
        
        # Should be able to execute with full battery
        self.simulator.current_battery_level = 1.0
        self.assertTrue(self.simulator.can_execute_task(task))
        
        # Should not be able to execute with critical battery
        self.simulator.current_battery_level = 0.05
        self.assertFalse(self.simulator.can_execute_task(task))
    
    def test_task_execution(self):
        """Test task execution and energy consumption."""
        task = Task("T001", "imaging", 0.5, 5.0, 5.0)
        initial_battery = self.simulator.current_battery_level
        
        # Execute task
        success = self.simulator.execute_task(task)
        
        if success:
            # Battery level should decrease
            self.assertLess(self.simulator.current_battery_level, initial_battery)
            
            # Task should be marked as completed
            self.assertTrue(task.completed)
            self.assertIn(task, self.simulator.completed_tasks)
        else:
            # Task should be deferred
            self.assertTrue(task.deferred)
            self.assertIn(task, self.simulator.deferred_tasks)


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)