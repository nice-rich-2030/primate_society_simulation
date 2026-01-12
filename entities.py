"""
Module: entities.py
Description:
    Defines the Primate Agents and their behavioral logic.
    Implements the core AI using State Machines, Strategy Pattern, and Reinforcement Learning.

Implementation Details:
    - Strategy Pattern: Abstract base class and concrete implementations for Foraging, Combat, Fleeing.
    - Agent Class:
        - Maintains state (HP, Energy, Position).
        - Holds Probability Distributions for strategies.
        - Finite State Machine (decision making loop).
        - Reinforcement Learning: update strategy probabilities based on interaction with "fitter" peers.

Dependencies:
    - Imports: pygame, random, math, config.py, utils.py.
    - Used By: main.py (manages list of agents).
"""

import pygame
import random
import math
from typing import Tuple, List, Dict, Optional
import config
import utils


# ============================================================================
# STRATEGY PATTERN - Abstract Base and Concrete Implementations
# ============================================================================

class Strategy:
    """Abstract base class for all strategies."""

    def execute(self, agent: 'Agent', environment, other_agents: List['Agent']) -> None:
        """
        Execute the strategy.

        Args:
            agent: The agent executing this strategy
            environment: The environment
            other_agents: List of all other agents
        """
        raise NotImplementedError("Subclasses must implement execute()")


# ============================================================================
# FORAGING STRATEGIES
# ============================================================================

class WideViewStrategy(Strategy):
    """Wide field of view, slower movement."""

    def execute(self, agent: 'Agent', environment, other_agents: List['Agent']) -> None:
        # Increase view range, decrease speed
        view_range = agent.config['view_range'] * 1.5
        speed_multiplier = 0.7

        # Find nearest food
        resources = environment.get_resources_in_range(agent.position, view_range)
        edible = [r for r in resources if r.resource_type in agent.config['diet']]

        if edible:
            target = min(edible, key=lambda r: utils.distance(agent.position, r.position))
            agent.move_towards(target.position, speed_multiplier)
        else:
            agent.wander(speed_multiplier)


class FastMoveStrategy(Strategy):
    """Fast movement, narrow field of view."""

    def execute(self, agent: 'Agent', environment, other_agents: List['Agent']) -> None:
        # Decrease view range, increase speed
        view_range = agent.config['view_range'] * 0.6
        speed_multiplier = 1.5

        resources = environment.get_resources_in_range(agent.position, view_range)
        edible = [r for r in resources if r.resource_type in agent.config['diet']]

        if edible:
            target = min(edible, key=lambda r: utils.distance(agent.position, r.position))
            agent.move_towards(target.position, speed_multiplier)
        else:
            agent.wander(speed_multiplier)


class RandomWalkStrategy(Strategy):
    """High randomness in movement."""

    def execute(self, agent: 'Agent', environment, other_agents: List['Agent']) -> None:
        # Random walk with occasional target seeking
        if random.random() < 0.3:
            resources = environment.get_resources_in_range(agent.position, agent.config['view_range'])
            edible = [r for r in resources if r.resource_type in agent.config['diet']]
            if edible:
                target = random.choice(edible)
                agent.move_towards(target.position, 1.0)
                return

        agent.wander(1.0)


class AmbushStrategy(Strategy):
    """Wait in place, minimal movement."""

    def execute(self, agent: 'Agent', environment, other_agents: List['Agent']) -> None:
        # Only move if food is very close
        view_range = agent.config['view_range'] * 0.4
        resources = environment.get_resources_in_range(agent.position, view_range)
        edible = [r for r in resources if r.resource_type in agent.config['diet']]

        if edible:
            target = min(edible, key=lambda r: utils.distance(agent.position, r.position))
            agent.move_towards(target.position, 0.5)
        # Otherwise, stay put


# ============================================================================
# COMBAT STRATEGIES (placeholders for now)
# ============================================================================

