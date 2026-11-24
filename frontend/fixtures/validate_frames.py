"""Check frontend frame fixtures against the snapshot contract.

Usage: python frontend/fixtures/validate_frames.py [frame.json ...]
With no arguments, validates every frame_*.json next to this script.

Rules come from docs/environment-api.md ("Frontend Snapshot", reset() and
step() sections). Fields outside `snapshot` (max_steps, last_step) are the
frontend's proposed envelope, see frontend/design/README.md.
"""

import json
import sys
from pathlib import Path

STATUSES = {"running", "terminated", "truncated"}
ACTIONS = {0, 1, 2, 3, 4}


def is_cell(value, n):
    return (
        isinstance(value, list)
        and len(value) == 2
        and all(isinstance(v, int) and not isinstance(v, bool) for v in value)
        and all(0 <= v < n for v in value)
    )


def validate(frame):
    errors = []
    err = errors.append

    if frame.get("episode_status") not in STATUSES:
        err(f"episode_status must be one of {sorted(STATUSES)}")
    max_steps = frame.get("max_steps")
    if not isinstance(max_steps, int) or max_steps < 1:
        err("max_steps must be an integer >= 1")

    snap = frame.get("snapshot")
    if not isinstance(snap, dict):
        return errors + ["snapshot must be an object"]
    if set(snap) != {"tick", "grid_size", "obstacles", "robots"}:
        err(f"snapshot keys must be tick, grid_size, obstacles, robots; got {sorted(snap)}")

    n = snap.get("grid_size")
    if not isinstance(n, int) or n < 2:
        return errors + ["grid_size must be an integer >= 2"]
    tick = snap.get("tick")
    if not isinstance(tick, int) or tick < 0:
        err("tick must be a non-negative integer")
    elif isinstance(max_steps, int) and tick > max_steps:
        err("tick exceeds max_steps")

    obstacles = snap.get("obstacles", [])
    for cell in obstacles:
        if not is_cell(cell, n):
            err(f"obstacle {cell} is not an in-grid [row, col] pair")
    obstacle_set = {tuple(c) for c in obstacles if is_cell(c, n)}

    robots = snap.get("robots")
    if not isinstance(robots, dict) or not robots:
        return errors + ["robots must be a non-empty object"]

    positions, goals = [], []
    for rid, robot in robots.items():
        if set(robot) != {"position", "goal", "reached_goal"}:
            err(f"{rid}: keys must be position, goal, reached_goal")
            continue
        pos, goal = robot["position"], robot["goal"]
        if not is_cell(pos, n) or not is_cell(goal, n):
            err(f"{rid}: position/goal must be in-grid [row, col] pairs")
            continue
        if tuple(pos) in obstacle_set:
            err(f"{rid}: position {pos} is on an obstacle")
        if tuple(goal) in obstacle_set:
            err(f"{rid}: goal {goal} is on an obstacle")
        if not isinstance(robot["reached_goal"], bool):
            err(f"{rid}: reached_goal must be a boolean")
        elif robot["reached_goal"] and pos != goal:
            err(f"{rid}: reached_goal is true but robot is not on its goal")
        positions.append(tuple(pos))
        goals.append(tuple(goal))

    if len(set(positions)) != len(positions):
        err("two robots share a position")
    if len(set(goals)) != len(goals):
        err("two robots share a goal")

    status = frame.get("episode_status")
    all_done = all(r.get("reached_goal") is True for r in robots.values())
    if status == "terminated" and not all_done:
        err("terminated requires every robot to have reached_goal")
    if status == "running" and all_done:
        err("running but every robot has reached its goal")
    if status == "truncated" and tick != max_steps:
        err("truncated requires tick == max_steps")

    last = frame.get("last_step")
    if tick == 0 and last is not None:
        err("last_step must be null at tick 0")
    if last is not None:
        for key in ("actions", "rewards", "collision_attempt"):
            if set(last.get(key, {})) != set(robots):
                err(f"last_step.{key} must have exactly the robot IDs")
        for rid, action in last.get("actions", {}).items():
            if action not in ACTIONS:
                err(f"last_step.actions.{rid} must be in Discrete(5)")

    return errors


def main(paths):
    if not paths:
        paths = sorted(Path(__file__).parent.glob("frame_*.json"))
    failed = False
    for path in map(Path, paths):
        errors = validate(json.loads(path.read_text()))
        print(f"{'FAIL' if errors else 'ok  '} {path.name}")
        for e in errors:
            print(f"     - {e}")
        failed |= bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
