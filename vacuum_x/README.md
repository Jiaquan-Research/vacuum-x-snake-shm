# Vacuum-X
**Primary embodied probe for efficiency–survival trade-offs under risk pricing**

---

## Purpose

Vacuum-X is the **primary evidentiary system** in this repository.

It exposes how a fixed controller behaves when:
- efficiency is rewarded
- survival is constrained
- future viability becomes insufficient

---

## Environment

- Grid-world vacuum-like task
- Limited energy and movement
- Explicit recharge location
- Deterministic dynamics

The agent must balance:
- productive work (cleaning)
- movement cost
- survival time

---

## Control Structure

- Fixed logic
- No learning
- No planning
- No policy switching

Controller form:

> **π(s; α)**

Where α rescales risk sensitivity only.

---

## Life Pressure Index (LPI)

LPI tracks accumulated stress and proximity to failure.

### Mathematical Formulation (Simplified)

```text
LPI[t] = decay * LPI[t-1] + (1 - decay) * Stress_Input[t]

Effective_Risk = Estimated_Risk * (1 + α * LPI[t])
````

* `decay ∈ (0,1)` smooths accumulation
* α rescales the influence of accumulated stress
* No new state variables introduced

---

## Risk Pricing Parameter (α)

* α does **not** change controller logic
* α does **not** add actions
* α only rescales risk sensitivity

**Baseline**

> α = 0.0 → greedy, risk-neutral control

Interpretation:

* Low α → aggressive, efficiency-first
* High α → conservative, survival-first

---

## Metrics

Collected per run:

* **Survival Steps**
* **Useful Work Ratio**

  * Fraction of steps in NORMAL operation
  * Excludes Panic / NOOP
* **Panic Ratio**
* **Total Cleaned Cells**

Metrics are environment-defined, not α-defined.

---

## Observations

α-sweep produces a **clear efficiency–survival trade-off**:

* Increasing α:

  * reduces productive work
  * increases early safety behavior
  * reshapes panic timing

No optimal α is claimed.

---

## Falsification

The observation would be falsified if:

> In insufficient states,
> non-NOOP actions improve both survival and productivity
> without increasing LPI.

No such behavior observed.

---

## Reproducibility

* Deterministic seeds
* CPU-only
* No stochastic resets
* Outputs committed under `data/` and `figures/`

---

## Status

Vacuum-X is **concluded and frozen**.

It serves as the **primary measurement instrument**.

