# Snake-SHM
**Risk-priced behavior shaping under spatial constraint**

---

## Purpose

Snake-SHM provides **secondary embodied corroboration**.

It demonstrates that:

> With fixed control logic,  
> **risk pricing alone reshapes behavioral style**,  
> even when optimization is impossible.

All primary claims are derived from **Vacuum-X**.

---

## Environment

- Classic Snake grid
- Deterministic dynamics
- Growing body length
- Collision-based termination

Termination is **practically inevitable**
due to finite space and growth mechanics.

---

## Control Structure

Identical across all runs:

- No learning
- No adaptation
- No policy switching
- No parameter-dependent branches

The agent operates with:
- greedy food-seeking baseline
- panic / survival mode under insufficiency

Panic / NOOP are **valid control outputs**, not errors.

---

## Risk Pricing Parameter (α)

Single scalar parameter swept.

> α controls how strongly accumulated risk influences panic thresholds.

Properties:
- No new actions introduced
- No logic changes
- Risk sensitivity only

**Interpretation**

- **High α** → risk priced expensive → conservative thresholds  
  → enter panic / survival mode more readily to preserve viability

- **Low α** → risk priced cheap → aggressive thresholds  
  → defer panic, prioritize growth

---

## Experimental Design

```text
α ∈ {0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0}
````

For each α:

* identical logic
* identical environment
* deterministic seeds

---

## Metrics

Collected per run:

* Survival Steps
* Final Length
* Panic Ratio

Metrics are minimal and non-optimized.

---

## Observed Behavior

α-sweep yields a **monotone style transition**:

* Increasing α:

  * increases panic frequency
  * reduces growth
  * shortens survival

There is **no optimal α**.

This is expected.

---

## Interpretation

Snake-SHM shows:

* Panic / NOOP can be **viable under constraint**
* Risk pricing reshapes *how* the agent survives,
  not *whether* it wins

Unlike Vacuum-X:

* No efficiency–survival sweet spot exists
* Behavior forms a continuous spectrum

---

## Boundaries

Supports only:

> Risk pricing reshapes behavior under fixed logic.

Does **not** support:

* optimality claims
* performance comparison
* transfer claims

---

## Reproducibility

* Deterministic seeds
* CPU-only
* Minimal dependencies
* Outputs in `data/` and `figures/`

---

## Status

Snake-SHM is **concluded and frozen**.

It exists solely as **secondary embodied evidence**.


