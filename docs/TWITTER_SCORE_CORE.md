# 🧠 TWITTER SCORE CORE — Phase 1 Documentation

## Overview

**Phase 1** implements the core intelligence layer for the Connections Module — a unified scoring system that doesn't depend on Twitter API but is architecturally ready for it.

> **Key Principle:** Build the brain first, connect data sources later.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     TWITTER SCORE CORE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Phase 1.1: UNIFIED TWITTER SCORE                               │
│  ─────────────────────────────────                              │
│  • Single 0-1000 score (like credit score)                     │
│  • Grade: D / C / B / A / S                                    │
│  • Confidence: LOW / MED / HIGH                                │
│  • Explainable components                                       │
│                                                                 │
│  Phase 1.2: AUDIENCE QUALITY ENGINE                             │
│  ────────────────────────────────────                           │
│  • Purity score (low overlap + low bot risk)                   │
│  • Smart followers proxy                                        │
│  • Bot share detection                                          │
│  • Ready for real follower data                                 │
│                                                                 │
│  Phase 1.3: HOPS / SOCIAL DISTANCE                              │
│  ──────────────────────────────────                             │
│  • BFS shortest path (1-3 hops)                                │
│  • Authority proximity score                                    │
│  • "2 handshakes to whale"                                     │
│  • Network influence propagation                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

# Phase 1.1: Unified Twitter Score

## Concept

A single, explainable score (0-1000) that aggregates all Connections metrics into one number — like a "credit score" for Twitter accounts.

## Formula

```
Twitter Score = Σ(component × weight) × (1 - penalty)

Components:
├── influence (35%) — base engagement/reach
├── quality (20%) — x_score + signal/noise
├── trend (20%) — velocity + acceleration  
├── network (15%) — audience_quality + authority_proximity
└── consistency (10%) — behavioral stability

Penalties:
├── risk_level: LOW=0%, MED=10%, HIGH=25%
└── red_flags: per-flag penalties (5-15% each)
```

## Grade System

| Grade | Score Range | Description |
|-------|-------------|-------------|
| **S** | 850-1000 | Top-tier, highly credible |
| **A** | 700-849 | Strong, sustainable influence |
| **B** | 550-699 | Good, growth potential |
| **C** | 400-549 | Average, improvements needed |
| **D** | 0-399 | High risk or low signal |

## Confidence Levels

| Level | Requirements |
|-------|--------------|
| **HIGH** | base_influence + x_score + velocity + acceleration |
| **MED** | base_influence + x_score |
| **LOW** | Missing core metrics |

## API Endpoints

### Compute Score
```http
POST /api/connections/twitter-score
Content-Type: application/json

{
  "account_id": "test_001",
  "base_influence": 650,
  "x_score": 580,
  "signal_noise": 6.5,
  "velocity": 15,
  "acceleration": 8,
  "risk_level": "LOW",
  "red_flags": [],
  "early_signal_badge": "rising",
  "audience_quality_score_0_1": 0.75,
  "authority_proximity_score_0_1": 0.50
}
```

Response:
```json
{
  "ok": true,
  "data": {
    "account_id": "test_001",
    "twitter_score_1000": 642,
    "grade": "B",
    "confidence": "HIGH",
    "components": {
      "influence": 0.65,
      "quality": 0.61,
      "trend": 0.61,
      "network_proxy": 0.66,
      "consistency": 0.55,
      "risk_penalty": 0
    },
    "explain": {
      "summary": "Good account with growth potential...",
      "drivers": ["Positive dynamics", "Strong network signal"],
      "concerns": [],
      "recommendations": []
    }
  }
}
```

### Other Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/connections/twitter-score` | POST | Compute single score |
| `/api/connections/twitter-score/batch` | POST | Batch compute (max 100) |
| `/api/connections/twitter-score/mock` | GET | Test examples |
| `/api/connections/twitter-score/info` | GET | Version and weights |
| `/api/connections/twitter-score/config` | GET | Current config |
| `/api/connections/twitter-score/config` | PUT | Update config (admin) |

## Configuration

File: `backend/src/modules/connections/core/twitter-score/twitter-score.config.ts`

```typescript
export const twitterScoreConfig = {
  version: "1.0.0",
  
  weights: {
    influence: 0.35,
    quality: 0.20,
    trend: 0.20,
    network_proxy: 0.15,
    consistency: 0.10,
  },
  
  penalties: {
    risk_level: { LOW: 0, MED: 0.10, HIGH: 0.25 },
    red_flags: {
      LIKE_HEAVY: 0.05,
      REPOST_FARM: 0.12,
      BOT_LIKE_PATTERN: 0.15,
      // ...
    },
    max_total_penalty: 0.35,
  },
  
  grades: [
    { grade: "S", min: 850 },
    { grade: "A", min: 700 },
    { grade: "B", min: 550 },
    { grade: "C", min: 400 },
    { grade: "D", min: 0 },
  ],
};
```

