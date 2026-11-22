# Python API Reference

**Version:** `0.1.0-draft` · **Status:** Proposed — Pending Team Review

This page documents the **planned** Python interface for Marlattice's warehouse environment. These are Sphinx Python-domain declarations, **not automatically extracted from an implemented module**. When `WarehouseEnv` exists, replace the manual declarations with `autoclass` / `automethod` directives as appropriate.

For the complete functional contract, see [Environment API](environment-api.md).

## WarehouseEnv

```{eval-rst}
.. py:class:: marlattice.envs.warehouse.WarehouseEnv(grid_size=10, num_agents=3, max_steps=200, reward_mode="individual")

   Proposed multi-agent grid warehouse environment complying with PettingZoo's ``ParallelEnv`` protocol.

   One ``step(actions)`` advances one discrete simulation tick. The game-like continuous simulation is orchestrated by a separate runner calling ``step`` repeatedly.

   .. py:attribute:: agents
      :type: list[str]

      Identifiers of agents currently active in the episode. Empty after the final transition.

   .. py:attribute:: possible_agents
      :type: list[str]

      Fixed set of agent identifiers supported by the environment instance.

   .. py:attribute:: num_agents
      :type: int

      Number of currently active agents (``len(agents)``).

   .. py:attribute:: max_num_agents
      :type: int

      Maximum supported agent count (``len(possible_agents)``).

   .. py:method:: reset(seed=None, options=None)

      Initialize a new episode, reset agent positions and goal status, and provide initial per-agent observations.

      :param int seed: Optional reproducibility seed.
      :param dict options: Optional reset configuration, not yet finalized.
      :returns: ``(observations, infos)`` keyed by agent ID.
      :rtype: tuple[dict, dict]

   .. py:method:: step(actions)

      Advance the environment one simultaneous action tick, resolving all movement conflicts from the same preceding state.

      :param dict actions: A mapping from each active agent ID to an integer in ``Discrete(5)``.
      :returns: ``(observations, rewards, terminations, truncations, infos)``.
      :rtype: tuple[dict, dict, dict, dict, dict]

   .. py:method:: action_space(agent)

      Return an agent's planned discrete action space, ``Discrete(5)``.

      :param str agent: Agent ID.
      :rtype: gymnasium.spaces.Discrete

   .. py:method:: observation_space(agent)

      Return the planned dictionary observation space for the agent. Full-map observation is proposed for v0.1.

      :param str agent: Agent ID.
      :rtype: gymnasium.spaces.Dict

   .. py:method:: render()

      Display or return a representation of current warehouse state if a render mode is implemented.

   .. py:method:: close()

      Release environment resources, if any.

   .. py:method:: state()

      Optional future extension for centralized-training algorithms. **Not required in v0.1.**
```

## Action encoding

| Value | Action | Change in `(row, col)` |
|---:|---|---|
| `0` | Stay | `(0, 0)` |
| `1` | Up | `(-1, 0)` |
| `2` | Down | `(+1, 0)` |
| `3` | Left | `(0, -1)` |
| `4` | Right | `(0, +1)` |

## Example

```python
from marlattice.envs.warehouse import WarehouseEnv  # planned module

env = WarehouseEnv(grid_size=10, num_agents=3, max_steps=200)
observations, infos = env.reset(seed=42)
while env.agents:
    actions = {
        agent: env.action_space(agent).sample()
        for agent in env.agents
    }
    observations, rewards, terminations, truncations, infos = env.step(actions)
env.close()
```

**Note:** This example is illustrative until the environment is implemented and validated.
