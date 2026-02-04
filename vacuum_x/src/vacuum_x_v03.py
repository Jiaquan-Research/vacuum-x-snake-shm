"""
Vacuum-X v0.3 (ALIGNED): Coasean Synthesis + LPI + Rescue Metrics
-----------------------------------------------------------------
Goal:
- System A: Greedy/Random baseline (no self-monitoring)
- System B: StructGate + LPI (dynamic thresholds) + enhanced escape actions
- Provide auditable metrics:
  * Avg survival steps
  * Avg useful-move ratio
  * Deadlock time
  * Recharge cycles
  * Panic events + Rescue rate (panic actually helped)

Constraints:
- Zero-shot monitor (no learning)
- No heavy planning (no global map search)
- CPU-only

Author intent:
- Engineering demo showing "dynamic trade-off suppresses Goodhart-like trap"
"""

import random
from collections import deque, defaultdict
import numpy as np


# ---------------------------
# 0) Config
# ---------------------------
class Cfg:
    W = 12
    H = 12
    OBSTACLE_DENSITY = 0.25
    SEED_START = 1000
    N_SEEDS = 50

    BATTERY_MAX = 60
    LOW_BAT_BASE = 20            # base return-to-dock trigger
    PANIC_TH_BASE = 0.80         # base panic trigger
    ESCAPE_STEPS = 4             # escape burst length
    COOLDOWN_STEPS = 6           # post-escape cooldown (avoid chattering)

    # StructGate (trajectory SVD)
    SVD_WINDOW = 10
    SVD_GAIN = 5.0               # map entropy -> panic scale

    # LPI dynamics
    LPI_RHO = 0.75               # inertia (stress residue)
    DAMAGE_GAIN = 2.0            # damage rate -> LPI
    OVERRIDE_GAIN = 0.0          # reserved; keep 0 in Vacuum-X
    STEP_DECAY = 0.001           # slow health decay
    COLLAPSE_DECAY = 0.04        # decay due to deadlock indicator
    RECOVERY_GAIN = 0.06         # recover when at dock

    # Coasean pricing (dynamic thresholds)
    HUNGER_GAIN_BAT = 20.0       # LPI raises battery threshold (more conservative)
    HUNGER_GAIN_PANIC = 0.40     # LPI lowers panic threshold (more sensitive)
    BAT_PRESSURE_GAIN = 0.25     # low battery directly lowers panic threshold a bit

    # Deadlock / productivity proxy
    STUCK_RADIUS = 0             # "not moved" counts as stuck
    STUCK_WINDOW = 12            # for deadlock scoring
    RESCUE_WINDOW = 12           # after panic event, evaluate rescue success

    # Enhanced escape: choose action maximizing local free-space estimate
    LOCAL_REACH_DEPTH = 30       # BFS budget on grid for reachability (still tiny)


# ---------------------------
# 1) Grid world
# ---------------------------
ACTIONS = ["UP", "DOWN", "LEFT", "RIGHT", "STAY"]
DIRS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
    "STAY": (0, 0),
}