---

# Phase 1.2: Audience Quality Engine

## Concept

Assess **quality** of an account's audience without Twitter API — using proxy signals from existing data. Ready for real follower data later.

## Formula

```
Audience Quality = Σ(component × weight)

Components:
├── purity (45%) — 1 - (overlap_pressure + bot_risk)
├── smart_followers_proxy (30%) — signal quality + purity
├── signal_quality (15%) — x_score + signal/noise
└── consistency (10%) — behavioral stability

Bot Risk = Σ(red_flag_penalties)
├── AUDIENCE_OVERLAP: 0.20
├── BOT_LIKE_PATTERN: 0.30
├── REPOST_FARM: 0.25
├── VIRAL_SPIKE: 0.10
└── LIKE_HEAVY: 0.10
```

## Output Fields

| Field | Range | Description |
|-------|-------|-------------|
| `audience_quality_score_0_1` | 0-1 | Main quality score |
| `smart_followers_score_0_1` | 0-1 | Proxy for smart followers |
| `top_followers_count` | 0 | Placeholder (Twitter later) |
| `tier1_share_0_1` | 0.5 | Neutral (Twitter later) |
| `bot_share_0_1` | 0-1 | Bot risk estimate |
| `audience_purity_score_0_1` | 0-1 | Purity score |

## API Endpoints

### Compute Audience Quality
```http
POST /api/connections/audience-quality
Content-Type: application/json

{
  "account_id": "test_001",
  "x_score": 720,
  "signal_noise": 7.5,
  "consistency_0_1": 0.65,
  "red_flags": ["VIRAL_SPIKE"],
  "overlap": {
    "avg_jaccard": 0.06,
    "max_jaccard": 0.14,
    "avg_shared": 18,
    "max_shared": 42,
    "sample_size": 9
  }
}
```

### Other Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/connections/audience-quality` | POST | Compute quality |
| `/api/connections/audience-quality/batch` | POST | Batch (max 100) |
| `/api/connections/audience-quality/mock` | GET | Test examples |
| `/api/connections/audience-quality/info` | GET | Version and weights |
| `/api/connections/audience-quality/config` | GET | Current config |

### Admin Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/admin/connections/audience-quality/config` | GET | Get config |
| `/api/admin/connections/audience-quality/config` | PATCH | Update weights |
| `/api/admin/connections/audience-quality/red-flags` | GET | Get penalties |
| `/api/admin/connections/audience-quality/red-flags` | PUT | Update penalties |

## Integration with Twitter Score

Audience Quality feeds into Twitter Score:
```typescript
// In twitter-score.engine.ts
const network01 = 0.65 * audience_quality + 0.35 * authority_proximity;
```

---

# Phase 1.3: Hops / Social Distance Engine

## Concept

Understand **social distance** — "how many handshakes to strong nodes?"

This is the core of the original vision:
> "If Elon Musk follows you — that changes everything"

## Algorithm

**BFS (Breadth-First Search)** to find shortest paths:

1. Start from account
2. Explore neighbors (edges with strength > threshold)
3. Track path + bottleneck strength
4. Stop at max_hops (1-3)
5. Calculate proximity to top nodes

## Formula

```
Authority Proximity = Σ(hop_weight[h] × path_mix) / top_nodes_count

hop_weight = { 1: 1.00, 2: 0.65, 3: 0.40 }
path_mix = (1 - strength_weight) + strength_weight × path_strength
strength_weight = 0.35
```

## Output

```json
{
  "account_id": "test_account",
  "summary": {
    "max_hops": 3,
    "reachable_top_nodes": 3,
    "min_hops_to_any_top": 2,
    "avg_hops_to_reached_top": 2.33,
    "closest_top_targets": [
      { "target_id": "whale_alpha", "hops": 2, "path_strength_0_1": 0.58 },
      { "target_id": "influencer_001", "hops": 3, "path_strength_0_1": 0.50 }
    ],
    "authority_proximity_score_0_1": 0.48,
    "confidence": "MED"
  },
  "paths_to_top": [
    { "hops": 2, "path": ["test_account", "connector_001", "whale_alpha"], "path_strength_0_1": 0.58 }
  ],
  "explain": {
    "summary": "Account is well-embedded in the network of strong nodes.",
    "drivers": ["2 hops to top nodes", "Reaches 3 strong nodes"],
    "recommendations": ["Connect follow-edges (Twitter) for accurate paths"]
  }
}
```