class AggressiveStrategy(Strategy):
    """Aggressive combat - high damage, high risk."""

    def execute(self, agent: 'Agent', environment, other_agents: List['Agent']) -> None:
        # Find nearby enemies
        enemies = [a for a in other_agents
                   if a.state != 'dead'
                   and a.species != agent.species
                   and utils.distance(tuple(agent.position), tuple(a.position)) < 100]

        if not enemies:
            return

        # Target the weakest enemy
        target = min(enemies, key=lambda e: e.hp)
        dist_to_target = utils.distance(tuple(agent.position), tuple(target.position))

        # Approach target
        if dist_to_target > 20:
            agent.move_towards(tuple(target.position), 1.5)
        else:
            # Attack with high damage
            damage = agent.config['attack_power'] * 1.5
            target.hp -= damage
            target.state = 'fleeing'
            target.threat_position = tuple(agent.position)
            target.last_attacker = agent  # Record attacker for defensive counter

            # Track attack
            agent.stats['attacks'] += 1

            # Take counter damage (high risk)
            counter_damage = target.config['attack_power'] * 0.5
            agent.hp -= counter_damage

            # High energy cost
            agent.energy -= 2.0


class DefensiveStrategy(Strategy):
    """Defensive combat - counter attacks with low risk."""

    def execute(self, agent: 'Agent', environment, other_agents: List['Agent']) -> None:
        # Only attack if recently attacked
        if hasattr(agent, 'last_attacker') and agent.last_attacker:
            target = agent.last_attacker
            if target.state == 'dead':
                agent.last_attacker = None
                return

            dist_to_target = utils.distance(tuple(agent.position), tuple(target.position))

            # Move towards attacker for counter
            if dist_to_target > 20:
                agent.move_towards(tuple(target.position), 1.0)
            else:
                # Counter attack with defense bonus
                defense_bonus = agent.config['defense']
                damage = agent.config['attack_power'] * 0.8 + defense_bonus
                target.hp -= damage

                # Track attack
                agent.stats['attacks'] += 1

                # Low counter damage (defensive stance)
                counter_damage = target.config['attack_power'] * 0.2
                agent.hp -= counter_damage

                # Medium energy cost
                agent.energy -= 1.0

                # Clear attacker after counter
                agent.last_attacker = None


class GroupStrategy(Strategy):
    """Group combat - coordinate with allies for bonus damage."""

    def execute(self, agent: 'Agent', environment, other_agents: List['Agent']) -> None:
        # Find nearby allies (same species)
        allies = [a for a in other_agents
                  if a.state != 'dead'
                  and a.species == agent.species
                  and utils.distance(tuple(agent.position), tuple(a.position)) < 150]

        # Find nearby enemies
        enemies = [a for a in other_agents
                   if a.state != 'dead'
                   and a.species != agent.species
                   and utils.distance(tuple(agent.position), tuple(a.position)) < 100]

        if not enemies or len(allies) < 2:
            return

        # Target nearest enemy
        target = min(enemies, key=lambda e: utils.distance(tuple(agent.position), tuple(e.position)))
        dist_to_target = utils.distance(tuple(agent.position), tuple(target.position))

        # Approach target
        if dist_to_target > 20:
            agent.move_towards(tuple(target.position), 1.2)
        else:
            # Group bonus damage (more allies = more damage)
            group_bonus = min(len(allies), 5) * 0.3
            damage = agent.config['attack_power'] * (1.0 + group_bonus)
            target.hp -= damage
            target.state = 'fleeing'
            target.threat_position = tuple(agent.position)
            target.last_attacker = agent  # Record attacker

            # Track attack
            agent.stats['attacks'] += 1

            # Distributed counter damage
            counter_damage = target.config['attack_power'] * 0.3
            agent.hp -= counter_damage

            # Share energy cost with allies
            agent.energy -= 1.5
            for ally in allies[:2]:
                ally.energy -= 0.5


# ============================================================================
# FLEE STRATEGIES (placeholders for now)
# ============================================================================

