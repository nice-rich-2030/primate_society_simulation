"""
Module: ui.py
Description:
    Handles all rendering operations that are overlays or specialized visualizations.
    Manages the Heads-Up Display (HUD) and statistics panel.

Implementation Details:
    - UI Class:
        - Helper methods to draw background and grid lines.
        - `draw_agents`: Rendering agents with species-specific colors and status indicators.
        - `draw_panel`: Rendering text statistics (population counts, simulation info).

Dependencies:
    - Imports: pygame, config.py.
    - Used By: main.py (called in the render loop).
"""

import pygame
from typing import List
import config


class UI:
    """
    Manages all UI rendering including HUD, panels, and overlays.

    Attributes:
        screen: Pygame display surface
        font: Font for text rendering
        font_small: Smaller font for details
    """

    def __init__(self, screen: pygame.Surface):
        """
        Initialize the UI system.

        Args:
            screen: Pygame display surface
        """
        self.screen = screen
        pygame.font.init()
        self.font = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 20)

    def draw_background(self) -> None:
        """Draw the background for the simulation area."""
        # Main simulation area
        self.screen.fill(config.COLOR_BACKGROUND, rect=(0, 0, config.MAP_WIDTH, config.SCREEN_HEIGHT))

        # Info panel on the right
        self.screen.fill(config.COLOR_PANEL_BG, rect=(config.MAP_WIDTH, 0, config.INFO_PANEL_WIDTH, config.SCREEN_HEIGHT))

        # Statistics panel on the far right
        self.screen.fill(config.COLOR_PANEL_BG, rect=(config.MAP_WIDTH + config.INFO_PANEL_WIDTH, 0, config.STATS_PANEL_WIDTH, config.SCREEN_HEIGHT))

    def draw_agents(self, agents: List, selected_agent=None) -> None:
        """
        Draw all agents on the screen.

        Args:
            agents: List of Agent objects
            selected_agent: Currently selected agent (if any)
        """
        for agent in agents:
            if agent.state != 'dead':
                is_selected = (selected_agent is not None and agent.id == selected_agent.id)
                agent.draw(self.screen, selected=is_selected)

    def draw_panel(self, agents: List, fps: float, frame_count: int) -> None:
        """
        Draw the information panel on the right side.

        Args:
            agents: List of all agents
            fps: Current frames per second
            frame_count: Total frame count
        """
        panel_x = config.MAP_WIDTH + 10
        y_offset = 20

        # Title
        title = self.font.render("Primate Society", True, config.COLOR_TEXT)
        self.screen.blit(title, (panel_x, y_offset))
        y_offset += 40

        # FPS
        fps_text = self.font_small.render(f"FPS: {fps:.1f}", True, config.COLOR_TEXT)
        self.screen.blit(fps_text, (panel_x, y_offset))
        y_offset += 25

        # Frame count
        frame_text = self.font_small.render(f"Frame: {frame_count}", True, config.COLOR_TEXT)
        self.screen.blit(frame_text, (panel_x, y_offset))
        y_offset += 35

        # Population counts
        pop_title = self.font.render("Population", True, config.COLOR_TEXT)
        self.screen.blit(pop_title, (panel_x, y_offset))
        y_offset += 30

        # Count each species
        gorilla_count = sum(1 for a in agents if a.species == 'Gorilla' and a.state != 'dead')
        chimp_count = sum(1 for a in agents if a.species == 'Chimp' and a.state != 'dead')
        bonobo_count = sum(1 for a in agents if a.species == 'Bonobo' and a.state != 'dead')
        total_count = gorilla_count + chimp_count + bonobo_count

        # Draw colored squares and counts
        # Gorilla
        pygame.draw.rect(self.screen, config.COLOR_GORILLA, (panel_x, y_offset, 15, 15))
        gorilla_text = self.font_small.render(f"Gorilla: {gorilla_count}", True, config.COLOR_TEXT)
        self.screen.blit(gorilla_text, (panel_x + 20, y_offset))
        y_offset += 25

        # Chimp
        pygame.draw.rect(self.screen, config.COLOR_CHIMP, (panel_x, y_offset, 15, 15))
        chimp_text = self.font_small.render(f"Chimp: {chimp_count}", True, config.COLOR_TEXT)
        self.screen.blit(chimp_text, (panel_x + 20, y_offset))
        y_offset += 25

        # Bonobo
        pygame.draw.rect(self.screen, config.COLOR_BONOBO, (panel_x, y_offset, 15, 15))
        bonobo_text = self.font_small.render(f"Bonobo: {bonobo_count}", True, config.COLOR_TEXT)
        self.screen.blit(bonobo_text, (panel_x + 20, y_offset))
        y_offset += 25

        # Total
        total_text = self.font_small.render(f"Total: {total_count}", True, config.COLOR_TEXT)
        self.screen.blit(total_text, (panel_x, y_offset))
        y_offset += 40

        # Strategy legend
        legend_title = self.font.render("Strategies", True, config.COLOR_TEXT)
        self.screen.blit(legend_title, (panel_x, y_offset))
        y_offset += 30

        # Show foraging strategy colors
        strategies = [
            ('WideView', 'Wide View'),
            ('FastMove', 'Fast Move'),
            ('RandomWalk', 'Random'),
            ('Ambush', 'Ambush'),
        ]

        for strategy_key, strategy_label in strategies:
            color = config.STRATEGY_COLORS.get(strategy_key, (255, 255, 255))
            pygame.draw.circle(self.screen, color, (panel_x + 7, y_offset + 7), 7, 2)
            strategy_text = self.font_small.render(strategy_label, True, config.COLOR_TEXT)
            self.screen.blit(strategy_text, (panel_x + 20, y_offset))
            y_offset += 20

        y_offset += 20

        # Controls
        y_offset += 360

        controls = [
            "ESC: Quit",
            "SPACE: Pause",
        ]

        for control in controls:
            control_text = self.font_small.render(control, True, config.COLOR_TEXT)
            self.screen.blit(control_text, (panel_x, y_offset))
            y_offset += 20

    def draw_species_statistics(self, agents: List) -> None:
        """
        Draw detailed statistics for each species.

        Args:
            agents: List of all agents
        """
        panel_x = config.MAP_WIDTH + 10
        y_offset = 380

        stats_title = self.font.render("Statistics", True, config.COLOR_TEXT)
        self.screen.blit(stats_title, (panel_x, y_offset))
        y_offset += 25

        # Calculate statistics per species
        for species in ['Gorilla', 'Chimp', 'Bonobo']:
            species_agents = [a for a in agents if a.species == species and a.state != 'dead']
            if not species_agents:
                continue

            # Calculate averages
            avg_hp = sum(a.hp for a in species_agents) / len(species_agents)
            avg_energy = sum(a.energy for a in species_agents) / len(species_agents)
            total_hp = sum(a.hp for a in species_agents)

            # Calculate totals for statistics
            total_comms = sum(a.stats['communications'] for a in species_agents)
            total_meals = sum(a.stats['meals'] for a in species_agents)
            total_attacks = sum(a.stats['attacks'] for a in species_agents)
            total_escapes = sum(a.stats['escapes'] for a in species_agents)

            # Most common strategy
            strategies = [a.current_foraging_strategy for a in species_agents]
            if strategies:
                most_common = max(set(strategies), key=strategies.count)
                strategy_short = most_common[:4]
            else:
                strategy_short = "N/A"

            # Draw species name with colored icon
            if species == 'Gorilla':
                icon_color = config.COLOR_GORILLA
                species_name = "Gorilla"
            elif species == 'Chimp':
                icon_color = config.COLOR_CHIMP
                species_name = "Chimp"
            else:
                icon_color = config.COLOR_BONOBO
                species_name = "Bonobo"

            # Draw colored square icon
            pygame.draw.rect(self.screen, icon_color, (panel_x, y_offset, 15, 15))
            species_text = self.font_small.render(species_name, True, config.COLOR_TEXT)
            self.screen.blit(species_text, (panel_x + 20, y_offset))
            y_offset += 18

            # Draw stats
            hp_text = self.font_small.render(f"  HP: {avg_hp:.0f} (Σ{total_hp:.0f})", True, config.COLOR_TEXT)
            self.screen.blit(hp_text, (panel_x, y_offset))
            y_offset += 16

            energy_text = self.font_small.render(f"  Eng: {avg_energy:.0f}", True, config.COLOR_TEXT)
            self.screen.blit(energy_text, (panel_x, y_offset))
            y_offset += 16

            strat_text = self.font_small.render(f"  Top: {strategy_short}", True, config.COLOR_TEXT)
            self.screen.blit(strat_text, (panel_x, y_offset))
            y_offset += 16

            # Draw action statistics - line 1
            actions_text1 = self.font_small.render(f"  Talk:{total_comms} Eat:{total_meals}", True, (180, 180, 255))
            self.screen.blit(actions_text1, (panel_x, y_offset))
            y_offset += 16

            # Draw action statistics - line 2
            actions_text2 = self.font_small.render(f"  Atk:{total_attacks} Flee:{total_escapes}", True, (255, 180, 180))
            self.screen.blit(actions_text2, (panel_x, y_offset))
            y_offset += 16

            # Draw current states distribution
            state_counts = {}
            for a in species_agents:
                state = a.state
                state_counts[state] = state_counts.get(state, 0) + 1

            # Show state distribution (only non-zero states)
            states_display = []
            if state_counts.get('fighting', 0) > 0:
                states_display.append(f"Fi{state_counts['fighting']}")
            if state_counts.get('fleeing', 0) > 0:
                states_display.append(f"Fl{state_counts['fleeing']}")
            if state_counts.get('foraging', 0) > 0:
                states_display.append(f"Fo{state_counts['foraging']}")

            if states_display:
                states_text = self.font_small.render(f"  {' '.join(states_display)}", True, (200, 200, 100))
                self.screen.blit(states_text, (panel_x, y_offset))

            y_offset += 20

    def draw_selected_agent_popup(self, agent) -> None:
        """
        Draw a popup showing detailed information about the selected agent.

        Args:
            agent: Selected agent
        """
        if agent is None or agent.state == 'dead':
            return

        # Popup dimensions
        popup_width = 280
        popup_height = 380
        popup_x = 20
        popup_y = 20

        # Draw semi-transparent background
        popup_surface = pygame.Surface((popup_width, popup_height))
        popup_surface.set_alpha(230)
        popup_surface.fill((30, 30, 30))
        self.screen.blit(popup_surface, (popup_x, popup_y))

        # Draw border
        pygame.draw.rect(self.screen, (255, 255, 255), (popup_x, popup_y, popup_width, popup_height), 2)

        # Content
        x = popup_x + 10
        y = popup_y + 10

        # Title
        title = self.font.render(f"{agent.species} #{agent.id}", True, (255, 255, 100))
        self.screen.blit(title, (x, y))
        y += 30

        # Basic stats
        stats = [
            f"State: {agent.state}",
            f"HP: {agent.hp:.0f}/{agent.max_hp}",
            f"Energy: {agent.energy:.0f}/{agent.max_energy}",
            f"Age: {agent.age:.1f}/{agent.config['max_age']}",
            f"Position: ({agent.position[0]:.0f}, {agent.position[1]:.0f})",
            f"Hunger Threshold: {agent.hunger_threshold*100:.0f}%",
        ]

        for stat in stats:
            text = self.font_small.render(stat, True, config.COLOR_TEXT)
            self.screen.blit(text, (x, y))
            y += 18

        # Strategy probabilities
        y += 10
        strat_title = self.font_small.render("Foraging Strategies:", True, (200, 200, 255))
        self.screen.blit(strat_title, (x, y))
        y += 20

        for strategy, prob in agent.strategy_probs['foraging'].items():
            is_current = (strategy == agent.current_foraging_strategy)
            marker = ">" if is_current else " "
            color = (255, 255, 0) if is_current else config.COLOR_TEXT

            text = self.font_small.render(f"{marker} {strategy}: {prob*100:.1f}%", True, color)
            self.screen.blit(text, (x, y))
            y += 16

        # Fitness
        y += 5
        fitness = agent.calculate_fitness()
        fitness_text = self.font_small.render(f"Fitness: {fitness:.2f}/2.0", True, (150, 255, 150))
        self.screen.blit(fitness_text, (x, y))
        y += 25

        # Action Statistics
        stats_title = self.font_small.render("Actions:", True, (200, 200, 255))
        self.screen.blit(stats_title, (x, y))
        y += 18

        action_stats = [
            f"Communications: {agent.stats['communications']}",
            f"Meals Eaten: {agent.stats['meals']}",
            f"Attacks: {agent.stats['attacks']}",
            f"Escapes: {agent.stats['escapes']}",
        ]

        for stat in action_stats:
            text = self.font_small.render(stat, True, config.COLOR_TEXT)
            self.screen.blit(text, (x, y))
            y += 16

    def draw_debug_info(self, agents: List) -> None:
        """
        Draw debug information about agents (optional).

        Args:
            agents: List of all agents
        """
        # Sample a few agents and show their strategy probabilities
        alive_agents = [a for a in agents if a.state != 'dead']
        if not alive_agents:
            return

        sample_agent = alive_agents[0]

        panel_x = config.MAP_WIDTH + 10
        y_offset = 700

        debug_title = self.font_small.render("Debug (Agent 0)", True, config.COLOR_TEXT)
        self.screen.blit(debug_title, (panel_x, y_offset))
        y_offset += 20

        # Show foraging strategy probabilities
        for strategy, prob in sample_agent.strategy_probs['foraging'].items():
            text = self.font_small.render(f"{strategy[:4]}: {prob:.2f}", True, config.COLOR_TEXT)
            self.screen.blit(text, (panel_x, y_offset))
            y_offset += 18


