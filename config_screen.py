"""
Module: config_screen.py
Description:
    Configuration screen for setting SPECIES_CONFIG parameters before starting the simulation.
    Allows users to customize each species' attributes and initial population.

Implementation Details:
    - ConfigScreen class: Interactive UI for parameter adjustment
    - Slider controls for numerical values
    - Checkbox controls for diet selection
    - Start and Reset buttons
    - Real-time parameter display

Dependencies:
    - Imports: pygame, config
    - Used By: main.py (shown before simulation starts and on restart)
"""

import pygame
from typing import Dict, Any, Tuple, List
import config


class Slider:
    """A slider UI component for adjusting numerical values."""

    def __init__(self, x: int, y: int, width: int, label: str,
                 min_val: float, max_val: float, initial_val: float,
                 is_int: bool = False):
        """
        Initialize a slider.

        Args:
            x, y: Position
            width: Slider width
            label: Display label
            min_val: Minimum value
            max_val: Maximum value
            initial_val: Initial value
            is_int: Whether value should be integer
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = 20
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.is_int = is_int
        self.dragging = False

        # Calculate handle position
        self.handle_x = self._value_to_x(initial_val)

    def _value_to_x(self, value: float) -> int:
        """Convert value to handle x position."""
        ratio = (value - self.min_val) / (self.max_val - self.min_val)
        return int(self.x + ratio * self.width)

    def _x_to_value(self, x: int) -> float:
        """Convert x position to value."""
        x = max(self.x, min(x, self.x + self.width))
        ratio = (x - self.x) / self.width
        value = self.min_val + ratio * (self.max_val - self.min_val)
        return int(value) if self.is_int else round(value, 1)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle mouse events.

        Returns:
            True if event was handled
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            # Check if click is on handle
            handle_rect = pygame.Rect(self.handle_x - 5, self.y - 5, 10, self.height + 10)
            if handle_rect.collidepoint(mouse_x, mouse_y):
                self.dragging = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging:
                self.dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_x, _ = event.pos
                self.value = self._x_to_value(mouse_x)
                self.handle_x = self._value_to_x(self.value)
                return True
        return False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Draw the slider."""
        # Draw label
        label_text = font.render(f"{self.label}: {self.value}", True, (255, 255, 255))
        surface.blit(label_text, (self.x, self.y - 25))

        # Draw track
        pygame.draw.rect(surface, (100, 100, 100),
                        (self.x, self.y, self.width, self.height), 0, 3)

        # Draw handle
        pygame.draw.circle(surface, (255, 255, 255),
                          (self.handle_x, self.y + self.height // 2), 8)
        pygame.draw.circle(surface, (200, 200, 200),
                          (self.handle_x, self.y + self.height // 2), 6)


class Checkbox:
    """A checkbox UI component."""

    def __init__(self, x: int, y: int, label: str, checked: bool = False):
        """Initialize a checkbox."""
        self.x = x
        self.y = y
        self.size = 20
        self.label = label
        self.checked = checked
        self.rect = pygame.Rect(x, y, self.size, self.size)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle mouse events.

        Returns:
            True if checkbox was toggled
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                return True
        return False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Draw the checkbox."""
        # Draw box
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 0, 3)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, 3)

        # Draw checkmark if checked
        if self.checked:
            check_points = [
                (self.x + 4, self.y + 10),
                (self.x + 8, self.y + 14),
                (self.x + 16, self.y + 6)
            ]
            pygame.draw.lines(surface, (50, 200, 50), False, check_points, 3)

        # Draw label
        text = font.render(self.label, True, (255, 255, 255))
        surface.blit(text, (self.x + self.size + 8, self.y - 2))


class Button:
    """A simple button UI component."""

    def __init__(self, x: int, y: int, width: int, height: int, text: str, color: Tuple[int, int, int]):
        """Initialize a button."""
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = tuple(min(c + 30, 255) for c in color)
        self.hovered = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle mouse events.

        Returns:
            True if button was clicked
        """
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered:
                return True
        return False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Draw the button."""
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect, 0, 5)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, 5)

        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


class ConfigScreen:
    """
    Configuration screen for setting species parameters.
    """

    def __init__(self, screen: pygame.Surface):
        """
        Initialize the configuration screen.

        Args:
            screen: Pygame display surface
        """
        self.screen = screen
        pygame.font.init()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        # Current config (deep copy of original)
        self.current_config = self._deep_copy_config(config.SPECIES_CONFIG)

        # Store original for reset
        self.original_config = self._deep_copy_config(config.SPECIES_CONFIG)

        # Current species being edited
        self.current_species = 'Gorilla'
        self.species_list = ['Gorilla', 'Chimp', 'Bonobo']
        self.species_index = 0

        # Create sliders and checkboxes for current species
        self.sliders: List[Slider] = []
        self.checkboxes: Dict[str, Checkbox] = {}
        self._create_controls()

        # Create buttons
        button_y = 700
        self.start_button = Button(950, button_y, 150, 50, "START", (50, 150, 50))
        self.reset_button = Button(1120, button_y, 150, 50, "RESET", (150, 50, 50))
        self.prev_button = Button(50, button_y, 120, 50, "< PREV", (50, 100, 150))
        self.next_button = Button(180, button_y, 120, 50, "NEXT >", (50, 100, 150))

    def _deep_copy_config(self, config_dict: Dict) -> Dict:
        """Deep copy the species config."""
        return {
            species: {
                key: value.copy() if isinstance(value, list) else value
                for key, value in params.items()
            }
            for species, params in config_dict.items()
        }

    def _create_controls(self):
        """Create sliders and checkboxes for the current species."""
        self.sliders.clear()
        self.checkboxes.clear()
        species_config = self.current_config[self.current_species]

        # Left column: Sliders
        x_start = 50
        y_start = 150
        y_spacing = 60
        slider_width = 300

        # Define slider parameters
        slider_defs = [
            ('max_hp', 'Max HP', 50, 300, True),
            ('max_energy', 'Max Energy', 50, 200, True),
            ('base_speed', 'Base Speed', 0.5, 5.0, False),
            ('attack_power', 'Attack Power', 5, 50, True),
            ('defense', 'Defense', 5, 40, True),
            ('view_range', 'View Range', 50, 200, True),
            ('max_age', 'Max Age', 500, 2000, True),
            ('social_recovery', 'Social Recovery', 0.0, 2.0, False),
            ('food_requirement', 'Food Requirement', 10, 60, True),
        ]

        y = y_start
        for key, label, min_val, max_val, is_int in slider_defs:
            slider = Slider(x_start, y, slider_width, label,
                          min_val, max_val, species_config[key], is_int)
            self.sliders.append((key, slider))
            y += y_spacing

        # Right column: Diet checkboxes
        diet_x = 650
        diet_y = 150

        # Create checkboxes for diet
        current_diet = species_config['diet']
        self.checkboxes['plant'] = Checkbox(diet_x, diet_y, "Plant", 'plant' in current_diet)
        self.checkboxes['meat'] = Checkbox(diet_x, diet_y + 30, "Meat", 'meat' in current_diet)

    def _update_config_from_controls(self):
        """Update current config from slider and checkbox values."""
        # Update from sliders
        for key, slider in self.sliders:
            self.current_config[self.current_species][key] = slider.value

        # Update diet from checkboxes
        diet = []
        if self.checkboxes['plant'].checked:
            diet.append('plant')
        if self.checkboxes['meat'].checked:
            diet.append('meat')

        # Ensure at least one food type is selected
        if not diet:
            diet = ['plant']  # Default to plant if nothing selected
            self.checkboxes['plant'].checked = True

        self.current_config[self.current_species]['diet'] = diet

    def _switch_species(self, direction: int):
        """Switch to next/previous species."""
        self._update_config_from_controls()
        self.species_index = (self.species_index + direction) % len(self.species_list)
        self.current_species = self.species_list[self.species_index]
        self._create_controls()

    def handle_events(self) -> str:
        """
        Handle events for the config screen.

        Returns:
            'start' if user clicked start, 'running' otherwise
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'quit'
                elif event.key == pygame.K_RETURN:
                    self._update_config_from_controls()
                    return 'start'
                elif event.key == pygame.K_LEFT:
                    self._switch_species(-1)
                elif event.key == pygame.K_RIGHT:
                    self._switch_species(1)

            # Handle button clicks
            if self.start_button.handle_event(event):
                self._update_config_from_controls()
                return 'start'
            if self.reset_button.handle_event(event):
                self.current_config = self._deep_copy_config(self.original_config)
                self._create_controls()
            if self.prev_button.handle_event(event):
                self._switch_species(-1)
            if self.next_button.handle_event(event):
                self._switch_species(1)

            # Handle slider events
            for _, slider in self.sliders:
                slider.handle_event(event)

            # Handle checkbox events
            for checkbox in self.checkboxes.values():
                checkbox.handle_event(event)

        return 'running'

    def draw(self):
        """Draw the configuration screen."""
        self.screen.fill((30, 30, 40))

        # Title
        title = self.font_large.render("SPECIES CONFIGURATION", True, (255, 255, 100))
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 50))
        self.screen.blit(title, title_rect)

        # Current species indicator
        species_colors = {
            'Gorilla': config.COLOR_GORILLA,
            'Chimp': config.COLOR_CHIMP,
            'Bonobo': config.COLOR_BONOBO,
        }
        species_color = species_colors[self.current_species]

        species_text = self.font_medium.render(f"Editing: {self.current_species}", True, species_color)
        self.screen.blit(species_text, (50, 100))

        # Draw sliders
        for _, slider in self.sliders:
            slider.draw(self.screen, self.font_small)

        # Draw diet selection (right side)
        diet_x = 450
        diet_y = 150
        diet_title = self.font_medium.render("Diet Selection", True, (255, 255, 255))
        self.screen.blit(diet_title, (diet_x, diet_y))

        # Draw diet checkboxes
        diet_info = self.font_small.render("(Select at least one)", True, (150, 150, 150))
        self.screen.blit(diet_info, (diet_x, diet_y + 30))

        for checkbox in self.checkboxes.values():
            checkbox.draw(self.screen, self.font_small)

        # Draw all species summary (right side)
        summary_x = 450
        summary_y = 250
        summary_title = self.font_medium.render("All Species Summary", True, (255, 255, 255))
        self.screen.blit(summary_title, (summary_x, summary_y))

        y = summary_y + 40
        for species in self.species_list:
            species_color = species_colors[species]
            species_label = self.font_small.render(f"{species}:", True, species_color)
            self.screen.blit(species_label, (summary_x, y))

            species_cfg = self.current_config[species]
            summary_line1 = self.font_small.render(
                f"HP:{species_cfg['max_hp']} Spd:{species_cfg['base_speed']} Atk:{species_cfg['attack_power']}",
                True, (200, 200, 200)
            )
            self.screen.blit(summary_line1, (summary_x + 20, y + 20))

            # Add diet and food requirement info
            diet_str = "/".join([d[0].upper() for d in species_cfg['diet']])  # P or M or P/M
            summary_line2 = self.font_small.render(
                f"Diet:{diet_str} FoodReq:{species_cfg['food_requirement']}",
                True, (180, 180, 180)
            )
            self.screen.blit(summary_line2, (summary_x + 20, y + 38))
            y += 75

        # Draw population settings
        pop_x = 850
        pop_y = 250
        pop_title = self.font_medium.render("Initial Population", True, (255, 255, 255))
        self.screen.blit(pop_title, (pop_x, pop_y))

        populations = [
            (f"Gorilla: {config.INITIAL_GORILLA_COUNT}", config.COLOR_GORILLA),
            (f"Chimp: {config.INITIAL_CHIMP_COUNT}", config.COLOR_CHIMP),
            (f"Bonobo: {config.INITIAL_BONOBO_COUNT}", config.COLOR_BONOBO),
        ]

        y = pop_y + 40
        for pop_text, color in populations:
            text = self.font_small.render(pop_text, True, color)
            self.screen.blit(text, (pop_x, y))
            y += 30

        # Draw buttons
        self.start_button.draw(self.screen, self.font_medium)
        self.reset_button.draw(self.screen, self.font_medium)
        self.prev_button.draw(self.screen, self.font_small)
        self.next_button.draw(self.screen, self.font_small)

        # Instructions
        instructions = [
            "Use sliders to adjust species parameters",
            "Click PREV/NEXT or use arrow keys to switch species",
            "Click START or press ENTER to begin simulation",
            "Press ESC to quit",
        ]

        inst_y = 600
        for instruction in instructions:
            text = self.font_small.render(instruction, True, (150, 150, 150))
            self.screen.blit(text, (50+400, inst_y))
            inst_y += 25

        pygame.display.flip()

    def get_config(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the final configuration.

        Returns:
            Updated SPECIES_CONFIG dictionary
        """
        self._update_config_from_controls()
        return self.current_config

    def run(self) -> Tuple[str, Dict[str, Dict[str, Any]]]:
        """
        Run the configuration screen.

        Returns:
            Tuple of (status, config) where status is 'start' or 'quit'
        """
        clock = pygame.time.Clock()

        while True:
            status = self.handle_events()

            if status == 'start':
                return ('start', self.get_config())
            elif status == 'quit':
                return ('quit', None)

            self.draw()
            clock.tick(60)
