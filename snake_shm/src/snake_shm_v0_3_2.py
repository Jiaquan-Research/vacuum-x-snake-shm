"""
Snake-SHM v0.3.2: Final Engineering Edition
-------------------------------------------
Mandatory Patch Summary:
1. Fix: Coordinate variable name errors (hy -> cy).
2. Symmetry: Enforce shared motor floor (remove hard-coded 'UP' fallback).
3. Semantics: Implement Panic State Machine (record episodes, not steps).
4. Hygiene: Unified obstacle semantics across BFS and Flood Fill.
5. Reproducibility: Explicitly seed NumPy RNG.
"""

import random
from collections import deque
import numpy as np


class Config:
    # --- Environment ---
    GRID_W = 20
    GRID_H = 20
    MAX_STEPS_WITHOUT_FOOD = 200
    MAX_TOTAL_STEPS = 20000
    SEED_START = 1000
    N_SEEDS = 50

    # --- Risk Assessment (StructGate) ---
    W_TOPO = 0.7
    W_GEOM = 0.3
    SVD_ENTROPY_SCALE = 5.0

    # --- Coasean Pricing ---
    RISK_THRESHOLD_BASE = 0.35
    RISK_HUNGER_GAIN = 0.50

    # --- Metrics ---
    RESCUE_WINDOW = 20


class Algs:
    MOVES = [
        ("UP", (0, -1)),
        ("DOWN", (0, 1)),
        ("LEFT", (-1, 0)),
        ("RIGHT", (1, 0)),
    ]

    @staticmethod
    def bfs_path(start, goal, obstacles, w, h):
        q = deque([(start, [])])
        visited = {start}
        obs_set = set(obstacles)

        while q:
            (cx, cy), path = q.popleft()
            if (cx, cy) == goal:
                return path[0] if path else None

            for m_name, (dx, dy) in Algs.MOVES:
                nx, ny = cx + dx, cy + dy
                if (
                    0 <= nx < w and 0 <= ny < h
                    and (nx, ny) not in obs_set
                    and (nx, ny) not in visited
                ):
                    visited.add((nx, ny))
                    q.append(((nx, ny), path + [m_name]))
        return None

    @staticmethod
    def flood_fill_count(start, obstacles, w, h):
        q = deque([start])
        visited = {start}
        obs_set = set(obstacles)
        count = 0

        while q:
            cx, cy = q.popleft()
            count += 1
            for _, (dx, dy) in Algs.MOVES:
                nx, ny = cx + dx, cy + dy
                if (
                    0 <= nx < w and 0 <= ny < h
                    and (nx, ny) not in obs_set
                    and (nx, ny) not in visited
                ):
                    visited.add((nx, ny))
                    q.append((nx, ny))
        return count

    @staticmethod
    def get_max_reach_move(head, obstacles, w, h):
        best_move = None
        max_area = -1
        hx, hy = head

        for m_name, (dx, dy) in Algs.MOVES:
            nx, ny = hx + dx, hy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in set(obstacles):
                area = Algs.flood_fill_count((nx, ny), obstacles, w, h)
                if area > max_area:
                    max_area = area
                    best_move = m_name
        return best_move


class StructGate:
    @staticmethod
    def analyze_risk(snake_body, w, h):
        if len(snake_body) < 3:
            return 0.0

        pts = np.array(snake_body)
        pts = pts - np.mean(pts, axis=0)

        try:
            _, s, _ = np.linalg.svd(pts, full_matrices=False)
            entropy = s[1] / (s[0] + 1e-8) if len(s) >= 2 else 0.0
            geom_risk = np.clip(
                1.0 - entropy * Config.SVD_ENTROPY_SCALE, 0.0, 1.0
            )
        except Exception:
            geom_risk = 0.0

        area = Algs.flood_fill_count(snake_body[0], snake_body, w, h)
        topo_risk = np.clip(
            1.0 - (area / max(1, len(snake_body))), 0.0, 1.0
        )

        return Config.W_TOPO * topo_risk + Config.W_GEOM * geom_risk