class VacuumWorld:
    def __init__(self, seed: int):
        random.seed(seed)
        np.random.seed(seed)
        self.w = Cfg.W
        self.h = Cfg.H
        self.grid = np.zeros((self.w, self.h), dtype=np.int8)  # 0 free, 1 obstacle

        # dock fixed for comparability
        self.dock = (0, 0)

        # place obstacles
        n_cells = self.w * self.h
        n_obs = int(n_cells * Cfg.OBSTACLE_DENSITY)
        placed = 0
        while placed < n_obs:
            x = random.randrange(self.w)
            y = random.randrange(self.h)
            if (x, y) == self.dock:
                continue
            if self.grid[x, y] == 0:
                self.grid[x, y] = 1
                placed += 1

        # spawn agent
        while True:
            x = random.randrange(self.w)
            y = random.randrange(self.h)
            if self.grid[x, y] == 0 and (x, y) != self.dock:
                self.pos = (x, y)
                break

        self.battery = Cfg.BATTERY_MAX
        self.steps = 0
        self.recharge_cycles = 0

    def in_bounds(self, p):
        x, y = p
        return 0 <= x < self.w and 0 <= y < self.h

    def is_free(self, p):
        x, y = p
        return self.in_bounds(p) and self.grid[x, y] == 0

    def step(self, action: str):
        self.steps += 1
        x, y = self.pos
        dx, dy = DIRS[action]
        np_ = (x + dx, y + dy)

        moved = False
        if self.is_free(np_):
            self.pos = np_
            moved = (np_ != (x, y))

        # battery
        if self.pos == self.dock:
            if self.battery < Cfg.BATTERY_MAX:
                self.recharge_cycles += 1
            self.battery = Cfg.BATTERY_MAX
        else:
            self.battery -= 1

        done = self.battery <= 0
        return {
            "pos": self.pos,
            "battery": self.battery,
            "dock": self.dock,
            "moved": moved,
            "done": done,
        }


# ---------------------------
# 2) Helpers: reachability
# ---------------------------
def local_reachable_count(world: VacuumWorld, start, max_expand=Cfg.LOCAL_REACH_DEPTH):
    """Tiny BFS to estimate how much free space head can reach (budgeted)."""
    q = deque([start])
    vis = {start}
    expanded = 0
    while q and expanded < max_expand:
        p = q.popleft()
        expanded += 1
        x, y = p
        for a in ["UP", "DOWN", "LEFT", "RIGHT"]:
            dx, dy = DIRS[a]
            np_ = (x + dx, y + dy)
            if np_ in vis:
                continue
            if world.is_free(np_):
                vis.add(np_)
                q.append(np_)
    return len(vis)


def choose_escape_action(world: VacuumWorld):
    """Enhanced escape: pick action maximizing local reachable free space."""
    best = None
    best_score = -1
    for a in ["UP", "DOWN", "LEFT", "RIGHT"]:
        x, y = world.pos
        dx, dy = DIRS[a]
        np_ = (x + dx, y + dy)
        if not world.is_free(np_):
            continue
        score = local_reachable_count(world, np_)
        if score > best_score:
            best_score = score
            best = a
    if best is None:
        # if boxed, allow STAY (will be counted as stuck)
        return "STAY"
    return best


def greedy_to_dock_action(world: VacuumWorld):
    """Simple homing (no global planning): move towards dock greedily."""
    px, py = world.pos
    tx, ty = world.dock
    cand = []
    if tx > px:
        cand.append("RIGHT")
    if tx < px:
        cand.append("LEFT")
    if ty > py:
        cand.append("DOWN")
    if ty < py:
        cand.append("UP")
    random.shuffle(cand)
    for a in cand:
        dx, dy = DIRS[a]
        np_ = (px + dx, py + dy)
        if world.is_free(np_):
            return a
    # fallback
    return random.choice(["UP", "DOWN", "LEFT", "RIGHT", "STAY"])


# ---------------------------
# 3) StructGate: SVD trajectory panic
# ---------------------------
class StructGate:
    def __init__(self, window=Cfg.SVD_WINDOW):
        self.hist = deque(maxlen=window)

    def update(self, pos):
        self.hist.append(pos)

    def panic(self):
        if len(self.hist) < self.hist.maxlen:
            return 0.0
        pts = np.array(self.hist, dtype=float)
        pts = pts - pts.mean(axis=0, keepdims=True)
        try:
            _, s, _ = np.linalg.svd(pts, full_matrices=False)
            if len(s) < 2:
                return 0.0
            entropy = s[1] / (s[0] + 1e-6)  # in [0,1] roughly
            # map: low entropy => high panic
            p = 1.0 - min(entropy * Cfg.SVD_GAIN, 1.0)
            return float(np.clip(p, 0.0, 1.0))
        except Exception:
            return 0.0


