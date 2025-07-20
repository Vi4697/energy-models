"""
Rover configuration parameters for energy modeling simulation.
Contains physical constants and rover specifications.
"""

class RoverConfig:
    """Configuration class containing rover physical parameters."""
    
    # Physical constants
    GRAVITY_MARS = 3.71  # m/s^2 (Mars gravity)
    GRAVITY_EARTH = 9.81  # m/s^2 (Earth gravity for comparison)
    
    # Rover physical specifications
    MASS = 899.0  # kg (approximate mass of Perseverance rover)
    WHEEL_RADIUS = 0.2667  # m (wheel radius)
    WHEEL_COUNT = 6  # number of wheels
    
    # Battery specifications
    BATTERY_CAPACITY = 42.24  # kWh (42,240 Wh)
    MAX_POWER_CONSUMPTION = 125.0  # W (maximum power draw)
    
    # Motion parameters
    ROLLING_RESISTANCE_COEFF = 0.15  # dimensionless rolling resistance
    MOTOR_EFFICIENCY = 0.85  # motor efficiency (0-1)
    DRIVETRAIN_EFFICIENCY = 0.90  # drivetrain efficiency (0-1)
    
    # Operational parameters
    NOMINAL_VELOCITY = 0.042  # m/s (1.5 cm/s typical rover speed)
    MAX_VELOCITY = 0.045  # m/s (maximum rover speed)
    MIN_VELOCITY = 0.01  # m/s (minimum operational speed)
    
    # Task execution power requirements (W)
    TASK_POWER = {
        'navigation': 50.0,
        'sample_collection': 80.0,
        'drilling': 120.0,
        'imaging': 30.0,
        'spectrometry': 45.0,
        'communication': 25.0,
        'idle': 10.0
    }
    
    # Energy safety margins
    ENERGY_RESERVE_RATIO = 0.20  # Keep 20% battery as reserve
    CRITICAL_ENERGY_THRESHOLD = 0.10  # Critical level at 10%
    
    @classmethod
    def get_available_energy(cls, current_battery_level=1.0):
        """
        Calculate available energy for mission tasks.
        
        Args:
            current_battery_level (float): Current battery level (0-1)
            
        Returns:
            float: Available energy in kWh
        """
        total_energy = cls.BATTERY_CAPACITY * current_battery_level
        reserve_energy = cls.BATTERY_CAPACITY * cls.ENERGY_RESERVE_RATIO
        return max(0, total_energy - reserve_energy)
    
    @classmethod
    def is_critical_energy(cls, current_battery_level):
        """
        Check if rover is in critical energy state.
        
        Args:
            current_battery_level (float): Current battery level (0-1)
            
        Returns:
            bool: True if in critical energy state
        """
        return current_battery_level <= cls.CRITICAL_ENERGY_THRESHOLD