class SnakeGame:
    def __init__(self, seed):
        random.seed(seed)
        np.random.seed(seed)  # 🔒 Reproducibility fix

        self.w = Config.GRID_W
        self.h = Config.GRID_H
        self.snake = deque([(self.w // 2, self.h // 2)])
        self.food = self._spawn_food()
        self.steps_since_food = 0
        self.steps_total = 0
        self.done = False
        self.death = "ALIVE"

    def _spawn_food(self):
        occupied = set(self.snake)
        for _ in range(100):
            x = random.randint(0, self.w - 1)
            y = random.randint(0, self.h - 1)
            if (x, y) not in occupied:
                return (x, y)
        return (0, 0)

    def step(self, action):
        if self.done:
            return

        self.steps_total += 1
        self.steps_since_food += 1

        hx, hy = self.snake[0]
        dx, dy = 0, 0

        if action == "UP":
            dy = -1
        elif action == "DOWN":
            dy = 1
        elif action == "LEFT":
            dx = -1
        elif action == "RIGHT":
            dx = 1

        nx, ny = hx + dx, hy + dy

        if not (0 <= nx < self.w and 0 <= ny < self.h) or (nx, ny) in list(self.snake)[:-1]:
            self.done = True
            self.death = "Collision"
            return

        self.snake.appendleft((nx, ny))

        if (nx, ny) == self.food:
            self.steps_since_food = 0
            self.food = self._spawn_food()
        else:
            self.snake.pop()

        if self.steps_since_food >= Config.MAX_STEPS_WITHOUT_FOOD:
            self.done = True
            self.death = "Starvation"


class BaseAgent:
    def __init__(self, is_coase=False):
        self.is_coase = is_coase
        self.panic_history = []
        self.in_panic = False

    def get_action(self, game):
        state = {
            "snake": list(game.snake),
            "food": game.food,
            "w": game.w,
            "h": game.h,
            "hunger": game.steps_since_food,
        }

        head = state["snake"][0]
        body_no_tail = state["snake"][:-1]

        action = Algs.bfs_path(
            head, state["food"], body_no_tail, state["w"], state["h"]
        )

        if self.is_coase:
            risk = StructGate.analyze_risk(
                state["snake"], state["w"], state["h"]
            )
            hunger_ratio = min(
                1.0, state["hunger"] / Config.MAX_STEPS_WITHOUT_FOOD
            )
            threshold = (
                Config.RISK_THRESHOLD_BASE
                + hunger_ratio * Config.RISK_HUNGER_GAIN
            )

            if risk >= threshold:
                if not self.in_panic:
                    self.panic_history.append(game.steps_total)
                    self.in_panic = True

                tail = state["snake"][-1]
                escape_move = Algs.bfs_path(
                    head, tail, body_no_tail, state["w"], state["h"]
                )
                if escape_move:
                    action = escape_move
                else:
                    action = Algs.get_max_reach_move(
                        head, body_no_tail, state["w"], state["h"]
                    )
            else:
                self.in_panic = False

        if not action:
            action = Algs.get_max_reach_move(
                head, body_no_tail, state["w"], state["h"]
            )

        return action


def run_experiment():
    print("Snake-SHM v0.3.2: Final Engineering Consistency Check")

    results = {"Greedy": [], "Coase": []}

    for name, is_coase in [("Greedy", False), ("Coase", True)]:
        for seed in range(
            Config.SEED_START, Config.SEED_START + Config.N_SEEDS
        ):
            game = SnakeGame(seed)
            agent = BaseAgent(is_coase=is_coase)

            while not game.done and game.steps_total < Config.MAX_TOTAL_STEPS:
                action = agent.get_action(game)
                game.step(action)

            rescue_count = sum(
                1
                for p in agent.panic_history
                if game.steps_total - p >= Config.RESCUE_WINDOW
            )

            results[name].append(
                {
                    "steps": game.steps_total,
                    "len": len(game.snake),
                    "death": game.death,
                    "panics": len(agent.panic_history),
                    "rescues": rescue_count,
                }
            )

        res = results[name]
        avg_steps = np.mean([r["steps"] for r in res])
        avg_len = np.mean([r["len"] for r in res])
        total_p = sum(r["panics"] for r in res)
        total_r = sum(r["rescues"] for r in res)

        print(f"\n=== Agent: {name} ===")
        print(f"Survival Steps: {avg_steps:.1f} | Final Length: {avg_len:.2f}")
        print(
            f"Death Types: "
            f"{ {d: [r['death'] for r in res].count(d) for d in set(r['death'] for r in res)} }"
        )

        if is_coase:
            rate = (total_r / total_p * 100) if total_p > 0 else 0
            print(f"Rescue Rate (Episodes): {rate:.1f}% ({total_r}/{total_p})")


if __name__ == "__main__":
    run_experiment()
