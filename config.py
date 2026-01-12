"""
Module: config.py
Description:
    Defines all global constants, configuration parameters, and hyper-parameters for the simulation.
    This acts as the single source of truth for balancing the simulation dynamics.

Implementation Details:
    - System Constants: Screen size, FPS.
    - Colors: RGB tuples for rendering.
    - Simulation Parameters: Resource spawn rates, map dimensions, learning rates.
    - Species Configuration: Base stats (HP, Speed, Diet) for Gorilla, Chimp, and Bonobo.
    - Strategy Registry: Lists of available strategies for foraging, combat, and fleeing.

Dependencies:
    - Imports: pygame (internal usage for colors if needed, though strictly just tuples here).
    - Used By: main.py, entities.py, environment.py, ui.py (Global dependency).
"""

# ============================================================================
# SYSTEM CONSTANTS
# ============================================================================
SCREEN_WIDTH = 1350
SCREEN_HEIGHT = 800
MAP_WIDTH = 800  # Left side for simulation field
INFO_PANEL_WIDTH = 200  # Right side for info panel
STATS_PANEL_WIDTH = 350  # Statistics panel on the far right
FPS = 60

# Visual settings
# Visual settings

# ============================================================================
# COLORS (RGB tuples)
# ============================================================================
# Background
COLOR_BACKGROUND = (245, 235, 220)  # Beige (soil/grass color)
COLOR_PANEL_BG = (50, 50, 50)  # Dark gray

# Species colors
COLOR_GORILLA = (200, 50, 50)  # Red
COLOR_CHIMP = (50, 100, 200)  # Blue
COLOR_BONOBO = (50, 200, 100)  # Green

# Resource colors
COLOR_PLANT = (100, 180, 100)  # Light green
COLOR_MEAT = (180, 100, 100)  # Light red

# UI colors
COLOR_TEXT = (255, 255, 255)  # White
COLOR_OBSTACLE = (100, 80, 60)  # Brown

# Strategy border colors (for visualization)
STRATEGY_COLORS = {
    # Foraging
    'WideView': (255, 255, 0),      # Yellow
    'FastMove': (255, 128, 0),      # Orange
    'RandomWalk': (128, 0, 128),    # Purple
    'Ambush': (64, 64, 64),         # Dark gray
    # Combat
    'Aggressive': (255, 0, 0),      # Red
    'Defensive': (0, 0, 255),       # Blue
    'Group': (0, 255, 0),           # Green
    # Flee
    'Speed': (0, 255, 255),         # Cyan
    'Hide': (128, 128, 0),          # Olive
    'Scatter': (255, 0, 255),       # Magenta
}

# ============================================================================
# SIMULATION PARAMETERS
# ============================================================================
# Resource spawning
RESOURCE_SPAWN_INTERVAL = 60  # frames between spawn attempts (increased from 120)
RESOURCE_MAX_PLANT = 100  # Increased to support population
RESOURCE_MAX_MEAT = 40  # Increased to support population
RESOURCE_PLANT_NUTRITION = 30
RESOURCE_MEAT_NUTRITION = 60

# Learning
LEARNING_RATE = 0.1  # α for strategy probability updates
INTERACTION_RADIUS = 80  # pixels - distance for agent interactions

# Agent metabolism
METABOLISM_RATE = 0.1667/10  # Energy drain per frame (Chimp depletes in 12 seconds)
AGE_INCREMENT = 0.022  # 1 frame = 1/45 years (1 year = 0.75 seconds)

# Initial population
INITIAL_GORILLA_COUNT = 10  # Reduced to prevent overpopulation
INITIAL_CHIMP_COUNT = 10
INITIAL_BONOBO_COUNT = 10

# ============================================================================
# SPECIES CONFIGURATION
# ============================================================================
SPECIES_CONFIG = {
    'Gorilla': {
        'max_hp': 150,
        'max_energy': 100,
        'base_speed': 1.5,
        'attack_power': 12,  # Reduced from 30 (60% reduction for survivability)
        'defense': 20,
        'view_range': 120,
        'max_age': 1800,  # 40 years = 30 seconds
        'diet': ['plant'],  # Plant-only
        'social_recovery': 0.5,  # HP recovery from grooming
        'food_requirement': 40,  # High food needs
        'reproduction_cooldown': 3,  # 2 years (biological age in years)
    },
    'Chimp': {
        'max_hp': 100,
        'max_energy': 120,
        'base_speed': 3.0,
        'attack_power': 10,  # Reduced from 25 (60% reduction for survivability)
        'defense': 10,
        'view_range': 110,
        'max_age': 1575,  # 35 years = 26.25 seconds
        'diet': ['plant', 'meat'],  # Omnivore
        'social_recovery': 0.3,
        'food_requirement': 30,
        'reproduction_cooldown': 2,  # 2 years (biological age in years)
    },
    'Bonobo': {
        'max_hp': 80,
        'max_energy': 110,
        'base_speed': 2.5,
        'attack_power': 6,  # Reduced from 15 (60% reduction for survivability)
        'defense': 15,
        'view_range': 140,
        'max_age': 1800,  # 40 years = 30 seconds
        'diet': ['plant'],  # Plant-only
        'social_recovery': 1.0,  # High social recovery
        'food_requirement': 25,  # Low food needs
        'reproduction_cooldown': 3,  # 3 years (biological age in years)
    },
}

# ============================================================================
# STRATEGY REGISTRY
# ============================================================================
# Foraging Strategies
FORAGING_STRATEGIES = ['WideView', 'FastMove', 'RandomWalk', 'Ambush']

# Combat Strategies
COMBAT_STRATEGIES = ['Aggressive', 'Defensive', 'Group']

# Flee Strategies
FLEE_STRATEGIES = ['Speed', 'Hide', 'Scatter']

# All strategies (for reference)
ALL_STRATEGIES = FORAGING_STRATEGIES + COMBAT_STRATEGIES + FLEE_STRATEGIES

# ============================================================================
# REPRODUCTION CONFIGURATION
# ============================================================================
MIN_REPRODUCTION_AGE = 12  # 12 years (biological age in years)
MATING_RANGE = 100  # Distance in pixels for mating
REPRODUCTION_ENERGY_COST = 0.2  # 20% energy cost for each parent (reduced from 0.3)
REPRODUCTION_HP_COST = 0.1  # 10% HP cost for each parent (reduced from 0.2)
MUTATION_RATE = 0.1  # 10% mutation rate for strategy inheritance

# ============================================================================
# STATISTICS PANEL CONFIGURATION
# ============================================================================
STATS_UPDATE_INTERVAL = 10  # Update statistics every N frames
STATS_BAR_HEIGHT = 8
STATS_BAR_SPACING = 2  # Spacing between species bars
STATS_STRATEGY_SPACING = 10  # Spacing between different strategies
STATS_CATEGORY_SPACING = 20  # Spacing between categories
STATS_SHOW_PERCENTAGES = True
STATS_SHOW_GRID = True

# Statistics bar colors (lighter versions of species colors)
STATS_COLOR_GORILLA = (200, 70, 70)
STATS_COLOR_CHIMP = (70, 120, 200)
STATS_COLOR_BONOBO = (70, 200, 70)

# ============================================================================
# ASSET CONFIGURATION
# ============================================================================
USE_IMAGE = True
IMAGE_PATHS = {
    'Gorilla': 'assets/gorilla.png',
    'Chimp': 'assets/chimp.png',
    'Bonobo': 'assets/bonobo.png',
    'plant': 'assets/plant.png',
    'meat': 'assets/meat.png'
}
