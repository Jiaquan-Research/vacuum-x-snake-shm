"""
Snake-SHM v0.3.4: The Clean Sweep (Frozen Secondary Evidence)
-------------------------------------------------------------
Architecture: Inheritance-based extension (No Monkey Patching).
Parameter: alpha scales 'Risk Hunger Gain' (Risk Pricing Sensitivity).
Target: Generate Secondary Evidence consistent with Vacuum-X narrative.

Engineering fixes in this version:
- Stable import from src/ regardless of CWD.
- Stable output paths: data/ and figures/ (no src pollution).
- Savefig quality: dpi=300 + tight_layout + close().
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ===== Stable project-relative paths (no CWD dependency) =====
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))          # .../snake_shm/src
PROJECT_ROOT = os.path.dirname(PROJECT_ROOT)                      # .../snake_shm

SRC_DIR = os.path.join(PROJECT_ROOT, "src")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
FIG_DIR = os.path.join(PROJECT_ROOT, "figures")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

# Ensure we can import v0.3.2 from src/ regardless of where the script is launched.
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Explicitly importing from the frozen v0.3.2 engineering edition
from snake_shm_v0_3_2 import Config, SnakeGame, BaseAgent, StructGate, Algs


# --- 1) Define the Sweep Agent (Inheritance, NOT Rewrite) ---
class SweepAgent(BaseAgent):
    """
    Extends BaseAgent to inject alpha parameter into the pricing logic.
    Strictly preserves System 1 (Motor) and System 1.5 (Escape) logic from v0.3.2.
    """

    def __init__(self, alpha: float):
        super().__init__(is_coase=True)  # Must be Coase to have pricing
        self.alpha = float(alpha)
        self.steps_in_panic = 0  # Metric: time spent in panic mode

    def get_action(self, game: SnakeGame):
        # --- Context Setup (Identical structure to BaseAgent) ---
        state = {
            "snake": list(game.snake),
            "food": game.food,
            "w": game.w,
            "h": game.h,
            "hunger": game.steps_since_food,
        }
        head = state["snake"][0]
        body_no_tail = state["snake"][:-1]

        # System 1: Default Greedy (Identical)
        action = Algs.bfs_path(head, state["food"], body_no_tail, state["w"], state["h"])

        # System 2: Coasean Pricing (ONLY injection point)
        risk = StructGate.analyze_risk(state["snake"], state["w"], state["h"])
        hunger_ratio = min(1.0, state["hunger"] / Config.MAX_STEPS_WITHOUT_FOOD)

        # === ALPHA INJECTION ===
        # alpha = 0.0 -> effective gain = 0 -> threshold stays at base -> panic earlier (more conservative)
        # alpha > 1.0 -> effective gain higher -> threshold grows with hunger -> panic later (more aggressive)
        effective_gain = Config.RISK_HUNGER_GAIN * self.alpha
        threshold = Config.RISK_THRESHOLD_BASE + (hunger_ratio * effective_gain)
        # =======================

        if risk >= threshold:
            # Strict copy of v0.3.2 logic to ensure consistency
            if not self.in_panic:
                self.panic_history.append(game.steps_total)  # episode start index
                self.in_panic = True

            # Escape Strategy (Identical)
            tail = state["snake"][-1]
            escape_move = Algs.bfs_path(head, tail, body_no_tail, state["w"], state["h"])
            if escape_move:
                action = escape_move
            else:
                action = Algs.get_max_reach_move(head, body_no_tail, state["w"], state["h"])
        else:
            self.in_panic = False

        # Metric Tracking (behavioral ratio)
        if self.in_panic:
            self.steps_in_panic += 1

        # System 1.5: Motor Floor (Identical)
        if not action:
            action = Algs.get_max_reach_move(head, body_no_tail, state["w"], state["h"])

        return action


# --- 2) Run the sweep ---
def run_clean_sweep():
    print("Starting Snake-SHM v0.3.4 Clean Sweep...")

    # Sweep parameters (secondary evidence only)
    alphas = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    n_seeds = 30  # keep small & consistent

    results = []

    for alpha in alphas:
        print(f"  > Testing alpha = {alpha}...")

        for seed in range(Config.SEED_START, Config.SEED_START + n_seeds):
            game = SnakeGame(seed)
            agent = SweepAgent(alpha=alpha)

            while not game.done and game.steps_total < Config.MAX_TOTAL_STEPS:
                action = agent.get_action(game)
                game.step(action)

            panic_ratio = (agent.steps_in_panic / game.steps_total) if game.steps_total > 0 else 0.0

            results.append({
                "alpha": alpha,
                "seed": seed,
                "steps": game.steps_total,
                "len": len(game.snake),
                "panic_ratio": panic_ratio,
                "death": game.death,
            })

    # --- 3) Save outputs (NO src pollution) ---
    df = pd.DataFrame(results)

    csv_path = os.path.join(DATA_DIR, "snake_clean_sweep.csv")
    df.to_csv(csv_path, index=False)

    # Aggregation for terminal output (consistency check)
    summary = df.groupby("alpha")[["steps", "panic_ratio", "len"]].mean()
    print("\n=== SWEEP RESULTS (Mean over seeds) ===")
    print(summary)

    # Frontier plot (minimal, no extra semantics)
    mean_panic = df.groupby("alpha")["panic_ratio"].mean()
    mean_steps = df.groupby("alpha")["steps"].mean()

    plt.figure(figsize=(8, 5))
    plt.scatter(mean_panic, mean_steps)
    plt.plot(mean_panic, mean_steps, linestyle="--", alpha=0.35)

    # annotate alpha values (lightweight)
    for a in alphas:
        x = float(mean_panic.loc[a])
        y = float(mean_steps.loc[a])
        plt.text(x, y, f"α={a}", fontsize=9, ha="left", va="bottom")

    plt.title("Snake-SHM Frontier (α Sweep)")
    plt.xlabel("Panic Mode Ratio")
    plt.ylabel("Survival Steps")
    plt.grid(alpha=0.15)
    plt.tight_layout()

    fig_path = os.path.join(FIG_DIR, "snake_sweep_frontier.png")
    plt.savefig(fig_path, dpi=300)
    plt.close()

    print(f"\nSaved CSV : {csv_path}")
    print(f"Saved Fig : {fig_path}")


if __name__ == "__main__":
    run_clean_sweep()
