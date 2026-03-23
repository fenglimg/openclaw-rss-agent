# X Integration Flow v1

How X signals should flow into the current evolution discovery system.

---

## Desired chain

```text
x-watchlist
  → collector
  → x-author-signals-v1.json
  → x-linked-objects-v1.json
  → x-candidate-boosts-v1.json
  → canonical object merge
  → source judgment / enrichment priority / editorial context
  → final calibrated outputs
```

---

## Stage 1 — watchlist collection

Input:
- `x-watchlist-v0`
- `x-watchlist-seeds-v0`

Output:
- watched-author post signals

---

## Stage 2 — canonicalization

Transform raw post links into durable canonical objects.

Examples:
- X post → GitHub repo
- X post → docs page
- X post → release note

Goal:
- prevent tweet objects from becoming the main durable unit

---

## Stage 3 — candidate boost layer

Use X-derived convergence signals to increase attention on canonical objects when:
- multiple trusted authors mention them
- posts cluster in a short time window
- posts link practical workflow/tooling artifacts

Effects:
- higher candidate priority
- earlier enrichment
- possible stronger follow pressure

---

## Stage 4 — editorial context layer

Use short post excerpts to answer:
- why is this suddenly worth attention?
- what practical value are builders seeing?
- what framing is emerging around this object?

This is especially useful for:
- applied briefs
- follow queues
- adoption notes

---

## Stage 5 — weak risk/evidence layer

If watched authors report:
- broken workflows
- low trust
- hype mismatch
- disappointing real usage

attach weak `risk/evidence` metadata to the canonical object.

This should dampen confidence, not dominate judgment by itself.

---

## What X should improve in the current system

### 1. earlier candidate generation
Surface objects before they become visible in slower sources.

### 2. better multi-signal blending
Add author-signal as one more signal lane.

### 3. stronger author weighting
Different authors should not count equally.

### 4. repeat-convergence detection
Repeated multi-author linking should trigger candidate boosts.

### 5. better editorial explanation
X often explains “why now” better than a bare repo title.

---

## What X should not replace

X should not replace:
- source packs
- GitHub / docs / release note validation
- source judgment
- calibration rules

It is an additional signal lane, not the whole system.
