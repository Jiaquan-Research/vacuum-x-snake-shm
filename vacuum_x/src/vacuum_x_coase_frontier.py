"""
Vacuum-X v0.4 — Coase Frontier Probe (FROZEN)

Purpose
-------
Sweep Coase parameter α to expose the efficiency–survival frontier.
All behavior logic is IDENTICAL to Vacuum-X v0.3.
Only difference: α scales marginal price of risk.

α ∈ {0.2, 0.5, 0.8}
"""

import random
import numpy as np
from collections import deque, defaultdict

# ============================================================
# Config
# ============================================================

GRID_W = 12
GRID_H = 12
OBSTACLE_DENSITY = 0.25

N_SEEDS = 50
SEED_START = 1000
MAX_STEPS = 2000

SVD_WINDOW = 10
DEADLOCK_WINDOW = 12
RESCUE_WINDOW = 12

BASE_PANIC_TH = 0.8
BASE_LOW_BAT = 20
BAT_MAX = 60

GAIN_PANIC = 0.4
GAIN_BAT = 20.0
GAIN_BAT_PRESSURE = 0.25

LPI_RHO = 0.75

ALPHAS = [0.0, 0.5, 1.0, 2.0, 4.0]


# ============================================================
# Environment
# ============================================================

class VacuumWorld:
    def __init__(self, seed):
        random.seed(seed)
        self.grid = np.zeros((GRID_W, GRID_H), dtype=int)
        for x in range(GRID_W):
            for y in range(GRID_H):
                if random.random() < OBSTACLE_DENSITY:
                    self.grid[x, y] = 1
        self.grid[0, 0] = 0
        self.pos = (0, 0)
        self.battery = BAT_MAX
        self.steps = 0

    def step(self, action):
        x, y = self.pos
        dx, dy = 0, 0
        if action == "UP": dy = -1
        if action == "DOWN": dy = 1
        if action == "LEFT": dx = -1
        if action == "RIGHT": dx = 1

        nx, ny = x + dx, y + dy
        if 0 <= nx < GRID_W and 0 <= ny < GRID_H and self.grid[nx, ny] == 0:
            self.pos = (nx, ny)

        self.battery -= 1
        if self.pos == (0, 0):
            self.battery = BAT_MAX

        self.steps += 1

    def done(self):
        return self.battery <= 0 or self.steps >= MAX_STEPS


# ============================================================
# StructGate + LPI
# ============================================================

class StructGate:
    def __init__(self):
        self.hist = deque(maxlen=SVD_WINDOW)

    def update(self, pos):
        self.hist.append(pos)

    def risk(self):
        if len(self.hist) < 5:
            return 0.0
        pts = np.array(self.hist)
        pts = pts - pts.mean(axis=0)
        try:
            _, s, _ = np.linalg.svd(pts, full_matrices=False)
            if len(s) < 2:
                return 0.0
            entropy = s[1] / (s[0] + 1e-6)
            return 1.0 - min(entropy * 5.0, 1.0)
        except:
            return 0.0


class LPIMonitor:
    def __init__(self):
        self.H = 1.0
        self.LPI = 0.0

    def update(self, risk, forced=False):
        damage = 0.001 + 0.05 * risk
        if forced:
            damage += 0.1
        H_prev = self.H
        self.H = max(0.0, self.H - damage)
        dH = max(0.0, H_prev - self.H)
        raw = risk + dH
        self.LPI = LPI_RHO * self.LPI + (1 - LPI_RHO) * raw
        return self.LPI


# ============================================================
# Agent
# ============================================================

class CoaseAgent:
    def __init__(self, alpha):
        self.alpha = alpha
        self.sg = StructGate()
        self.lpi = LPIMonitor()
        self.mode = "NORMAL"
        self.deadlock_hist = deque(maxlen=DEADLOCK_WINDOW)
        self.panic_events = 0
        self.panic_saved = 0
        self.last_panic_step = None

    def choose(self, world: VacuumWorld):
        self.sg.update(world.pos)
        r = self.sg.risk()
        lpi = self.lpi.update(r)

        bat_ratio = 1.0 - world.battery / BAT_MAX

        panic_th = (
            BASE_PANIC_TH
            - self.alpha * GAIN_PANIC * lpi
            - self.alpha * GAIN_BAT_PRESSURE * bat_ratio
        )
        low_bat_th = BASE_LOW_BAT + self.alpha * GAIN_BAT * lpi

        if world.battery < low_bat_th:
            self.mode = "SURVIVAL"
        elif r > panic_th:
            if self.mode != "PANIC":
                self.panic_events += 1
                self.last_panic_step = world.steps
            self.mode = "PANIC"
        else:
            self.mode = "NORMAL"

        # rescue accounting
        if self.last_panic_step is not None:
            if world.steps - self.last_panic_step == RESCUE_WINDOW:
                if not world.done():
                    self.panic_saved += 1
                self.last_panic_step = None

        # actions
        if self.mode == "NORMAL":
            return random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
        if self.mode == "SURVIVAL":
            return "LEFT"
        return random.choice(["UP", "DOWN", "LEFT", "RIGHT"])


# ============================================================
# Experiment
# ============================================================

def run_alpha(alpha):
    steps = []
    useful = []
    panic = []
    saved = []

    for i in range(N_SEEDS):
        seed = SEED_START + i
        world = VacuumWorld(seed)
        agent = CoaseAgent(alpha)

        useful_steps = 0
        while not world.done():
            act = agent.choose(world)
            world.step(act)
            if agent.mode == "NORMAL":
                useful_steps += 1

        steps.append(world.steps)
        useful.append(useful_steps / max(1, world.steps))
        panic.append(agent.panic_events)
        saved.append(agent.panic_saved)

    return {
        "steps": np.mean(steps),
        "useful": np.mean(useful),
        "panic": np.mean(panic),
        "save_rate": np.sum(saved) / max(1, np.sum(panic)),
    }


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("\n=== Vacuum-X Coase Frontier v0.4 ===\n")

    for a in ALPHAS:
        r = run_alpha(a)
        print(
            f"α={a:.1f} | "
            f"AvgSteps={r['steps']:.1f} | "
            f"UsefulRatio={r['useful']:.3f} | "
            f"PanicAvg={r['panic']:.1f} | "
            f"RescueRate={r['save_rate']:.3f}"
        )
