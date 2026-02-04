# Vacuum-X × Snake-SHM

**Minimal embodied probes for risk pricing and efficiency–survival trade-offs under fixed control logic**

---

## Overview

This repository contains **two minimal embodied experimental systems** designed to probe a single control-theoretic question:

> **When future viability or actionable information is insufficient, inaction
> (NOOP / Panic) can be a valid and necessary control output — not an error mode.**

The repository is intentionally scoped as a **frozen engineering artifact**:

* no learning
* no optimization
* no policy search
* no theoretical generalization claims

Its purpose is **measurement and exposure**, not solution design.

---

## Systems Included

### Vacuum-X (Primary System)

A grid-world vacuum-like environment exposing an explicit **efficiency–survival trade-off frontier** under fixed control logic.

* Explicit internal stress tracking (Life Pressure Index, LPI)
* Risk-priced decision threshold controlled by a single scalar parameter α
* Clear Pareto-like trade-off between productive work and survival duration

Vacuum-X is the **primary evidentiary system** in this repository.

---

### Snake-SHM (Secondary System)

A minimal Snake-based environment used as **secondary embodied corroboration**.

* Same fixed control structure
* No learning, no planning, no policy switching
* Strong spatial constraints and inevitable termination

Snake-SHM exists to demonstrate that **risk pricing alone reshapes behavioral style**, even when optimization is impossible and no efficiency–survival “sweet spot” exists.

---

## Core Principle (Restricted Claim)

The repository supports **only** the following restricted statement:

> Under fixed control logic and bounded observability,
> **risk pricing alone is sufficient to reshape behavior**,
> and **inaction (NOOP / Panic) is a valid admissible control output
> when future viability is insufficient**.

No claims are made regarding:

* optimality
* learning
* general intelligence
* alignment solutions
* real-world deployment

---

## Operational Definitions (Entry-Level Contract)

The following definitions are **non-negotiable invariants** used throughout the repository.
Canonical definitions live in [`shared/terminology.md`](./shared/terminology.md).

* **NOOP**
  An explicit action output that produces no state-changing effect except time advance.

* **Panic**
  A controller state indicating insufficient future viability; in this state, NOOP is intentionally emitted.

* **Risk Pricing (α)**
  A scalar coefficient that rescales sensitivity to accumulated risk signals.
  α does **not** introduce new behaviors or code paths.

* **Insufficiency (Operational)**
  A condition where internal risk signals exceed a viability threshold such that non-NOOP actions are no longer admissible under the controller’s safety constraints.

> If an interpretation conflicts with `shared/terminology.md`,
> **the terminology file takes precedence**.

---

## What Would Falsify the Core Claim?

The central claim would be falsified **within these systems** if:

* In states flagged as insufficient,
  **non-NOOP actions consistently improve survival or efficiency**
  without increasing accumulated risk.

No such regime was observed in the frozen experiments.

---

## Control Structure (Frozen)

Across **all runs in both systems**:

* No learning
* No adaptation
* No policy switching
* No parameter-dependent logic branches

The controller is a **single deterministic function class**:

```
π(s; α)
```

Where:

* the code paths are fixed
* α only rescales an existing risk term
* no new state variables are introduced

Changing α changes **risk sensitivity**, not controller structure.

---

## Determinism & Reproducibility Contract

* CPU-only execution
* Deterministic seeds
* No multiprocessing
* No stochastic environment resets
* Outputs written deterministically to `data/` and `figures/`

The audit target is **tag `v1.0`**, which is frozen.

---

## Interpretation Boundaries

This repository **does not** demonstrate:

* optimal policies
* Pareto-optimality proofs
* normative rationality (utility maximization)
* generalization beyond these environments

The term *“rational”* is used **strictly in a control-theoretic sense**:

> *admissible under constraint*,
> not *optimal under a utility function*.

---

## Why Two Systems?

* **Vacuum-X** exposes a visible efficiency–survival trade-off frontier.
* **Snake-SHM** exhibits a monotone behavioral style continuum with no optimum.

The contrast is deliberate:

> risk pricing reshapes behavior differently depending on environmental structure,
> yet the **admissibility of NOOP / Panic under insufficiency remains invariant**.

---

## Repository Structure

```
vacuum-x-snake-shm/
├── README.md                # This file (root contract)
├── shared/
│   └── terminology.md       # Canonical definitions (constitutional layer)
├── vacuum_x/                # Primary system
│   ├── README.md
│   ├── src/
│   ├── data/
│   └── figures/
└── snake_shm/               # Secondary corroboration system
    ├── README.md
    ├── src/
    ├── data/
    └── figures/
```

---

## Status

**Project Concluded & Frozen**

* All experiments complete
* All figures committed
* No further mechanisms planned

This repository is retained as a **foundational reference artifact** for subsequent work.

---

## What This Repository Is Not

* Not a reinforcement learning project
* Not an optimization benchmark
* Not an alignment solution
* Not a theoretical proof
* Not a product prototype

It is an **engineering probe** designed to make structural trade-offs visible.


