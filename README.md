# Vacuum-X × Snake-SHM

**Risk Pricing and Survival–Efficiency Trade-offs in Embodied Agents**

---

## Overview

This repository contains **two minimal, self-contained embodied experimental systems**:

* **Vacuum-X** — a grid-based environment used to expose an explicit
  **efficiency–survival trade-off** under *fixed control logic*.
* **Snake-SHM** — a Snake-game-based environment used as **secondary embodied evidence**,
  demonstrating how *risk pricing* reshapes behavior style under spatial constraints.

Both systems are designed to study a single engineering principle:

> When future viability or actionable information is insufficient,
> **inaction (NOOP / PANIC / SURVIVAL mode) is a rational and necessary control output**,
> not a failure mode.

The repository is intentionally **small, deterministic, and CPU-only**,
prioritizing **auditability and reproducibility** over performance.

---

## Repository Structure

```text
vacuum-x-snake-shm/
├─ shared/
│  └─ terminology.md    # Canonical definitions (panic, NOOP, risk pricing)
│
├─ vacuum_x/            # Primary experimental system
│  ├─ src/              # Simulation & sweep logic
│  ├─ data/             # Recorded trajectories (benign / stress)
│  └─ figures/          # Final presentation figures
│
├─ snake_shm/           # Secondary validation system
│  ├─ src/              # Frozen implementations
│  ├─ data/             # Aggregated sweep results
│  └─ figures/          # Frontier visualization
│
└─ README.md            # (this file)
```

---

## Shared Terminology (Important)

Precise meanings of key terms such as **Panic**, **NOOP**, **Risk Pricing**,
and **Survival Mode** are **defined once and only once** in:

```
shared/terminology.md
```

All code and documentation in this repository **adhere strictly** to those definitions.
If an interpretation conflicts with `shared/terminology.md`, the terminology file **takes precedence**.

This is intentional, and treated as a **hard boundary**.

---

## Vacuum-X (Primary System)

**Vacuum-X** is the primary experimental artifact in this repository.

It introduces a single scalar parameter **α (risk pricing coefficient)** which:

* does **not** change the control structure,
* does **not** introduce new strategies,
* only modulates **how risk is priced** under identical logic.

### Design characteristics

* Fixed controller (no learning, no policy switching)
* Explicit **Life Pressure Index (LPI)** tracking accumulated stress
* Panic / NOOP treated as **valid control outputs**
* Sweeping α exposes a **Pareto frontier** between productive work and survival

### Core result

The α-sweep reveals a clear **efficiency–survival trade-off**:

* Lower α → higher useful work ratio, shorter survival
* Higher α → longer survival, lower useful work ratio

<p align="center">
  <img src="vacuum_x/figures/vacuum_x_frontier.png" width="650">
</p>

Additional crisis-handling statistics (reference only):

<p align="center">
  <img src="vacuum_x/figures/vacuum_x_rescue_stats.png" width="650">
</p>

> **Minimal interpretation:**
> Risk pricing alone is sufficient to induce qualitatively different survival behaviors,
> even when the controller itself is unchanged.

---

## Snake-SHM (Secondary Evidence)

**Snake-SHM** serves as **secondary embodied validation**, not as a performance benchmark.

It uses a Snake environment to examine how **risk pricing reshapes behavior style**
under strong spatial and temporal constraints.

### Scope and intent

* Identical control structure across all runs
* Only α (risk sensitivity) is varied
* No attempt to optimize for winning or score
* Focus is on **behavioral shift**, not task performance

<p align="center">
  <img src="snake_shm/figures/snake_sweep_frontier.png" width="650">
</p>

### Key observation

Snake-SHM exhibits a **continuous behavioral transition** rather than an optimum:

* Increasing α monotonically reduces panic frequency
* Survival time and growth decrease smoothly
* **Panic Mode / NOOP cycling** emerges as a *viable survival output* under extreme constraint,
  not as an error or instability

This contrast with Vacuum-X is deliberate:

* **Vacuum-X** exposes a trade-off frontier with a visible bend
* **Snake-SHM** demonstrates a monotone, style-shaping continuum

---

## What This Repository Is *Not*

To avoid misinterpretation, this repository is **not**:

* ❌ a reinforcement learning benchmark
* ❌ an alignment solution
* ❌ a policy optimization algorithm
* ❌ a claim about human cognition or psychology
* ❌ a claim about social, political, or economic systems

It is a **small engineering probe** for studying **failure boundaries and trade-offs**
under partial observability.

---

## Reproducibility

* Deterministic seeds
* CPU-only execution
* Minimal dependencies (standard Python scientific stack)
* All generated artifacts are written to `data/` and `figures/`
* No source-directory pollution

Each system can be run independently from its respective `src/` directory.

---

## Design Philosophy

This repository adheres to strict constraints:

* **Minimalism over completeness**
* **Negative results are acceptable**
* **NOOP / PANIC is a first-class control output**
* **Risk is priced, not eliminated**
* **Frozen code paths for auditability**

These constraints are deliberate and non-negotiable.

---

## Status

* **Vacuum-X**: Concluded & Frozen
  (frontier sweep complete; figures committed)
* **Snake-SHM**: Concluded & Frozen
  (clean sweep complete; figures committed)

No further mechanisms are planned for this repository.
It serves as a compact, auditable reference point for subsequent work that operates under the same design constraints.

---

## License

MIT License 