class SpeedStrategy(Strategy):
    """Flee at maximum speed in straight line."""

    def execute(self, agent: 'Agent', environment, other_agents: List['Agent']) -> None:
        # Move away from threats at maximum speed
        if hasattr(agent, 'threat_position') and agent.threat_position:
            direction = utils.sub(tuple(agent.position), agent.threat_position)
            normalized = utils.normalize(direction)
            agent.velocity = list(utils.scale(normalized, agent.config['base_speed'] * 2.0))

            # High energy cost
            agent.energy -= 0.3

            # Track escape
            if not hasattr(agent, '_escape_counted'):
                agent.stats['escapes'] += 1
                agent._escape_counted = True


class HideStrategy(Strategy):
    """Hide behind obstacles."""

    def execute(self, agent: 'Agent', environment, other_agents: List['Agent']) -> None:
        # Find nearest obstacle and move towards it
        if environment.obstacles and hasattr(agent, 'threat_position') and agent.threat_position:
            nearest = min(environment.obstacles,
                         key=lambda o: utils.distance(tuple(agent.position), (o.centerx, o.centery)))

            # Calculate position behind obstacle (opposite side from threat)
            threat_to_obstacle = utils.sub(
                (nearest.centerx, nearest.centery),
                agent.threat_position
            )
            normalized = utils.normalize(threat_to_obstacle)
            hide_pos = utils.add(
                (nearest.centerx, nearest.centery),
                utils.scale(normalized, 30)
            )

            agent.move_towards(hide_pos, 1.5)

            # Low energy cost when hiding
            if utils.distance(tuple(agent.position), hide_pos) < 15:
                agent.velocity = [0, 0]
                agent.energy -= 0.05
            else:
                agent.energy -= 0.15

            # Track escape
            if not hasattr(agent, '_escape_counted'):
                agent.stats['escapes'] += 1
                agent._escape_counted = True


class ScatterStrategy(Strategy):
    """Unpredictable fleeing pattern with zigzag movement."""

    def execute(self, agent: 'Agent', environment, other_agents: List['Agent']) -> None:
        # Random direction changes for unpredictable movement
        if random.random() < 0.3:
            angle = random.uniform(0, 2 * math.pi)
            direction = (math.cos(angle), math.sin(angle))

            # Bias towards moving away from threat
            if hasattr(agent, 'threat_position') and agent.threat_position:
                escape_dir = utils.normalize(
                    utils.sub(tuple(agent.position), agent.threat_position)
                )
                # Mix random and escape direction
                direction = (
                    (direction[0] + escape_dir[0]) / 2,
                    (direction[1] + escape_dir[1]) / 2
                )
                normalized = utils.normalize(direction)
            else:
                normalized = utils.normalize(direction)

            agent.velocity = list(utils.scale(normalized, agent.config['base_speed'] * 1.5))
            agent.energy -= 0.2

            # Track escape
            if not hasattr(agent, '_escape_counted'):
                agent.stats['escapes'] += 1
                agent._escape_counted = True


# ============================================================================
# STRATEGY REGISTRY
# ============================================================================

STRATEGY_MAP = {
    'WideView': WideViewStrategy(),
    'FastMove': FastMoveStrategy(),
    'RandomWalk': RandomWalkStrategy(),
    'Ambush': AmbushStrategy(),
    'Aggressive': AggressiveStrategy(),
    'Defensive': DefensiveStrategy(),
    'Group': GroupStrategy(),
    'Speed': SpeedStrategy(),
    'Hide': HideStrategy(),
    'Scatter': ScatterStrategy(),
}


# ============================================================================
# AGENT CLASS
# ============================================================================