## API Endpoints

### Compute Hops
```http
POST /api/connections/hops
Content-Type: application/json

{
  "account_id": "test_account",
  "max_hops": 3,
  "top_nodes": {
    "mode": "top_n",
    "top_n": 20,
    "score_field": "twitter_score"
  },
  "edge_min_strength": 0.35,
  "include_weak_edges": false
}
```

### Other Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/connections/hops` | POST | Compute paths |
| `/api/connections/hops/batch` | POST | Batch (max 50) |
| `/api/connections/hops/mock` | GET | Test examples |
| `/api/connections/hops/info` | GET | Version and scoring |
| `/api/connections/hops/config` | GET | Current config |

### Admin Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/admin/connections/hops/config` | GET | Get config |
| `/api/admin/connections/hops/config` | PATCH | Update params |
| `/api/admin/connections/hops/scoring` | GET | Scoring weights |

## Integration with Twitter Score

Hops feeds into Twitter Score:
```typescript
// In twitter-score.engine.ts
const network01 = 0.65 * audience_quality + 0.35 * authority_proximity;
```

---

# File Structure

```
backend/src/modules/connections/
├── contracts/
│   ├── twitter-score.contracts.ts      # Phase 1.1
│   ├── audience-quality.contracts.ts   # Phase 1.2
│   └── hops.contracts.ts               # Phase 1.3
│
├── core/
│   ├── twitter-score/
│   │   ├── twitter-score.config.ts
│   │   ├── twitter-score.math.ts
│   │   ├── twitter-score.engine.ts
│   │   └── index.ts
│   │
│   ├── audience-quality/
│   │   ├── audience-quality.config.ts
│   │   ├── audience-quality.math.ts
│   │   ├── audience-quality.engine.ts
│   │   ├── audience-quality.explain.ts
│   │   └── index.ts
│   │
│   └── hops/
│       ├── hops.config.ts
│       ├── hops.graph-adapter.ts
│       ├── hops.engine.ts
│       └── index.ts
│
├── api/
│   ├── twitter-score.routes.ts
│   ├── audience-quality.routes.ts
│   └── hops.routes.ts
│
└── admin/
    ├── audience-quality-admin.routes.ts
    └── hops-admin.routes.ts
```

---

# Integration Summary

## How Everything Connects

```
                    ┌─────────────────────────┐
                    │    TWITTER SCORE        │
                    │       (0-1000)          │
                    └───────────┬─────────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          │                     │                     │
          ▼                     ▼                     ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│   Base Metrics  │   │  AUDIENCE       │   │  HOPS           │
│   (existing)    │   │  QUALITY        │   │  ENGINE         │
│                 │   │  (Phase 1.2)    │   │  (Phase 1.3)    │
│ • influence     │   │                 │   │                 │
│ • x_score       │   │ • purity        │   │ • proximity     │
│ • velocity      │   │ • bot_risk      │   │ • paths         │
│ • acceleration  │   │ • smart_proxy   │   │ • reachability  │
└─────────────────┘   └────────┬────────┘   └────────┬────────┘
                               │                     │
                               └──────────┬──────────┘
                                          │
                                          ▼
                               ┌─────────────────────┐
                               │   network_proxy     │
                               │   = 0.65 × AQ +     │
                               │     0.35 × Hops     │
                               └─────────────────────┘
```

## Twitter Score Composition

| Component | Weight | Source |
|-----------|--------|--------|
| influence | 35% | Base metrics |
| quality | 20% | x_score + signal_noise |
| trend | 20% | velocity + acceleration |
| **network** | 15% | **AQ (65%) + Hops (35%)** |
| consistency | 10% | Stability proxy |

---

# Why This Matters (Before Twitter)

## What We Built

1. **Unified Score** — single number everyone understands
2. **Audience Assessment** — quality not quantity
3. **Social Distance** — network influence propagation
4. **Full Explainability** — every score has reasons

## Ready for Twitter

When Twitter data arrives:
- `audience_quality` gets real follower analysis
- `hops` gets real follow edges
- `twitter_score` immediately improves
- **No code changes needed** — just data

## Original Vision Achieved

✅ "Who is really influential?" → Twitter Score
✅ "Is the audience real?" → Audience Quality  
✅ "How connected are they?" → Hops Engine
✅ "Why this score?" → Explain Layer

---

*Phase 1 Documentation v1.0*
*Connections Module — Twitter Score Core*
*Created: 2026-02-06*
