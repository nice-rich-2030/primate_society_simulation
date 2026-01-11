# Primate Society Simulation - Implementation TODO List

## Phase 1: Foundation & Configuration (Steps 1-6)
- [ ] 1. Initialize Git repository and create `.gitignore` (Python/Pygame).
- [ ] 2. Create empty module files (`main.py`, `config.py`, `utils.py`, `entities.py`, `environment.py`, `ui.py`).
- [ ] 3. Setup virtual environment and `requirements.txt` (pygame, numpy).
- [ ] 4. Define global constants in `config.py` (Screen dims, FPS, Colors).
- [ ] 5. Define `SPECIES_CONFIG` dictionary in `config.py` with stats for Gorilla, Chimp, Bonobo.
- [ ] 6. Define Strategy constants in `config.py`:
    - Foraging: `WideView`, `FastMove`, `RandomWalk`, `Ambush`.
    - Combat: `Aggressive`, `Defensive`, `Group`.
    - Flee: `Speed`, `Hide`, `Scatter`.

## Phase 2: Utilities & Math (Steps 7-9)
- [ ] 7. Implement `utils.py`: `distance(p1, p2)` function.
- [ ] 8. Implement `utils.py`: Vector operations (`normalize`, `add`, `sub`).
- [ ] 9. Implement `utils.py`: `random_position(bounds)` helper.

## Phase 3: the World (Environment) (Steps 10-14)
- [ ] 10. Implement `Resource` class in `environment.py` (properties: type, amount, pos).
- [ ] 11. Implement `Environment` class structure with lists for resources and obstacles.
- [ ] 12. Implement `Environment.spawn_resource()` logic (random generation, limits).
- [ ] 13. Implement `Environment.update()` to trigger spawns periodically.
- [ ] 14. Implement `Environment.draw()` to render resources as colored circles.

## Phase 4: Agent Core & State Machine (Steps 15-18)
- [ ] 15. Create `Agent` class in `entities.py` initializing `hunger_threshold` (e.g. 20-80%) and `SPECIES_CONFIG`.
- [ ] 16. Implement `Agent.update()` base method (age, metabolism, death check).
- [ ] 17. Implement simple State Machine skeleton (`state` variable, transition logic).
- [ ] 18. Implement `Agent.move()` handling velocity and boundary clamping.

## Phase 5: Strategy Pattern Implementation (Steps 19-23)
- [ ] 19. Define `Strategy` abstract base class in `entities.py`.
- [ ] 20. Implement Foraging Strategies: `WideView`, `FastMove`, `RandomWalk`, `Ambush`.
- [ ] 21. Implement Combat Strategies: `Aggressive`, `Defensive`, `Group`.
- [ ] 22. Implement Flee Strategies: `Speed`, `Hide`, `Scatter`.
- [ ] 23. Implement `Agent.pick_strategy(context)` method using weighted random choice.

## Phase 6: Core Behaviors & Learning (Steps 24-27)
- [ ] 24. Implement `Agent.execute_foraging()`: Use strategy to find/move to food.
- [ ] 25. Implement `Agent.eat()`: Restore energy/HP, remove resource.
- [ ] 26. Implement `Agent.learn_from(teacher)`:
    - Update strategy probability weights ($P_{self} \leftarrow (1 - \alpha) P_{self} + \alpha P_{teacher}$).
    - Update `hunger_threshold` towards teacher's value.
- [ ] 27. Add interaction hook in update loop to search for neighbors and trigger learning.

## Phase 7: Main Loop & Integration (Steps 28-30)
- [ ] 28. Setup `main.py`: Pygame init, Window creation, Clock.
- [ ] 29. Instantiate `Environment` and initial list of `Agent`s in `main.py`.
- [ ] 30. Implement the Main Game Loop: Event Processing -> `env.update()` -> `agent.update()` -> Render.

## Phase 8: UI & Visualization (Steps 31-33)
- [ ] 31. Implement `UI` class in `ui.py` with font initialization.
- [ ] 32. Implement `UI.draw_agents()`: Draw circles with species colors.
    - Visualize active strategy (e.g., border color) as per SPEC.
- [ ] 33. Implement `UI.draw_panel()`: Display Population counts and FPS.

## Phase 9: Verification (Steps 34-35)
- [ ] 34. Run simulation and verify basic movement and resource spawning.
- [ ] 35. Debug: Print strategy probabilities to console to verify learning is happening.
