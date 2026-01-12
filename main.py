"""
Module: main.py
Description:
    The entry point of the Primate Society Simulation application.
    Orchestrates the Simulation Loop (Input -> Update -> Render).

Implementation Details:
    - Initialization: Sets up Pygame window, clock, and seeds the random generator.
    - Configuration Screen: Allows users to customize species parameters before starting.
    - Main Loop:
        - Process User Input (Pygame events).
        - Update: Advances Environment and Agent states.
        - Interaction Logic: Handles high-level agent interactions (learning hooks).
        - Render: Calls UI and entity draw methods.
    - Restart Feature: Allows restarting simulation with new configuration.
    - Data Management: Instantiates initial population of Agents.

Dependencies:
    - Imports: pygame, sys, random, config, environment, entities, ui, utils, config_screen.
    - Role: Root controller that binds all other modules together.
"""

import pygame
import sys
import random
from typing import List, Dict, Any

import config
from environment import Environment
from entities import Agent
from ui import UI, StatisticsPanel
from config_screen import ConfigScreen
import utils


def apply_species_config(new_config: Dict[str, Dict[str, Any]]) -> None:
    """
    Apply the species configuration to the global config.

    Args:
        new_config: Updated SPECIES_CONFIG dictionary
    """
    config.SPECIES_CONFIG = new_config


def create_initial_population(environment: Environment) -> List[Agent]:
    """
    Create the initial population of agents.

    Args:
        environment: The environment

    Returns:
        List of Agent objects
    """
    agents = []

    # Create Gorillas
    for _ in range(config.INITIAL_GORILLA_COUNT):
        position = utils.random_position((50, 50, config.MAP_WIDTH - 50, config.SCREEN_HEIGHT - 50))
        agent = Agent('Gorilla', position)
        agents.append(agent)

    # Create Chimps
    for _ in range(config.INITIAL_CHIMP_COUNT):
        position = utils.random_position((50, 50, config.MAP_WIDTH - 50, config.SCREEN_HEIGHT - 50))
        agent = Agent('Chimp', position)
        agents.append(agent)

    # Create Bonobos
    for _ in range(config.INITIAL_BONOBO_COUNT):
        position = utils.random_position((50, 50, config.MAP_WIDTH - 50, config.SCREEN_HEIGHT - 50))
        agent = Agent('Bonobo', position)
        agents.append(agent)

    return agents


def handle_agent_interactions(agents: List[Agent]) -> None:
    """
    Handle interactions between agents (learning).

    Args:
        agents: List of all agents
    """
    alive_agents = [a for a in agents if a.state != 'dead']

    for agent in alive_agents:
        # Find nearby agents
        nearby = []
        for other in alive_agents:
            if other.id != agent.id:
                dist = utils.distance(tuple(agent.position), tuple(other.position))
                if dist <= config.INTERACTION_RADIUS:
                    nearby.append(other)

        # Learn from nearby agents
        for other in nearby:
            agent.learn_from(other)


def handle_reproduction(agents: List[Agent], frame_count: int) -> List[Agent]:
    """
    Handle reproduction between agents.

    Args:
        agents: List of all agents
        frame_count: Current frame count for debug logging

    Returns:
        List of newly born agents
    """
    new_agents = []
    alive_agents = [a for a in agents if a.state != 'dead']

    # Debug: Count reproduction attempts every 10 seconds
    debug_mode = (frame_count % 600 == 0)

    if debug_mode:
        print(f"\n🔬 REPRODUCTION DEBUG (Frame {frame_count}):")
        print(f"  Total alive agents: {len(alive_agents)}")

        # Count by species
        for species in ['Gorilla', 'Chimp', 'Bonobo']:
            species_agents = [a for a in alive_agents if a.species == species]
            can_reproduce_count = sum(1 for a in species_agents if a.can_reproduce())
            print(f"  {species}: {len(species_agents)} alive, {can_reproduce_count} can reproduce")

            # Show details for first agent of each species
            if species_agents:
                species_agents[0].can_reproduce(debug=True)

    # Track which agents have already mated this cycle to avoid double-mating
    mated_this_cycle = set()
    reproduction_attempts = 0
    no_mate_count = 0

    for agent in alive_agents:
        # Skip if already mated this cycle
        if agent.id in mated_this_cycle:
            continue

        # Check if can reproduce
        if agent.can_reproduce():
            reproduction_attempts += 1

            # Find a mate
            mate = agent.find_mate([a for a in alive_agents if a.id not in mated_this_cycle])

            if mate:
                # Create offspring
                child = agent.reproduce(mate)
                new_agents.append(child)

                # Log birth
                print(f"👶 BIRTH | {child.species} #{child.id} | "
                      f"Parents: #{agent.id} & #{mate.id} | "
                      f"Position: ({child.position[0]:.0f}, {child.position[1]:.0f})")

                # Mark both parents as mated this cycle
                mated_this_cycle.add(agent.id)
                mated_this_cycle.add(mate.id)
            else:
                no_mate_count += 1

    if debug_mode and reproduction_attempts > 0:
        print(f"  Reproduction attempts: {reproduction_attempts}")
        print(f"  No mate found: {no_mate_count}")
        print(f"  Successful births: {len(new_agents)}\n")

    return new_agents