class Agent:
    """
    Represents a primate agent with AI behaviors, state machine, and learning.

    Attributes:
        id: Unique identifier
        species: 'Gorilla', 'Chimp', or 'Bonobo'
        position: (x, y) coordinates
        velocity: (vx, vy) movement vector
        hp: Current health points
        max_hp: Maximum health points
        energy: Current energy (hunger)
        max_energy: Maximum energy
        age: Age in simulation time units
        state: Current state ('idle', 'foraging', 'fleeing', 'fighting')
        config: Species configuration from SPECIES_CONFIG
        hunger_threshold: Percentage of energy that triggers foraging
        strategy_probs: Probability distributions for each strategy type
        current_foraging_strategy: Currently active foraging strategy name
        target_resource: Current target resource (if any)
    """

    _next_id = 0

    def __init__(self, species: str, position: Tuple[float, float]):
        """
        Initialize an agent.

        Args:
            species: Species name ('Gorilla', 'Chimp', 'Bonobo')
            position: Starting position (x, y)
        """
        self.id = Agent._next_id
        Agent._next_id += 1

        self.species = species
        self.position = list(position)  # Mutable for easier updates
        self.velocity = [0.0, 0.0]

        # Load species configuration
        self.config = config.SPECIES_CONFIG[species]

        # Initialize stats
        self.max_hp = self.config['max_hp']
        self.hp = self.max_hp
        self.max_energy = self.config['max_energy']
        self.energy = self.max_energy
        self.age = 0.0

        # State machine
        self.state = 'idle'

        # Random hunger threshold (20-80%)
        self.hunger_threshold = random.uniform(0.2, 0.8)

        # Initialize strategy probability distributions with random values
        self.strategy_probs = {
            'foraging': {},
            'combat': {},
            'flee': {},
        }
        self._initialize_random_strategy_probs()

        # Current strategy
        self.current_foraging_strategy = self.pick_strategy('foraging')
        self.current_combat_strategy = self.pick_strategy('combat')
        self.current_flee_strategy = self.pick_strategy('flee')

        # Target tracking
        self.target_resource = None
        self.wander_target = None

        # Combat and flee tracking
        self.threat_position = None  # Position of current threat
        self.last_attacker = None     # Last agent that attacked this one

        # Statistics tracking
        self.stats = {
            'communications': 0,  # Number of learning interactions
            'attacks': 0,         # Number of attacks
            'meals': 0,           # Number of times eaten
            'escapes': 0,         # Number of times fled
            'offspring': 0,       # Number of children produced
        }

        # Reproduction tracking
        self.time_since_last_reproduction = 0  # Frames since last reproduction
        self.total_offspring = 0  # Lifetime offspring count

    def _initialize_random_strategy_probs(self) -> None:
        """
        Initialize strategy probabilities with random values that sum to 1.0.
        This creates diversity in initial agent behaviors for better learning.
        """
        def random_distribution(n: int) -> list:
            """Generate n random values that sum to 1.0."""
            # Generate random values
            raw = [random.random() for _ in range(n)]
            # Normalize to sum to 1.0
            total = sum(raw)
            return [x / total for x in raw]

        # Foraging strategies (4 strategies)
        foraging_dist = random_distribution(len(config.FORAGING_STRATEGIES))
        self.strategy_probs['foraging'] = {
            strategy: prob
            for strategy, prob in zip(config.FORAGING_STRATEGIES, foraging_dist)
        }

        # Combat strategies (3 strategies)
        combat_dist = random_distribution(len(config.COMBAT_STRATEGIES))
        self.strategy_probs['combat'] = {
            strategy: prob
            for strategy, prob in zip(config.COMBAT_STRATEGIES, combat_dist)
        }

        # Flee strategies (3 strategies)
        flee_dist = random_distribution(len(config.FLEE_STRATEGIES))
        self.strategy_probs['flee'] = {
            strategy: prob
            for strategy, prob in zip(config.FLEE_STRATEGIES, flee_dist)
        }

    def pick_strategy(self, context: str) -> str:
        """
        Pick a strategy based on probability distribution.

        Args:
            context: 'foraging', 'combat', or 'flee'

        Returns:
            Strategy name
        """
        strategies = list(self.strategy_probs[context].keys())
        probabilities = list(self.strategy_probs[context].values())
        return random.choices(strategies, weights=probabilities, k=1)[0]

    def calculate_fitness(self) -> float:
        """
        Calculate fitness score for learning.

        Returns:
            Fitness value (0-2, higher is better)
        """
        hp_ratio = self.hp / self.max_hp
        energy_ratio = self.energy / self.max_energy
        return hp_ratio + energy_ratio

    def learn_from(self, teacher: 'Agent') -> None:
        """
        Learn strategies from a fitter agent.

        Args:
            teacher: Agent to learn from
        """
        # Only learn if teacher is fitter
        if teacher.calculate_fitness() <= self.calculate_fitness():
            return

        alpha = config.LEARNING_RATE

        # Update strategy probabilities
        for context in ['foraging', 'combat', 'flee']:
            for strategy in self.strategy_probs[context]:
                self_prob = self.strategy_probs[context][strategy]
                teacher_prob = teacher.strategy_probs[context][strategy]
                # P_self ← (1 - α) * P_self + α * P_teacher
                self.strategy_probs[context][strategy] = (1 - alpha) * self_prob + alpha * teacher_prob

        # Update hunger threshold
        self.hunger_threshold = (1 - alpha) * self.hunger_threshold + alpha * teacher.hunger_threshold

        # Track communication
        self.stats['communications'] += 1

    def can_reproduce(self, debug=False) -> bool:
        """
        Check if agent can reproduce.

        Args:
            debug: If True, print debug information

        Returns:
            True if agent meets all reproduction conditions
        """
        alive = self.state != 'dead'
        mature = self.age > config.MIN_REPRODUCTION_AGE and self.age < config.MIN_REPRODUCTION_AGE + 10 #10年間だけ
        has_energy = self.energy > self.max_energy * 0.4
        has_hp = self.hp > self.max_hp * 0.4
        cooldown_passed = self.time_since_last_reproduction > self.config['reproduction_cooldown']

        if debug:
            print(f"  🔍 {self.species} #{self.id} reproduce check:")
            print(f"    - Alive: {alive} | Mature: {mature} (age={self.age:.0f}/{config.MIN_REPRODUCTION_AGE})")
            print(f"    - Energy: {has_energy} ({self.energy:.0f}/{self.max_energy:.0f} = {self.energy/self.max_energy*100:.1f}%)")
            print(f"    - HP: {has_hp} ({self.hp:.0f}/{self.max_hp:.0f} = {self.hp/self.max_hp*100:.1f}%)")
            print(f"    - Cooldown: {cooldown_passed} (time={self.time_since_last_reproduction}/{self.config['reproduction_cooldown']})")

        return alive and mature and has_energy and has_hp and cooldown_passed

    def find_mate(self, other_agents: List['Agent']) -> Optional['Agent']:
        """
        Find a suitable mate from nearby agents.

        Args:
            other_agents: List of all other agents

        Returns:
            Suitable mate or None if not found
        """
        potential_mates = [
            agent for agent in other_agents
            if (agent.species == self.species and  # Same species
                agent.id != self.id and  # Not self
                agent.state != 'dead' and  # Alive
                agent.can_reproduce() and  # Can reproduce
                utils.distance(tuple(self.position), tuple(agent.position)) < config.MATING_RANGE)
        ]

        return random.choice(potential_mates) if potential_mates else None

    def reproduce(self, mate: 'Agent') -> 'Agent':
        """
        Reproduce with a mate to create offspring.

        Args:
            mate: The other parent

        Returns:
            New Agent (offspring)
        """
        # Child position near parents
        child_position = (
            (self.position[0] + mate.position[0]) / 2 + random.uniform(-30, 30),
            (self.position[1] + mate.position[1]) / 2 + random.uniform(-30, 30)
        )

        # Clamp to map boundaries
        child_position = (
            utils.clamp(child_position[0], 20, config.MAP_WIDTH - 20),
            utils.clamp(child_position[1], 20, config.SCREEN_HEIGHT - 20)
        )

        # Create offspring
        child = Agent(self.species, child_position)

        # Inherit strategies from parents with mutation
        for context in ['foraging', 'combat', 'flee']:
            for strategy in child.strategy_probs[context]:
                # Average parent probabilities
                parent_avg = (
                    self.strategy_probs[context][strategy] +
                    mate.strategy_probs[context][strategy]
                ) / 2

                # Add mutation
                mutation = random.uniform(-config.MUTATION_RATE, config.MUTATION_RATE)
                child.strategy_probs[context][strategy] = max(0, parent_avg + mutation)

            # Normalize to sum to 1.0
            total = sum(child.strategy_probs[context].values())
            if total > 0:
                for strategy in child.strategy_probs[context]:
                    child.strategy_probs[context][strategy] /= total

        # Inherit hunger threshold with mutation
        parent_avg_hunger = (self.hunger_threshold + mate.hunger_threshold) / 2
        mutation = random.uniform(-0.1, 0.1)
        child.hunger_threshold = utils.clamp(parent_avg_hunger + mutation, 0.2, 0.8)

        # Re-pick strategies based on new probabilities
        child.current_foraging_strategy = child.pick_strategy('foraging')
        child.current_combat_strategy = child.pick_strategy('combat')
        child.current_flee_strategy = child.pick_strategy('flee')

        # Parents pay reproduction cost
        self.energy -= self.max_energy * config.REPRODUCTION_ENERGY_COST
        self.hp -= self.max_hp * config.REPRODUCTION_HP_COST
        mate.energy -= mate.max_energy * config.REPRODUCTION_ENERGY_COST
        mate.hp -= mate.max_hp * config.REPRODUCTION_HP_COST

        # Reset reproduction timers
        self.time_since_last_reproduction = 0
        mate.time_since_last_reproduction = 0

        # Update statistics
        self.total_offspring += 1
        mate.total_offspring += 1
        self.stats['offspring'] += 1
        mate.stats['offspring'] += 1

        return child

    def move_towards(self, target: Tuple[float, float], speed_multiplier: float = 1.0) -> None:
        """
        Move towards a target position.

        Args:
            target: Target position (x, y)
            speed_multiplier: Speed modifier
        """
        direction = utils.sub(target, tuple(self.position))
        normalized = utils.normalize(direction)
        speed = self.config['base_speed'] * speed_multiplier
        self.velocity = list(utils.scale(normalized, speed))

    def wander(self, speed_multiplier: float = 1.0) -> None:
        """
        Random wandering behavior.

        Args:
            speed_multiplier: Speed modifier
        """
        # Pick a new random target occasionally
        if self.wander_target is None or random.random() < 0.05:
            self.wander_target = (
                random.uniform(0, config.MAP_WIDTH),
                random.uniform(0, config.SCREEN_HEIGHT)
            )

        self.move_towards(self.wander_target, speed_multiplier * 0.5)

    def update(self, environment, other_agents: List['Agent']) -> None:
        """
        Update agent state (called each frame).

        Args:
            environment: The environment
            other_agents: List of all other agents
        """
        # Age and metabolism
        self.age += config.AGE_INCREMENT
        self.energy -= config.METABOLISM_RATE

        # Increment reproduction timer (in years, same as age)
        self.time_since_last_reproduction += config.AGE_INCREMENT

        # HP degradation when energy is very low (starvation damage)
        if self.energy < self.max_energy * 0.2:  # Below 20% energy
            starvation_damage = 0.2  # HP loss per frame when starving
            self.hp -= starvation_damage

        # Death conditions
        if self.hp <= 0 or self.energy <= 0 or self.age >= self.config['max_age']:
            # Determine cause of death
            if self.hp <= 0:
                cause = "HP depleted (combat/starvation)"
            elif self.energy <= 0:
                cause = "Energy depleted (starvation)"
            else:
                cause = "Old age"

            # Log death
            age_seconds = self.age / 60  # Convert frames to seconds
            print(f"💀 DEATH | {self.species} #{self.id} | Age: {age_seconds:.1f}s | "
                  f"Cause: {cause} | Offspring: {self.total_offspring} | "
                  f"Meals: {self.stats['meals']} | Attacks: {self.stats['attacks']}")

            self.state = 'dead'
            return

        # State machine logic with priority
        hp_ratio = self.hp / self.max_hp
        energy_ratio = self.energy / self.max_energy

        # Priority 1: Flee if HP is low
        if hp_ratio < 0.3:
            self.state = 'fleeing'
            self.execute_fleeing(environment, other_agents)
        # Priority 2: Fight if conditions are met
        elif self.should_fight(other_agents):
            self.state = 'fighting'
            self.execute_combat(environment, other_agents)
        # Priority 3: Forage if hungry
        elif energy_ratio < self.hunger_threshold:
            self.state = 'foraging'
            self.execute_foraging(environment, other_agents)
        # Priority 4: Idle/wander
        else:
            self.state = 'idle'
            self.wander(0.3)
            # Clear threat if safe
            if hasattr(self, '_escape_counted'):
                delattr(self, '_escape_counted')

        # Apply movement
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]

        # Clamp to boundaries
        self.position[0] = utils.clamp(self.position[0], 0, config.MAP_WIDTH)
        self.position[1] = utils.clamp(self.position[1], 0, config.SCREEN_HEIGHT)

        # Decay velocity
        self.velocity[0] *= 0.9
        self.velocity[1] *= 0.9

    def should_fight(self, other_agents: List['Agent']) -> bool:
        """
        Determine if agent should engage in combat.

        Args:
            other_agents: List of all other agents

        Returns:
            True if should fight, False otherwise
        """
        # Need sufficient energy to fight
        if self.energy < self.max_energy * 0.4:
            return False

        # Check for nearby enemies (within view_range)
        combat_range = self.config['view_range']
        nearby = [a for a in other_agents
                  if a.state != 'dead'
                  and a.species != self.species
                  and utils.distance(tuple(self.position), tuple(a.position)) < combat_range]

        if not nearby:
            return False

        # Fight if significantly stronger than nearest enemy
        nearest_enemy = min(nearby, key=lambda e: utils.distance(tuple(self.position), tuple(e.position)))
        my_fitness = self.calculate_fitness()
        enemy_fitness = nearest_enemy.calculate_fitness()

        # Attack if 20% fitter
        return my_fitness > enemy_fitness * 1.2

    def execute_combat(self, environment, other_agents: List['Agent']) -> None:
        """
        Execute combat behavior using current strategy.

        Args:
            environment: The environment
            other_agents: List of all other agents
        """
        # Pick new strategy occasionally
        if random.random() < 0.05:
            self.current_combat_strategy = self.pick_strategy('combat')

        # Pick combat strategy
        strategy = STRATEGY_MAP[self.current_combat_strategy]
        strategy.execute(self, environment, other_agents)

    def execute_fleeing(self, environment, other_agents: List['Agent']) -> None:
        """
        Execute fleeing behavior using current strategy.

        Args:
            environment: The environment
            other_agents: List of all other agents
        """
        # Calculate threat detection range based on view_range
        # Base: 1.5x view_range, Ambush bonus: 1.3x
        threat_detection_range = self.config['view_range'] * 1.5
        if self.current_foraging_strategy == 'Ambush':
            threat_detection_range *= 1.3

        # Find nearest threat if not already set
        if not self.threat_position:
            enemies = [a for a in other_agents
                       if a.state != 'dead'
                       and a.species != self.species
                       and utils.distance(tuple(self.position), tuple(a.position)) < threat_detection_range]

            if enemies:
                nearest = min(enemies, key=lambda e: utils.distance(tuple(self.position), tuple(e.position)))
                self.threat_position = tuple(nearest.position)

        # Pick new strategy occasionally
        if random.random() < 0.05:
            self.current_flee_strategy = self.pick_strategy('flee')

        # Pick flee strategy and execute
        strategy = STRATEGY_MAP[self.current_flee_strategy]
        strategy.execute(self, environment, other_agents)

        # Check if escaped far enough (2.0x view_range)
        safe_distance = self.config['view_range'] * 2.0
        if self.threat_position:
            if utils.distance(tuple(self.position), self.threat_position) > safe_distance:
                self.threat_position = None

    def execute_foraging(self, environment, other_agents: List['Agent']) -> None:
        """
        Execute foraging behavior using current strategy.

        Args:
            environment: The environment
            other_agents: List of all other agents
        """
        # Pick new strategy occasionally (mutation-like)
        if random.random() < 0.1:
            self.current_foraging_strategy = self.pick_strategy('foraging')

        # Execute strategy
        strategy = STRATEGY_MAP[self.current_foraging_strategy]
        strategy.execute(self, environment, other_agents)

        # Try to eat nearby food
        self.eat(environment)

    def eat(self, environment) -> None:
        """
        Attempt to consume nearby resources.

        Args:
            environment: The environment
        """
        nearby_resources = environment.get_resources_in_range(tuple(self.position), 15)
        edible = [r for r in nearby_resources if r.resource_type in self.config['diet']]

        if edible:
            # Eat the closest one
            resource = min(edible, key=lambda r: utils.distance(tuple(self.position), r.position))
            self.energy = min(self.max_energy, self.energy + resource.amount)
            self.hp = min(self.max_hp, self.hp + resource.amount * 0.5)
            environment.remove_resource(resource)

            # Track meal
            self.stats['meals'] += 1

    def draw(self, surface: pygame.Surface, selected: bool = False) -> None:
        """
        Draw the agent on the surface.

        Args:
            surface: Pygame surface to draw on
            selected: Whether this agent is selected
        """
        if hasattr(config, 'USE_IMAGE') and config.USE_IMAGE:
            self._draw_image(surface, selected)
        else:
            self._draw_circle(surface, selected)

    def _draw_image(self, surface: pygame.Surface, selected: bool) -> None:
        """Draw agent using loaded image."""
        if not hasattr(Agent, '_images'):
            Agent._images = {}
        
        # Load image if not cached
        if self.species not in Agent._images:
            try:
                path = config.IMAGE_PATHS[self.species]
                # Load and scale
                img = pygame.image.load(path).convert_alpha()
                # Scale based on max HP or fixed size? Fixed size 32x32 is good
                img = pygame.transform.scale(img, (32, 32))
                Agent._images[self.species] = img
            except Exception as e:
                print(f"Error loading image for {self.species}: {e}")
                # Fallback
                self._draw_circle(surface, selected)
                return

        image = Agent._images[self.species]
        rect = image.get_rect(center=(int(self.position[0]), int(self.position[1])))
        surface.blit(image, rect)

        # Draw strategy indicator (ring around image)
        if self.state == 'foraging' and self.current_foraging_strategy in config.STRATEGY_COLORS:
            border_color = config.STRATEGY_COLORS[self.current_foraging_strategy]
            pygame.draw.circle(surface, border_color, (int(self.position[0]), int(self.position[1])), 18, 2)

        # Draw selection indicator
        if selected:
            pygame.draw.rect(surface, (255, 255, 255), rect.inflate(4, 4), 2)

        # Health bar (tiny)
        hp_ratio = self.hp / self.max_hp
        bar_width = 24
        bar_height = 3
        bar_x = self.position[0] - bar_width // 2
        bar_y = self.position[1] - 20
        pygame.draw.rect(surface, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, bar_width * hp_ratio, bar_height))

    def _draw_circle(self, surface: pygame.Surface, selected: bool) -> None:
        """Draw agent as a circle (fallback mode)."""
        # Species color
        if self.species == 'Gorilla':
            color = config.COLOR_GORILLA
        elif self.species == 'Chimp':
            color = config.COLOR_CHIMP
        else:
            color = config.COLOR_BONOBO

        # Size based on health
        base_radius = 8
        health_ratio = self.hp / self.max_hp
        radius = int(base_radius * (0.5 + 0.5 * health_ratio))

        # Draw agent body
        pygame.draw.circle(surface, color, (int(self.position[0]), int(self.position[1])), radius)

        # Draw border indicating current strategy
        if self.state == 'foraging' and self.current_foraging_strategy in config.STRATEGY_COLORS:
            border_color = config.STRATEGY_COLORS[self.current_foraging_strategy]
            pygame.draw.circle(surface, border_color, (int(self.position[0]), int(self.position[1])), radius + 2, 2)

        # Draw selection indicator
        if selected:
            pygame.draw.circle(surface, (255, 255, 255), (int(self.position[0]), int(self.position[1])), radius + 4, 3)