class StatisticsPanel:
    """
    Displays strategy probability distributions for each species.
    Shows bar charts comparing strategy adoption across Gorilla, Chimp, and Bonobo.
    """

    def __init__(self, screen: pygame.Surface):
        """
        Initialize the statistics panel.

        Args:
            screen: Pygame display surface
        """
        self.screen = screen
        pygame.font.init()
        self.font = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        self.font_tiny = pygame.font.Font(None, 16)

        # Panel position (far right)
        self.x = config.MAP_WIDTH + config.INFO_PANEL_WIDTH
        self.y = 0
        self.width = config.STATS_PANEL_WIDTH
        self.height = config.SCREEN_HEIGHT

        # Update control
        self.update_interval = config.STATS_UPDATE_INTERVAL
        self.frame_counter = 0

        # Species statistics cache
        self.species_stats = {
            'Gorilla': {'foraging': {}, 'combat': {}, 'flee': {}},
            'Chimp': {'foraging': {}, 'combat': {}, 'flee': {}},
            'Bonobo': {'foraging': {}, 'combat': {}, 'flee': {}},
        }

        # Species colors
        self.species_colors = {
            'Gorilla': config.STATS_COLOR_GORILLA,
            'Chimp': config.STATS_COLOR_CHIMP,
            'Bonobo': config.STATS_COLOR_BONOBO,
        }

    def update(self, agents: List) -> None:
        """
        Update statistics (called every frame, but only recalculates periodically).

        Args:
            agents: List of all agents
        """
        self.frame_counter += 1
        if self.frame_counter % self.update_interval == 0:
            self._calculate_species_stats(agents)

    def _calculate_species_stats(self, agents: List) -> None:
        """
        Calculate average strategy probabilities for each species.

        Args:
            agents: List of all agents
        """
        for species in ['Gorilla', 'Chimp', 'Bonobo']:
            species_agents = [a for a in agents if a.species == species and a.state != 'dead']

            if len(species_agents) == 0:
                # No agents of this species - set all probabilities to 0
                for context in ['foraging', 'combat', 'flee']:
                    if context == 'foraging':
                        strategies = config.FORAGING_STRATEGIES
                    elif context == 'combat':
                        strategies = config.COMBAT_STRATEGIES
                    else:
                        strategies = config.FLEE_STRATEGIES

                    for strategy in strategies:
                        self.species_stats[species][context][strategy] = 0.0
            else:
                # Calculate average probabilities
                for context in ['foraging', 'combat', 'flee']:
                    if context == 'foraging':
                        strategies = config.FORAGING_STRATEGIES
                    elif context == 'combat':
                        strategies = config.COMBAT_STRATEGIES
                    else:
                        strategies = config.FLEE_STRATEGIES

                    for strategy in strategies:
                        total_prob = sum(
                            agent.strategy_probs[context].get(strategy, 0.0)
                            for agent in species_agents
                        )
                        avg_prob = total_prob / len(species_agents)
                        self.species_stats[species][context][strategy] = avg_prob

    def draw(self) -> None:
        """Draw the statistics panel with bar charts."""
        x = self.x + 10
        y = 20

        # Title
        title = self.font.render("STRATEGY STATISTICS", True, config.COLOR_TEXT)
        self.screen.blit(title, (x, y))
        y += 30

        # Update info
        update_info = self.font_tiny.render(f"Updated every {self.update_interval} frames", True, (150, 150, 150))
        self.screen.blit(update_info, (x, y))
        y += 25

        # Draw separator line
        pygame.draw.line(self.screen, (100, 100, 100), (x, y), (x + self.width - 20, y), 1)
        y += 15

        # Draw each category
        categories = [
            ('FORAGING', config.FORAGING_STRATEGIES),
            ('COMBAT', config.COMBAT_STRATEGIES),
            ('FLEE', config.FLEE_STRATEGIES),
        ]

        for category_name, strategies in categories:
            y = self._draw_category(x, y, category_name, strategies)
            y += config.STATS_CATEGORY_SPACING

        # Draw legend at the bottom
        y = self.height - 50
        legend = self.font_small.render("Legend:", True, config.COLOR_TEXT)
        self.screen.blit(legend, (x, y))
        y += 20

        species_list = [
            ('Gorilla', config.STATS_COLOR_GORILLA),
            ('Chimp', config.STATS_COLOR_CHIMP),
            ('Bonobo', config.STATS_COLOR_BONOBO),
        ]

        legend_x = x
        for species_name, color in species_list:
            # Draw colored rectangle
            pygame.draw.rect(self.screen, color, (legend_x, y, 15, 10))
            pygame.draw.rect(self.screen, (200, 200, 200), (legend_x, y, 15, 10), 1)

            # Draw species name
            text = self.font_tiny.render(species_name, True, config.COLOR_TEXT)
            self.screen.blit(text, (legend_x + 18, y - 2))

            legend_x += 90

    def _draw_category(self, x: int, y: int, category_name: str, strategies: List[str]) -> int:
        """
        Draw a category section with its strategy bars.

        Args:
            x: X position
            y: Y position
            category_name: Name of the category
            strategies: List of strategy names

        Returns:
            Updated y position
        """
        # Category header
        header = self.font.render(category_name, True, (200, 200, 255))
        self.screen.blit(header, (x, y))
        y += 25

        # Get the context name for accessing stats
        context = category_name.lower()
        if context not in ['foraging', 'combat', 'flee']:
            context = 'foraging'  # Default fallback

        # Draw each strategy with 3 species bars
        for strategy in strategies:
            y = self._draw_strategy_bars(x, y, strategy, context)

        return y

    def _draw_strategy_bars(self, x: int, y: int, strategy: str, context: str) -> int:
        """
        Draw bars for a single strategy across all three species.

        Args:
            x: X position
            y: Y position
            strategy: Strategy name
            context: Context (foraging, combat, flee)

        Returns:
            Updated y position
        """
        # Strategy label (shortened if needed)
        strategy_label = strategy[:10]  # Limit to 10 characters
        label = self.font_small.render(strategy_label, True, config.COLOR_TEXT)
        self.screen.blit(label, (x, y))

        # Bar area starts after label
        bar_x = x + 90
        bar_width_max = self.width - 120  # Maximum width for 100%

        # Draw bars for each species
        species_order = ['Gorilla', 'Chimp', 'Bonobo']
        bar_y = y

        for species in species_order:
            prob = self.species_stats[species][context].get(strategy, 0.0)
            bar_width = int(prob * bar_width_max)

            # Draw background grid (25% increments) if enabled
            if config.STATS_SHOW_GRID:
                for i in range(1, 4):
                    grid_x = bar_x + int(bar_width_max * i * 0.25)
                    pygame.draw.line(self.screen, (80, 80, 80), (grid_x, bar_y), (grid_x, bar_y + config.STATS_BAR_HEIGHT), 1)

            # Draw bar
            if bar_width > 0:
                color = self.species_colors[species]
                pygame.draw.rect(self.screen, color, (bar_x, bar_y, bar_width, config.STATS_BAR_HEIGHT))

                # Draw border
                border_color = (int(color[0] * 0.6), int(color[1] * 0.6), int(color[2] * 0.6))
                pygame.draw.rect(self.screen, border_color, (bar_x, bar_y, bar_width, config.STATS_BAR_HEIGHT), 1)

            # Draw percentage text if enabled
            if config.STATS_SHOW_PERCENTAGES:
                percentage_text = self.font_tiny.render(f"{prob*100:.0f}%", True, (180, 180, 180))
                self.screen.blit(percentage_text, (bar_x + bar_width_max + 5, bar_y - 2))

            bar_y += config.STATS_BAR_HEIGHT + config.STATS_BAR_SPACING

        # Return updated y position (after all three species bars + spacing)
        return bar_y + config.STATS_STRATEGY_SPACING
