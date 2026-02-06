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
    - network_proxy (15%) - proxy until follower data
    - consistency (10%) - proxy until timeseries
  - Penalty system for risk_level and red_flags
  - Explainable: drivers, concerns, recommendations
  - API: /api/connections/twitter-score/*

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

### P1 (High Priority) - Pending
- [ ] Twitter API integration (live data)
- [ ] Alert delivery (Telegram/Discord)

### P2 (Medium Priority) - In Progress
- [x] P2.2 Share Graph State
- [ ] ML-enhanced scoring
- [ ] Reddit Module
- [ ] News Module

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
