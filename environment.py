"""
Module: environment.py
Description:
    Manages the physical world of the simulation, including the map boundaries,
    static obstacles, and dynamic resources (food).

Implementation Details:
    - Resource Class: Represents food items (Plant/Meat).
    - Environment Class:
        - Spawns resources periodically based on logic.
        - Manages list of active resources and obstacles.
        - Checks collisions between agents and resources.
        - Rendering method for environment objects.

Dependencies:
    - Imports: pygame, random, config.py, utils.py.
    - Used By: main.py (instantiation and update), entities.py (agents query environment for resources).
"""

import pygame
import random
from typing import List, Tuple
import config
import utils


class Resource:
    """
    Represents a food resource in the environment.

    Attributes:
        resource_type: 'plant' or 'meat'
        position: (x, y) coordinates
        amount: Nutrition value
        radius: Visual radius for rendering
    """

    def __init__(self, resource_type: str, position: Tuple[float, float], amount: int):
        """
        Initialize a resource.

        Args:
            resource_type: 'plant' or 'meat'
            position: (x, y) coordinates
            amount: Nutrition value
        """
        self.resource_type = resource_type
        self.position = position
        self.amount = amount
        self.radius = 5 if resource_type == 'plant' else 8

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the resource on the given surface.

        Args:
            surface: Pygame surface to draw on
        """
        if hasattr(config, 'USE_IMAGE') and config.USE_IMAGE:
            self._draw_image(surface)
        else:
            self._draw_circle(surface)

    def _draw_image(self, surface: pygame.Surface) -> None:
        """Draw resource using loaded image."""
        if not hasattr(Resource, '_images'):
            Resource._images = {}

        if self.resource_type not in Resource._images:
            try:
                path = config.IMAGE_PATHS[self.resource_type]
                img = pygame.image.load(path).convert_alpha()
                # Scale
                size = 24 if self.resource_type == 'plant' else 24
                img = pygame.transform.scale(img, (size, size))
                Resource._images[self.resource_type] = img
            except Exception as e:
                print(f"Error loading resource image: {e}")
                self._draw_circle(surface)
                return
        
        image = Resource._images[self.resource_type]
        rect = image.get_rect(center=(int(self.position[0]), int(self.position[1])))
        surface.blit(image, rect)

    def _draw_circle(self, surface: pygame.Surface) -> None:
        """Draw resource as circle (fallback)."""
        color = config.COLOR_PLANT if self.resource_type == 'plant' else config.COLOR_MEAT
        pygame.draw.circle(surface, color, (int(self.position[0]), int(self.position[1])), self.radius)




class Environment:
    """
    Manages the simulation environment including resources and obstacles.

    Attributes:
        width: Map width in pixels
        height: Map height in pixels
        resources: List of active resources
        obstacles: List of obstacle rectangles
        spawn_timer: Frame counter for resource spawning
    """

    def __init__(self, width: int, height: int):
        """
        Initialize the environment.

        Args:
            width: Map width in pixels
            height: Map height in pixels
        """
        self.width = width
        self.height = height
        self.resources: List[Resource] = []
        self.obstacles: List[pygame.Rect] = []
        self.spawn_timer = 0

        # Create some obstacles (simple rectangles for now)
        self._create_obstacles()

        # Initial resource spawn
        for _ in range(config.RESOURCE_MAX_PLANT // 2):
            self.spawn_resource('plant')
        for _ in range(config.RESOURCE_MAX_MEAT // 2):
            self.spawn_resource('meat')

    def _create_obstacles(self) -> None:
        """Create static obstacles in the environment."""
        # Create a few random obstacles (houses, trees)
        num_obstacles = 5
        for _ in range(num_obstacles):
            w = random.randint(30, 60)
            h = random.randint(30, 60)
            x = random.randint(50, self.width - 50 - w)
            y = random.randint(50, self.height - 50 - h)
            self.obstacles.append(pygame.Rect(x, y, w, h))

    def spawn_resource(self, resource_type: str) -> None:
        """
        Spawn a new resource if under the maximum limit.

        Args:
            resource_type: 'plant' or 'meat'
        """
        # Check current count
        current_count = sum(1 for r in self.resources if r.resource_type == resource_type)

        max_count = config.RESOURCE_MAX_PLANT if resource_type == 'plant' else config.RESOURCE_MAX_MEAT
        if current_count >= max_count:
            return

        # Generate random position (avoid obstacles)
        position = None
        for _ in range(10):  # Try up to 10 times to find a good position
            pos = utils.random_position((20, 20, self.width - 20, self.height - 20))
            # Check if position overlaps with obstacles
            overlaps = False
            for obstacle in self.obstacles:
                if obstacle.collidepoint(pos):
                    overlaps = True
                    break
            if not overlaps:
                position = pos
                break

        if position is None:
            # Couldn't find a good position, just place it randomly
            position = utils.random_position((20, 20, self.width - 20, self.height - 20))

        # Create resource
        amount = config.RESOURCE_PLANT_NUTRITION if resource_type == 'plant' else config.RESOURCE_MEAT_NUTRITION
        resource = Resource(resource_type, position, amount)
        self.resources.append(resource)

    def update(self) -> None:
        """Update environment state (spawn resources periodically)."""
        self.spawn_timer += 1

        if self.spawn_timer >= config.RESOURCE_SPAWN_INTERVAL:
            self.spawn_timer = 0

            # Spawn plants more frequently than meat
            if random.random() < 0.7:
                self.spawn_resource('plant')
            else:
                self.spawn_resource('meat')

    def remove_resource(self, resource: Resource) -> None:
        """
        Remove a resource from the environment.

        Args:
            resource: Resource to remove
        """
        if resource in self.resources:
            self.resources.remove(resource)

    def get_resources_in_range(self, position: Tuple[float, float], radius: float) -> List[Resource]:
        """
        Get all resources within a certain radius of a position.

        Args:
            position: Center position (x, y)
            radius: Search radius

        Returns:
            List of resources within range
        """
        nearby = []
        for resource in self.resources:
            dist = utils.distance(position, resource.position)
            if dist <= radius:
                nearby.append(resource)
        return nearby

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw all environment elements.

        Args:
            surface: Pygame surface to draw on
        """
        # Draw obstacles
        for obstacle in self.obstacles:
            pygame.draw.rect(surface, config.COLOR_OBSTACLE, obstacle)

        # Draw resources
        for resource in self.resources:
            resource.draw(surface)
