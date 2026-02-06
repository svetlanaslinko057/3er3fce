# Connections Module - PRD

## Original Problem Statement
Реализовать полноценный **Influence Graph** как продуктовый экран в Connections модуле:
- Backend Graph API с contracts, builder, config
- Frontend с ForceGraphCore, фильтрами, suggestions, selection
- Admin config для управления параметрами графа
- **БЕЗ TWITTER** - на mock/Mongo данных

## Архитектура

### Navigation
```
Sidebar:
└── Connections (dropdown)
    ├── Influencers → /connections
    ├── Graph → /connections/graph  ← НОВЫЙ ЭКРАН
    └── Radar → /connections/radar
```

### Backend Structure
```
/backend/src/modules/connections/
├── contracts/
│   └── graph.contracts.ts       ← P0.1 ✅
├── core/graph/
│   ├── graph-config.ts          ← P0.2 ✅
│   ├── graph-scoring.ts         ← P0.2 ✅
│   └── build-graph.ts           ← P0.2 ✅
├── api/
│   └── graph.routes.ts          ← P0.3 ✅
└── admin/
    └── graph-admin.routes.ts    ← P0.4 ✅
```

## P0 - Backend Graph API ✅ DONE

### P0.1 Contracts ✅
- `GraphNode`, `GraphEdge`, `ConnectionsGraphResponse`
- `GraphFiltersSchema`, `GraphConfig`
- Zod schemas для валидации

### P0.2 Graph Builder ✅
- `buildConnectionsGraph()` - собирает граф из MongoDB
- `computeEdgeWeight()` - расчёт веса рёбер
- Pairwise overlap calculation
- Mock data generators

### P0.3 Endpoints ✅
- `GET /api/connections/graph` - граф с фильтрами
- `GET /api/connections/graph/suggestions` - рекомендации
- `GET /api/connections/graph/filters` - schema для UI
- `GET /api/connections/graph/mock` - тестовые данные
- `GET /api/connections/graph/node/:id` - детали узла
- `GET /api/connections/graph/ranking` - таблица ранкинга

### P0.4 Admin Config ✅
- `GET /api/admin/connections/graph/config`
- `PATCH /api/admin/connections/graph/config`
- `GET /api/admin/connections/graph/stats`

## P1 - Frontend Graph UI (IN PROGRESS)

### P1.1 Навигация ✅
- Connections dropdown с 3 вкладками
- Tabs: Influencers | Graph | Radar

### P1.2 Graph Canvas ✅
- ForceGraphCore визуализация
- 30 nodes, 233 edges
- Drag/zoom/pan

### P1.3 Filter Modal 🔜
- Schema-driven (из /graph/filters API)
- Nodes: followers, influence, profile, risk, early signal
- Edges: min_jaccard, min_shared, strength

### P1.4 Suggestions Panel 🔜
- "Explore suggestions" из /graph/suggestions
- Быстрое переключение seed

### P1.5 Node Selection → Compare 🔜
- Side panel при клике
- Compare modal integration

## P2 - Product Polish (TODO)
- Admin UI секция Graph
- Performance & caching
- Parity with old project

## Тестирование
- Backend API: 100%
- Frontend rendering: 100%
- Filter integration: pending
- Admin UI: pending

## MOCK данные
Граф работает на mock данных (generateMockAccounts). Twitter API НЕ требуется.

## Next Tasks
1. Реализовать Filter Modal (schema-driven)
2. Добавить Suggestions panel
3. Node Selection → Side Panel → Compare
4. Admin UI для graph config