def run_simulation(screen: pygame.Surface, clock: pygame.time.Clock) -> str:
    """
    Run the main simulation loop.

    Args:
        screen: Pygame display surface
        clock: Pygame clock

    Returns:
        'restart' if user wants to restart, 'quit' otherwise
    """
    # Reset Agent ID counter for new simulation
    Agent._next_id = 0

    # Create environment
    environment = Environment(config.MAP_WIDTH, config.SCREEN_HEIGHT)

    # Create initial population
    agents = create_initial_population(environment)

    # Create UI
    ui = UI(screen)
    stats_panel = StatisticsPanel(screen)

    # Simulation state
    running = True
    paused = False
    frame_count = 0
    selected_agent = None  # Currently selected agent for observation

    # Main loop
    while running:
        # Event processing
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'quit'
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    # Ctrl+R to restart
                    return 'restart'
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle agent selection with mouse click
                mouse_x, mouse_y = event.pos
                # Only check clicks in the simulation area (not panel)
                if mouse_x < config.MAP_WIDTH:
                    # Find closest agent to click
                    closest_agent = None
                    min_distance = 30  # Maximum click distance
                    for agent in agents:
                        if agent.state != 'dead':
                            dist = utils.distance((mouse_x, mouse_y), tuple(agent.position))
                            if dist < min_distance:
                                min_distance = dist
                                closest_agent = agent
                    selected_agent = closest_agent

        # Update (if not paused)
        if not paused:
            # Update environment
            environment.update()

            # Update all agents
            for agent in agents:
                if agent.state != 'dead':
                    agent.update(environment, agents)

            # Handle agent interactions (learning)
            if frame_count % 30 == 0:  # Check interactions every 30 frames for performance
                handle_agent_interactions(agents)

            # Handle reproduction
            if frame_count % 60 == 0:  # Check reproduction every 60 frames (1 second)
                new_agents = handle_reproduction(agents, frame_count)
                agents.extend(new_agents)

            # Update statistics panel
            stats_panel.update(agents)

            frame_count += 1

        # Render
        ui.draw_background()
        environment.draw(screen)
        ui.draw_agents(agents, selected_agent)

        # Calculate FPS
        fps = clock.get_fps()
        ui.draw_panel(agents, fps, frame_count)

        # Draw species statistics
        ui.draw_species_statistics(agents)

        # Draw statistics panel
        stats_panel.draw()

        # Draw selected agent popup
        ui.draw_selected_agent_popup(selected_agent)

        # Optional: Draw debug info
        # ui.draw_debug_info(agents)

        # Update display
        pygame.display.flip()

        # Cap frame rate
        clock.tick(config.FPS)

    return 'quit'


def main():
    """Main entry point for the simulation."""
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("Primate Society Simulation")
    clock = pygame.time.Clock()

    # Seed random number generator
    random.seed()

    # Main application loop
    while True:
        # Show configuration screen
        config_screen = ConfigScreen(screen)
        status, new_config = config_screen.run()

        if status == 'quit':
            break

        # Apply configuration
        if new_config:
            apply_species_config(new_config)

        # Run simulation
        result = run_simulation(screen, clock)

        if result == 'quit':
            break
        # If result is 'restart', loop continues and shows config screen again

    # Cleanup
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