# ---------------------------
# 4) LPI monitor: health + stress residue
# ---------------------------
class LPIMonitor:
    def __init__(self):
        self.H = 1.0
        self.lpi = 0.0

    def update(self, d_t, is_safe: bool):
        # health dynamics
        H_prev = self.H
        delta_H = -Cfg.STEP_DECAY - (Cfg.COLLAPSE_DECAY * d_t)
        if is_safe:
            delta_H += Cfg.RECOVERY_GAIN

        self.H = float(np.clip(self.H + delta_H, 0.0, 1.0))

        # only damage counts into stress
        damage = max(0.0, H_prev - self.H)
        lpi_raw = (Cfg.DAMAGE_GAIN * damage)  # u_t term reserved but unused here

        # inertia / residue
        self.lpi = Cfg.LPI_RHO * self.lpi + (1 - Cfg.LPI_RHO) * lpi_raw
        return self.lpi, self.H, damage


# ---------------------------
# 5) Agents
# ---------------------------
class AgentA_Baseline:
    """
    Baseline: random walk + greedy homing when very low battery.
    (Intentionally "dumb": no self-monitoring.)
    """

    def __init__(self):
        self.mode = "NORMAL"

    def act(self, world: VacuumWorld, _state_cache=None):
        if world.battery < Cfg.LOW_BAT_BASE:
            self.mode = "SURVIVAL"
            return greedy_to_dock_action(world), {"mode": self.mode}
        self.mode = "NORMAL"
        return random.choice(["UP", "DOWN", "LEFT", "RIGHT"]), {"mode": self.mode}


class AgentB_StructGate:
    """
    StructGate + Coasean pricing:
    - Computes panic d_t from trajectory SVD
    - Computes LPI from damage
    - Dynamic thresholds:
        panic_th = base - lpi*gain - battery_pressure_gain*(1-bat_ratio)
        bat_th   = base + lpi*gain
    - Mode machine with cooldown
    - Enhanced escape action selection to maximize local reachability
    """

    def __init__(self):
        self.gate = StructGate()
        self.mon = LPIMonitor()
        self.mode = "NORMAL"
        self.escape_timer = 0
        self.cooldown = 0

        # Rescue accounting
        self.pending_rescue = None  # dict: {"t":int, "start_risk":float, "start_pos":(x,y)}
        self.panic_events = 0
        self.panic_saved = 0
        self.risk_drop_events = 0
        self.risk_drop_success = 0

    def _dynamic_thresholds(self, lpi, battery):
        bat_ratio = battery / float(Cfg.BATTERY_MAX)
        # “饥饿/资源压力”直接提高风险容忍度（更敢冒险），但 LPI（受损）让它更保守
        battery_pressure = (1.0 - bat_ratio)  # 0..1
        panic_th = Cfg.PANIC_TH_BASE - (lpi * Cfg.HUNGER_GAIN_PANIC) - (Cfg.BAT_PRESSURE_GAIN * battery_pressure)
        panic_th = float(np.clip(panic_th, 0.20, 0.95))

        bat_th = Cfg.LOW_BAT_BASE + (lpi * Cfg.HUNGER_GAIN_BAT)
        bat_th = float(np.clip(bat_th, 5.0, Cfg.BATTERY_MAX - 1))
        return panic_th, bat_th

    def act(self, world: VacuumWorld, state_cache: dict):
        # update monitors
        self.gate.update(world.pos)
        d_t = self.gate.panic()
        lpi, H, dmg = self.mon.update(d_t, is_safe=(world.pos == world.dock))

        panic_th, bat_th = self._dynamic_thresholds(lpi, world.battery)

        # rescue window update: after some steps, decide success
        t = state_cache["t"]
        if self.pending_rescue is not None:
            if t - self.pending_rescue["t"] >= Cfg.RESCUE_WINDOW:
                # success if risk meaningfully dropped OR agent moved out of stuck loop
                start_risk = self.pending_rescue["start_risk"]
                now_risk = d_t
                self.risk_drop_events += 1
                if now_risk < start_risk - 0.15:
                    self.risk_drop_success += 1
                # define "saved": not dead and risk not saturated
                self.panic_saved += 1  # survived the rescue window by definition here (battery not 0)
                self.pending_rescue = None

        # mode machine
        if self.cooldown > 0:
            self.cooldown -= 1

        target_mode = self.mode

        # battery survival has priority
        if world.battery < bat_th:
            target_mode = "SURVIVAL"

        # panic/escape triggers only if not in cooldown and not already escaping
        if target_mode == "NORMAL" and self.cooldown == 0 and d_t >= panic_th:
            target_mode = "ESCAPE"
            self.escape_timer = Cfg.ESCAPE_STEPS
            self.cooldown = Cfg.COOLDOWN_STEPS

            # start rescue accounting
            self.panic_events += 1
            self.pending_rescue = {"t": t, "start_risk": d_t, "start_pos": world.pos}

        if self.mode == "ESCAPE":
            if self.escape_timer <= 0:
                target_mode = "NORMAL"

        self.mode = target_mode

        # action selection
        if self.mode == "SURVIVAL":
            a = greedy_to_dock_action(world)
        elif self.mode == "ESCAPE":
            a = choose_escape_action(world)
            self.escape_timer -= 1
        else:
            # Normal: mild exploration but avoid STAY
            a = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])

        info = {
            "mode": self.mode,
            "panic": d_t,
            "lpi": lpi,
            "H": H,
            "panic_th": panic_th,
            "bat_th": bat_th,
        }
        return a, info


