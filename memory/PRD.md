# Connections Module - PRD

## Original Problem Statement
Развернуть проект Connections Module с GitHub (https://github.com/svetlanaslinko057/e5e5e5e) - изолированный модуль платформы для формирования справедливого рейтинга инфлюенсеров в социальных сетях (Twitter и др.).

## Architecture
```
/app/
├── backend/
│   ├── server.py                   # Python FastAPI proxy (port 8001)
│   └── src/
│       ├── server-minimal.ts       # Node.js Fastify (port 8003)
│       └── modules/connections/
│           ├── api/                # Core API routes
│           ├── share/              # P2.2: Graph State Share
│           ├── notifications/      # Telegram alerts
│           └── admin/              # Admin config
├── frontend/
│   └── src/
│       └── pages/
│           └── ConnectionsInfluenceGraphPage.jsx  # Graph with Share
└── docs/                           # Documentation
```

## User Personas
1. **Analyst** - использует Connections для анализа инфлюенсеров
2. **Admin** - управляет настройками через Admin Panel

## Core Requirements (Static)
- [x] Influence Scoring - quality-adjusted score
- [x] Trend Analysis - velocity + acceleration
- [x] Early Signal Detection - breakout/rising signals
- [x] Risk Detection - накрутка/боты
- [x] Admin Panel - авторизация, управление
- [x] Mock Mode - работа без внешних API

## What's Been Implemented
- **2026-02-06**: Initial deployment from GitHub
  - Cloned repository
  - Configured .env files (MongoDB, Telegram token)
  - Installed dependencies (yarn)
  - Backend: Node.js Fastify + Python proxy running
  - Frontend: React app running
  - Added test accounts
  - All API endpoints tested (18/18 passing)
  - Frontend pages verified (Connections, Radar, Admin)
  - Removed Russian text from Connections UI

- **2026-02-06**: P2.2 Share Graph State
  - Backend encode/decode API endpoints
  - GraphState v1 schema with normalization
  - Frontend buildGraphState/applyGraphState helpers
  - URL sync with replaceState (no history pollution)
  - Share button with clipboard copy
  - Telegram templates with Graph links
  - Admin config: graph_share_enabled toggle

- **2026-02-06**: **PHASE 1.1 - Unified Twitter Score v1.0**
  - Twitter Score Engine (0-1000 scale)
  - Grade system: S (850+) / A (700+) / B (550+) / C (400+) / D (<400)
  - Confidence levels: LOW / MED / HIGH
  - Weighted components:
    - influence (35%) - base engagement/reach
    - quality (20%) - x_score + signal/noise
    - trend (20%) - velocity + acceleration
    - network_proxy (15%) - now uses audience_quality when available
    - consistency (10%) - proxy until timeseries
  - Penalty system for risk_level and red_flags
  - Explainable: drivers, concerns, recommendations
  - API: /api/connections/twitter-score/*

- **2026-02-06**: **PHASE 1.2 - Audience Quality Engine v1.0**
  - Audience quality assessment with proxy signals
  - Components:
    - purity (45%) - inverse of overlap + bot risk
    - smart_followers_proxy (30%) - signal quality + purity
    - signal_quality (15%) - x_score + signal/noise
    - consistency (10%) - behavioral consistency
  - Overlap pressure calculation from jaccard + shared engaged ids
  - Bot risk from red flags (AUDIENCE_OVERLAP, BOT_LIKE_PATTERN, REPOST_FARM, etc.)
  - Integrated into Twitter Score (replaces network_proxy)
  - Admin config for weights and thresholds
  - API: /api/connections/audience-quality/*

- **2026-02-06**: **PHASE 1.3 - Hops / Social Distance Engine v1.0**
  - BFS shortest path algorithm (1-3 hops)
  - Authority proximity score calculation
  - Components:
    - hop_weight: {1: 1.0, 2: 0.65, 3: 0.40}
    - strength_weight: 0.35 (path bottleneck contribution)
  - Summary includes:
    - reachable_top_nodes
    - min_hops_to_any_top
    - closest_top_targets (with hops + strength)
    - authority_proximity_score_0_1
  - Integrated into Twitter Score:
    - network = 0.65*audience_quality + 0.35*authority_proximity
  - Explain layer: "2 hops to whale_alpha"
  - Admin config for scoring/confidence
  - API: /api/connections/hops/*

## P2.2 Share Graph State - Contract

### GraphState v1 Schema
```typescript
interface GraphStateV1 {
  version: '1.0';
  filters?: {
    profiles?: string[];
    early_signal?: string[];
    risk_level?: string[];
    edge_strength?: string[];
    hide_isolated?: boolean;
    limit_nodes?: number;
  };
  selected_nodes?: string[];
  compare?: { left?: string; right?: string; active?: boolean } | null;
  view?: 'graph' | 'table' | 'compare';
  sort?: { field?: string; order?: 'asc' | 'desc' };
  focus?: string;
}
```

### API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/connections/graph/state/encode | POST | Encode state to URL-safe base64 |
| /api/connections/graph/state/decode | POST | Decode base64 back to state |
| /api/connections/graph/state/info | GET | Version and capabilities info |

## Prioritized Backlog
### P0 (Critical) - Done
- [x] Backend deployment
- [x] Frontend deployment  
- [x] MongoDB connection
- [x] Admin authentication

### PHASE 1 - Twitter Score Core - COMPLETE ✅
- [x] **1.1 Unified Twitter Score v1.0** - DONE
- [x] **1.2 Audience Quality Engine v1.0** - DONE
- [x] **1.3 Hops / Social Distance v1.0** - DONE

### PHASE 2 - Time & Behavior Analytics
- [ ] 2.1 Time Series Storage (scaffold)
- [ ] 2.2 Charts & Timelines UI

### PHASE 3 - AI Intelligence Layer
- [ ] 3.1 AI Summary Engine (LLM analysis)

### P2 (Medium Priority) - Done
- [x] P2.2 Share Graph State

### Future
- [ ] Twitter API Integration (after Phase 1 complete)
- [ ] Reddit/News Modules

## Credentials
- Admin: `admin` / `admin12345`
- Telegram Bot Token: Configured in .env

## URLs
- Connections: `/connections`
- Graph: `/connections/graph`
- Radar: `/connections/radar`
- Admin: `/admin/connections`

## Next Tasks
1. Test Share links in different browsers
2. Add Inline Keyboard buttons to Telegram alerts
3. Configure Twitter API for live data
