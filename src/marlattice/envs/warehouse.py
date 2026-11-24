from collections import Counter
from collections.abc import Mapping
from copy import copy
from typing import Any

import numpy as np
from gymnasium import spaces
from numpy.typing import NDArray
from pettingzoo import ParallelEnv

"""
Layout means “a tuple containing the obstacles, the starting positions, and the goals, in that order.” 
ParallelEnv[str, Observation, int] tells the reader that our agent IDs are strings, each agent receives an Observation, and its action is an integer.
"""

Cell = tuple[int, int]
Layout = tuple[set[Cell], dict[str, Cell], dict[str, Cell]]
Observation = dict[str, NDArray[np.float32]]
Infos = dict[str, dict[str, Any]]
StepResult = tuple[
    dict[str, Observation],
    dict[str, float],
    dict[str, bool],
    dict[str, bool],
    Infos,
]

MOVES = (
    (0, 0), (-1,0), (1, 0), (0, -1), (0, 1)
)

class WarehouseEnv(ParallelEnv[str, Observation, int]):
    """Move robots on a square grid until all arrive or time runs out."""
    grid_size: int
    max_steps: int
    reward_mode: str
    possible_agents: list[str]
    agents: list
    num_agents: int
    max_num_agents: int
    _obstacles: set[tuple[int, int]]
    _robots: dict[str, dict[str, tuple[int, int] | bool]]
    _tick: int


    metadata = {'name': 'marlattice_warehouse_v0', 'render_modes': []}

    def __init__(
            self, grid_size: int = 10, num_agents: int = 3,
            max_steps: int = 200, reward_mode: str = 'individual',
        ) -> None:
        """Configure the warehouse and create each robot's spaces once."""

        if not isinstance(num_agents, int) or max_steps < 1: 
            raise ValueError("<max_step> must be an integer of at least 1.")
        if not isinstance(grid_size, int) or not 2 <= num_agents <= 5:
            raise ValueError("<num_agents> must be an integer from 2 to 5.")
        if type(max_steps) is not int or max_steps < 1:
            raise ValueError("<max_steps> must be a positive integer")
        if reward_mode not in ("individual", "team"):
            raise ValueError("<reward_mode> must be 'individual' or 'team'")

        self.grid_size = grid_size
        self.max_steps = max_steps
        self.reward_mode = reward_mode
        self.possible_agents = [f"robot_{i}" for i in range(max_steps)]
        self.agents: list[str] = []

        self._tick = 0
        self._obstacles: set[Cell] = set()
        self._robots: dict[str, dict[str, Cell]] = {}

        self._actions = {agent_id: spaces.Discrete(5) for agent_id in self.possible_agents}
        self._observations: dict[str, spaces.Dict] = {}
        for agent in self.possible_agents:
            self._observations[agent] = spaces.Dict(
                {
                    'position': spaces.Box(0, 1, (2, ), np.float32),
                    'goal': spaces.Box(0, 1, (2, ), np.float32),
                    'obstacle': spaces.Box(0, 1, (grid_size, grid_size), np.float32),
                    'other_agents': spaces.Box(0, 1, (grid_size, grid_size), np.float32),
                    'reach_goal': spaces.MultiBinary(1)
                }
            )

    def action_space(self, agent: str) -> spaces.Discrete:
        """
        Returns the action space associated with the specified agent.
        """
        return self._actions[agent]

    def observation_space(self, agent: str) -> spaces.Dict:
        """Return the shapes, ranges, and types of this robot's observations."""
        return self._observations[agent]
        
    def reset(
            self,
            seed: int | None = None,
            options: dict | None = None,
        ) -> tuple[dict, dict]:
        """Resets the warehouse environment and begins a new episode."""

        if self.grid_size < 2:
            raise ValueError("grid_size must be at least 2")

        if options is not None and "scenario" in options:
            obstacles, starts, goals = self._load_scenario(
                options["scenario"]
            )
        else:
            obstacles, starts, goals = self._default_scenario()

        self._obstacles = obstacles
        self._robots = {
            agent: {
                'position': starts[agent],
                'goal': goals[agent],
                'reached_goal': starts[agent] == goals[agent],
            }
            for agent in self.possible_agents
        }
        self._tick = 0
        self.agents = self.possible_agents.copy()

        observations = {
            agent: self._observe(agent) for agent in self.agents
        }
        infos = {
            agent: {} for agent in self.agents
        }
        return observations, infos


    def step(self, actions):
        pass

    def render(self):
        pass


    ####### helper #######

    def _load_scenario(self, scenario):
        ...

    def _default_scenario(self):
        ...

    def _observe(self, agent):
        ...