# ---------------------------
# 6) Experiment
# ---------------------------
def run_single(agent_type: str, seed: int, max_steps=2000):
    world = VacuumWorld(seed)
    if agent_type == "A":
        agent = AgentA_Baseline()
    else:
        agent = AgentB_StructGate()

    # productivity proxy: moved ratio and stuck time
    moved_hist = deque(maxlen=Cfg.STUCK_WINDOW)
    deadlock_steps = 0
    useful_moves = 0

    for t in range(max_steps):
        state_cache = {"t": t}
        a, info = agent.act(world, state_cache)
        res = world.step(a)

        moved_hist.append(1 if res["moved"] else 0)
        if res["moved"]:
            useful_moves += 1

        # deadlock proxy: too many no-moves in window
        if len(moved_hist) == moved_hist.maxlen and sum(moved_hist) == 0:
            deadlock_steps += 1

        if res["done"]:
            break

    out = {
        "seed": seed,
        "steps": world.steps,
        "battery_end": world.battery,
        "recharge_cycles": world.recharge_cycles,
        "deadlock_steps": deadlock_steps,
        "useful_ratio": useful_moves / max(1, world.steps),
    }

    if agent_type == "B":
        out.update({
            "panic_events": agent.panic_events,
            "panic_saved": agent.panic_saved,
            "risk_drop_events": agent.risk_drop_events,
            "risk_drop_success": agent.risk_drop_success,
        })
    else:
        out.update({
            "panic_events": 0,
            "panic_saved": 0,
            "risk_drop_events": 0,
            "risk_drop_success": 0,
        })
    return out


def summarize(rows):
    def avg(k):
        return sum(r[k] for r in rows) / len(rows)

    s = {
        "avg_steps": avg("steps"),
        "avg_recharge": avg("recharge_cycles"),
        "avg_deadlock": avg("deadlock_steps"),
        "avg_useful": avg("useful_ratio"),
    }
    # rescue metrics
    pe = sum(r["panic_events"] for r in rows)
    ps = sum(r["panic_saved"] for r in rows)
    rde = sum(r["risk_drop_events"] for r in rows)
    rds = sum(r["risk_drop_success"] for r in rows)

    s["panic_events"] = pe
    s["panic_saved"] = ps
    s["panic_save_rate"] = (ps / pe) if pe > 0 else 0.0
    s["risk_drop_rate"] = (rds / rde) if rde > 0 else 0.0
    return s


