# Vacuum-X
**Risk-priced efficiency–survival trade-offs under fixed control logic**

---

## Purpose
Vacuum-X is a minimal embodied grid-world system designed to expose an explicit trade-off between:
* productive work
* survival duration

under fixed control logic, modulated solely by **risk pricing**.

Vacuum-X is the **primary evidentiary system** in this repository.
All secondary systems (e.g. Snake-SHM) exist only to corroborate its conclusions.

---

## Core Question (Restricted)
> How does risk pricing alone reshape behavior when
> control logic is fixed and future viability is bounded?

Vacuum-X does **not** attempt to find optimal policies or maximize reward.

---

## Environment Overview
Vacuum-X operates in a deterministic grid world with:
* spatial movement
* task completion (“useful work”)
* internal stress accumulation
* finite survivability

The agent must trade off:
1. continuing productive actions
2. versus entering safety / recovery behavior

Termination is inevitable under sustained stress.

---

## Control Structure (Frozen)
Across all runs:
* No learning
* No adaptation
* No policy switching
* No parameter-dependent branches

The controller is a single deterministic function class:
> **π(s; α)**

Where:
* code paths are identical for all α
* α only rescales sensitivity to accumulated risk
* no new actions, states, or heuristics are introduced

---

## Risk Pricing Parameter (α)
A single scalar parameter **α** is swept.

* α does **not** change control logic
* α does **not** add new behaviors
* α only rescales *how strongly risk influences admissible actions*

**Baseline Definition:**
> **α = 0.0** serves as the **greedy baseline** (risk-neutral control), representing standard efficiency-first behavior.

**Interpretation:**
* High α → risk is expensive → conservative behavior
* Low α → risk is cheap → aggressive behavior

α is the **only experimental degree of freedom**.

---

## Life Pressure Index (LPI)
Vacuum-X tracks an internal scalar stress signal: **Life Pressure Index (LPI)**.

LPI:
* accumulates under continued operation
* reflects proximity to failure / infeasibility
* is used solely for *viability assessment*, not optimization

LPI is **not** a reward signal and is **not** tuned to maximize any metric.

### Mathematical Formulation (Simplified)
To ensure auditability, the core risk dynamics are formally defined as:

```text
LPI[t] = decay * LPI[t-1] + (1 - decay) * Stress_Input

Effective_Risk_Cost = Estimated_Risk * (1 + alpha * LPI)

```

This explicitly defines LPI as a **state variable**, not a post-hoc label.

---

## Insufficiency (Operational Definition)

A state is flagged as **insufficient** when:

> internal risk signals (e.g. LPI) exceed a viability threshold such that
> **non-NOOP actions are no longer admissible** under controller safety constraints.

In such states, **Panic / NOOP** is intentionally emitted.
See `shared/terminology.md` for canonical definitions.

---

## Metrics Collected

Each run records:

* **Survival Steps**
Total steps before termination.
* **Useful Ratio**
Fraction of steps spent performing productive work
(i.e., not in Panic / NOOP).
* **Rescue / Recovery Events**
Instances where conservative behavior extends survival.

Metrics are **descriptive**, not optimized.

---

## Key Observation

Sweeping α produces a clean **efficiency–survival trade-off**:

* **Low α** → higher efficiency, shorter survival
* **High α** → lower efficiency, longer survival
* **Intermediate α** → visible frontier bend

This trade-off emerges **without changing control logic**.

---

## What Would Falsify This Result?

The core observation would be falsified if:

> In states flagged as insufficient,
> **non-NOOP actions consistently improve both survival and efficiency**
> without increasing accumulated risk.

No such regime was observed in the frozen experiments.

---

## Determinism & Reproducibility

* CPU-only
* Deterministic seeds
* No multiprocessing
* No stochastic resets
* All outputs written to `data/` and `figures/`

The audit target is **tag v1.0**.

---

## Interpretation Boundaries

Vacuum-X does **not** claim:

* optimality
* Pareto-optimality proofs
* generality beyond this environment
* normative decision-theoretic rationality

The term “rational” is used strictly as:

> **admissible under constraint**,
> not optimal under utility maximization.

---

## Status

**Concluded & Frozen**

* All α-sweeps completed
* Frontier figures committed
* No further mechanisms planned

Vacuum-X is retained as a reference measurement artifact.

