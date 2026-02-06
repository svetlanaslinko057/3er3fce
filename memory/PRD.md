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
│       └── modules/connections/    # Connections Module
├── frontend/
│   └── src/
│       └── pages/                  # React pages (port 3000)
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
  - Added 3 test accounts (crypto_whale, alpha_hunter, defi_expert)
  - All API endpoints tested (18/18 passing)
  - Frontend pages verified (Connections, Radar, Admin)

## Prioritized Backlog
### P0 (Critical) - Done
- [x] Backend deployment
- [x] Frontend deployment  
- [x] MongoDB connection
- [x] Admin authentication

### P1 (High Priority) - Pending
- [ ] Twitter API integration (live data)
- [ ] Alert delivery (Telegram/Discord)

### P2 (Medium Priority) - Backlog
- [ ] ML-enhanced scoring
- [ ] Reddit Module
- [ ] News Module

## API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/health | GET | System health |
| /api/connections/health | GET | Module health |
| /api/connections/accounts | GET | List accounts |
| /api/connections/score | POST | Calculate score |
| /api/connections/trends | POST | Trend analysis |
| /api/connections/early-signal | POST | Early signals |
| /api/admin/auth/login | POST | Admin login |
| /api/admin/connections/overview | GET | Admin overview |

## Credentials
- Admin: `admin` / `admin12345`
- Telegram Bot Token: Configured in .env

## URLs
- Connections: http://localhost:3000/connections
- Radar: http://localhost:3000/connections/radar
- Admin: http://localhost:3000/admin/connections

## Next Tasks
1. Test Alerts Engine via Admin Panel
2. Configure Telegram delivery when needed
3. Twitter API integration for live data