def run_experiment():
    print("=== Vacuum-X v0.3 (ALIGNED) ===")
    print(f"Grid {Cfg.W}x{Cfg.H} | Seeds={Cfg.N_SEEDS} start={Cfg.SEED_START}")
    print(f"Obstacle density={Cfg.OBSTACLE_DENSITY}")
    print(f"SVD window={Cfg.SVD_WINDOW} | PanicTh base={Cfg.PANIC_TH_BASE} | LowBat base={Cfg.LOW_BAT_BASE}")
    print(f"LPI rho={Cfg.LPI_RHO} | Coase gains: bat+{Cfg.HUNGER_GAIN_BAT}, panic-{Cfg.HUNGER_GAIN_PANIC}, bat_pressure-{Cfg.BAT_PRESSURE_GAIN}")
    print(f"RescueWindow={Cfg.RESCUE_WINDOW} | DeadlockWindow={Cfg.STUCK_WINDOW}")
    print()

    seeds = list(range(Cfg.SEED_START, Cfg.SEED_START + Cfg.N_SEEDS))

    A = [run_single("A", s) for s in seeds]
    B = [run_single("B", s) for s in seeds]

    sa = summarize(A)
    sb = summarize(B)

    print("=== Agent A (Baseline) ===")
    print(f"N={len(A)}")
    print(f"Avg Steps         : {sa['avg_steps']:.1f}")
    print(f"Avg Recharge Cycles: {sa['avg_recharge']:.2f}")
    print(f"Avg Deadlock Steps : {sa['avg_deadlock']:.2f}")
    print(f"Avg Useful Ratio   : {sa['avg_useful']:.3f}")
    print()

    print("=== Agent B (StructGate + LPI + Coase) ===")
    print(f"N={len(B)}")
    print(f"Avg Steps         : {sb['avg_steps']:.1f}")
    print(f"Avg Recharge Cycles: {sb['avg_recharge']:.2f}")
    print(f"Avg Deadlock Steps : {sb['avg_deadlock']:.2f}")
    print(f"Avg Useful Ratio   : {sb['avg_useful']:.3f}")
    print(f"Panic Events Total : {sb['panic_events']}")
    print(f"Panic Saved Total  : {sb['panic_saved']}")
    print(f"Panic Save Rate    : {sb['panic_save_rate']:.3f}")
    print(f"Risk Drop Rate     : {sb['risk_drop_rate']:.3f}")
    print()

    print("=== Delta (B - A) ===")
    print(f"dSteps      : {sb['avg_steps'] - sa['avg_steps']:+.1f}")
    print(f"dRecharge   : {sb['avg_recharge'] - sa['avg_recharge']:+.2f}")
    print(f"dDeadlock   : {sb['avg_deadlock'] - sa['avg_deadlock']:+.2f}")
    print(f"dUsefulRatio: {sb['avg_useful'] - sa['avg_useful']:+.3f}")
    print()

    print("Sample (first 5 seeds):")
    print("seed | A_steps A_rechg A_deadlk A_use || B_steps B_rechg B_deadlk B_use | panic ev saved")
    for rA, rB in zip(A[:5], B[:5]):
        print(f"{rA['seed']} | "
              f"{rA['steps']:6d} {rA['recharge_cycles']:7d} {rA['deadlock_steps']:7d} {rA['useful_ratio']:.2f} || "
              f"{rB['steps']:6d} {rB['recharge_cycles']:7d} {rB['deadlock_steps']:7d} {rB['useful_ratio']:.2f} | "
              f"{rB['panic_events']:4d} {rB['panic_saved']:5d}")


if __name__ == "__main__":
    run_experiment()
