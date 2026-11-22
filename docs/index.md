# Marlattice Documentation

**Simulate. Learn. Coordinate.**

Marlattice is a proposed extensible multi-agent simulation and reinforcement learning benchmarking platform. Its first environment is a discrete multi-robot warehouse scenario built against the PettingZoo Parallel API.

> **Draft specification:** The API and environment rules have not yet been approved by all team members or verified against an implementation. Do not interpret examples as evidence that features have been released.

## Developer documentation

- [Environment API specification](environment-api.md): full behavior, observation/action schema, rewards, collisions and tests.
- [Python API reference](reference.md): concise class, attributes and method signatures in the style of PettingZoo's API documentation.

```{toctree}
:maxdepth: 3
:caption: Developer documentation
:hidden:

environment-api
reference
```

## Underlying standards

- [PettingZoo Parallel API](https://pettingzoo.farama.org/api/parallel/)
- [Gymnasium Spaces](https://gymnasium.farama.org/api/spaces/)
- [PettingZoo Environment Tests](https://pettingzoo.farama.org/content/environment_tests/)
