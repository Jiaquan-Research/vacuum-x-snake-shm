# Terminology

**Canonical Definitions for Vacuum-X × Snake-SHM**

---

## Scope and Authority

This document defines the **canonical meanings** of key terms used across:

* Vacuum-X
* Snake-SHM
* Top-level repository documentation

**All code, figures, and README files MUST conform to the definitions here.**

If any description or interpretation elsewhere conflicts with this file,
**this document takes precedence**.

---

## Control Output Terms

### NORMAL (Normal Operation)

**Definition**
A control state in which the agent performs **task-directed, productive actions**.

**Characteristics**

* Advances task objectives (e.g., movement, collection, progress)
* Consumes resources in exchange for productive work
* Represents the system’s *intended operational mode*

**Notes**

* NORMAL does **not** imply safety
* NORMAL actions may still carry risk

---

### PANIC

**Definition**
A control output indicating **insufficient immediate viability** under current conditions.

**Characteristics**

* Triggered when perceived risk exceeds a threshold
* Suspends normal task-directed behavior
* Prioritizes short-term survivability over productivity

**Important Clarification**

* PANIC is **not an error state**
* PANIC is **not a failure**
* PANIC is a **deliberate control output**

PANIC may involve evasive movement, retreat, or repeated NOOP actions,
depending on the environment.

---

### NOOP (No Operation)

**Definition**
An explicit control output representing **intentional inaction**.

**Characteristics**

* Produces no direct task progress
* May conserve resources or avoid compounding risk
* Used when action is assessed as more harmful than inaction

**Notes**

* NOOP is **not equivalent to indecision**
* NOOP is treated as a **valid, first-class action**

In constrained environments, repeated NOOPs may appear cyclic;
this is considered an acceptable survival behavior.

---

### SURVIVAL MODE

**Definition**
A collective term referring to PANIC and/or NOOP-dominated behavior
aimed at **preserving viability rather than advancing tasks**.

**Characteristics**

* Reduced or zero productive output
* Focus on avoiding irreversible failure
* Temporarily overrides efficiency considerations

SURVIVAL MODE does not imply success or optimality;
it only indicates **risk-dominant control**.

---

## Risk and Pricing Terms

### Risk

**Definition**
A scalar or composite measure estimating the likelihood of
**irreversible failure** under current conditions.

**Notes**

* Risk is environment-specific
* Risk is **estimated**, not observed
* Risk does not directly dictate actions; it informs thresholds

---

### Risk Pricing

**Definition**
The process by which **risk estimates are weighted** when determining control outputs.

Risk pricing answers the question:

> *How expensive is risk relative to productive progress?*

Risk pricing does **not** eliminate risk;
it only determines how strongly risk influences decisions.

---

### α (Risk Pricing Coefficient)

**Definition**
A scalar parameter controlling the **marginal price of risk**.

**Properties**

* α does **not** change control logic
* α does **not** introduce new behaviors
* α only scales sensitivity to accumulated or estimated risk

**Interpretation**

* Low α → risk is cheap → aggressive behavior
* High α → risk is expensive → conservative behavior

α is the **only swept parameter** in the core experiments.

---

## Internal State Terms

### Life Pressure Index (LPI)

**Definition**
A scalar internal state tracking **accumulated stress and proximity to failure**.

**Characteristics**

* Aggregates recent risk exposure and structural damage
* Smoothed over time (e.g., EMA-like behavior)
* Does not directly select actions

**Role**
LPI influences **risk thresholds**, not decisions themselves.

It represents *pressure*, not reward, loss, or utility.

---

## Metrics and Observables

### Survival Steps

**Definition**
The total number of steps before termination.

---

### Useful Work Ratio

**Definition**
The fraction of steps spent in **NORMAL operation**.

**Notes**

* A high survival time with a low useful work ratio
  is considered low productivity
* Useful work is environment-specific but consistently defined

---

### Panic Count / Panic Ratio

**Definition**

* **Panic Count**: number of discrete panic episodes
* **Panic Ratio**: fraction of total steps spent in PANIC / SURVIVAL MODE

**Notes**

* Panic frequency and panic success are independent variables
* Fewer panic events do **not** imply greater stability

---

### Rescue Success Rate

**Definition**
The fraction of panic episodes that successfully return
to NORMAL operation.

**Notes**

* A system may panic often and still recover reliably
* A system may panic rarely and fail catastrophically

---

## Interpretation Boundaries

The terminology defined here supports **engineering-level analysis only**.

It does **not** imply:

* psychological states
* human decision-making analogies
* social, political, or economic interpretations

Any such mapping is **out of scope** for this repository.

---

## Status

This terminology file is **frozen**.

No new terms will be introduced without a corresponding
revision of all dependent documentation.


