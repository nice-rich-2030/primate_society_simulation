"""
Simple verification script to test core functionality without GUI.
"""

import config
import utils
from environment import Environment, Resource
from entities import Agent

def test_utils():
    """Test utility functions."""
    print("Testing utils...")

    # Distance
    p1 = (0, 0)
    p2 = (3, 4)
    dist = utils.distance(p1, p2)
    assert dist == 5.0, f"Distance test failed: {dist}"

    # Normalize
    v = (3, 4)
    normalized = utils.normalize(v)
    assert abs(normalized[0] - 0.6) < 0.01, "Normalize test failed"

    print("  [OK] Utils tests passed")

def test_environment():
    """Test environment."""
    print("Testing environment...")

    env = Environment(800, 600)
    assert len(env.resources) > 0, "No initial resources"
    assert len(env.obstacles) > 0, "No obstacles created"

    initial_count = len(env.resources)
    env.spawn_resource('plant')
    assert len(env.resources) >= initial_count, "Resource spawn failed"

    print(f"  [OK] Environment created with {len(env.resources)} resources and {len(env.obstacles)} obstacles")

def test_agents():
    """Test agent creation and basic behaviors."""
    print("Testing agents...")

    # Create agents of each species
    gorilla = Agent('Gorilla', (100, 100))
    chimp = Agent('Chimp', (200, 200))
    bonobo = Agent('Bonobo', (300, 300))

    assert gorilla.species == 'Gorilla', "Species assignment failed"
    assert gorilla.hp > 0, "HP not initialized"
    assert gorilla.energy > 0, "Energy not initialized"

    # Test fitness calculation
    fitness = gorilla.calculate_fitness()
    assert 0 <= fitness <= 2, f"Fitness out of range: {fitness}"

    # Test strategy probabilities
    assert 'foraging' in gorilla.strategy_probs, "Strategy probs not initialized"

    # Verify all strategies sum to 1.0
    foraging_sum = sum(gorilla.strategy_probs['foraging'].values())
    assert abs(foraging_sum - 1.0) < 0.01, f"Strategy probabilities don't sum to 1: {foraging_sum}"

    print(f"  [OK] Created 3 agents (Gorilla HP:{gorilla.hp}, Chimp HP:{chimp.hp}, Bonobo HP:{bonobo.hp})")

def test_learning():
    """Test learning mechanism."""
    print("Testing learning...")

    # Create two agents
    student = Agent('Gorilla', (100, 100))
    teacher = Agent('Gorilla', (150, 150))

    # Make teacher fitter
    teacher.hp = teacher.max_hp
    teacher.energy = teacher.max_energy
    student.hp = student.max_hp * 0.5
    student.energy = student.max_energy * 0.5

    # Store original strategy probs
    original_probs = dict(student.strategy_probs['foraging'])

    # Modify teacher's strategy
    teacher.strategy_probs['foraging']['WideView'] = 0.7
    teacher.strategy_probs['foraging']['FastMove'] = 0.1
    teacher.strategy_probs['foraging']['RandomWalk'] = 0.1
    teacher.strategy_probs['foraging']['Ambush'] = 0.1

    # Learn
    student.learn_from(teacher)

    # Check that probabilities changed
    new_probs = student.strategy_probs['foraging']
    assert new_probs != original_probs, "Learning did not change probabilities"

    # Check that WideView probability increased (moved toward teacher)
    assert new_probs['WideView'] > original_probs['WideView'], "Learning direction incorrect"

    print(f"  [OK] Learning works (WideView: {original_probs['WideView']:.2f} → {new_probs['WideView']:.2f})")

def test_simulation_step():
    """Test a few simulation steps."""
    print("Testing simulation step...")

    env = Environment(800, 600)
    agents = [Agent('Gorilla', (100, 100)), Agent('Chimp', (200, 200))]

    # Run a few update steps
    for _ in range(10):
        env.update()
        for agent in agents:
            agent.update(env, agents)

    # Check that agents are still alive
    alive = [a for a in agents if a.state != 'dead']
    assert len(alive) > 0, "All agents died too quickly"

    # Check that energy decreased (metabolism)
    assert agents[0].energy < agents[0].max_energy, "Energy not decreasing"

    print(f"  [OK] Simulation runs (Agent 0 energy: {agents[0].energy:.1f}/{agents[0].max_energy})")

if __name__ == "__main__":
    print("\n=== Primate Society Simulation - Verification Tests ===\n")

    test_utils()
    test_environment()
    test_agents()
    test_learning()
    test_simulation_step()

    print("\n=== All tests passed! ===")
    print("\nYou can now run the full simulation with: python main.py")
    print("Controls:")
    print("  - SPACE: Pause/Resume")
    print("  - ESC: Quit")
