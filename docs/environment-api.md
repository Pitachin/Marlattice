
# Marlattice Environment API

**Version:** 0.1.0-draft
**Status:** Proposed — Pending Team Review
**API Standard:** PettingZoo Parallel API
## Overview

Marlattice provides a multi-agent warehouse simulation environment for reinforcement learning, classical pathfinding, and algorithm benchmarking.

The environment is implemented as a subclass of PettingZoo's `ParallelEnv`, allowing multiple robots to act simultaneously within a shared environment.

Each robot is represented by an agent with its own observations, actions, and rewards.

A single call to `step(actions)` advances the simulation by one discrete tick. All actions are evaluated against the same initial state and applied through a simultaneous transition.

Continuous, game-like execution is achieved by repeatedly calling `step()` through a simulation runner.

The environment is designed to support:

- Multi-agent warehouse navigation
- Collision avoidance and coordination
- Shared-Policy PPO training
- Classical pathfinding baselines
- Reproducible experiments
- Interactive simulation visualization

The initial version focuses on point-to-point navigation with static obstacles. Pickup-and-delivery tasks and dynamic obstacles are future extensions.

For the underlying API specification, see [PettingZoo Parallel API](https://pettingzoo.farama.org/api/parallel/).

---

## Examples

### Multi-Robot Warehouse

The initial warehouse environment consists of a discrete two-dimensional grid containing autonomous robots, obstacles, and assigned destinations.

Each robot attempts to reach its destination while avoiding obstacles and conflicts with other robots.

The proposed default configuration is:

| Parameter | Default | Description |
|---|---|---|
| `grid_size` | 10 | Width and height of the square grid |
| `num_agents` | 3 | Number of robots |
| `max_steps` | 200 | Maximum simulation ticks per episode. Must be an integer of at least 1. |
| `reward_mode` | `"individual"` | Reward allocation strategy |

The initial implementation should support 2–5 robots, with two-agent configurations available for testing.

All robots are homogeneous and use the same action and observation spaces.

### Simultaneous Collision Example

Consider two robots in a warehouse.

Initial positions:

```python
positions = {
    "robot_0": (2, 1),
    "robot_1": (2, 3),
}
```

Both robots attempt to move into the same empty cell `(2, 2)`.

```python
actions = {
    "robot_0": 4,  # Right
    "robot_1": 3,  # Left
}
```

Under the proposed collision policy, neither robot moves.

Resulting positions:

```python
positions = {
    "robot_0": (2, 1),
    "robot_1": (2, 3),
}
```

Assuming neither robot has reached its goal, each receives a step penalty and a collision-attempt penalty.

```python
rewards = {
    "robot_0": -0.11,
    "robot_1": -0.11,
}

terminations = {
    "robot_0": False,
    "robot_1": False,
}

truncations = {
    "robot_0": False,
    "robot_1": False,
}

infos = {
    "robot_0": {"collision_attempt": True},
    "robot_1": {"collision_attempt": True},
}
```

The returned observations contain the unchanged robot positions and updated observation fields.

The active agent list remains:

```python
env.agents == ["robot_0", "robot_1"]
```

Collision resolution must not depend on the insertion order of the action dictionary.

---

## Usage

Marlattice environments follow the PettingZoo Parallel API.

The intended usage is:

```python
from marlattice.envs.warehouse import WarehouseEnv

env = WarehouseEnv(
    grid_size=10,
    num_agents=3,
    max_steps=200,
)

observations, infos = env.reset(seed=42)

while env.agents:
    actions = {
        agent: env.action_space(agent).sample()
        for agent in env.agents
    }

    observations, rewards, terminations, truncations, infos = (
        env.step(actions)
    )

env.close()
```

The example uses randomly sampled actions.

Reinforcement learning algorithms should replace random action selection with a policy.

For Shared-Policy PPO:

```python
actions = {
    agent: policy.act(observations[agent])
    for agent in env.agents
}
```

Here, `policy.act()` represents an interface implemented by Marlattice's algorithm layer, not a PettingZoo method.

### Automatic Simulation Execution

Marlattice supports continuous, game-like simulation execution.

Users do not need to manually submit actions for individual robots.

A simulation runner repeatedly performs the following operations:

1. Obtain observations for active agents.
2. Use the selected policy to generate actions.
3. Submit the action dictionary to `env.step()`.
4. Record the resulting simulation state.
5. Send updated state information to the visualization layer.
6. Repeat until the episode ends or execution is paused.

The frontend may provide:

- Start
- Pause
- Resume
- Reset
- Playback speed control

Simulation ticks and rendering frames are independent.

PPO training should run without artificial animation delays.

---

## WarehouseEnv

`class marlattice.envs.warehouse.WarehouseEnv(ParallelEnv)`

A discrete, multi-agent warehouse environment implementing the PettingZoo Parallel API.

The environment maintains robot positions, destinations, obstacles, rewards, and episode progress.

The constructor requires `max_steps` to be an integer of at least 1 and raises `ValueError` otherwise. This limit applies to default and explicit scenarios.

All active robots select actions for the same simulation tick before the environment applies a state transition.

### WarehouseEnv.possible_agents

**Type:** `list[str]`

A list containing every possible agent ID for the environment instance.

For a three-robot environment:

```python
["robot_0", "robot_1", "robot_2"]
```

This list remains unchanged during an episode and across resets.

### WarehouseEnv.agents

**Type:** `list[str]`

A list containing all currently active agents.

In the initial Marlattice environment, agents remain active until the entire episode ends, including robots that have already reached their destinations.

After episode completion:

```python
env.agents == []
```

### WarehouseEnv.num_agents

**Type:** `int`

The current number of active agents, equivalent to the length of `env.agents`.

### WarehouseEnv.max_num_agents

**Type:** `int`

The maximum number of agents supported by the current environment instance, equivalent to the length of `env.possible_agents`.

---

## WarehouseEnv.action_space(agent)

**Signature:**

```python
action_space(agent: str) -> gymnasium.spaces.Discrete
```

Returns the action space associated with the specified agent.

Each robot uses:

```python
Discrete(5)
```

The discrete actions are:

| Value | Action | Position Change |
|---|---|---|
| 0 | Stay | (0, 0) |
| 1 | Up | (-1, 0) |
| 2 | Down | (+1, 0) |
| 3 | Left | (0, -1) |
| 4 | Right | (0, +1) |

All positions use `(row, column)` coordinates.

The top-left corner is `(0, 0)`.

For a given agent, repeated calls to `action_space(agent)` must return the same space object throughout the lifetime of the environment instance, including across resets.

Actions outside the declared space are invalid inputs and should be rejected.

---

## WarehouseEnv.observation_space(agent)

**Signature:**

```python
observation_space(agent: str) -> gymnasium.spaces.Dict
```

Returns the observation space associated with the specified agent.

### Observation Model

The initial version uses full-map observations.

Each agent receives:

- Its own current position
- Its assigned destination
- The static obstacle map
- The positions of other robots
- Its own task completion status

The observation is represented as a dictionary.

| Field | Shape | dtype | Description |
|---|---|---|---|
| `position` | `(2,)` | float32 | Normalized robot position |
| `goal` | `(2,)` | float32 | Normalized destination |
| `obstacles` | `(N,N)` | float32 | Binary obstacle map |
| `other_agents` | `(N,N)` | float32 | Binary occupancy map of other robots |
| `reached_goal` | `(1,)` | float32 | Task completion indicator |

Here, `N` denotes `grid_size`.

For a 10×10 grid, each observation contains 205 numerical values when flattened.

Coordinates are normalized to `[0, 1]` by dividing by `N - 1`.

The `obstacles` and `other_agents` maps use binary values:

- `0`: Unoccupied
- `1`: Occupied

The observing robot is excluded from its own `other_agents` map.

Completed robots remain visible to other agents.

The observation includes the current positions of other robots but not their future actions.

### Example

```python
observation = {
    "position": np.array(
        [2 / 9, 3 / 9], dtype=np.float32
    ),
    "goal": np.array(
        [7 / 9, 8 / 9], dtype=np.float32
    ),
    "obstacles": obstacle_map,
    "other_agents": agent_map,
    "reached_goal": np.array(
        [0.0], dtype=np.float32
    ),
}
```

`obstacle_map` and `agent_map` are binary NumPy arrays of shape `(10, 10)` with dtype `float32`.

For a given agent, repeated calls to `observation_space(agent)` must return the same space object throughout the lifetime of the environment instance, including across resets.

Support for partial observations may be introduced in future versions.

---

## WarehouseEnv.reset()

**Signature:**

```python
reset(
    seed: int | None = None,
    options: dict | None = None,
) -> tuple[dict, dict]
```

Resets the warehouse environment and begins a new episode.

### Parameters

**seed**

An optional random seed accepted for reproducibility. In the MVP, changing the seed does not change the fixed default layout or an explicitly supplied scenario. To train or evaluate on a different map, pass a different scenario through `options`.

**options**

Pass an explicit scenario as `options={"scenario": {"obstacles": ..., "starts": ..., "goals": ...}}`. `obstacles` is a list of cells. `starts` and `goals` are mappings keyed by robot ID and must each contain exactly the IDs in `possible_agents`. All cells are specified as integer `[row, col]` pairs. Ignore unrecognized top-level keys in `options`. If `options` is omitted, is `None`, or does not contain `scenario`, use the default layout. If the `scenario` key is present, validate its value as an explicit scenario and raise `ValueError` if it is invalid.

### Default Scenario

If no explicit scenario is supplied, reset uses a fixed, obstacle-free layout determined by the grid size and robot count. Traverse the grid row by row, alternating left-to-right and right-to-left so consecutive cells are adjacent. Assign each robot a disjoint pair of consecutive cells in `possible_agents` order. The first cell of each pair is the start and the second is its goal.

This layout is independent of the seed. All robots can reach their goals in one simultaneous tick because their goal cells are initially empty and distinct. Configurations with fewer than two cells per robot raise `ValueError` when requesting this default layout. Explicit scenarios follow the validation rules below.

### Returns

**observations**

A dictionary mapping each active agent to its initial observation.

**infos**

A dictionary containing additional information for each active agent.

### Behavior

Calling `reset()` must:

1. Initialize or restore a valid warehouse scenario.
2. Assign valid robot starting positions.
3. Assign valid destinations.
4. Initialize the obstacle map.
5. Reset the simulation tick counter.
6. Set each robot's completion status based on whether it starts at its goal.
7. Restore the active agent list.
8. Return initial observations and infos.

`grid_size` must be at least `2`. Starting cells must be distinct, and goal cells must be distinct. All scenario cells must be inside the grid. Starts and goals must be free of obstacles. Each goal must be reachable from its robot's start through the static map.

A robot that starts at its own goal is marked as complete during reset and receives no arrival reward. At least one robot must start away from its own goal. Invalid configurations or explicit scenarios raise `ValueError`.

Identical seeds and environment configurations must reproduce identical initial scenarios.

---

## WarehouseEnv.step()

**Signature:**

```python
step(
    actions: dict[str, int]
) -> tuple[dict, dict, dict, dict, dict]
```

Advances the warehouse environment by one simulation tick.

Call `step()` only during an active episode. A call before the first successful `reset()` or after termination or truncation raises `RuntimeError` before action validation. This applies even to `step({})`. The simulation state and tick counter remain unchanged.

All agent actions are evaluated simultaneously.

### Parameters

**actions**

A dictionary mapping each currently active agent to one discrete action.

Example:

```python
{
    "robot_0": 4,
    "robot_1": 0,
    "robot_2": 1,
}
```

The keys in `actions` must match `env.agents` exactly, and every value must belong to `Discrete(5)`. Validate the full action dictionary before updating the simulation. Missing IDs, extra IDs, or invalid action values raise `ValueError` and leave the simulation state and tick counter unchanged.

A valid movement action rejected by the collision rules still consumes a simulation tick and sets `infos[agent]["collision_attempt"] = True`.

### Returns

**observations**

A dictionary containing the resulting observation for each agent active at the beginning of the tick.

**rewards**

A dictionary containing the reward assigned to each agent for the transition.

**terminations**

A dictionary of Boolean flags indicating whether agents have reached a natural terminal condition.

**truncations**

A dictionary of Boolean flags indicating whether agents have reached an external episode limit.

**infos**

A dictionary containing additional transition information.

For the initial version, each agent's info includes:

```python
{
    "collision_attempt": False
}
```

This flag becomes `True` whenever an agent's movement action is rejected due to any collision or invalid move (including grid boundaries, static obstacles, or conflicts with other robots).

### State Transition

The environment must:

1. Read all active agent actions.
2. Determine intended destination cells.
3. Check grid boundaries and obstacles.
4. Resolve simultaneous movement conflicts.
5. Apply all accepted movements together.
6. Update task completion status.
7. Calculate rewards.
8. Update the simulation tick counter.
9. Evaluate termination and truncation conditions.
10. Return transition results.

All movement decisions use the state at the beginning of the tick.

The insertion order of the action dictionary must not affect the transition result.

---

## Collision Resolution

The initial collision policy is deterministic.

### Boundary Collision

Robots cannot move outside the grid.

### Obstacle Collision

Robots cannot enter cells containing static obstacles.

### Vertex Conflict

When two or more robots attempt to enter the same empty cell, all conflicting movements are rejected.

### Occupied Cell

In v0.1, a robot cannot enter a cell occupied by another robot at the beginning of the tick, even if that robot intends to move away.

### Position Swapping

Direct position swaps between two robots are not allowed.

### Invalid Movement

A rejected movement leaves the robot in its original position, triggers `infos[agent]["collision_attempt"] = True`, and incurs the collision-attempt penalty (`-0.10`).

More permissive simultaneous movement rules may be introduced in later versions.

---

## Reward Model

Reward allocation is configurable.

The proposed initial version supports individual and shared team rewards for benchmarking.

### Individual Reward

Each robot receives a reward based on its own actions and task completion.

Proposed base reward events:

| Event | Reward |
|---|---|
| Robot unfinished at the start of the tick | -0.01 |
| First arrival at assigned goal | +1.00 |
| Invalid movement or collision attempt | -0.10 |

Apply the step penalty based on the robot's completion status at the start of the tick. Reward events are additive. A robot that moves into its goal for the first time receives `-0.01 + 1.00 = 0.99` for that tick. A rejected movement adds a `-0.10` penalty.

A robot that was already complete at the start of the tick still requires a valid action. The environment treats its action as `Stay`, assigns an individual base reward of `0`, and sets `collision_attempt` to `False`. In team mode, the robot still receives the same mean reward as the other active robots.

### Team Reward

Team rewards use the mean of the individual base rewards for the same simulation tick.

For `N` active robots:

```text
team_reward = sum(individual_base_rewards) / N
```

Every agent receives the same team reward for that tick.

The selected reward mode does not change the PettingZoo return structure.

Reward coefficients and the reward-mode comparison protocol are provisional and require experimental validation.

---

## Episode Lifecycle

An episode begins with `reset()` and ends when a terminal or truncation condition is reached.

### Successful Termination

When every robot reaches its assigned destination, the episode terminates.

All active agents receive:

```python
terminations[agent] = True
truncations[agent] = False
```

### Task Failure

The initial version does not define an additional fatal failure condition.

If a future task-failure condition is introduced, it will be specified as a natural terminal condition.

### Time Limit

If the simulation reaches `max_steps` before successful completion, the episode is truncated.

```python
terminations[agent] = False
truncations[agent] = True
```

Successful completion takes precedence when completion and the time limit occur on the same tick.

### Agent Removal

In v0.1, agents are not removed individually.

Robots that reach their goals remain stationary and active until the episode ends.

On the final transition, `step()` still returns the rewards, status flags, infos, and resulting observations for agents active at the beginning of that step.
`reached_goal` indicates individual task completion. `terminations` and `truncations` describe the outcome of the entire episode. After a time-limit truncation, the training loop can use the final observation returned by `step()` for value bootstrapping. Advantage recursion stops at the episode boundary.

After the final transition:

```python
env.agents == []
```

A new episode requires another call to `reset()`.

---

## WarehouseEnv.render()

**Signature:**

```python
render()
```

Displays or returns a representation of the current warehouse state when a rendering mode is supported.

The precise rendering modes are pending implementation.

The web frontend is not required to use PettingZoo's `render()` method directly.

## Frontend Snapshot

Call `env.snapshot()` to read the current state as a JSON-serializable dictionary after a successful `reset()` or `step()`. Calling it before the first successful reset raises `RuntimeError`. The method does not advance the simulation. Each call returns an independent copy, so later steps and edits to a returned snapshot cannot change previously recorded state or the environment. It contains `tick`, `grid_size`, `obstacles`, and a `robots` mapping keyed by robot ID. Each robot entry contains `position`, `goal`, and `reached_goal`. Positions, goals, and obstacle cells are integer `[row, col]` pairs.

`tick` is `0` immediately after reset. The final snapshot includes every robot after `env.agents` is cleared. When sending a snapshot to the frontend, the runner also provides an `episode_status` value. Use `"running"` after reset and during an active episode, `"terminated"` when the final step reports termination for all robots, and `"truncated"` when it reports truncation for all robots. The runner derives this value from `step()` before sending the final snapshot. The transport is pending frontend review.

---

## WarehouseEnv.close()

**Signature:**

```python
close() -> None
```

Releases resources associated with the environment.

For a headless environment without external resources, the method may perform no operation.

---

## WarehouseEnv.state()

**Status:** Optional — Future Extension

May provide a global environment state suitable for centralized training methods.

This is not required for the initial Shared-Policy PPO implementation.

A future state representation may support MAPPO or other centralized-critic methods.

---

## API Compliance

Marlattice environments must follow the PettingZoo Parallel API contract.

The implementation should be validated using PettingZoo's testing utilities.

### Parallel API Test

```python
from pettingzoo.test import parallel_api_test

env = WarehouseEnv()

parallel_api_test(env, num_cycles=100)
```

### Seed Test

```python
from pettingzoo.test import parallel_seed_test

parallel_seed_test(lambda: WarehouseEnv())
```

Additional Marlattice-specific tests must verify:

- Valid initial robot positions
- Observation and action space consistency
- Simultaneous state transitions
- Boundary and obstacle collisions
- Multi-robot vertex conflicts
- Collision independence from action dictionary ordering
- Reward calculations
- Goal completion
- Episode termination
- Episode truncation
- Deterministic initialization with a fixed seed

Passing PettingZoo tests does not replace application-specific behavioral testing.

---

## Benchmark Scenarios

Use fixed scenarios for benchmark comparisons. Validate each scenario by resetting to its specified initial state and replaying a joint action sequence through `WarehouseEnv.step()`. The replay must end in successful termination within `max_steps`.

Joint breadth-first search (BFS) can generate a candidate sequence for small scenarios. Coordinated A* can also generate a candidate sequence. A joint search must follow the environment's simultaneous movement and collision rules, including keeping completed robots stationary. Apply the same replay check to sequences from either planner.

Routine resets check each robot's reachability through the static map. Benchmark replay verifies that all robots can reach their goals together within the step limit.

---

## Design Decisions Pending Review

The following decisions require team approval before the API is considered stable:

- [ ] Full-map observation representation
- [ ] Observation normalization
- [ ] Static obstacle and goal generation
- [ ] Conservative collision policy
- [ ] Individual and team reward definitions
- [ ] Reward coefficients
- [ ] Completed robot behavior
- [ ] Episode lifecycle rules
- [ ] Frontend snapshot requirements

Changes to the environment contract must be documented and reviewed before integration.

---

## References

- [PettingZoo Parallel API](https://pettingzoo.farama.org/api/parallel/)
- [PettingZoo Environment Creation](https://pettingzoo.farama.org/content/environment_creation/)
- [PettingZoo Environment Testing](https://pettingzoo.farama.org/content/environment_tests/)
- [Gymnasium Spaces](https://gymnasium.farama.org/api/spaces/)
