# Vacuum-X × Snake-SHM
**Minimal embodied probes for risk pricing and efficiency–survival trade-offs under fixed control logic**

---

## Overview
This repository contains two minimal embodied experimental systems designed to probe a single control-theoretic question:

> When future viability or actionable information is insufficient,  
> inaction (**NOOP / Panic**) can be a **valid and necessary control output**.

This repository is intentionally scoped as a **frozen engineering artifact**:
- no learning
- no optimization
- no policy search
- no generalization claims

Purpose: **measurement and exposure**, not solution design.

---

## Systems Included

### Vacuum-X (Primary System)
A grid-world vacuum-like environment exposing an explicit **efficiency–survival trade-off** under fixed control logic.

- Explicit internal stress accumulation (**Life Pressure Index, LPI**)
- Risk-priced decision threshold controlled by scalar **α**
- Observable trade-off between productive work and survival duration

**Vacuum-X is the primary evidentiary system.**

---

### Snake-SHM (Secondary System)
A minimal Snake-based environment used for **secondary embodied corroboration**.

- Identical fixed control structure
- Strong spatial constraint
- Practically inevitable termination

Snake-SHM exists to show that **risk pricing reshapes behavioral style**
even when no efficiency–survival optimum exists.

---

## Restricted Claim

The repository supports **only** the following statement:

> Under fixed control logic and bounded observability,  
> **risk pricing alone reshapes behavior**,  
> and NOOP / Panic are **admissible control outputs** under insufficiency.

No claims are made regarding:
- optimality
- learning
- intelligence
- alignment solutions
- real-world deployment

---

## Operational Definitions (Contract)

Canonical definitions live in `shared/terminology.md`.

### NOOP
An explicit action producing no state change except time advance.

### Panic
A controller state indicating insufficient future viability;  
in this state, NOOP is intentionally emitted.

### Risk Pricing (α)
A scalar coefficient that rescales sensitivity to accumulated risk.

- α does **not** introduce new action types
- α does **not** introduce new code branches
- All actions exist for all α; only trigger frequency changes

**Baseline**
> **α = 0.0** is the greedy, risk-neutral baseline where risk is unpriced.

### Insufficiency
A condition where internal risk exceeds a viability threshold such that
non-NOOP actions are no longer admissible.

**LPI Math**
> See `vacuum_x/README.md` for the decay-based accumulation formula.

If interpretations conflict, `shared/terminology.md` takes precedence.

---

## Falsification Criterion

The core claim would be falsified **within these systems** if:

> In states flagged as insufficient,  
> **non-NOOP actions consistently improve survival or efficiency**  
> without increasing accumulated risk.

No such regime was observed.

---

## Control Structure (Frozen)

Across all systems and runs:

- No learning
- No adaptation
- No policy switching
- No parameter-dependent branches

Single deterministic controller:

> **π(s; α)**

α rescales risk sensitivity only; logic is invariant.

---

## Determinism & Reproducibility

- CPU-only
- Deterministic seeds
- No multiprocessing
- No stochastic resets
- Deterministic outputs to `data/` and `figures/`

Audit target: **tag v1.1** (frozen).

---

## Interpretation Boundaries

This repository does **not** demonstrate:
- Pareto optimality
- Utility maximization
- Rational choice theory
- Generalization

“Rational” is used strictly as:
> **admissible under constraint**

---

## Why Two Systems?

- Vacuum-X: exposes a visible efficiency–survival trade-off
- Snake-SHM: exhibits monotone behavioral style without an optimum

The invariance:  
**NOOP / Panic admissibility under insufficiency**.

---

## Status

**Concluded & Frozen**

- Experiments complete
- Figures committed
- No further mechanisms planned

---

## What This Repository Is Not

- Not RL
- Not optimization
- Not alignment solution
- Not product prototype

It is an **engineering probe**.
