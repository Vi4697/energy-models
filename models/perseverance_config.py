"""
Realistic Perseverance Mars Rover configuration based on actual NASA specifications.
Updated with real-world energy parameters and operational constraints.
"""

class PerseveranceConfig:
    """Configuration class for NASA Perseverance rover with realistic parameters."""
    
    # ========================================
    # POWER SYSTEM (RTG + Battery) - REAL DATA
    # ========================================
    
    # Multi-Mission Radioisotope Thermoelectric Generator (MMRTG)
    RTG_CONTINUOUS_POWER = 110.0  # W (continuous output)
    RTG_DAILY_ENERGY = 2.5  # kWh (2500 Wh per sol)
    RTG_ANNUAL_DEGRADATION = 0.015  # 1.5% per year (optional)
    
    # Battery System (2x Li-Ion batteries)
    BATTERY_TOTAL_CAPACITY = 2.4  # kWh (2400 Wh total)
    BATTERY_USABLE_DOD = 0.53  # 53% depth of discharge allowed
    BATTERY_USABLE_CAPACITY = BATTERY_TOTAL_CAPACITY * BATTERY_USABLE_DOD  # 1.272 kWh
    BATTERY_NOMINAL_VOLTAGE = 28.0  # V
    BATTERY_CAPACITY_AH = 43.0 * 2  # Ah (2 batteries)
    
    # Power System Constraints
    MAX_PEAK_POWER = 900.0  # W (RTG + battery surge combined)
    IDLE_POWER_CONSUMPTION = 40.0  # W (thermal, CPU, avionics baseline)
    
    # Battery State of Charge Management
    BATTERY_MIN_SOC = 0.47  # Never discharge below 47% SoC
    BATTERY_START_SOC = 0.95  # Typical start-of-sol charge (95%)
    OVERNIGHT_RECHARGE_ENERGY = 0.7  # kWh (700 Wh restored overnight)
    OVERNIGHT_RECHARGE_POWER = 75.0  # W (average overnight charging rate)
    
    # ========================================
    # SOL TIMING (Martian Day = 24.6 hours)
    # ========================================
    
    SOL_DURATION_HOURS = 24.6  # Earth hours per Martian sol
    SOL_DURATION_SECONDS = SOL_DURATION_HOURS * 3600  # 88,560 seconds
    
    # Operational time windows
    ACTIVE_OPERATIONS_HOURS = 14.0  # Active task execution window
    OVERNIGHT_RECHARGE_HOURS = 10.6  # Overnight low-power recharge period
    
    # ========================================
    # REALISTIC TASK ENERGY CONSUMPTION - PERSEVERANCE DATA
    # ========================================
    
    # Task definitions with real Perseverance energy requirements
    TASK_LIBRARY = {
        # Mobility tasks
        'drive_50m': {
            'description': 'Drive 50 meters on average terrain',
            'power_watts': 150,
            'duration_minutes': 120,
            'energy_wh': 300,
            'category': 'mobility'
        },
        
        # Science instruments
        'mastcam_panorama': {
            'description': 'Mastcam-Z panoramic imaging (30-50 photos)',
            'power_watts': 20,
            'duration_minutes': 10,
            'energy_wh': 3,
            'category': 'imaging'
        },
        
        'supercam_laser': {
            'description': 'SuperCam laser spectroscopy (1 target)',
            'power_watts': 65,
            'duration_minutes': 5,
            'energy_wh': 5,
            'category': 'spectroscopy'
        },
        
        'pixl_analysis': {
            'description': 'PIXL/SHERLOC contact science analysis',
            'power_watts': 80,
            'duration_minutes': 60,
            'energy_wh': 80,
            'category': 'contact_science'
        },
        
        'drill_core_sample': {
            'description': 'Percussive drilling and core collection',
            'power_watts': 600,
            'duration_minutes': 10,
            'energy_wh': 100,
            'category': 'sampling'
        },
        
        'sample_handling': {
            'description': 'Sample tube sealing and manipulation',
            'power_watts': 40,
            'duration_minutes': 30,
            'energy_wh': 20,
            'category': 'sampling'
        },
        
        'moxie_oxygen': {
            'description': 'MOXIE oxygen production experiment',
            'power_watts': 300,
            'duration_minutes': 60,
            'energy_wh': 300,
            'category': 'experiment'
        },
        
        'weather_reading': {
            'description': 'MEDA environmental monitoring',
            'power_watts': 18,
            'duration_minutes': 15,
            'energy_wh': 5,
            'category': 'monitoring'
        },
        
        'arm_deployment': {
            'description': 'Robotic arm positioning and deployment',
            'power_watts': 30,
            'duration_minutes': 2,
            'energy_wh': 1,
            'category': 'manipulation'
        },
        
        # Communications
        'uhf_transmission': {
            'description': 'UHF data transmission to orbiter (100-150MB)',
            'power_watts': 15,
            'duration_minutes': 10,
            'energy_wh': 3,
            'category': 'communication'
        },
        
        'direct_earth_comm': {
            'description': 'Direct-to-Earth communication (high power)',
            'power_watts': 35,
            'duration_minutes': 20,
            'energy_wh': 12,
            'category': 'communication'
        }
    }
    
    # ========================================
    # PHYSICAL SPECIFICATIONS
    # ========================================
    
    # Rover physical parameters
    MASS = 1025.0  # kg (Perseverance total mass including fuel)
    WHEEL_RADIUS = 0.2675  # m (52.5 cm diameter wheels)
    WHEEL_COUNT = 6
    LENGTH = 2.2  # m
    WIDTH = 3.0  # m
    HEIGHT = 3.4  # m
    
    # Mars environment
    GRAVITY_MARS = 3.71  # m/s²
    ATMOSPHERIC_PRESSURE = 0.6  # kPa (average)
    TEMPERATURE_RANGE = (-90, 20)  # °C (night to day)
    
    # Mobility parameters
    MAX_VELOCITY = 0.042  # m/s (4.2 cm/s - actual Perseverance max speed)
    TYPICAL_VELOCITY = 0.016  # m/s (1.6 cm/s - conservative operational speed)
    ROLLING_RESISTANCE_COEFF = 0.15  # Martian regolith
    
    # Motor and drivetrain
    MOTOR_EFFICIENCY = 0.85
    DRIVETRAIN_EFFICIENCY = 0.90
    
    # ========================================
    # OPERATIONAL CONSTRAINTS
    # ========================================
    
    # Energy management
    ENERGY_RESERVE_RATIO = 0.15  # Keep 15% as operational reserve
    CRITICAL_ENERGY_THRESHOLD = 0.30  # Critical level at 30% SoC
    
    # Task scheduling constraints
    MAX_CONCURRENT_POWER = MAX_PEAK_POWER * 0.9  # 90% of max for safety
    HIGH_POWER_TASK_LIMIT = 2  # Max 2 high-power tasks per sol
    DRIVE_ENERGY_BUDGET_RATIO = 0.60  # Max 60% of daily energy for driving
    
    # Safety margins
    THERMAL_POWER_MARGIN = 50.0  # W reserved for thermal management
    COMMUNICATION_POWER_MARGIN = 20.0  # W reserved for emergency communication
    
    @classmethod
    def get_daily_energy_budget(cls, sol_number=0):
        """
        Calculate total daily energy budget including RTG degradation.
        
        Args:
            sol_number (int): Sol number (for degradation calculation)
            
        Returns:
            float: Daily energy budget in kWh
        """
        years_elapsed = sol_number / 687  # Mars year = 687 sols
        degradation_factor = (1 - cls.RTG_ANNUAL_DEGRADATION) ** years_elapsed
        return cls.RTG_DAILY_ENERGY * degradation_factor
    
    @classmethod
    def get_available_energy(cls, current_soc=None, sol_number=0):
        """
        Calculate available energy for task execution.
        
        Args:
            current_soc (float): Current battery state of charge (0-1)
            sol_number (int): Sol number for RTG degradation
            
        Returns:
            dict: Energy availability breakdown
        """
        if current_soc is None:
            current_soc = cls.BATTERY_START_SOC
            
        # RTG energy for the day
        daily_rtg_energy = cls.get_daily_energy_budget(sol_number)
        
        # Battery energy available
        battery_total = cls.BATTERY_USABLE_CAPACITY * current_soc
        battery_reserve = cls.BATTERY_USABLE_CAPACITY * cls.ENERGY_RESERVE_RATIO
        battery_available = max(0, battery_total - battery_reserve)
        
        # Idle consumption for active operations
        idle_consumption = (cls.IDLE_POWER_CONSUMPTION * cls.ACTIVE_OPERATIONS_HOURS) / 1000  # kWh
        
        # Total available for tasks
        total_available = daily_rtg_energy + battery_available - idle_consumption
        
        return {
            'rtg_daily': daily_rtg_energy,
            'battery_total': battery_total,
            'battery_available': battery_available,
            'idle_consumption': idle_consumption,
            'total_available': max(0, total_available),
            'current_soc': current_soc
        }
    
    @classmethod
    def is_critical_energy(cls, current_soc):
        """Check if rover is in critical energy state."""
        return current_soc <= cls.CRITICAL_ENERGY_THRESHOLD
    
    @classmethod
    def is_task_allowed(cls, task_name, current_soc, current_power_draw=0):
        """
        Check if task can be executed given current energy state.
        
        Args:
            task_name (str): Task identifier
            current_soc (float): Current battery state of charge
            current_power_draw (float): Current power consumption (W)
            
        Returns:
            dict: Task execution feasibility analysis
        """
        if task_name not in cls.TASK_LIBRARY:
            return {'allowed': False, 'reason': 'Unknown task'}
        
        task = cls.TASK_LIBRARY[task_name]
        
        # Check power limit
        total_power = current_power_draw + task['power_watts']
        if total_power > cls.MAX_CONCURRENT_POWER:
            return {'allowed': False, 'reason': 'Exceeds peak power limit'}
        
        # Check energy availability
        energy_budget = cls.get_available_energy(current_soc)
        task_energy_kwh = task['energy_wh'] / 1000
        
        if task_energy_kwh > energy_budget['total_available']:
            return {'allowed': False, 'reason': 'Insufficient energy budget'}
        
        # Check battery SoC after task
        battery_energy_needed = max(0, task_energy_kwh - energy_budget['rtg_daily'] / 24)  # Hourly RTG
        new_soc = current_soc - (battery_energy_needed / cls.BATTERY_USABLE_CAPACITY)
        
        if new_soc < cls.BATTERY_MIN_SOC:
            return {'allowed': False, 'reason': 'Would violate minimum SoC'}
        
        return {
            'allowed': True,
            'energy_required_kwh': task_energy_kwh,
            'power_required_w': task['power_watts'],
            'duration_min': task['duration_minutes'],
            'projected_soc': new_soc
        }
    
    @classmethod
    def simulate_overnight_recharge(cls, current_soc):
        """
        Simulate overnight battery recharge from RTG.
        
        Args:
            current_soc (float): Current battery state of charge
            
        Returns:
            dict: Recharge simulation results
        """
        # Available RTG power for charging (total - idle consumption)
        available_charging_power = cls.RTG_CONTINUOUS_POWER - cls.IDLE_POWER_CONSUMPTION
        
        # Energy available for charging overnight
        max_charge_energy = (available_charging_power * cls.OVERNIGHT_RECHARGE_HOURS) / 1000  # kWh
        
        # Current battery energy
        current_battery_energy = current_soc * cls.BATTERY_USABLE_CAPACITY
        
        # Maximum battery can hold
        max_battery_energy = cls.BATTERY_USABLE_CAPACITY
        
        # Energy that can actually be added
        energy_to_add = min(max_charge_energy, max_battery_energy - current_battery_energy)
        
        # New state of charge
        new_soc = min(1.0, current_soc + (energy_to_add / cls.BATTERY_USABLE_CAPACITY))
        
        return {
            'initial_soc': current_soc,
            'final_soc': new_soc,
            'energy_added_kwh': energy_to_add,
            'charging_hours': cls.OVERNIGHT_RECHARGE_HOURS,
            'charging_power_w': available_charging_power
        }

# Legacy compatibility - map old config to new realistic config
class RoverConfig(PerseveranceConfig):
    """Legacy compatibility wrapper for existing code."""
    
    # Map old attributes to new realistic values
    BATTERY_CAPACITY = PerseveranceConfig.BATTERY_USABLE_CAPACITY
    MAX_POWER_CONSUMPTION = PerseveranceConfig.MAX_PEAK_POWER
    
    TASK_POWER = {
        'navigation': 150,  # Updated to drive power
        'sample_collection': 80,  # PIXL analysis
        'drilling': 600,    # Drill core sample
        'imaging': 20,      # Mastcam
        'spectrometry': 65, # SuperCam
        'communication': 15, # UHF transmission
        'idle': 40          # Realistic idle consumption
    }